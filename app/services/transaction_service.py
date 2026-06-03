from uuid import UUID
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import TransactionType
from app.exceptions.transaction import (
    TransactionInvestmentRequiresProject,
    TransactionProjectOnlyForInvestment,
)
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionResponse


class TransactionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _create(
        self,
        tx_hash: str,
        type: TransactionType,
        wallet_id: UUID,
        project_id: Optional[UUID] = None,
    ) -> TransactionResponse:
        if type == TransactionType.INVESTMENT and not project_id:
            raise TransactionInvestmentRequiresProject()

        if type != TransactionType.INVESTMENT and project_id:
            raise TransactionProjectOnlyForInvestment()

        transaction = Transaction(
            tx_hash=tx_hash,
            type=type,
            wallet_id=wallet_id,
            project_id=project_id,
        )

        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)

        return TransactionResponse.model_validate(transaction)

    async def create_buy(self, tx_hash: str, wallet_id: UUID) -> TransactionResponse:
        return await self._create(
            tx_hash=tx_hash, type=TransactionType.BUY, wallet_id=wallet_id
        )

    async def create_sell(self, tx_hash: str, wallet_id: UUID) -> TransactionResponse:
        return await self._create(
            tx_hash=tx_hash, type=TransactionType.SELL, wallet_id=wallet_id
        )

    async def create_dividend(
        self, tx_hash: str, wallet_id: UUID
    ) -> TransactionResponse:
        return await self._create(
            tx_hash=tx_hash, type=TransactionType.DIVIDEND, wallet_id=wallet_id
        )

    async def create_investment(
        self, tx_hash: str, wallet_id: UUID, project_id: UUID
    ) -> TransactionResponse:
        return await self._create(
            tx_hash=tx_hash,
            type=TransactionType.INVESTMENT,
            wallet_id=wallet_id,
            project_id=project_id,
        )
