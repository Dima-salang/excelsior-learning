import os
import logging
import traceback

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from pydantic import ValidationError
from alembic.config import Config
from alembic import command
from api.llm import router as llm_router
from api.auth.auth import router as auth_router
from api.lectures import router as lectures_router
from api.decks import router as decks_router
from api.quiz import router as quiz_router
from api.chat.chat import router as chat_router
from typing import Annotated
from sqlalchemy import text
from db.engine import engine
from core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("excelsior")

app = FastAPI(
    title="Excelsior Learning", description="AI-powered lectures and flashcards"
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP {exc.status_code} on {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.error(
        f"Validation error on {request.url.path}:\n"
        f"  Errors: {exc.errors()}\n"
        f"  Traceback: {traceback.format_exc()}"
    )
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception on {request.url.path}:\n"
        f"  Type: {type(exc).__name__}\n"
        f"  Message: {str(exc)}\n"
        f"  Traceback: {traceback.format_exc()}"
    )
    debug_mode = os.getenv("DEBUG", "").lower() in ("1", "true", "yes")
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"{type(exc).__name__}: {str(exc)}"
            if debug_mode
            else "Internal server error"
        },
    )


app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://excelsior-learning.vercel.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

app.include_router(llm_router)
app.include_router(auth_router)
app.include_router(lectures_router)
app.include_router(decks_router)
app.include_router(quiz_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    logger.info("GET /")
    return {"message": "Welcome to Excelsior Learning API"}


@app.get("/dashboard")
async def dashboard(token: Annotated[str, Depends(oauth2_scheme)]):
    logger.info("GET /dashboard")
    return {"message": "Welcome to Excelsior Learning API"}


async def check_database():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            connection.commit()
        return True
    except Exception:
        return False


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ready")
async def ready():
    db_ok = await check_database()
    if not db_ok:
        raise HTTPException(status_code=503, detail="Database not ready")
    return {"status": "ok", "database": "ready"}


@app.on_event("startup")
def on_startup():
    logger.info("Starting Excelsior Learning API...")
    alembic_cfg = Config("alembic.ini")
    with engine.begin() as connection:
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")
    logger.info("Database migrations complete")
