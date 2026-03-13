from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

if TYPE_CHECKING:
    from .lecture_section import LectureSection
    from .card import Card


class LectureStepBase(SQLModel):
    title: str
    content: str | None = None
    order_key: int = Field(default=0)
    completed: bool = Field(default=False, alias="is_completed")

    @property
    def is_completed(self) -> bool:
        return self.completed

    @is_completed.setter
    def is_completed(self, value: bool):
        self.completed = value

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True


class LectureStep(LectureStepBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    lecture_section_id: int = Field(foreign_key="lecturesection.id")
    lecture_section: "LectureSection" = Relationship(back_populates="steps")

    cards: list["Card"] = Relationship(back_populates="step")


class LectureStepCreate(LectureStepBase):
    lecture_section_id: int


class LectureStepUpdate(LectureStepBase):
    pass


class LectureStepDelete(SQLModel):
    id: int
