from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import PublicationStatus, TradeStatus
from app.exceptions.marketplace import (
    CannotBuyOwnPublication,
    InsufficientAvailableTokens,
    PublicationNotActive,
    PublicationNotFound,
    TradeNotFound,
)
from app.models.publication import Publication
from app.models.trade import Trade
from app.schemas.trade import TradeCreate, TradeResponse
from app.services.investment_service import InvestmentService   


class TradeService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._investment_service = InvestmentService(session)  

    async def create_trade(self, data: TradeCreate, buyer_id: UUID) -> TradeResponse:
        publication = await self.session.scalar(
            select(Publication).where(Publication.id == data.publication_id)
        )
        if not publication:
            raise PublicationNotFound()
        if publication.status != PublicationStatus.active:
            raise PublicationNotActive()
        if publication.seller_id == buyer_id:
            raise CannotBuyOwnPublication()
        if publication.available < data.amount:
            raise InsufficientAvailableTokens()

        total_price = data.amount * publication.price_per_token

        trade = Trade(
            publication_id=data.publication_id,
            buyer_id=buyer_id,
            amount=data.amount,
            total_price=total_price,
            status=TradeStatus.pending,
        )
        self.session.add(trade)

        publication.available -= data.amount
        if publication.available == 0:
            publication.status = PublicationStatus.completed

        await self.session.commit()
        await self.session.refresh(trade)
        return TradeResponse.model_validate(trade)

    async def confirm_trade(self, trade_id: UUID, tx_hash: str) -> TradeResponse:
        trade = await self.session.scalar(
            select(Trade)
            .options(selectinload(Trade.publication))
            .where(Trade.id == trade_id)
        )
        if not trade:
            raise TradeNotFound()

        publication = trade.publication

        # 1. Descontar holdings del vendedor (FIFO sobre sus Investment activas)
        await self._investment_service.consume_holdings(
            user_id=publication.seller_id,
            token_id=publication.token_id,
            amount=trade.amount,
        )

        # 2. Crear el Investment del comprador
        await self._investment_service.register_marketplace_purchase(
            buyer_id=trade.buyer_id,
            token_id=publication.token_id,
            amount=trade.amount,
            unit_price=publication.price_per_token,
            tx_hash=tx_hash,
        )

        trade.status = TradeStatus.confirmed
        trade.tx_hash = tx_hash
        await self.session.commit()
        await self.session.refresh(trade)
        return TradeResponse.model_validate(trade)

    async def fail_trade(self, trade_id: UUID) -> TradeResponse:
        trade = await self.session.scalar(select(Trade).where(Trade.id == trade_id))
        if not trade:
            raise TradeNotFound()

        # devolver los tokens a la publicacion
        publication = await self.session.scalar(
            select(Publication).where(Publication.id == trade.publication_id)
        )
        if publication:
            publication.available += trade.amount
            if publication.status == PublicationStatus.completed:
                publication.status = PublicationStatus.active

        trade.status = TradeStatus.failed
        await self.session.commit()
        await self.session.refresh(trade)
        return TradeResponse.model_validate(trade)

    async def get_trades_by_buyer(self, buyer_id: UUID) -> list[TradeResponse]:
        trades = await self.session.scalars(
            select(Trade).where(Trade.buyer_id == buyer_id)
        )
        return [TradeResponse.model_validate(t) for t in trades]

    async def get_trades_by_publication(
        self, publication_id: UUID
    ) -> list[TradeResponse]:
        trades = await self.session.scalars(
            select(Trade).where(Trade.publication_id == publication_id)
        )
        return [TradeResponse.model_validate(t) for t in trades]
