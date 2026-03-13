from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

if TYPE_CHECKING:
    from .lecture import Lecture
    from .lecture_step import LectureStep


class LectureSectionBase(SQLModel):
    title: str
    completion_percentage: float = Field(default=0.0)
    order_key: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class LectureSection(LectureSectionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    lecture_id: int | None = Field(default=None, foreign_key="lecture.id")
    lecture: "Lecture" = Relationship(back_populates="sections")

    steps: list["LectureStep"] = Relationship(back_populates="lecture_section")


class LectureSectionCreate(LectureSectionBase):
    lecture_id: int


class LectureSectionUpdate(LectureSectionBase):
    pass


class LectureSectionDelete(SQLModel):
    id: int
