from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.core.enums import TradeStatus


class TradeCreate(BaseModel):
    publication_id: UUID
    amount: Decimal


class TradeResponse(BaseModel):
    id: UUID
    publication_id: UUID
    buyer_id: UUID
    amount: Decimal
    total_price: Decimal
    status: TradeStatus
    tx_hash: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TradeUpdateStatus(BaseModel):
    tx_hash: str