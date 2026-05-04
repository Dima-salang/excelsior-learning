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
    LectureUpdate,
)
from models.card import CardPublic, CardUpdate, Card, CardListPublic
from schema.paginated_response import PaginatedResponse
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from litellm.exceptions import APIError, RateLimitError, ServiceUnavailableError

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


@router.get("/{lecture_id}", response_model=LecturePublic)
def get_lecture(lecture_id: int, session: Session = Depends(get_session)):
    logger.info(f"GET /lectures/{lecture_id}")
    service = LectureService(session)
    return service.get_lecture_with_sections(lecture_id)


@router.patch("/{lecture_id}", response_model=LecturePublic)
def update_lecture(
    lecture_id: int,
    lecture_update: LectureUpdate,
    session: Session = Depends(get_session),
):
    logger.info(f"PATCH /lectures/{lecture_id}")
    service = LectureService(session)
    return service.update_lecture(lecture_id, lecture_update)


@router.delete("/{lecture_id}")
def delete_lecture(lecture_id: int, session: Session = Depends(get_session)):
    logger.info(f"DELETE /lectures/{lecture_id}")
    service = LectureService(session)
    service.delete_lecture(lecture_id)
    return {"message": "Lecture deleted successfully"}


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


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=5),
    retry=retry_if_exception_type(APIError | RateLimitError | ServiceUnavailableError),
)
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
    logger.info(f"POST /lectures/steps/{step_id}/complete")
    service = LectureService(session)
    step = service.complete_lecture_step(step_id)
    return LectureStepListPublic.model_validate(step)
