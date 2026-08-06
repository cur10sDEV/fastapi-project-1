from typing import Any, Annotated

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.utils.main import decode_token
from .services import UserService

user_service = UserService()


class AuthBearerToken(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict[str, Any]:
        creds = await super().__call__(request=request)

        token_data = decode_token(token=creds.credentials)

        if token_data is None:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Invalid or Expired Token"
            )

        self.verify_token_data(token_data)

        return token_data

    def verify_token_data(self, token_data: dict):
        raise NotImplementedError("Please implement this")


class AccessTokenBearer(AuthBearerToken):
    def verify_token_data(self, token_data: dict):
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Please provide a valid Access Token"
            )


class RefreshTokenBearer(AuthBearerToken):
    def verify_token_data(self, token_data: dict):
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Please provide a valid Refresh Token"
            )


async def get_current_user(
    auth: Annotated[dict, Depends(AccessTokenBearer())],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    user_id = auth["sub"]

    user = await user_service.get_user_by_id(user_id, session)

    if user is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "User not found with this user_id associated to this token",
        )

    return user
