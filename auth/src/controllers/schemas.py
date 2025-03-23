from typing import Optional
import re

from pydantic import (
    BaseModel, 
    EmailStr, 
    Field, 
    field_validator, 
    model_validator
)


class UserSignupRequest(BaseModel):
    firstname: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="The first name of the user. Must be between 3 and 50 characters.",
        example="John"
    )
    lastname: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="The last name of the user. Must be between 3 and 50 characters.",
        example="Doe"
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="The username of the user. Must be between 3 and 50 characters.",
        example="johndoe"
    )
    email: EmailStr = Field(
        ...,
        description="The email address of the user. Must be a valid email format.",
        example="john.doe@example.com"
    )
    phone: Optional[str] = Field(
        None,
        description="The phone number of the user. Must be a valid international \
            phone number format.",
        example="+1234567890"
    )
    password: str = Field(
        ...,
        min_length=8,
        description="The password for the user account. Must be at least 8 characters long, \
            include at least one uppercase letter, and one special character.",
        example="Secure@123"
    )

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        """Validate password to ensure it meets security requirements."""
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if all(char not in "!@#$%^&*(),.?\":{}|<>" for char in value):
            raise ValueError("Password must contain at least one special character.")
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return value

    @field_validator("phone")
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        """Validate phone number to ensure it follows an international format."""
        if value is None:
            return value
        phone_pattern = r'^\+?[1-9]\d{1,14}$'
        if not re.match(phone_pattern, value):
            raise ValueError("Invalid phone number. Must follow the E.164 international format.")
        return value


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="The access token for authentication, \
        usually short-lived.")
    refresh_token: str = Field(..., description="The refresh token for obtaining \
        new access tokens when the current one expires.")
    token_type: str = Field(..., description="The type of token issued. Usually 'Bearer'.")


class UserSignupResponse(BaseModel):
    id: str = Field(..., description="The unique identifier of the user.")
    username: str = Field(..., description="The username of the newly registered user.")


class AuthForm(BaseModel):
    username: Optional[str] = Field(
        default=None,
        description="The user's unique username. Optional, but either this \
            or phone must be provided.",
        example="user123"
    )
    phone: Optional[str] = Field(
        default=None,
        description="The user's phone number in international format. Optional, but either \
            this or username must be provided.",
        example="+1234567890"
    )
    password: str = Field(
        ...,
        description="The user's account password. This field is required and must be secure.",
        example="Secure@123"
    )

    @model_validator(mode="after")
    def validate_username_email_or_phone(cls, values: "AuthForm") -> "AuthForm":
        """
        Validates that at least one of the following fields is provided:
        username, email, or phone.
        """
        if not values.username and not values.phone:
            raise ValueError("At least one of 'username' or 'phone' must be provided.")
        return values


class TokensForm(BaseModel):
    access_token: str = Field(
        ...,
        description="The access token used for authenticating user requests. \
            This token has a short expiration time.",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.\
            eyJ1c2VyX2lkIjoxMjM0NTY3ODkwLCJleHAiOjE2ODAwMDAwMDB9.\
            s0m3RAnd0m3s1gn47ur3"
    )
    refresh_token: str = Field(
        ...,
        description="The refresh token used for renewing the access token after it expires. \
            This token has a longer expiration time.",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.\
            eyJ1c2VyX2lkIjoxMjM0NTY3ODkwLCJleHAiOjE3MDAwMDAwMDB9.\
            s1gn4tur3b4ck1nd0wnt1m3"
    )


class UserAuthResponse(BaseModel):
    uuid: str = Field(
        ...,
        description="Unique identifier of the user.",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    username: str = Field(
        ...,
        description="The user's unique username.",
        example="johndoe"
    )
    is_active: bool = Field(
        ...,
        description="Indicates whether the user's account is active.",
        example=True
    )
    role: str = Field(
        ...,
        description="The role assigned to the user in the system.",
        example="admin"
    )
