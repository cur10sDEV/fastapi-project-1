from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException, Body
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.utils.main import verify_password, create_jwt_token
from .models import User
from .schemas import UserCreateSchema, UserLoginSchema
from .services import UserService

auth_router = APIRouter(tags=["users"])
user_service = UserService()


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


@auth_router.post("/login", status_code=200)
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

    access_token = create_jwt_token(user_id=user_id)

    if access_token is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Unable to register User"
        )

    refresh_token = create_jwt_token(user_id=user_id, refresh=True)

    if refresh_token is None:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Unable to register User"
        )

    return JSONResponse({"access_token": access_token, "refresh_token": refresh_token})
