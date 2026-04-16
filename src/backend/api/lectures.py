from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional
import logging
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
from models.card import CardPublic, CardUpdate, Card, CardListPublic
from schema.paginated_response import PaginatedResponse
from schema.lecture_schema_json import LectureSortEnum

logger = logging.getLogger("excelsior")
router = APIRouter(prefix="/lectures", tags=["lectures"])


@router.get("/", response_model=PaginatedResponse[LectureListPublic])
def get_lectures(
    user_id: int,
    session: Session = Depends(get_session),
    limit: int = 10,
    offset: int = 0,
    search: Optional[str] = Query(None, description="Search by title"),
    sort: Optional[str] = Query(
        None, description="Sort order: 'ascending' or 'descending'"
    ),
    status: Optional[str] = Query(
        None, description="Filter by status: 'not_started', 'in_progress', 'completed'"
    ),
):
    logger.info(
        f"GET /lectures/?user_id={user_id}, search={search}, sort={sort}, status={status}"
    )

    # Build filter options
    filter_options = {}
    if search:
        filter_options["title"] = search
    if sort:
        filter_options["sort"] = sort

    service = LectureService(session)
    lectures, total = service.get_lectures(user_id, limit, offset, filter_options)

    # Apply status filter client-side for range-based filtering
    return PaginatedResponse.from_sqlmodel(lectures, total, limit, offset)


@router.get("/{lecture_id}", response_model=LectureListPublic)
def get_lecture(lecture_id: int, session: Session = Depends(get_session)):
    logger.info(f"GET /lectures/{lecture_id}")
    service = LectureService(session)
    return service.get_lecture(lecture_id)


@router.get("/{lecture_id}/sections", response_model=List[LectureSectionListPublic])
def get_lecture_sections(lecture_id: int, session: Session = Depends(get_session)):
    logger.info(f"GET /lectures/{lecture_id}/sections")
    service = LectureService(session)
    return service.get_lecture_sections(lecture_id)


@router.get(
    "/{lecture_id}/sections/{section_id}/steps",
    response_model=List[LectureStepListPublic],
)
def get_section_steps(
    lecture_id: int, section_id: int, session: Session = Depends(get_session)
):
    logger.info(f"GET /lectures/{lecture_id}/sections/{section_id}/steps")
    service = LectureService(session)
    return service.get_section_steps(section_id)


@router.get("/steps/{step_id}", response_model=LectureStepListPublic)
def get_step_direct(step_id: int, session: Session = Depends(get_session)):
    logger.info(f"GET /lectures/steps/{step_id}")
    service = LectureService(session)
    return service.get_lecture_step(step_id)


@router.get("/{lecture_id}/steps/{step_id}", response_model=LectureStepListPublic)
def get_step(lecture_id: int, step_id: int, session: Session = Depends(get_session)):
    logger.info(f"GET /lectures/{lecture_id}/steps/{step_id}")
    service = LectureService(session)
    return service.get_lecture_step(step_id)


@router.get("/steps/{step_id}/cards", response_model=List[CardListPublic])
def get_step_cards(step_id: int, session: Session = Depends(get_session)):
    logger.info(f"GET /lectures/steps/{step_id}/cards")
    try:
        cards = session.exec(select(Card).where(Card.step_id == step_id)).all()
        result = []
        for card in cards:
            try:
                result.append(CardListPublic.model_validate(card))
            except Exception as e:
                logger.error(f"Card serialization error: {e}")
                raise HTTPException(
                    status_code=500, detail=f"Card serialization error: {e}"
                )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching cards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
