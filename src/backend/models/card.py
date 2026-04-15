from typing import TYPE_CHECKING, Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, JSON
from pydantic import BaseModel


class CardStatus(str, Enum):
    UNANSWERED = "UNANSWERED"
    GREAT = "GREAT"
    MASTERED = "MASTERED"
    NOT_MASTERED = "NOT_MASTERED"


if TYPE_CHECKING:
    from .deck import Deck
    from .lecture_step import LectureStep
    from .quiz import Quiz


class CardType(str, Enum):
    MULTICHOICE = "multichoice"
    TRUEFALSE = "truefalse"


class CardBase(SQLModel):
    type: str
    front: str
    options: Optional[list[str]] = Field(default=None)
    options_ans: Optional[int] = Field(default=None)
    user_selected_ans: Optional[int] = Field(default=None)
    explanation: Optional[str] = Field(default=None)
    is_correct: Optional[bool] = Field(default=None)
    status: Optional[CardStatus] = Field(default=CardStatus.UNANSWERED)

    # sm-2
    repetition_count: int = Field(default=0)
    ease_factor: float = Field(default=1.3)
    day_interval: int = Field(default=1)
    next_review: datetime = Field(default_factory=datetime.now)


class Card(CardBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    options: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    deck_id: int | None = Field(default=None, foreign_key="deck.id", nullable=True)
    deck: "Deck" = Relationship(back_populates="cards")

    step_id: int | None = Field(
        default=None, foreign_key="lecturestep.id", nullable=True
    )
    step: "LectureStep" = Relationship(back_populates="cards")

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CardPublic(CardBase):
    id: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CardCreate(CardBase):
    deck_id: Optional[int] = None
    step_id: Optional[int] = None


class CardUpdate(SQLModel):
    user_selected_ans: Optional[int] = None
    is_correct: Optional[bool] = None


class CardDelete(SQLModel):
    id: int


class QuizCard(CardBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    options: list[str] | None = Field(default=None, sa_column=Column(JSON))
    card_id: int | None = Field(default=None, foreign_key="card.id")
    quiz_id: int | None = Field(default=None, foreign_key="quizdb.id")


class QuizCardPublic(CardBase):
    id: int
    card_id: int | None = None
    quiz_id: int | None = None


class CardList(BaseModel):
    cards: list[CardBase]
