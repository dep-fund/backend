from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import TransactionType

from datetime import datetime


class TransactionResponse(BaseModel):
    id: UUID
    tx_hash: str
    type: TransactionType
    wallet_id: UUID
    project_id: Optional[UUID] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
