from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BookSchema(BaseModel):
    id: UUID
    title: str
    description: str | None
    author_id: UUID
    publisher_id: UUID
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime


class BookCreateSchema(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    description: str | None = Field(
        default=None,
        max_length=1000,
    )
    publisher_id: str
    published_date: date
    page_count: int = Field(gt=0)
    language: str = Field(min_length=2, max_length=10)


class BookUpdateSchema(BookCreateSchema):
    pass
