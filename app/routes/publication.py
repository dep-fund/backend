from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.dependencies.user_dependencies import get_current_standard_user
from app.models.user import User
from app.schemas.publication import PublicationCreate, PublicationResponse
from app.schemas.trade import TradeCreate, TradeResponse
from app.services.publication_service import PublicationService

router = APIRouter(prefix="/publications", tags=["Publications"])


@router.get("", response_model=list[PublicationResponse])
async def get_publications(
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await PublicationService(session).get_all_publications()


@router.get("/my", response_model=list[PublicationResponse])
async def get_my_publications(
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await PublicationService(session).get_my_publications(seller_id=current_user.id)

@router.get("/{publication_id}", response_model=PublicationResponse)
async def get_publication(
    publication_id: UUID,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await PublicationService(session).get_publication(publication_id)


@router.post("", response_model=PublicationResponse, status_code=201)
async def create_publication(
    data: PublicationCreate,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await PublicationService(session).create_publication(data, seller_id=current_user.id)


@router.patch("/{publication_id}/cancel", response_model=PublicationResponse)
async def cancel_publication(
    publication_id: UUID,
    current_user: User = Depends(get_current_standard_user),
    session: AsyncSession = Depends(get_session),
):
    return await PublicationService(session).cancel_publication(publication_id, user_id=current_user.id)
