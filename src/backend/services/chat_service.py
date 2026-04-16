from sqlmodel import Session, select
from services.llm_service import LLMService
from models.chat import Chat, ChatMessage, ChatMessageGeneration
from models.user import User
from models.lecture import Lecture
from datetime import datetime
from fastapi import HTTPException
from enum import Enum


class ROLE_CHOICES(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatService:
    def __init__(self, session: Session, llm_service: LLMService):
        self.session = session
        self.llm_service = llm_service

    def add_chat_conversation(
        self, user_id: int, lecture_id: int | None = None, title: str = "New Chat"
    ):
        # check if the lecture exists
        if lecture_id is not None:
            lecture = self.session.get(Lecture, lecture_id)
            if not lecture:
                raise HTTPException(status_code=404, detail="Lecture not found")

        chat = Chat(user_id=user_id, lecture_id=lecture_id, title=title)
        self.session.add(chat)
        self.session.commit()
        self.session.refresh(chat)
        return chat

    def get_chat_conversation(self, user_id: int, chat_id: int) -> Chat:
        chat = self.session.get(Chat, chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        if chat.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="You are not authorized to access this chat"
            )

        # update chat.updated_at
        chat.updated_at = datetime.now()
        self.session.add(chat)
        self.session.commit()
        self.session.refresh(chat)
        return chat

    def get_chat_conversations(self, user_id: int) -> list[Chat]:
        chats = self.session.exec(
            select(Chat).where(Chat.user_id == user_id).order_by(Chat.updated_at.desc())
        ).all()
        return chats

    def update_chat_conversation(self, user_id: int, chat_id: int, title: str):
        chat = self.get_chat_conversation(user_id, chat_id)
        chat.title = title
        chat.updated_at = datetime.now()
        self.session.add(chat)
        self.session.commit()
        self.session.refresh(chat)
        return chat

    def add_chat_message(
        self, user_id: int, chat_id: int, role: ROLE_CHOICES, content: str
    ) -> ChatMessage:
        # validate if chat exists
        chat = self.get_chat_conversation(user_id, chat_id)

        # validate if role is valid
        if role not in ROLE_CHOICES:
            raise HTTPException(status_code=400, detail="Invalid role")

        chat_message = ChatMessage(chat_id=chat.id, role=role, content=content)
        self.session.add(chat_message)
        self.session.commit()
        self.session.refresh(chat_message)
        return chat_message

    def generate_chat_message(
        self,
        user_id: int,
        chat_id: int,
        user_prompt: str,
        provider_id: int,
        chat_history: list[dict[str, str]] | None = None,
    ) -> str:
        # validate if chat exists
        chat = self.get_chat_conversation(user_id, chat_id)

        # get chat history
        chat_history = self.get_chat_messages(user_id, chat.id)

        # generate chat message
        chat_message = self.llm_service.generate_chat_message(
            user_prompt, provider_id, chat_history
        )

        # add assistant chat message to database
        self.add_chat_message(user_id, chat.id, ROLE_CHOICES.ASSISTANT, chat_message)

        return chat_message

    def get_chat_messages(self, user_id: int, chat_id: int) -> list[ChatMessage]:
        # validate if chat exists
        chat = self.get_chat_conversation(user_id, chat_id)

        chat_messages = self.session.exec(
            select(ChatMessage)
            .where(ChatMessage.chat_id == chat.id)
            .order_by(ChatMessage.created_at.asc())
        ).all()
        return chat_messages

    def delete_chat_conversation(self, user_id: int, chat_id: int):
        chat = self.get_chat_conversation(user_id, chat_id)
        self.session.delete(chat)
        self.session.commit()
        return True
