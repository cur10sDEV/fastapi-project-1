from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, status, Body, Path
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.db.redis import (
    set_refresh_token_jti,
    check_refresh_token_jti,
    delete_refresh_token_jti,
)
from src.errors import UserAlreadyExists, UserNotFound, InvalidCredentials, InvalidToken
from src.mail.main import send_user_verification_message
from src.schemas import ResponseSchema
from src.utils.main import (
    verify_password,
    create_jwt_token,
    generate_verification_token,
    validate_verification_token,
)
from .dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
)
from .models import User
from .schemas import UserCreateSchema, UserLoginSchema, UserDetailSchema, UserSchema
from .services import UserService

auth_router = APIRouter(tags=["users"])
user_service = UserService()
refresh_token_bearer = RefreshTokenBearer()
access_token_bearer = AccessTokenBearer()


@auth_router.post(
    "/register",
    response_model=ResponseSchema[UserSchema],
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_data: Annotated[UserCreateSchema, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    existing_user = await user_service.user_exists(
        email=user_data.email, username=user_data.username, session=session
    )

    if existing_user:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)

    new_user_dict = UserSchema.model_validate(new_user).model_dump()

    verification_token = generate_verification_token(
        email=new_user_dict["email"], username=new_user_dict["username"]
    )

    await send_user_verification_message(
        username=new_user_dict["username"],
        email=new_user_dict["email"],
        verification_token=verification_token,
    )

    return ResponseSchema(
        status_code=status.HTTP_201_CREATED,
        message="User registration successful. Please check your mail for verification link.",
        data=new_user,
    )


@auth_router.get(
    "/verify/{verification_token}",
    response_model=ResponseSchema[UserSchema],
    status_code=status.HTTP_200_OK,
)
async def verify_user(
    verification_token: Annotated[str, Path()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    decoded = validate_verification_token(verification_token)

    if decoded is None:
        raise InvalidToken()

    user = await user_service.get_user_by_email(email=decoded["email"], session=session)

    if user is None:
        raise UserNotFound()

    verified_user = await user_service.verify_user(str(user.id), session)

    return ResponseSchema(
        status_code=status.HTTP_200_OK, message="Account Verified", data=verified_user
    )


@auth_router.post(
    "/login", response_model=ResponseSchema[dict], status_code=status.HTTP_200_OK
)
async def login_user(
    user_data: Annotated[UserLoginSchema, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    email = user_data.email
    password = user_data.password

    user = await user_service.get_user_by_email(email, session)

    if user is None:
        raise UserNotFound()

    valid_password = await verify_password(password, user.password)

    if valid_password is None or valid_password == False:
        raise InvalidCredentials()

    user_id = str(user.id)
    token_jti = str(uuid4())

    access_token = create_jwt_token(user_id=user_id, role=user.role, jti=token_jti)

    refresh_token = create_jwt_token(
        user_id=user_id, role=user.role, jti=token_jti, refresh=True
    )

    # store refresh token in redis
    await set_refresh_token_jti(token_jti, user_id)

    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        message="Login Successful",
        data={"access_token": access_token, "refresh_token": refresh_token},
    )


@auth_router.post(
    "/refresh-token",
    response_model=ResponseSchema[dict],
    status_code=status.HTTP_200_OK,
)
async def generate_new_token_pair(auth: Annotated[dict, Depends(refresh_token_bearer)]):
    token_jti = auth["jti"]
    user_id = auth["sub"]
    user_role = auth["role"]

    # validate the token, jti and its attributes
    is_jti_valid = await check_refresh_token_jti(token_jti, user_id)
    if not is_jti_valid:
        raise InvalidToken()

    # blacklist / delete the current jti
    await delete_refresh_token_jti(token_jti)

    # check if user is valid or not

    new_token_jti = str(uuid4())

    # create new token pairs
    access_token = create_jwt_token(user_id=user_id, role=user_role, jti=new_token_jti)

    refresh_token = create_jwt_token(
        user_id=user_id, role=user_role, refresh=True, jti=new_token_jti
    )

    # store refresh token in redis
    await set_refresh_token_jti(new_token_jti, user_id)

    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        message="New token pair generated",
        data={"access_token": access_token, "refresh_token": refresh_token},
    )


@auth_router.post(
    "/logout", response_model=ResponseSchema[None], status_code=status.HTTP_200_OK
)
async def logout_user(auth: Annotated[dict, Depends(access_token_bearer)]):
    token_jti = auth["jti"]

    await delete_refresh_token_jti(token_jti)

    return ResponseSchema(
        status_code=status.HTTP_200_OK, message="Logged out successfully", data=None
    )


@auth_router.get(
    "/me",
    response_model=ResponseSchema[UserDetailSchema],
    status_code=status.HTTP_200_OK,
)
async def get_current_user(
    user: Annotated[User, Depends(get_current_user)],
):
    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        message="User Details fetched successfully",
        data=user,
    )
