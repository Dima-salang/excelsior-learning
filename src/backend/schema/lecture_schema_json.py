from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


# sort enum
class LectureSortEnum(str, Enum):
    ASCENDING = "ascending"
    DESCENDING = "descending"


class LectureLengthEnum(int, Enum):
    SHORT = 3
    MEDIUM = 6
    LONG = 10


# lecture filter schema
class LectureFilterSchema(BaseModel):
    title: Optional[str] = Field(default=None, description="Title of the lecture")
    description: Optional[str] = Field(
        default=None, description="Description of the lecture"
    )
    completion_percentage: Optional[int] = Field(
        default=None, description="Completion percentage of the lecture"
    )
    created_at: Optional[str] = Field(
        default=None, description="Creation date of the lecture"
    )
    last_accessed_at: Optional[str] = Field(
        default=None, description="Last accessed date of the lecture"
    )
    sort: Optional[LectureSortEnum] = Field(
        default=LectureSortEnum.DESCENDING, description="Sort order of the lecture"
    )
    limit: Optional[int] = Field(default=10, description="Limit of the lecture")
    offset: Optional[int] = Field(default=0, description="Offset of the lecture")


class StepFlashcardSchema(BaseModel):
    type: Literal["multichoice", "truefalse", "standard"] = Field(description="Type of flashcard: 'multichoice' or 'truefalse', or 'standard'")
    front: str = Field(description="The question or front of the flashcard")
    back: str = Field(description="The answer or back of the flashcard for the standard card type", default=None)
    options: Optional[list[str]] = Field(
        default=None, description="Options for multichoice cards and truefalse cards"
    )
    options_ans: Optional[int] = Field(
        default=None,
        description="Index of the correct option for multichoice cards and truefalse cards",
    )
    explanation: Optional[str] = Field(
        default=None, description="Explanation for the answer"
    )


class LectureStepSchema(BaseModel):
    title: str
    order_key: int = Field(description="Order key of the lecture step")
    content: Optional[str] = Field(
        default=None, description="Markdown content of the step"
    )
    flashcards: Optional[list[StepFlashcardSchema]] = Field(
        default=None, description="Flashcards for this step"
    )


class LectureSectionSchema(BaseModel):
    title: str = Field(description="Title of the section")
    order_key: int = Field(description="Order key of the lecture section")
    steps: list[LectureStepSchema] = Field(
        description="List of steps for this section. YOU MUST GENERATE A MINIMUM OF 5 STEPS PER SECTION."
    )


class LectureSchema(BaseModel):
    title: str = Field(description="Title of the lecture")
    description: str = Field(description="Brief overview of the lecture")
    sections: list[LectureSectionSchema] = Field(
        description="List of sections for the lecture. YOU MUST GENERATE A MINIMUM OF 10 SECTIONS."
    )
    cards: Optional[list[StepFlashcardSchema]] = Field(default=None)
