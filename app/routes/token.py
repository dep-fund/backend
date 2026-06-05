from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_session
from app.core.dependencies.user_dependencies import get_current_standard_user
from app.models.user import User
from app.schemas.token import TokenResponse, TokenProjectResponse
from app.services.token_service import TokenContractService

router = APIRouter(prefix="/tokens", tags=["Tokens"])


@router.get("", response_model=list[TokenResponse])
async def get_all_tokens(
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await TokenContractService(session).get_all_tokens()


@router.get("/{token_id}", response_model=TokenResponse)
async def get_token(
    token_id: UUID,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await TokenContractService(session).get_token(token_id)


@router.get("/project/{project_id}", response_model=TokenProjectResponse)
async def get_token_by_project(
    project_id: UUID,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await TokenContractService(session).get_token_project_by_project(project_id)
