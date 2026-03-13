from pydantic import BaseModel, Field
from typing import Optional


class StepFlashcardSchema(BaseModel):
    type: str = Field(description="Type of flashcard: 'multichoice' or 'truefalse'")
    front: str = Field(description="The question or front of the flashcard")
    options: Optional[list[str]] = Field(
        default=None, description="Options for multichoice cards"
    )
    options_ans: Optional[int] = Field(
        default=None, description="Index of the correct option"
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
    title: str
    order_key: int = Field(description="Order key of the lecture section")
    steps: list[LectureStepSchema]


class LectureSchema(BaseModel):
    title: str
    description: str
    sections: list[LectureSectionSchema]
    flashcards: Optional[list[StepFlashcardSchema]] = Field(default=None)
