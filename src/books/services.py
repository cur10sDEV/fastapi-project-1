from sqlmodel import select, insert, update, delete, desc
from sqlmodel.ext.asyncio.session import AsyncSession

from .models import Book


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))

        result = await session.exec(statement)

        await session.commit()

        return result.all()

    async def get_user_books(self, user_id: str, session: AsyncSession):
        statement = (
            select(Book)
            .where(Book.author_id == user_id)
            .order_by(desc(Book.created_at))
        )

        result = await session.exec(statement)

        await session.commit()

        return result.all()

    async def get_book_by_id(self, book_id: str, session: AsyncSession):
        statement = select(Book).where(Book.id == book_id)

        result = await session.exec(statement)

        await session.commit()

        return result.one_or_none()

    async def create_book(self, book_data_dict: dict, session: AsyncSession):

        statement = insert(Book).values(book_data_dict).returning("*")

        result = await session.exec(statement)

        await session.commit()

        return result.one_or_none()

    async def update_book(
        self, book_id: str, book_data_dict: dict, session: AsyncSession
    ):
        statement = (
            update(Book).where(Book.id == book_id).values(book_data_dict).returning("*")
        )

        result = await session.exec(statement)

        await session.commit()

        return result.one_or_none()

    async def delete_book_by_id(self, book_id: str, session: AsyncSession):
        statement = delete(Book).where(Book.id == book_id).returning("*")

        result = await session.exec(statement)

        await session.commit()

        return result.one_or_none()
