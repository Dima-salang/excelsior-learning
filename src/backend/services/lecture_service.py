from sqlmodel import Session, select, func
from datetime import datetime
from schema.lecture_schema_json import LectureFilterSchema, LectureSortEnum
from models.lecture import (
    Lecture,
    LectureCreate,
    LecturePublic,
    LectureListPublic,
    LectureUpdate,
    LectureSectionPublic,
    LectureSectionListPublic,
    LectureStepPublic,
    LectureStepListPublic,
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
        lecture = Lecture(**lecture.model_dump(exclude_unset=True))
        self.session.add(lecture)
        self.session.commit()
        self.session.refresh(lecture)

        # validate by LecturePublic
        return LecturePublic.model_validate(lecture)

    def get_lecture(self, lecture_id: int) -> LectureListPublic:
        lecture = self.session.get(Lecture, lecture_id)
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        lecture.last_accessed_at = datetime.now()
        lecture.updated_at = datetime.now()
        self.session.add(lecture)
        self.session.commit()
        self.session.refresh(lecture)
        return LectureListPublic.model_validate(lecture)

    def get_lectures(
        self, user_id: int, limit: int = 10, offset: int = 0, filter: dict = None
    ) -> tuple[list[LectureListPublic], int]:
        statement = select(Lecture).where(Lecture.user_id == user_id)

        if filter and isinstance(filter, dict):
            title = filter.get("title")
            sort = filter.get("sort")

            if title:
                statement = statement.where(Lecture.title.ilike(f"%{title}%"))

            if sort == "ascending":
                statement = statement.order_by(Lecture.last_accessed_at.asc())
            else:
                statement = statement.order_by(Lecture.last_accessed_at.desc())
        else:
            statement = statement.order_by(Lecture.last_accessed_at.desc())

        statement = statement.limit(limit).offset(offset)
        lectures = self.session.exec(statement).all()

        result = [LectureListPublic.model_validate(lecture) for lecture in lectures]

        count_statement = (
            select(func.count()).select_from(Lecture).where(Lecture.user_id == user_id)
        )
        if filter and isinstance(filter, dict):
            title = filter.get("title")
            if title:
                count_statement = count_statement.where(
                    Lecture.title.ilike(f"%{title}%")
                )
        total = self.session.exec(count_statement).first()

        return result, total

    def update_lecture(
        self, lecture_id: int, lecture_update: LectureUpdate
    ) -> LecturePublic:
        lecture = self.session.get(Lecture, lecture_id)
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        update_data = lecture_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(lecture, key):
                setattr(lecture, key, value)

        self._recalculate_completion(lecture)

        self.session.add(lecture)
        self.session.commit()
        self.session.refresh(lecture)
        return LecturePublic.model_validate(lecture)

    def _recalculate_completion(self, lecture: Lecture) -> None:
        total_steps = self.session.exec(
            select(func.count(LectureStep.id))
            .select_from(LectureStep)
            .join(LectureSection)
            .where(LectureSection.lecture_id == lecture.id)
        ).first()

        completed_steps = self.session.exec(
            select(func.count(LectureStep.id))
            .select_from(LectureStep)
            .join(LectureSection)
            .where(
                LectureSection.lecture_id == lecture.id, LectureStep.completed == True
            )
        ).first()

        lecture.completion_percentage = (
            (completed_steps / total_steps) * 100 if total_steps > 0 else 0
        )
        lecture.last_accessed_at = datetime.now()

    def delete_lecture(self, lecture_id: int) -> LecturePublic:
        lecture = self.session.get(Lecture, lecture_id)
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")
        self.session.delete(lecture)
        self.session.commit()
        return LecturePublic.model_validate(lecture)

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

    def update_lecture_section(
        self, lecture_section_id: int, lecture_section_update: LectureSectionUpdate
    ) -> LectureSectionPublic:
        lecture_section = self.session.get(LectureSection, lecture_section_id)
        if not lecture_section:
            raise HTTPException(status_code=404, detail="Lecture section not found")

        # update lecture section
        for key, value in lecture_section_update.dict().items():
            if hasattr(lecture_section, key) and value is not None:
                setattr(lecture_section, key, value)
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
        lecture_steps = self.session.exec(
            select(LectureStep)
            .where(LectureStep.lecture_section_id == lecture_section_id)
            .order_by(LectureStep.order_key.asc())
        ).all()
        return [
            LectureStepPublic.model_validate(lecture_step)
            for lecture_step in lecture_steps
        ]

    def update_lecture_step(
        self, lecture_step_id: int, lecture_step_update: LectureStepUpdate
    ) -> LectureStepPublic:
        lecture_step = self.get_lecture_step(lecture_step_id)
        if not lecture_step:
            raise HTTPException(status_code=404, detail="Lecture step not found")

        # update lecture step
        for key, value in lecture_step_update.dict().items():
            if hasattr(lecture_step, key) and value is not None:
                setattr(lecture_step, key, value)

        # update lecture completion percentage
        lecture_section = self.get_lecture_section(lecture_step.lecture_section_id)
        # get total steps for lecture section
        total_steps = self.session.exec(
            select(func.count())
            .select_from(LectureStep)
            .where(LectureStep.lecture_section_id == lecture_section.id)
        ).first()

        # completion percentage
        completion_percentage = (
            lecture_section.completion_percentage + (100 / total_steps)
            if total_steps > 0
            else 0
        )

        # update lecture section
        self.update_lecture_section(
            lecture_section.id,
            LectureSectionUpdate(
                completion_percentage=completion_percentage,
            ),
        )

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

    def get_lecture_with_sections(self, lecture_id: int) -> LecturePublic:
        lecture = self.session.get(Lecture, lecture_id)
        if not lecture:
            raise HTTPException(status_code=404, detail="Lecture not found")

        sections = self.session.exec(
            select(LectureSection)
            .where(LectureSection.lecture_id == lecture_id)
            .order_by(LectureSection.order_key.asc())
        ).all()

        lecture.last_accessed_at = datetime.now()
        lecture.updated_at = datetime.now()
        self.session.add(lecture)
        self.session.commit()
        self.session.refresh(lecture)

        sections_with_steps = []
        for section in sections:
            steps = self.session.exec(
                select(LectureStep)
                .where(LectureStep.lecture_section_id == section.id)
                .order_by(LectureStep.order_key.asc())
            ).all()
            sections_with_steps.append(
                LectureSectionPublic(
                    id=section.id,
                    title=section.title,
                    completion_percentage=section.completion_percentage,
                    order_key=section.order_key,
                    created_at=section.created_at,
                    updated_at=section.updated_at,
                    steps=[LectureStepListPublic.model_validate(s) for s in steps],
                )
            )

        return LecturePublic(
            id=lecture.id,
            title=lecture.title,
            description=lecture.description,
            completion_percentage=lecture.completion_percentage,
            last_accessed_at=lecture.last_accessed_at,
            sections=sections_with_steps,
        )

    def get_lecture_sections(self, lecture_id: int) -> list[LectureSectionListPublic]:
        sections = self.session.exec(
            select(LectureSection)
            .where(LectureSection.lecture_id == lecture_id)
            .order_by(LectureSection.order_key.asc())
        ).all()
        return [LectureSectionListPublic.model_validate(s) for s in sections]

    def get_section_steps(self, section_id: int) -> list[LectureStepListPublic]:
        steps = self.session.exec(
            select(LectureStep)
            .where(LectureStep.lecture_section_id == section_id)
            .order_by(LectureStep.order_key.asc())
        ).all()
        return [LectureStepListPublic.model_validate(s) for s in steps]

    def complete_lecture_step(self, lecture_step_id: int) -> LectureStep:
        lecture_step = self.session.get(LectureStep, lecture_step_id)
        if not lecture_step:
            raise HTTPException(status_code=404, detail="Lecture step not found")

        lecture_step.completed = True
        self.session.add(lecture_step)

        section = self.session.get(LectureSection, lecture_step.lecture_section_id)
        if section and section.lecture_id:
            lecture = self.session.get(Lecture, section.lecture_id)
            if lecture:
                self._recalculate_completion(lecture)
                self.session.add(lecture)

        self.session.commit()
        self.session.refresh(lecture_step)
        return lecture_step
