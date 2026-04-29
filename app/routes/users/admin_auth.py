from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth.auth_service import AuthService
from app.core.enums import UserType

router = APIRouter(prefix="/admin/auth", tags=["Administrators - Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    return await AuthService(session).login(data, allowed_type=UserType.ADMIN)