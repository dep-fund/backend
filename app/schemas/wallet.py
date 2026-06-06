from uuid import UUID
from pydantic import BaseModel, ConfigDict, field_validator
import re


class WalletCreateRequest(BaseModel):
    address: str

    @field_validator("address")
    @classmethod
    def validate_ethereum_address(cls, v: str) -> str:
        if not re.fullmatch(r"0x[0-9a-fA-F]{40}", v):
            raise ValueError("Invalid Ethereum address format")
        return v.lower()


class WalletResponse(BaseModel):
    id: UUID
    address: str
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)
