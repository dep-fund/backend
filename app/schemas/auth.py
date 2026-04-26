from pydantic import BaseModel, EmailStr, field_validator, model_validator


class LoginRequest(BaseModel):
    identifier: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    
    
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class MessageResponse(BaseModel):
    message: str


class ResetPasswordRequest(BaseModel):
    identifier: str
    token: str
    new_password: str
    confirm_password: str

    @field_validator("new_password", "confirm_password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v

    @model_validator(mode='after')
    def verify_passwords_match(self) -> 'ResetPasswordRequest':
        if self.new_password != self.confirm_password:
            raise ValueError("Las contraseñas no coinciden")
        return self