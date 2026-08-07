from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Enum as SQLEnum, Column, DateTime, Relationship

from src.utils.main import utcnow

if TYPE_CHECKING:
    from src.books.models import Book  # noqa: F401


class UserRole(StrEnum):
    USER = "USER"
    ADMIN = "ADMIN"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    username: str = Field(unique=True)

    role: UserRole = Field(
        sa_column=Column(
            SQLEnum(
                UserRole, name="userrole"
            ),  # name must match what's in the migration
            nullable=False,
            server_default=UserRole.USER,
        )
    )

    email: str = Field(unique=True)

    first_name: str = Field(min_length=1, max_length=256)

    last_name: str = Field(min_length=1, max_length=256)

    is_verified: bool = Field(default=False)

    password: str = Field(min_length=1, max_length=256, exclude=True)

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, default=utcnow),
    )

    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), nullable=False, onupdate=utcnow, default=utcnow
        ),
    )

    books: list["Book"] = Relationship(
        back_populates="author", sa_relationship_kwargs={"lazy": "selectin"}
    )
