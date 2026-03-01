from fastapi import FastAPI
from sqlmodel import SQLModel
from db.engine import engine
from api.llm import router as llm_router

app = FastAPI(
    title="Excelsior Learning", description="AI-powered lectures and flashcards"
)

# Register routers
app.include_router(llm_router)


@app.get("/")
async def root():
    return {"message": "Welcome to Excelsior Learning API"}


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
