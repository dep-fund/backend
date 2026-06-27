from fastapi import APIRouter, Depends, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.dependencies.user_dependencies import get_current_standard_user
from app.models.user import User
from app.schemas.transaction import TransactionResponse
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transaction", tags=["transaction"])


@router.get(
    "/history",
    response_model=list[TransactionResponse],
    status_code=status.HTTP_200_OK,
)
async def get_history(
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await TransactionService(session).get_history(current_user.id)


@router.get("/projects/{project_id}/dividends/history")
async def get_dividend_history(
    project_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_standard_user),
):
    return await TransactionService(session).get_dividend_history_by_project(
        project_id, current_user.id
    )
