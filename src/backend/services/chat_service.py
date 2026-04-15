from sqlmodel import Session, select
from services.llm_service import LLMService
from models.chat import Chat, ChatMessage
from fastapi import HTTPException



class ChatService:
    def __init__(self, session: Session, llm_service: LLMService):
        self.session = session
        self.llm_service = llm_service

    def add_chat_conversation(self, user_id: int, lecture_id: int | None = None, title: str = "New Chat"):
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
            raise HTTPException(status_code=403, detail="You are not authorized to access this chat")
        return chat

    def get_chat_conversations(self, user_id: int) -> list[Chat]:
        chats = self.session.exec(
            select(Chat)
            .where(Chat.user_id == user_id)
            .order_by(Chat.updated_at.desc())
        ).all()
        return chats

    def add_chat_message(self, chat_id: int, role: str, content: str):
        chat_message = ChatMessage(chat_id=chat_id, role=role, content=content)
        self.session.add(chat_message)
        self.session.commit()
        self.session.refresh(chat_message)
        return chat_message

    def get_chat_messages(self, chat_id: int) -> list[ChatMessage]:
        chat_messages = self.session.exec(
            select(ChatMessage)
            .where(ChatMessage.chat_id == chat_id)
            .order_by(ChatMessage.created_at.asc())
        ).all()
        return chat_messages

    
        