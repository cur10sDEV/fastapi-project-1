from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    model_validator,
    AfterValidator,
)

from src.utils.main import validate_password_strength, validate_username


class UserSchema(BaseModel):
    id: UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class UserCreateSchema(BaseModel):
    username: str = Annotated[
        Field(min_length=1, max_length=256), AfterValidator(validate_username)
    ]
    email: EmailStr = Field(min_length=1, max_length=256)
    first_name: str = Field(min_length=1, max_length=256, alias="first-name")
    last_name: str = Field(min_length=1, max_length=256, alias="last-name")
    password: str = Field(min_length=8, max_length=256)
    confirm_password: str = Field(
        min_length=8, max_length=256, alias="confirm-password"
    )

    @model_validator(mode="after")
    def validate_password(self):
        validate_password_strength(self.password)
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(min_length=1, max_length=256)
    password: str = Annotated[
        Field(min_length=8, max_length=256), AfterValidator(validate_password_strength)
    ]
