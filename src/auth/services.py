from pydantic import EmailStr
from sqlmodel import select, insert
from sqlmodel.ext.asyncio.session import AsyncSession

from src.utils.main import hash_password
from .models import User
from .schemas import UserCreateSchema


class UserService:

    async def get_user_by_email(self, email: EmailStr, session: AsyncSession):
        statement = select(User).where(User.email == email)

        result = await session.exec(statement)

        await session.commit()

        return result.one_or_none()

    async def get_user_by_username(self, username: str, session: AsyncSession):
        statement = select(User).where(User.username == username)

        result = await session.exec(statement)

        await session.commit()

        return result.one_or_none()

    async def user_exists(self, email: str, username: str, session: AsyncSession):
        existing_user = await self.get_user_by_email(email, session)

        if existing_user is not None:
            return True

        existing_user = await self.get_user_by_username(username, session)

        if existing_user is not None:
            return True

        else:
            return False

    async def create_user(self, user_data: UserCreateSchema, session: AsyncSession):
        user_data_dict = user_data.model_dump()

        password_hash = await hash_password(user_data_dict["password"])

        user_data_dict["password"] = password_hash
        del user_data_dict["confirm_password"]

        statement = insert(User).values(**user_data_dict).returning("*")

        result = await session.exec(statement)

        await session.commit()

        return result.one_or_none()
