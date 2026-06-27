import re
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class StandardUserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    birthdate: date
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def username_format(cls, v: str) -> str:
        stripped = v.strip()
        if not re.match(r"^[a-zA-Z0-9_.-]+$", stripped):
            raise ValueError("El usuario solo puede contener letras, números, guiones y puntos")
        return stripped

    @field_validator("birthdate")
    @classmethod
    def birthdate_range(cls, v: date) -> date:
        if v < date(1900, 1, 1):
            raise ValueError("Fecha de nacimiento no válida")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe tener al menos una mayúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe tener al menos una minúscula")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe tener al menos un número")
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
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe tener al menos una mayúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe tener al menos una minúscula")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe tener al menos un número")
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
