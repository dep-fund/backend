from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enums import PublicationStatus
from app.exceptions.marketplace import (
    PublicationNotActive,
    PublicationNotFound,
)
from app.models.publication import Publication
from app.schemas.publication import PublicationCreate, PublicationResponse


class PublicationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_publication(
        self, data: PublicationCreate, seller_id: UUID
    ) -> PublicationResponse:
        publication = Publication(
            token_id=data.token_id,
            seller_id=seller_id,
            total=data.total,
            available=data.total,
            price_per_token=data.price_per_token,
            listing_id=data.listing_id,
            status=PublicationStatus.active,
        )
        self.session.add(publication)
        await self.session.commit()
        await self.session.refresh(publication)
        return await self._get_publication_with_relations(publication.id)

    async def get_publication(self, publication_id: UUID) -> PublicationResponse:
        publication = await self._get_publication_with_relations(publication_id)
        if not publication:
            raise PublicationNotFound()
        return publication

    async def get_all_publications(self) -> list[PublicationResponse]:
        result = await self.session.scalars(
            select(Publication)
            .options(selectinload(Publication.token))
            .where(Publication.status == PublicationStatus.active)
        )
        return [PublicationResponse.model_validate(p) for p in result]

    async def cancel_publication(
        self, publication_id: UUID, user_id: UUID
    ) -> PublicationResponse:
        publication = await self.session.scalar(
            select(Publication).where(Publication.id == publication_id)
        )
        if not publication:
            raise PublicationNotFound()
        if publication.status != PublicationStatus.active:
            raise PublicationNotActive()

        publication.status = PublicationStatus.canceled
        await self.session.commit()
        await self.session.refresh(publication)
        return await self._get_publication_with_relations(publication.id)

    async def _get_publication_with_relations(
        self, publication_id: UUID
    ) -> PublicationResponse:
        publication = await self.session.scalar(
            select(Publication)
            .options(selectinload(Publication.token))
            .where(Publication.id == publication_id)
        )
        if not publication:
            raise PublicationNotFound()
        return PublicationResponse.model_validate(publication)
    
    async def get_my_publications(self, seller_id: UUID) -> list[PublicationResponse]:
        result = await self.session.scalars(
            select(Publication)
            .options(selectinload(Publication.token))
            .where(Publication.seller_id == seller_id)
            .order_by(Publication.created_at.desc())
        )
        return [PublicationResponse.model_validate(p) for p in result]