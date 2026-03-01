from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

if TYPE_CHECKING:
    from .card import Card
    from .user import User


class DeckBase(SQLModel):
    title: str
    description: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Deck(DeckBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="decks")

    cards: list["Card"] = Relationship(back_populates="deck")


class DeckPublic(DeckBase):
    id: int


class DeckCreate(DeckBase):
    user_id: int


class DeckDelete(SQLModel):
    id: int
