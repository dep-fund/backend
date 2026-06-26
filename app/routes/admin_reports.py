from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.dependencies.user_dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.report import FundraisingReport
from app.services.report_service import ReportService

router = APIRouter(prefix="/admin/reports", tags=["Administrators - Reports"])


@router.get("/fundraising", response_model=FundraisingReport)
async def fundraising_report(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_admin_user),
):
    return await ReportService(session).get_fundraising_report()
