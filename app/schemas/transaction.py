from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.enums import TransactionType


class TransactionResponse(BaseModel):
    id: UUID
    tx_hash: str
    type: TransactionType
    wallet_id: UUID
    project_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)
