from decimal import Decimal
from pydantic import BaseModel, Field


class DistributeRequest(BaseModel):
    usdc_amount: Decimal = Field(
        ..., gt=0, description="Monto en USDC a distribuir (con decimales)"
    )
