from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserLLMConfigBase(SQLModel):
    provider_name: str
    model_name: str
    api_key: str | None = None
    base_url: Optional[str] = None
    additional_params: Optional[str] = None


class UserLLMConfig(UserLLMConfigBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UserLLMConfigCreate(UserLLMConfigBase):
    pass


class UserLLMConfigUpdate(UserLLMConfigBase):
    pass


class UserLLMConfigDelete(SQLModel):
    id: int


class UserLLMConfigPublic(UserLLMConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime
