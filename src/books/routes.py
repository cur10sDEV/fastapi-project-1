from typing import Annotated

from fastapi import HTTPException, status, APIRouter, Body, Path, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.auth.models import UserRole
from src.db.main import get_session
from .schemas import BookSchema, BookCreateSchema, BookUpdateSchema, BookDetailSchema
from .services import BookService

user_role_checker = Depends(RoleChecker([UserRole.USER]))

book_router = APIRouter(tags=["Books"], dependencies=[user_role_checker])
book_service = BookService()
access_token_bearer = AccessTokenBearer()


@book_router.get("/", response_model=list[BookSchema], status_code=status.HTTP_200_OK)
async def get_books(session: Annotated[AsyncSession, Depends(get_session)]):
    books = await book_service.get_all_books(session)

    return books


@book_router.get(
    "/user", response_model=list[BookSchema], status_code=status.HTTP_200_OK
)
async def get_user_books(
    session: Annotated[AsyncSession, Depends(get_session)],
    auth: Annotated[dict, Depends(access_token_bearer)],
):
    user_id = auth["sub"]

    user_books = await book_service.get_user_books(user_id, session)

    return user_books


@book_router.get(
    "/{book_id}", response_model=BookDetailSchema, status_code=status.HTTP_200_OK
)
async def get_book(
    book_id: Annotated[str, Path()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    book = await book_service.get_book_by_id(book_id, session)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    return book


@book_router.post("/", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def add_book(
    book_data: Annotated[BookCreateSchema, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
    auth: Annotated[dict, Depends(access_token_bearer)],
):
    book_data_dict = book_data.model_dump()
    book_data_dict["author_id"] = auth["sub"]

    book = await book_service.create_book(book_data_dict, session)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to add book"
        )

    return book


@book_router.patch(
    "/{book_id}", response_model=BookSchema, status_code=status.HTTP_200_OK
)
async def update_book_by_id(
    book_id: Annotated[str, Path()],
    book_data: Annotated[BookUpdateSchema, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
    auth: Annotated[dict, Depends(access_token_bearer)],
):
    book_data_dict = book_data.model_dump()

    book = await book_service.get_book_by_id(book_id, session)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="book not found"
        )

    if not str(book.author_id) == auth["sub"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You are not the author")

    updated_book = await book_service.update_book(book_id, book_data_dict, session)

    if updated_book is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update book"
        )

    return updated_book


@book_router.delete(
    "/{book_id}", response_model=BookSchema, status_code=status.HTTP_200_OK
)
async def delete_book_by_id(
    book_id: Annotated[str, Path()],
    session: Annotated[AsyncSession, Depends(get_session)],
    auth: Annotated[dict, Depends(access_token_bearer)],
):
    book = await book_service.get_book_by_id(book_id, session)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="book not found"
        )

    if not str(book.author_id) == auth["sub"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You are not the author")

    deleted_book = await book_service.delete_book_by_id(book_id, session)

    if deleted_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Failed to delete book"
        )

    return deleted_book
