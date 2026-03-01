from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

if TYPE_CHECKING:
    from .lecture_section import LectureSection


class LectureStepBase(SQLModel):
    title: str
    content: str | None = None
    order_key: int = Field(default=0)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class LectureStep(LectureStepBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    lecture_section_id: int = Field(foreign_key="lecturesection.id")
    lecture_section: "LectureSection" = Relationship(back_populates="steps")


class LectureStepPublic(LectureStepBase):
    id: int


class LectureStepCreate(LectureStepBase):
    lecture_section_id: int


class LectureStepDelete(SQLModel):
    id: int
