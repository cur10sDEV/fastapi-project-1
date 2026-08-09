from typing import Annotated

from fastapi import APIRouter, status, Depends, Body, Path
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import RoleChecker, AccessTokenBearer, get_current_user
from src.auth.models import UserRole, User
from src.books.services import BookService
from src.db.main import get_session
from src.errors import BookNotFound, ReviewNotFound, InsufficientPermission
from src.schemas import ResponseSchema
from .schemas import ReviewSchema, ReviewCreateSchema, ReviewUpdateSchema
from .services import ReviewService

user_role_checker = Depends(RoleChecker([UserRole.USER]))
access_token_bearer = Depends(AccessTokenBearer())

review_router = APIRouter(
    tags=["Reviews"], dependencies=[access_token_bearer, user_role_checker]
)

book_service = BookService()
review_service = ReviewService()


@review_router.post(
    "/books/{book_id}",
    response_model=ResponseSchema[ReviewSchema],
    status_code=status.HTTP_201_CREATED,
)
async def add_new_review(
    book_id: Annotated[str, Path()],
    review_data: Annotated[ReviewCreateSchema, Body()],
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    review_data_dict = review_data.model_dump()
    review_data_dict["user_id"] = str(user.id)

    book_exists = await book_service.get_book_by_id(book_id, session)

    if book_exists is None:
        raise BookNotFound()

    review_data_dict["book_id"] = str(book_id)

    new_review = await review_service.create_new_review(review_data_dict, session)

    return ResponseSchema(
        status_code=status.HTTP_201_CREATED,
        message="Review added successfully",
        data=new_review,
    )


@review_router.patch(
    "/{review_id}",
    response_model=ResponseSchema[ReviewSchema],
    status_code=status.HTTP_200_OK,
)
async def update_review_by_id(
    review_id: Annotated[str, Path()],
    review_data: Annotated[ReviewUpdateSchema, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[dict, Depends(get_current_user)],
):
    review_data_dict = review_data.model_dump()
    user_id = str(user.id)

    existing_review = await review_service.get_review_by_id(review_id, session)

    if existing_review is None:
        raise ReviewNotFound()

    if not str(existing_review.user_id) == user_id:
        raise InsufficientPermission()

    updated_review = await review_service.update_review_by_id(
        review_id, user_id, review_data_dict, session
    )

    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        message="Review updated successfully",
        data=updated_review,
    )
