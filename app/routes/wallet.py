from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.dependencies.user_dependencies import get_current_standard_user
from app.models.user import StandardUser
from app.schemas.pagination import PaginatedResponse
from app.schemas.wallet import WalletCreateRequest, WalletResponse
from app.services.wallet_service import WalletService

router = APIRouter(prefix="/wallets", tags=["Wallets"])


@router.post("", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
async def create_wallet(
    data: WalletCreateRequest,
    session: AsyncSession = Depends(get_session),
    current_user: StandardUser = Depends(get_current_standard_user),
):
    return await WalletService(session).create(data, current_user)


@router.get("/by-address", response_model=WalletResponse)
async def get_wallet_by_address(
    address: str = Query(...),
    session: AsyncSession = Depends(get_session),
    current_user: StandardUser = Depends(get_current_standard_user),
):
    return await WalletService(session).get_by_address(address, current_user)


@router.get("", response_model=PaginatedResponse[WalletResponse])
async def list_wallets(
    page: int = Query(1, gt=0),
    page_size: int = Query(10, gt=0, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: StandardUser = Depends(get_current_standard_user),
):
    total, items = await WalletService(session).list_by_user(
        current_user=current_user,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse[WalletResponse](
        total=total,
        page=page,
        page_size=page_size,
        results=items,
    )


@router.delete("/{wallet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wallet(
    wallet_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: StandardUser = Depends(get_current_standard_user),
):
    await WalletService(session).delete(wallet_id, current_user)
