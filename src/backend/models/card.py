from typing import TYPE_CHECKING, Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, JSON

if TYPE_CHECKING:
    from .deck import Deck
    from .lecture_step import LectureStep


class CardType(str, Enum):
    MULTICHOICE = "multichoice"
    TRUEFALSE = "truefalse"


class CardBase(SQLModel):
    type: str
    front: str
    options: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    options_ans: Optional[int] = Field(default=None)
    user_selected_ans: Optional[int] = Field(default=None)
    explanation: Optional[str] = Field(default=None)
    is_correct: Optional[bool] = Field(default=None)


class Card(CardBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    deck_id: int | None = Field(default=None, foreign_key="deck.id")
    deck: "Deck" = Relationship(back_populates="cards")

    step_id: int | None = Field(default=None, foreign_key="lecturestep.id")
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
