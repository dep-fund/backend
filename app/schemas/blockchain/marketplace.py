from pydantic import BaseModel

class ListingResponse(BaseModel):
    id: int
    total_amount: int
    remaining_amount: int
    price_per_token: int
    seller: str
    status: str  
    token: str


class MarketplaceInfoResponse(BaseModel):
    marketplace_address: str
    usdc_address: str
    factory_address: str