from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# sort enum
class DeckSortEnum(str, Enum):
    ASCENDING = "ascending"
    DESCENDING = "descending"


# deck filter schema
class DeckFilterSchema(BaseModel):
    title: Optional[str] = Field(default=None, description="Title of the deck")
    description: Optional[str] = Field(
        default=None, description="Description of the deck"
    )
    created_at: Optional[str] = Field(
        default=None, description="Creation date of the deck"
    )
    last_accessed_at: Optional[str] = Field(
        default=None, description="Last accessed date of the deck"
    )
    sort: Optional[DeckSortEnum] = Field(
        default=DeckSortEnum.DESCENDING, description="Sort order of the deck"
    )
    limit: Optional[int] = Field(default=10, description="Limit of the deck")
    offset: Optional[int] = Field(default=0, description="Offset of the deck")