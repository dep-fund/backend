from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.wallet import (
    WalletAlreadyExists,
    WalletHasTransactions,
    WalletNotFound,
    WalletNotOwnedByUser,
)
from app.models.transaction import Transaction
from app.models.user import StandardUser
from app.models.wallet import Wallet
from app.schemas.wallet import WalletCreateRequest, WalletResponse


class WalletService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _get(self, wallet_id: UUID) -> Wallet:
        wallet = await self.session.scalar(select(Wallet).where(Wallet.id == wallet_id))
        if not wallet:
            raise WalletNotFound()
        return wallet

    async def create(
        self, data: WalletCreateRequest, current_user: StandardUser
    ) -> WalletResponse:
        existing = await self.session.scalar(
            select(Wallet).where(Wallet.address == data.address)
        )
        if existing:
            raise WalletAlreadyExists()

        wallet = Wallet(address=data.address, user_id=current_user.id)
        self.session.add(wallet)
        await self.session.commit()
        await self.session.refresh(wallet)

        return WalletResponse.model_validate(wallet)

    async def get_by_address(
        self, address: str, current_user: StandardUser
    ) -> WalletResponse:
        wallet = await self.session.scalar(
            select(Wallet).where(Wallet.address == address)
        )
        if not wallet:
            raise WalletNotFound()
        if wallet.user_id != current_user.id:
            raise WalletNotOwnedByUser()

        return WalletResponse.model_validate(wallet)

    async def list_by_user(
        self,
        current_user: StandardUser,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[int, list[WalletResponse]]:
        query = select(Wallet).where(Wallet.user_id == current_user.id)

        total = await self.session.scalar(
            select(func.count()).select_from(query.subquery())
        )

        wallets = (
            await self.session.scalars(
                query.offset((page - 1) * page_size).limit(page_size)
            )
        ).all()

        return total or 0, [WalletResponse.model_validate(w) for w in wallets]

    async def delete(self, wallet_id: UUID, current_user: StandardUser) -> None:
        wallet = await self._get(wallet_id)

        if wallet.user_id != current_user.id:
            raise WalletNotOwnedByUser()

        has_transactions = await self.session.scalar(
            select(func.count()).where(Transaction.wallet_id == wallet_id)
        )

        if has_transactions:
            raise WalletHasTransactions()

        await self.session.delete(wallet)
        await self.session.commit()
