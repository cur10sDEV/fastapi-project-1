from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Text
from sqlmodel import Field, SQLModel

from src.utils.main import utcnow


class Book(SQLModel, table=True):
    __tablename__ = "books"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    title: str = Field(min_length=1, max_length=256)

    description: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        max_length=1000,
    )

    author_id: UUID = Field(foreign_key="users.id")

    # publisher_id: UUID = Field(foreign_key="publishers.id")
    publisher_id: UUID = Field(default_factory=uuid4)

    published_date: date

    page_count: int = Field(gt=0)

    language: str = Field(min_length=2, max_length=10)

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, default=utcnow),
    )

    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), nullable=False, onupdate=utcnow, default=utcnow
        ),
    )
    #
    # author: Author = Relationship(back_populates="books")
    # publisher: Publisher = Relationship(back_populates="books")
