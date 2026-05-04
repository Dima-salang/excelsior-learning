from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List, Literal
from fastapi.responses import StreamingResponse
from db.session import get_session
from services.llm_service import LLMService
from models.llm_provider import (
    UserLLMConfigCreate,
    UserLLMConfigUpdate,
    UserLLMConfigPublic,
)
from litellm.exceptions import APIError, RateLimitError
from pydantic import BaseModel
from models.lecture import Lecture
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


router = APIRouter(prefix="/llm", tags=["llm"])


class GenerateLectureRequest(BaseModel):
    prompt: str
    provider_id: int
    user_id: int


class GenerateCardsRequest(BaseModel):
    prompt: str
    provider_id: int
    user_id: int
    num_flashcards: int = 10
    difficulty: Literal["easy", "normal", "hard"] = "normal"


@router.post("/providers", response_model=UserLLMConfigPublic)
def add_provider(
    provider: UserLLMConfigCreate, session: Session = Depends(get_session)
):
    """
    Add a new LLM provider configuration for the user.
    """
    service = LLMService(session)
    return service.add_provider(provider)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=5),
    retry=retry_if_exception_type(Exception),
)
@router.get("/providers", response_model=List[UserLLMConfigPublic])
def get_providers(user_id: int, session: Session = Depends(get_session)):
    """
    Get all LLM provider configurations for a specific user.
    """
    service = LLMService(session)
    return service.get_providers(user_id)


@router.get("/providers/{provider_id}", response_model=UserLLMConfigPublic)
def get_provider(provider_id: int, session: Session = Depends(get_session)):
    """
    Get details of a specific LLM provider configuration.
    """
    service = LLMService(session)
    return service.get_provider(provider_id)


@router.patch("/providers/{provider_id}", response_model=UserLLMConfigPublic)
def update_provider(
    provider_id: int,
    provider_update: UserLLMConfigUpdate,
    session: Session = Depends(get_session),
):
    """
    Update an existing LLM provider configuration.
    """
    service = LLMService(session)
    return service.update_provider(provider_id, provider_update)


@router.delete("/providers/{provider_id}", response_model=UserLLMConfigPublic)
def delete_provider(provider_id: int, session: Session = Depends(get_session)):
    """
    Delete an LLM provider configuration.
    """
    service = LLMService(session)
    return service.delete_provider(provider_id)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=5),
    retry=retry_if_exception_type(APIError | RateLimitError),
)
@router.post("/generate/lecture", response_model=Lecture)
def generate_lecture(
    request: GenerateLectureRequest, session: Session = Depends(get_session)
):
    """
    Generate a lecture from a prompt using a specific provider.
    """
    service = LLMService(session)
    return service.generate_lecture(
        request.prompt, request.provider_id, request.user_id
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=5),
    retry=retry_if_exception_type(APIError | RateLimitError),
)
@router.post("/generate/{deck_id}/cards", response_model=int)
def generate_cards_for_deck(
    deck_id: int,
    request: GenerateCardsRequest,
    session: Session = Depends(get_session),
):
    """
    Generate a deck of cards from a prompt using a specific provider and existing deck
    """
    service = LLMService(session)
    return service.generate_cards(
        prompt=request.prompt,
        provider_id=request.provider_id,
        user_id=request.user_id,
        deck_id=deck_id,
        num_flashcards=request.num_flashcards,
        difficulty=request.difficulty,
    )


@router.post("/generate/cards", response_model=int)
def generate_cards(
    request: GenerateCardsRequest,
    session: Session = Depends(get_session),
):
    """
    Generate a deck of cards from a prompt using a specific provider.
    """
    service = LLMService(session)
    return service.generate_cards(
        prompt=request.prompt,
        provider_id=request.provider_id,
        user_id=request.user_id,
        num_flashcards=request.num_flashcards,
        difficulty=request.difficulty,
    )


@router.get("/models")
def get_model_list(session: Session = Depends(get_session)):
    """
    Get a list of available models for a specific provider.
    """
    service = LLMService(session)
    return service.get_model_list()


@router.get("/providers/{provider_id}/key")
def get_provider_key(provider_id: int, session: Session = Depends(get_session)):
    """
    Get the decrypted API key for a specific provider.
    """
    service = LLMService(session)
    try:
        key = service.get_api_key(provider_id)
        return {"api_key": key}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class GenerateChatRequest(BaseModel):
    prompt: str
    provider_id: int
    user_id: int
    lecture_context: str | None = None
    chat_history: list[dict[str, str]] | None = None


@router.post("/chat")
def generate_chat(
    request: GenerateChatRequest, session: Session = Depends(get_session)
):
    """
    Stream a chat response from the LLM as Server-Sent Events.
    """
    service = LLMService(session)
    generator = service.generate_chat(
        prompt=request.prompt,
        provider_id=request.provider_id,
        user_id=request.user_id,
        lecture_context=request.lecture_context,
        chat_history=request.chat_history,
    )

    def event_stream():
        try:
            for chunk in generator:
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except HTTPException as e:
            yield f"data: [ERROR] {e.detail}\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
