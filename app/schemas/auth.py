import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    identifier: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=1)

    @field_validator("identifier")
    @classmethod
    def identifier_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("El identificador no puede estar vacío")
        return stripped


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    
    
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class MessageResponse(BaseModel):
    message: str


class ResetPasswordRequest(BaseModel):
    token: str
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