from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.dependencies.user_dependencies import get_current_admin_user
from app.schemas.blockchain.dividend import DistributeRequest
from app.services.blockchain.services.dividend_service import DividendService

router = APIRouter(prefix="/admin/dividends", tags=["Administrators - Dividends"])


@router.post(
    "/{project_id}/distribute",
    status_code=status.HTTP_200_OK,
)
async def distribute_dividends(
    project_id: UUID,
    data: DistributeRequest,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_admin_user),
):
    return await DividendService(session).distribute(project_id, data.usdc_amount)
