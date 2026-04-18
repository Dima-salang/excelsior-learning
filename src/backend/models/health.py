from sqlmodel import Field, SQLModel
from datetime import datetime


class HealthPublic(SQLModel):
    status: str
    time: datetime


class Health(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    status: str
    time: datetime = Field(default_factory=datetime.now)
