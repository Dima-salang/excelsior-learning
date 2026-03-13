from sqlmodel import Session
from models.lecture import (
    Lecture,
    LectureCreate,
    LecturePublic,
    LectureUpdate,
    LectureSectionPublic,
    LectureStepPublic,
)
from models.lecture_section import (
    LectureSection,
    LectureSectionCreate,
    LectureSectionUpdate,
)
from models.lecture_step import LectureStep, LectureStepCreate, LectureStepUpdate
from fastapi import HTTPException


class LectureService:
    def __init__(self, session: Session):
        self.session = session

    def create_lecture(self, lecture: LectureCreate) -> LecturePublic:
        lecture = Lecture(**lecture.dict())
        self.session.add(lecture)
        self.session.commit()
        self.session.refresh(lecture)
        return lecture

    def get_lecture(self, lecture_id: int) -> LecturePublic:
        lecture = self.session.get(Lecture, lecture_id)
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        return lecture

    def get_lectures(self, user_id: int) -> list[LecturePublic]:
        lectures = (
            self.session.query(Lecture)
            .filter(Lecture.user_id == user_id)
            .order_by(Lecture.last_accessed_at.desc())
            .all()
        )
        return [LecturePublic.model_validate(lecture) for lecture in lectures]

    def update_lecture(
        self, lecture_id: int, lecture_update: LectureUpdate
    ) -> LecturePublic:
        lecture = self.session.get(Lecture, lecture_id)
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        lecture.title = lecture_update.title
        lecture.description = lecture_update.description
        lecture.completion_percentage = lecture_update.completion_percentage
        self.session.add(lecture)
        self.session.commit()
        self.session.refresh(lecture)
        return lecture

    def delete_lecture(self, lecture_id: int) -> LecturePublic:
        lecture = self.session.get(Lecture, lecture_id)
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        self.session.delete(lecture)
        self.session.commit()
        return lecture

    # LECTURE SECTIONS
    def create_lecture_section(
        self, lecture_section: LectureSectionCreate
    ) -> LectureSectionPublic:
        lecture_section = LectureSection(**lecture_section.dict())
        self.session.add(lecture_section)
        self.session.commit()
        self.session.refresh(lecture_section)
        return lecture_section

    def get_lecture_section(self, lecture_section_id: int) -> LectureSectionPublic:
        lecture_section = self.session.get(LectureSection, lecture_section_id)
        if not lecture_section:
            raise HTTPException(status_code=404, detail="Lecture section not found")
        return lecture_section

    def get_lecture_sections(self, lecture_id: int) -> list[LectureSectionPublic]:
        lecture_sections = (
            self.session.query(LectureSection)
            .filter(LectureSection.lecture_id == lecture_id)
            .order_by(LectureSection.order_key.asc())
            .all()
        )
        return [
            LectureSectionPublic.model_validate(lecture_section)
            for lecture_section in lecture_sections
        ]

    def update_lecture_section(
        self, lecture_section_id: int, lecture_section_update: LectureSectionUpdate
    ) -> LectureSectionPublic:
        lecture_section = self.session.get(LectureSection, lecture_section_id)
        if not lecture_section:
            raise HTTPException(status_code=404, detail="Lecture section not found")
        lecture_section.title = lecture_section_update.title
        lecture_section.completion_percentage = (
            lecture_section_update.completion_percentage
        )
        self.session.add(lecture_section)
        self.session.commit()
        self.session.refresh(lecture_section)
        return lecture_section

    def delete_lecture_section(self, lecture_section_id: int) -> LectureSectionPublic:
        lecture_section = self.session.get(LectureSection, lecture_section_id)
        if not lecture_section:
            raise HTTPException(status_code=404, detail="Lecture section not found")
        self.session.delete(lecture_section)
        self.session.commit()
        return lecture_section

    # LECTURE STEPS
    def create_lecture_step(self, lecture_step: LectureStepCreate) -> LectureStepPublic:
        lecture_step = LectureStep(**lecture_step.dict())
        self.session.add(lecture_step)
        self.session.commit()
        self.session.refresh(lecture_step)
        return lecture_step

    def get_lecture_step(self, lecture_step_id: int) -> LectureStepPublic:
        lecture_step = self.session.get(LectureStep, lecture_step_id)
        if not lecture_step:
            raise HTTPException(status_code=404, detail="Lecture step not found")
        return lecture_step

    def get_lecture_steps(self, lecture_section_id: int) -> list[LectureStepPublic]:
        lecture_steps = (
            self.session.query(LectureStep)
            .filter(LectureStep.lecture_section_id == lecture_section_id)
            .order_by(LectureStep.order_key.asc())
            .all()
        )
        return [
            LectureStepPublic.model_validate(lecture_step)
            for lecture_step in lecture_steps
        ]

    def update_lecture_step(
        self, lecture_step_id: int, lecture_step_update: LectureStepUpdate
    ) -> LectureStepPublic:
        lecture_step = self.session.get(LectureStep, lecture_step_id)
        if not lecture_step:
            raise HTTPException(status_code=404, detail="Lecture step not found")
        lecture_step.title = lecture_step_update.title
        lecture_step.content = lecture_step_update.content
        lecture_step.completed = lecture_step_update.completed
        self.session.add(lecture_step)
        self.session.commit()
        self.session.refresh(lecture_step)
        return lecture_step

    def delete_lecture_step(self, lecture_step_id: int) -> LectureStepPublic:
        lecture_step = self.session.get(LectureStep, lecture_step_id)
        if not lecture_step:
            raise HTTPException(status_code=404, detail="Lecture step not found")
        self.session.delete(lecture_step)
        self.session.commit()
        return lecture_step
