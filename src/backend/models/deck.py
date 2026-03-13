from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

if TYPE_CHECKING:
    from .card import Card
    from .user import User
    from .lecture import Lecture


class DeckBase(SQLModel):
    title: str
    description: str | None = None


class Deck(DeckBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="decks")

    cards: list["Card"] = Relationship(back_populates="deck")

    # lecture it belongs to
    lecture_id: int | None = Field(default=None, foreign_key="lecture.id")
    lecture: "Lecture" = Relationship(back_populates="deck")

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class DeckPublic(DeckBase):
    id: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class DeckCreate(DeckBase):
    user_id: int


class DeckDelete(SQLModel):
    id: int
