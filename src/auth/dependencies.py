from typing import Any

from fastapi import HTTPException, status
from fastapi.security import HTTPBearer
from starlette.requests import Request

from src.utils.main import decode_token


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
