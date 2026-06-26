from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.core.enums import PublicationStatus
from app.schemas.token import TokenResponse


class PublicationCreate(BaseModel):
    token_id: UUID
    total: Decimal
    price_per_token: Decimal
    listing_id: int


class PublicationResponse(BaseModel):
    id: UUID
    token_id: UUID
    seller_id: UUID
    status: PublicationStatus
    total: Decimal
    available: Decimal
    price_per_token: Decimal
    listing_id: int | None
    created_at: datetime
    updated_at: datetime
    token: TokenResponse

    model_config = ConfigDict(from_attributes=True)