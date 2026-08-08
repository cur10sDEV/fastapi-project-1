from sqlmodel import select, desc, insert, update
from sqlmodel.ext.asyncio.session import AsyncSession

from .models import Review


class ReviewService:
    async def get_all_reviews(self, session: AsyncSession):
        statement = select(Review).order_by(desc(Review.created_at))

        result = await session.exec(statement)

        await session.commit()

        return result.all()

    async def get_reviews_by_book_id(self, book_id: str, session: AsyncSession):
        statement = (
            select(Review)
            .where(Review.book_id == book_id)
            .order_by(desc(Review.created_at))
        )

        result = await session.exec(statement)

        await session.commit()

        return result.all()

    async def get_reviews_by_user_id(self, user_id: str, session: AsyncSession):
        statement = (
            select(Review)
            .where(Review.user_id == user_id)
            .order_by(desc(Review.created_at))
        )

        result = await session.exec(statement)

        await session.commit()

        return result.all()

    async def get_review_by_id(self, review_id: str, session: AsyncSession):
        statement = select(Review).where(Review.id == review_id)

        result = await session.exec(statement)

        await session.commit()

        return result.one_or_none()

    async def create_new_review(self, review_data: dict, session: AsyncSession):

        statement = insert(Review).values(review_data).returning("*")

        result = await session.exec(statement)

        await session.commit()

        return result.one_or_none()

    async def update_review_by_id(
        self, review_id: str, user_id: str, review_data: dict, session: AsyncSession
    ):
        statement = (
            update(Review)
            .where(Review.id == review_id)
            .where(Review.user_id == user_id)
            .values(review_data)
            .returning("*")
        )

        result = await session.exec(statement)

        await session.commit()

        return result.one_or_none()
