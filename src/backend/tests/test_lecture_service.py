from sqlmodel import Session
import pytest
from services.lecture_service import LectureService
from models.lecture import Lecture, LecturePublic, LectureUpdate
from models.lecture_section import LectureSection
from models.lecture_step import LectureStep
from datetime import datetime
from models.user import User
from fastapi import HTTPException


@pytest.fixture
def lecture_service(session: Session):
    return LectureService(session)


@pytest.fixture
def setup_data(session: Session):
    # Setup test user
    user = User(username="testuser", password="password")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Setup test lecture
    lecture = Lecture(title="Test Lecture", user_id=user.id)
    session.add(lecture)
    session.commit()
    session.refresh(lecture)

    # Setup test lecture sections
    sections = [
        LectureSection(title=f"Section {i}", lecture_id=lecture.id) for i in range(2)
    ]
    session.add_all(sections)
    session.commit()

    # Setup test lecture steps
    steps = [
        LectureStep(
            title=f"Step {i}",
            content=f"Step {i}",
            lecture_section_id=sections[i // 2].id,
        )
        for i in range(4)
    ]
    session.add_all(steps)
    session.commit()

    return user, lecture, sections, steps


def test_create_lecture(lecture_service: LectureService, setup_data, session: Session):
    user, lecture, sections, steps = setup_data

    # create a new lecture
    new_lecture = Lecture(title="New Lecture", user_id=user.id)
    lecture_model = lecture_service.create_lecture(new_lecture)
    assert lecture_model.title == new_lecture.title


def test_get_lecture(lecture_service: LectureService, setup_data, session: Session):
    user, lecture, sections, steps = setup_data
    retrieved_lecture = lecture_service.get_lecture(lecture.id)
    # determine whether lecture is lecturePublic in pydantic
    assert LecturePublic.model_validate(retrieved_lecture)
    assert retrieved_lecture.title == lecture.title


def test_get_lectures(lecture_service: LectureService, setup_data, session: Session):
    user, lecture, sections, steps = setup_data
    retrieved_lectures, total = lecture_service.get_lectures(user.id, limit=10, offset=0)
    assert total == 1
    assert len(retrieved_lectures) == 1
    # assert lecture is LecturePublic
    assert LecturePublic.model_validate(retrieved_lectures[0])
    assert retrieved_lectures[0].title == lecture.title

def test_get_lectures_pagination(lecture_service: LectureService, setup_data, session: Session):
    user, lecture, sections, steps = setup_data
    retrieved_lectures, total = lecture_service.get_lectures(user.id, limit=1, offset=0)
    assert total == 1
    assert len(retrieved_lectures) == 1
    # assert lecture is LecturePublic
    assert LecturePublic.model_validate(retrieved_lectures[0])
    assert retrieved_lectures[0].title == lecture.title

    retrieved_lectures, total = lecture_service.get_lectures(user.id, limit=1, offset=1)
    assert total == 1
    assert len(retrieved_lectures) == 0


def test_update_lecture(lecture_service: LectureService, setup_data, session: Session):
    user, lecture, sections, steps = setup_data
    # create LectureUpdate
    update_time = datetime.now()
    lecture_update = LectureUpdate(
        id=lecture.id,
        title="Updated Lecture",
        description="Updated Description",
        completion_percentage=0.5,
        last_accessed_at=update_time,
    )
    updated_lecture = lecture_service.update_lecture(
        lecture_id=lecture.id, lecture_update=lecture_update
    )
    assert updated_lecture.title == "Updated Lecture"
    assert updated_lecture.description == "Updated Description"
    assert updated_lecture.completion_percentage == 0.5
    assert updated_lecture.last_accessed_at.replace(
        microsecond=0
    ) == update_time.replace(microsecond=0)

    # validate
    assert LecturePublic.model_validate(updated_lecture)

    # test update lecture that does not exist
    with pytest.raises(HTTPException):
        lecture_service.update_lecture(lecture_id=999, lecture_update=lecture_update)


