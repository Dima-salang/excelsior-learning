from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

from .lecture_section import LectureSectionBase
from .lecture_step import LectureStepBase
from .card import CardPublic

if TYPE_CHECKING:
    from .user import User
    from .lecture_section import LectureSection
    from .deck import Deck


class LectureBase(SQLModel):
    title: str
    description: Optional[str] = None
    completion_percentage: float = Field(default=0.0)
    last_accessed_at: datetime = Field(default_factory=datetime.now)


class Lecture(LectureBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    user: "User" = Relationship(back_populates="lectures")

    sections: list["LectureSection"] = Relationship(back_populates="lecture")

    # deck
    deck: "Deck" = Relationship(back_populates="lecture")

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class LectureStepPublic(LectureStepBase):
    id: int
    cards: list["CardPublic"] = []

    class Config:
        from_attributes = True
        populate_by_name = True


class LectureSectionPublic(LectureSectionBase):
    id: int
    steps: list[LectureStepPublic] = []

    class Config:
        from_attributes = True


class LecturePublic(LectureBase):
    id: int
    sections: list[LectureSectionPublic] = []

    class Config:
        from_attributes = True


class LectureCreate(LectureBase):
    user_id: int


class LectureUpdate(LectureBase):
    id: int


class LectureDelete(SQLModel):
    id: int
