from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from .user import User
from .lecture_section import LectureSection

class LectureBase(SQLModel):
    title: str
    description: Optional[str] = None
    completion_percentage: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Lecture(LectureBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    user: User = Relationship(back_populates="lectures")

    sections: list["LectureSection"] = Relationship(back_populates="lecture")


class LecturePublic(LectureBase):
    id: int


class LectureCreate(LectureBase):
    user_id: int


class LectureDelete(SQLModel):
    id: int
