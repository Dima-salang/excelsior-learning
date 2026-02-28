from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from pydantic import BaseModel, ConfigDict
    

class ModelProvider(BaseModel):
    model_config = ConfigDict(frozen=True)

    model_name: str

class LLMProviderBase(SQLModel):
    provider_name: str
    api_key: str


class LLMProvider(LLMProviderBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    models: list["LLMModel"] = Relationship(back_populates="provider")



class LLMModelBase(SQLModel):
    model_name: str
    provider_id: int | None = Field(default=None, foreign_key="llm_provider.id")


class LLMModel(LLMModelBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    provider: LLMProvider = Relationship(back_populates="models")