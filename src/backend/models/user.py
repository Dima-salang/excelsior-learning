from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

if TYPE_CHECKING:
    from .lecture import Lecture
    from .deck import Deck


class UserBase(SQLModel):
    username: str
    email: str | None = None


class UserCreate(UserBase):
    password: str


class UserPublic(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    lectures: list["Lecture"] = Relationship(back_populates="user")
    decks: list["Deck"] = Relationship(back_populates="user")
