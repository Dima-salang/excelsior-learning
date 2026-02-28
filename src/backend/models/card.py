from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from .deck import Deck

class CardBase(SQLModel):
    front: str
    back: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Card(CardBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    deck_id: int = Field(foreign_key="deck.id")
    deck: Deck = Relationship(back_populates="cards")


class CardPublic(CardBase):
    id: int


class CardCreate(CardBase):
    deck_id: int


class CardDelete(SQLModel):
    id: int