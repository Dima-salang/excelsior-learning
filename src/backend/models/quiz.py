from sqlmodel import SQLModel, Field
from models.card import Card
from datetime import datetime


class QuizBase(SQLModel):
    # deck id
    deck_id: int
    # time started
    time_started: datetime = Field(default_factory=datetime.now)
    # time spent
    time_spent: float = Field(default=0.0)
    # score
    score: float


class Quiz(QuizBase):
    # card queue (transient)
    cards: list["Card"]


class QuizDB(QuizBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
