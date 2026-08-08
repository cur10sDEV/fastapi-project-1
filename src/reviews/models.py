from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, DateTime, Column, Relationship

from src.utils.main import utcnow

if TYPE_CHECKING:
    from src.auth.models import User  # noqa : F401
    from src.books.models import Book  # noqa : F401


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    id: UUID = Field(primary_key=True, default_factory=uuid4)

    user_id: UUID = Field(foreign_key="users.id")

    book_id: UUID = Field(foreign_key="books.id")

    rating: int = Field(le=5, ge=0)

    text: str = Field(min_length=0, max_length=256)

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, default=utcnow),
    )

    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), nullable=False, onupdate=utcnow, default=utcnow
        ),
    )

    user: "User" = Relationship(
        back_populates="reviews", sa_relationship_kwargs={"lazy": "selectin"}
    )

    book: "Book" = Relationship(
        back_populates="reviews", sa_relationship_kwargs={"lazy": "selectin"}
    )
