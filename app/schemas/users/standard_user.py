from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class StandardUserRegisterRequest(BaseModel):
    username: str
    name: str
    last_name: str
    birthdate: date
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class StandardUserUpdateRequest(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    last_name: Optional[str] = None
    birthdate: Optional[date] = None
    email: Optional[EmailStr] = None


class StandardUserChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class StandardUserResponse(BaseModel):
    id: UUID
    username: str
    name: str
    last_name: str
    birthdate: Optional[date]
    email: str
    image: Optional[str]
    activated: bool
    blocked: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
