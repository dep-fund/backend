from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.auth import TokenResponse
from app.services.auth.oauth_service import OAuthService
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Auth - OAuth"])


@router.get("/google")
async def google_login():
    redirect_url = OAuthService(None).get_google_redirect_url()
    return RedirectResponse(url=redirect_url)


@router.get("/google/callback", response_model=TokenResponse)
async def google_callback(
    code: str,
    session: AsyncSession = Depends(get_session),
):  
    token = await OAuthService(session).handle_google_callback(code)
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/auth/callback?token={token.access_token}")