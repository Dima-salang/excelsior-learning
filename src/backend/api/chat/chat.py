from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from db.session import get_session
from services.chat_service import ChatService
from services.llm_service import LLMService
from pydantic import BaseModel


class ChatMessageRequest(BaseModel):
    user_id: int
    role: str
    content: str


class GenerateChatMessageRequest(BaseModel):
    user_id: int
    user_prompt: str
    provider_id: int
    chat_history: list[dict[str, str]] | None = None


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
    user_id: int,
    chat_service: ChatService = Depends(get_chat_service),
):
    return chat_service.get_chat_conversation(user_id, chat_id)


@router.get("/conversations/{user_id}")
async def get_chat_conversations(
    user_id: int,
    chat_service: ChatService = Depends(get_chat_service),
):
    return chat_service.get_chat_conversations(user_id)


@router.patch("/conversation/{chat_id}")
async def update_chat_conversation(
    chat_id: int,
    user_id: int,
    title: str,
    chat_service: ChatService = Depends(get_chat_service),
):
    return chat_service.update_chat_conversation(user_id, chat_id, title)


@router.delete("/conversation/{chat_id}")
async def delete_chat_conversation(
    chat_id: int,
    user_id: int,
    chat_service: ChatService = Depends(get_chat_service),
):
    return chat_service.delete_chat_conversation(user_id=user_id, chat_id=chat_id)


@router.post("/conversation/{chat_id}/messages")
async def add_chat_message(
    chat_id: int,
    request: ChatMessageRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    return chat_service.add_chat_message(
        request.user_id, chat_id, request.role, request.content
    )


@router.get("/conversation/{chat_id}/messages")
async def get_chat_messages(
    chat_id: int,
    user_id: int,
    chat_service: ChatService = Depends(get_chat_service),
):
    return chat_service.get_chat_messages(user_id, chat_id)


@router.post("/conversation/{chat_id}/generate")
async def generate_chat_message(
    chat_id: int,
    request: GenerateChatMessageRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    event_stream = chat_service.generate_chat_message_stream(
        request.user_id,
        chat_id,
        request.user_prompt,
        request.provider_id,
        request.chat_history,
    )
    return StreamingResponse(
        event_stream,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
