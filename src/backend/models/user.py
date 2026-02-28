from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from .lecture import Lecture

class UserBase(SQLModel):
    username: str
    email: str | None = None
    password: str


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    lectures: list["Lecture"] = Relationship(back_populates="user")
