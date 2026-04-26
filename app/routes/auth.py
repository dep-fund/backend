from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.auth import (
    LoginRequest, 
    TokenResponse, 
    ForgotPasswordRequest, 
    ResetPasswordRequest, 
    MessageResponse
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    return await AuthService(session).login(data)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    return await AuthService(session).forgot_password(data, background_tasks)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    data: ResetPasswordRequest,
    session: AsyncSession = Depends(get_session),
):
    return await AuthService(session).reset_password(data)