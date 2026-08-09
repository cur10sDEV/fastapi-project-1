from typing import Callable

from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError


class CustomExceptionInitialDetailSchema(BaseModel):
    message: str
    error_code: str


class CustomException(Exception):
    """This is the custom exception class that will be used by custom exceptions of this project"""

    pass


class InvalidToken(CustomException):
    """User has provided an invalid or expired token"""

    pass


class RevokedToken(CustomException):
    """User has provided a token that has been revoked"""

    pass


class AccessTokenRequired(CustomException):
    """User has provided a refresh token when an access token is needed"""

    pass


class RefreshTokenRequired(CustomException):
    """User has provided an access token when a refresh token is needed"""

    pass


class UserAlreadyExists(CustomException):
    """User has provided an email for a user who exists during sign up."""

    pass


class InvalidCredentials(CustomException):
    """User has provided wrong email or password during log in."""

    pass


class InsufficientPermission(CustomException):
    """User does not have the necessary permissions to perform an action."""

    pass


class BookNotFound(CustomException):
    """Book Not found"""

    pass


class ReviewNotFound(CustomException):
    """Review Not found"""

    pass


class TagNotFound(CustomException):
    """Tag Not found"""

    pass


class TagAlreadyExists(CustomException):
    """Tag already exists"""

    pass


class UserNotFound(CustomException):
    """User Not found"""

    pass


class AccountNotVerified(CustomException):
    """Account not yet verified"""

    pass


def create_exception_handler(
    status_code: int, initial_detail: CustomExceptionInitialDetailSchema
) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(
        request: Request, exception: CustomException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status_code, content=initial_detail.model_dump()
        )

    return exception_handler


def register_all_errors(app: FastAPI):
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail=CustomExceptionInitialDetailSchema(
                message="Token is invalid or expired", error_code="invalid_token"
            ),
        ),
    )

    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail=CustomExceptionInitialDetailSchema(
                message="User with email already exists", error_code="user_exists"
            ),
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail=CustomExceptionInitialDetailSchema(
                message="User not found", error_code="user_not_found"
            ),
        ),
    )

    app.add_exception_handler(
        ReviewNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail=CustomExceptionInitialDetailSchema(
                message="Review not found", error_code="review_not_found"
            ),
        ),
    )

    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail=CustomExceptionInitialDetailSchema(
                message="Book not found", error_code="book_not_found"
            ),
        ),
    )

    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail=CustomExceptionInitialDetailSchema(
                message="Invalid Email Or Password",
                error_code="invalid_email_or_password",
            ),
        ),
    )

    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail=CustomExceptionInitialDetailSchema(
                message="Token is invalid Or expired", error_code="invalid_token"
            ),
        ),
    )

    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail=CustomExceptionInitialDetailSchema(
                message="Token is invalid or has been revoked",
                error_code="token_revoked",
            ),
        ),
    )

    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail=CustomExceptionInitialDetailSchema(
                message="Please provide a valid access token",
                error_code="access_token_required",
            ),
        ),
    )

    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail=CustomExceptionInitialDetailSchema(
                message="Please provide a valid refresh token",
                error_code="refresh_token_required",
            ),
        ),
    )

    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail=CustomExceptionInitialDetailSchema(
                message="You do not have enough permissions to perform this action",
                error_code="insufficient_permissions",
            ),
        ),
    )

    app.add_exception_handler(
        TagNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail=CustomExceptionInitialDetailSchema(
                message="Tag Not Found", error_code="tag_not_found"
            ),
        ),
    )

    app.add_exception_handler(
        TagAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail=CustomExceptionInitialDetailSchema(
                message="Tag Already exists", error_code="tag_exists"
            ),
        ),
    )

    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail=CustomExceptionInitialDetailSchema(
                message="Book Not Found", error_code="book_not_found"
            ),
        ),
    )

    app.add_exception_handler(
        AccountNotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail=CustomExceptionInitialDetailSchema(
                message="Account Not verified", error_code="account_not_verified"
            ),
        ),
    )

    @app.exception_handler(500)
    async def internal_server_error(request, exception):

        return JSONResponse(
            content=CustomExceptionInitialDetailSchema(
                message="Oops! Something went wrong", error_code="server_error"
            ).model_dump(),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @app.exception_handler(SQLAlchemyError)
    async def database__error(request, exception):
        print(str(exception))
        return JSONResponse(
            content=CustomExceptionInitialDetailSchema(
                message="Oops! Something went wrong", error_code="server_error"
            ).model_dump(),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
