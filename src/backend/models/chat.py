from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class ChatBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")
    lecture_id: int | None = Field(foreign_key="lecture.id")
    title: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Chat(ChatBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ChatMessageBase(SQLModel):
    chat_id: int = Field(foreign_key="chat.id")
    role: str
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ChatMessage(ChatMessageBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    