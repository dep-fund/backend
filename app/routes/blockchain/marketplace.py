from fastapi import APIRouter, Depends, Query

from app.core.dependencies.user_dependencies import get_current_standard_user
from app.models.user import StandardUser
from app.services.blockchain.contracts.marketplace_service import (
    MarketplaceService,
    ListingStatus,
)

from app.schemas.blockchain.marketplace import ListingResponse, MarketplaceInfoResponse
from app.services.blockchain.deployment import DeploymentReaderProduction

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


@router.get("/info", response_model=MarketplaceInfoResponse)
async def get_marketplace_info(
    current_user: StandardUser = Depends(get_current_standard_user),
):
    addresses = DeploymentReaderProduction.get_addresses()

    return MarketplaceInfoResponse(
        marketplace_address=addresses["marketplace_address"],
        usdc_address=addresses["usdc_address"],
        factory_address=addresses["factory_address"],
    )


@router.get("", response_model=list[ListingResponse])
async def get_active_listings(
    current_user: StandardUser = Depends(get_current_standard_user),
):
    """Returns all active listings."""
    return MarketplaceService().get_all_listings(status=ListingStatus.ACTIVE)


@router.get("/listings/{listing_id}", response_model=ListingResponse)
async def get_listing(
    listing_id: int,
    current_user: StandardUser = Depends(get_current_standard_user),
):
    """Returns a single listing by ID."""
    return MarketplaceService().get_listing(listing_id)


@router.get("/listings/seller/{seller_address}", response_model=list[ListingResponse])
async def get_listings_by_seller(
    seller_address: str,
    status: str = Query("active", pattern="^(active|finalized|cancelled)$"),
    current_user: StandardUser = Depends(get_current_standard_user),
):
    """
    Returns listings for a given seller address.
    Useful for 'my listings' view. Filter by status (default: active).
    """
    listing_status = ListingStatus[status.upper()]
    return MarketplaceService().get_listings_by_seller(
        seller_address, status=listing_status
    )


@router.get("/listings/token/{token_address}", response_model=list[ListingResponse])
async def get_listings_by_token(
    token_address: str,
    status: str = Query("active", pattern="^(active|finalized|cancelled)$"),
    current_user: StandardUser = Depends(get_current_standard_user),
):
    """
    Returns listings for a given DPF token address.
    Useful to see the market for a specific project.
    """
    listing_status = ListingStatus[status.upper()]
    return MarketplaceService().get_listings_by_token(
        token_address, status=listing_status
    )
