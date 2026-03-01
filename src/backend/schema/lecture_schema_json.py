from pydantic import BaseModel, Field


class LectureStepSchema(BaseModel):
    title: str
    order_key: int = Field(description="Order key of the lecture step")


class LectureSectionSchema(BaseModel):
    title: str
    order_key: int = Field(description="Order key of the lecture section")
    steps: list[LectureStepSchema]


class LectureSchema(BaseModel):
    title: str
    description: str
    sections: list[LectureSectionSchema]
