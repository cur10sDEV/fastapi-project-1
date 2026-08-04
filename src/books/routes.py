from typing import Annotated
from uuid import UUID

from fastapi import HTTPException, status, APIRouter, Depends, Body, Path
from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.schemas import BookSchema, BookCreateSchema, BookUpdateSchema
from src.books.services import BookService
from src.db.main import get_session

book_router = APIRouter(tags=["Books"])
book_service = BookService()


@book_router.get("/", response_model=list[BookSchema], status_code=status.HTTP_200_OK)
async def get_books(session: AsyncSession = Depends(get_session)):
    books = await book_service.get_all_books(session)

    return books


@book_router.get(
    "/{book_id}", response_model=BookSchema, status_code=status.HTTP_200_OK
)
async def get_book(
    book_id: Annotated[UUID, Path()], session: AsyncSession = Depends(get_session)
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
    session: AsyncSession = Depends(get_session),
):
    book = await book_service.create_book(book_data, session)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to add book"
        )

    return book


@book_router.patch(
    "/{book_id}", response_model=BookSchema, status_code=status.HTTP_200_OK
)
async def update_book_by_id(
    book_id: Annotated[UUID, Path()],
    book_data: Annotated[BookUpdateSchema, Body()],
    session: AsyncSession = Depends(get_session),
):
    book = await book_service.get_book_by_id(book_id, session)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="book not found"
        )

    updated_book = await book_service.update_book(book_id, book_data, session)

    if updated_book is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update book"
        )

    return updated_book


@book_router.delete(
    "/{book_id}", response_model=BookSchema, status_code=status.HTTP_200_OK
)
async def delete_book_by_id(
    book_id: Annotated[UUID, Path()], session: AsyncSession = Depends(get_session)
):
    book = await book_service.get_book_by_id(book_id, session)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="book not found"
        )

    deleted_book = await book_service.delete_book_by_id(book_id, session)

    if delete_book_by_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Failed to delete book"
        )

    return deleted_book
