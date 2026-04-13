from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from models.card import QuizCard, QuizCardPublic
from datetime import datetime

if TYPE_CHECKING:
    from .deck import Deck


class QuizBase(SQLModel):
    # deck id
    deck_id: int = Field(foreign_key="deck.id")
    # user id
    user_id: int | None = Field(default=None, foreign_key="user.id")
    # time started
    time_started: datetime = Field(default_factory=datetime.now)
    # time spent
    time_spent: float = Field(default=0.0)
    # score
    score: float


class Quiz(QuizBase):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    # card queue (transient)
    cards: list["QuizCardPublic"] = []
    # deck title (optional for display)
    deck_title: str | None = None


class QuizDB(QuizBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    deck: "Deck" = Relationship()
