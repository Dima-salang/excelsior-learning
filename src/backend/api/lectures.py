from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from db.session import get_session
from services.lecture_service import LectureService
from services.llm_service import LLMService
from models.lecture import (
    LecturePublic,
    LectureListPublic,
    LectureStepPublic,
    LectureSectionListPublic,
    LectureStepListPublic,
)
from models.card import CardPublic, CardUpdate, Card

router = APIRouter(prefix="/lectures", tags=["lectures"])


@router.get("/", response_model=List[LectureListPublic])
def get_lectures(user_id: int, session: Session = Depends(get_session)):
    service = LectureService(session)
    return service.get_lectures(user_id)


@router.get("/{lecture_id}", response_model=LectureListPublic)
def get_lecture(lecture_id: int, session: Session = Depends(get_session)):
    service = LectureService(session)
    return service.get_lecture(lecture_id)


@router.get("/{lecture_id}/sections", response_model=List[LectureSectionListPublic])
def get_lecture_sections(lecture_id: int, session: Session = Depends(get_session)):
    service = LectureService(session)
    return service.get_lecture_sections(lecture_id)


@router.get(
    "/{lecture_id}/sections/{section_id}/steps",
    response_model=List[LectureStepListPublic],
)
def get_section_steps(
    lecture_id: int, section_id: int, session: Session = Depends(get_session)
):
    service = LectureService(session)
    return service.get_section_steps(section_id)


@router.get("/steps/{step_id}", response_model=LectureStepListPublic)
def get_step_direct(step_id: int, session: Session = Depends(get_session)):
    service = LectureService(session)
    return service.get_lecture_step(step_id)


@router.get("/{lecture_id}/steps/{step_id}", response_model=LectureStepListPublic)
def get_step(lecture_id: int, step_id: int, session: Session = Depends(get_session)):
    service = LectureService(session)
    return service.get_lecture_step(step_id)


@router.get("/steps/{step_id}/cards", response_model=List[CardPublic])
def get_step_cards(step_id: int, session: Session = Depends(get_session)):
    cards = session.exec(select(Card).where(Card.step_id == step_id)).all()
    return [CardPublic.model_validate(card) for card in cards]


@router.post("/{lecture_id}/steps/{step_id}/generate", response_model=LectureStepPublic)
def generate_step_content(
    lecture_id: int,
    step_id: int,
    provider_id: int,
    session: Session = Depends(get_session),
):
    """
    Generate content for a specific lecture step.
    """
    llm_service = LLMService(session)
    return llm_service.generate_step_content(lecture_id, step_id, provider_id)


@router.patch("/cards/{card_id}", response_model=CardPublic)
def update_card(
    card_id: int,
    card_update: CardUpdate,
    session: Session = Depends(get_session),
):
    """
    Update a specific flashcard.
    """
    llm_service = LLMService(session)
    return llm_service.update_card(card_id, card_update.dict(exclude_unset=True))


@router.post("/steps/{step_id}/complete", response_model=LectureStepListPublic)
def complete_step(step_id: int, session: Session = Depends(get_session)):
    service = LectureService(session)
    step = service.get_lecture_step(step_id)
    step.completed = True
    session.add(step)
    session.commit()
    session.refresh(step)
    return LectureStepListPublic.model_validate(step)
