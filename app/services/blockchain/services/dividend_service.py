from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.project import ProjectNotFound
from app.models.investment import Investment
from app.models.wallet import Wallet
from app.services.blockchain.contracts.dividends_service import DividendsService
from app.services.project_service import ProjectService
from app.services.transaction_service import TransactionService


class DividendService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def distribute(self, project_id: UUID, usdc_amount: Decimal) -> dict:
        project_service = ProjectService(self.session)
        project = await project_service._get_project(project_id)

        if not project.dividend_address:
            raise ProjectNotFound()

        usdc_raw = int(usdc_amount * 10**6)

        dividends_service = DividendsService()
        dividends_service._contract = dividends_service.client.get_contract(
            "Dividends", project.dividend_address
        )
        receipt = dividends_service.distribute(usdc_raw)
        tx_hash = receipt["transactionHash"].hex()

        result = await self.session.execute(
            select(Wallet.id)
            .join(Investment, Investment.user_id == Wallet.user_id)
            .where(
                Investment.project_id == project_id,
                Investment.is_active.is_(True),
            )
            .distinct()
        )
        wallet_ids = result.scalars().all()

        await TransactionService(self.session).create_dividend_distribution_bulk(
            tx_hash, wallet_ids, project_id
        )

        return {
            "project_id": str(project_id),
            "dividend_address": project.dividend_address,
            "usdc_amount": str(usdc_amount),
        }
