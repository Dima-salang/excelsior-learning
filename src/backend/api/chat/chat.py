from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from db.session import get_session
from services.chat_service import ChatService
from services.llm_service import LLMService


router = APIRouter(prefix="/chat", tags=["chat"])


def get_chat_service(session: Session = Depends(get_session)) -> ChatService:
    llm_service = LLMService(session)
    return ChatService(session, llm_service)


@router.post("/conversation")
async def add_chat_conversation(
    user_id: int,
    lecture_id: int | None = None,
    title: str = "New Chat",
    chat_service: ChatService = Depends(get_chat_service),
):
    return chat_service.add_chat_conversation(user_id, lecture_id, title)


@router.get("/conversation/{chat_id}")
async def get_chat_conversation(
    chat_id: int,
    chat_service: ChatService = Depends(get_chat_service),
):
    return chat_service.get_chat_conversation(chat_id)


@router.get("/conversations/{user_id}")
async def get_chat_conversations(
    user_id: int,
    chat_service: ChatService = Depends(get_chat_service),
):
    return chat_service.get_chat_conversations(user_id)


@router.patch("/conversation/{chat_id}")
async def update_chat_conversation(
    chat_id: int,
    title: str,
    chat_service: ChatService = Depends(get_chat_service),
):
    return chat_service.update_chat_conversation(chat_id, title)


@router.delete("/conversation/{chat_id}")
async def delete_chat_conversation(
    chat_id: int,
    chat_service: ChatService = Depends(get_chat_service),
):
    return chat_service.delete_chat_conversation(chat_id)
