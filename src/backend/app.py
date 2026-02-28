from fastapi import FastAPI
from sqlmodel import SQLModel
from db.engine import engine

app = FastAPI(title="Excelsior Learning", description="AI-powered lectures and flashcards")


@app.get("/")
async def root():
    return {"Hello": "World"}


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)