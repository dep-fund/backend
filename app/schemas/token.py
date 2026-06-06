from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class TokenResponse(BaseModel):
    id: UUID
    name: str
    suffix: str
    contract_address: str

    model_config = ConfigDict(from_attributes=True)


class TokenProjectResponse(BaseModel):
    id: UUID
    token_id: UUID
    project_id: UUID
    total_supply: Decimal
    available_supply: Decimal
    token: TokenResponse
    current_price: Decimal | None = None

    model_config = ConfigDict(from_attributes=True)
