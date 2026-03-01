from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List
from db.session import get_session
from services.llm_service import LLMService
from models.llm_provider import (
    UserLLMConfigCreate,
    UserLLMConfigUpdate,
    UserLLMConfigPublic,
)
from pydantic import BaseModel
from models.lecture import Lecture

router = APIRouter(prefix="/llm", tags=["llm"])


class GenerateLectureRequest(BaseModel):
    prompt: str
    provider_id: int
    user_id: int


@router.post("/providers", response_model=UserLLMConfigPublic)
def add_provider(
    provider: UserLLMConfigCreate, session: Session = Depends(get_session)
):
    """
    Add a new LLM provider configuration for the user.
    """
    service = LLMService(session)
    return service.add_provider(provider)


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
