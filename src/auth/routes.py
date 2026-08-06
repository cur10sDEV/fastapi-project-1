from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, status, HTTPException, Body
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.db.redis import (
    set_refresh_token_jti,
    check_refresh_token_jti,
    delete_refresh_token_jti,
)
from src.utils.main import verify_password, create_jwt_token
from .dependencies import RefreshTokenBearer, AccessTokenBearer
from .models import User
from .schemas import UserCreateSchema, UserLoginSchema
from .services import UserService

auth_router = APIRouter(tags=["users"])
user_service = UserService()
refresh_token_bearer = RefreshTokenBearer()
access_token_bearer = AccessTokenBearer()


@auth_router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: Annotated[UserCreateSchema, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    existing_user = await user_service.user_exists(
        email=user_data.email, username=user_data.username, session=session
    )

    if existing_user:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "User already exists - email or username already registered",
        )

    new_user = await user_service.create_user(user_data, session)

    if new_user is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create User"
        )

    return new_user


@auth_router.post("/login", response_model=dict, status_code=status.HTTP_200_OK)
async def login_user(
    user_data: Annotated[UserLoginSchema, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    email = user_data.email
    password = user_data.password

    user = await user_service.get_user_by_email(email, session)

    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    valid_password = await verify_password(password, user.password)

    if valid_password is None or valid_password == False:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong Password")

    user_id = str(user.id)
    token_jti = str(uuid4())

    access_token = create_jwt_token(user_id=user_id, jti=token_jti)

    if access_token is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Unable to register User"
        )

    refresh_token = create_jwt_token(user_id=user_id, jti=token_jti, refresh=True)

    if refresh_token is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Unable to register User"
        )

    # store refresh token in redis
    jti_set = await set_refresh_token_jti(token_jti, user_id)

    if not jti_set:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Unable to set refresh token into redis",
        )

    return JSONResponse({"access_token": access_token, "refresh_token": refresh_token})


@auth_router.post("/refresh-token", response_model=dict, status_code=status.HTTP_200_OK)
async def generate_new_token_pair(auth: Annotated[dict, Depends(refresh_token_bearer)]):
    token_jti = auth["jti"]
    user_id = auth["sub"]

    # validate the token, jti and its attributes
    is_jti_valid = await check_refresh_token_jti(token_jti, user_id)
    if not is_jti_valid:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Refresh Token Malformed")

    # blacklist / delete the current jti
    deleted = await delete_refresh_token_jti(token_jti)
    if not deleted:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Cannot delete Refresh token from redis",
        )

    # check if user is valid or not

    new_token_jti = str(uuid4())

    # create new token pairs
    access_token = create_jwt_token(user_id=user_id, jti=new_token_jti)
    if access_token is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create new access token"
        )

    refresh_token = create_jwt_token(user_id=user_id, refresh=True, jti=new_token_jti)
    if refresh_token is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create new refresh token"
        )

    # store refresh token in redis
    jti_set = await set_refresh_token_jti(new_token_jti, user_id)
    if not jti_set:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Unable to set refresh token into redis",
        )

    return JSONResponse({"access_token": access_token, "refresh_token": refresh_token})


@auth_router.post("/logout", response_model=dict, status_code=status.HTTP_200_OK)
async def logout_user(auth: Annotated[dict, Depends(access_token_bearer)]):
    token_jti = auth["jti"]

    deleted = await delete_refresh_token_jti(token_jti)
    if not deleted:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Cannot delete Refresh token from redis",
        )

    return {}
