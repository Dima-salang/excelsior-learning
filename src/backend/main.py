import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from alembic.config import Config
from alembic import command
from api.llm import router as llm_router
from api.auth.auth import router as auth_router
from api.lectures import router as lectures_router
from api.decks import router as decks_router
from api.quiz import router as quiz_router
from typing import Annotated
from db.engine import engine
from core.logging_config import setup_logging

# Setup structured logging
setup_logging()

app = FastAPI(
    title="Excelsior Learning", description="AI-powered lectures and flashcards"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Register routers
app.include_router(llm_router)
app.include_router(auth_router)
app.include_router(lectures_router)
app.include_router(decks_router)
app.include_router(quiz_router)


@app.get("/")
async def root():
    return {"message": "Welcome to Excelsior Learning API"}


@app.get("/dashboard")
async def dashboard(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"message": "Welcome to Excelsior Learning API"}


@app.on_event("startup")
def on_startup():
    # Run migrations on startup using the app's engine to avoid locks
    alembic_cfg = Config("alembic.ini")
    with engine.begin() as connection:
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")
