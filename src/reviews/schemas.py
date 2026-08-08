from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

if TYPE_CHECKING:
    from src.auth.schemas import UserSchema  # noqa: F401
    from src.books.schemas import BookSchema  # noqa: F401


class ReviewSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    book_id: UUID
    rating: int = Field(..., le=5, ge=0)
    text: str = Field(..., min_length=0, max_length=256)
    created_at: datetime
    updated_at: datetime


class ReviewDetailSchema(ReviewSchema):
    user: "UserSchema"
    book: "BookSchema"


class ReviewCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rating: int = Field(..., le=5, ge=0)
    text: str = Field(..., min_length=0, max_length=256)


class ReviewUpdateSchema(ReviewCreateSchema):
    pass
