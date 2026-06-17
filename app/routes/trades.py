from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.dependencies.user_dependencies import get_current_standard_user
from app.models.user import User
from app.schemas.trade import TradeCreate, TradeResponse, TradeUpdateStatus
from app.services.trade_service import TradeService

router = APIRouter(prefix="/trades", tags=["Trades"])


@router.post("", response_model=TradeResponse, status_code=201)
async def create_trade(
    data: TradeCreate,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await TradeService(session).create_trade(data, buyer_id=current_user.id)


@router.patch("/{trade_id}/confirm", response_model=TradeResponse)
async def confirm_trade(
    trade_id: UUID,
    data: TradeUpdateStatus,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await TradeService(session).confirm_trade(trade_id, tx_hash=data.tx_hash)


@router.patch("/{trade_id}/fail", response_model=TradeResponse)
async def fail_trade(
    trade_id: UUID,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await TradeService(session).fail_trade(trade_id)


@router.get("/my-trades", response_model=list[TradeResponse])
async def get_my_trades(
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await TradeService(session).get_trades_by_buyer(buyer_id=current_user.id)


@router.get("/publication/{publication_id}", response_model=list[TradeResponse])
async def get_trades_by_publication(
    publication_id: UUID,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await TradeService(session).get_trades_by_publication(publication_id)