from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, status, Body, Path
from sqlmodel.ext.asyncio.session import AsyncSession

from src.celery_tasks import send_mail
from src.db.main import get_session
from src.db.redis import (
    set_refresh_token_jti,
    check_refresh_token_jti,
    delete_refresh_token_jti,
    set_url_safe_token,
    get_url_safe_token,
    delete_url_safe_token,
    RedisKeysPrefixes,
)
from src.errors import (
    UserAlreadyExists,
    UserNotFound,
    InvalidCredentials,
    InvalidToken,
    OldPasswordError,
)
from src.mail.schemas import MailSubjectTypes
from src.schemas import ResponseSchema
from src.utils.main import (
    verify_password,
    create_jwt_token,
    generate_url_safe_token,
    validate_url_safe_token,
    hash_password,
)
from .dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
)
from .models import User
from .schemas import (
    UserCreateSchema,
    UserLoginSchema,
    UserDetailSchema,
    UserSchema,
    ResetPasswordRequestSchema,
    ResetPasswordConfirmSchema,
)
from .services import UserService

auth_router = APIRouter(tags=["Users"])
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

    verification_token = generate_url_safe_token(email=new_user.email)

    await set_url_safe_token(
        prefix=RedisKeysPrefixes.USER_VERIFICATION_TOKEN,
        token=verification_token,
        user_email=new_user.email,
    )

    send_mail.delay(
        MailSubjectTypes.ACCOUNT_VERIFICATION,
        new_user.username,
        new_user.email,
        verification_token,
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
    decoded = validate_url_safe_token(verification_token)

    if decoded is None:
        raise InvalidToken()

    user_email = await get_url_safe_token(
        prefix=RedisKeysPrefixes.USER_VERIFICATION_TOKEN, token=verification_token
    )

    if user_email is None:
        raise InvalidToken()

    user = await user_service.get_user_by_email(email=decoded["email"], session=session)

    if user is None:
        raise UserNotFound()

    verified_user = await user_service.verify_user(str(user.id), session)

    await delete_url_safe_token(
        prefix=RedisKeysPrefixes.USER_VERIFICATION_TOKEN, token=verification_token
    )

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


@auth_router.post(
    "/reset-password",
    response_model=ResponseSchema[None],
    status_code=status.HTTP_200_OK,
)
async def reset_password_request(
    reset_password_request_data: Annotated[ResetPasswordRequestSchema, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    reset_password_request_data_dict = reset_password_request_data.model_dump()
    user_email = reset_password_request_data_dict["email"]

    user = await user_service.get_user_by_email(user_email, session)

    if user is None:
        raise UserNotFound()

    reset_password_token = generate_url_safe_token(email=user_email)

    await set_url_safe_token(
        prefix=RedisKeysPrefixes.PASSWORD_RESET_TOKEN,
        token=reset_password_token,
        user_email=user.email,
    )

    send_mail.delay(
        MailSubjectTypes.RESET_PASSWORD_REQUEST,
        user.username,
        user.email,
        reset_password_token,
    )

    return ResponseSchema(
        status_code=status.HTTP_200_OK,
        message="Reset Password link has been sent to your email. Please check your inbox.",
        data=None,
    )


@auth_router.post(
    "/reset-password/{reset_password_token}",
    response_model=ResponseSchema[None],
    status_code=status.HTTP_200_OK,
)
async def reset_password_confirm(
    reset_password_token: Annotated[str, Path()],
    reset_password_data: Annotated[ResetPasswordConfirmSchema, Body()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    reset_password_data_dict = reset_password_data.model_dump()

    decoded_token = validate_url_safe_token(reset_password_token)

    if decoded_token is None:
        raise InvalidToken()

    user_email = await get_url_safe_token(
        prefix=RedisKeysPrefixes.PASSWORD_RESET_TOKEN, token=reset_password_token
    )

    if (
        user_email is None
        or decoded_token["email"] is None
        or not user_email == decoded_token["email"]
    ):
        raise InvalidToken()

    user = await user_service.get_user_by_email(user_email, session)

    if user is None:
        raise UserNotFound()

    new_password_hash = await hash_password(reset_password_data_dict["new_password"])

    if user.password == new_password_hash:
        raise OldPasswordError()

    await user_service.update_password(
        user_id=str(user.id), new_password_hash=new_password_hash, session=session
    )

    await delete_url_safe_token(
        prefix=RedisKeysPrefixes.PASSWORD_RESET_TOKEN, token=reset_password_token
    )

    return ResponseSchema(
        status_code=status.HTTP_200_OK, message="Password reset successful", data=None
    )
