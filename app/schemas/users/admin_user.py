from typing import Optional
from uuid import UUID
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class AdminUserCreateRequest(BaseModel):
    admin_secret_key: str
    username: str
    name: str
    last_name: str
    birthdate: date
    email: EmailStr
    password: str
    image: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class AdminUserUpdateRequest(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    image: Optional[str] = None


class AdminUserChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class AdminUserResponse(BaseModel):
    id: UUID
    username: str
    name: str
    last_name: str
    email: str
    image: Optional[str]
    activated: bool
    blocked: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
