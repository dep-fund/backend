from enum import IntEnum

from app.services.blockchain.base_contract_service import BaseContractService
from app.core.config import settings
from app.services.blockchain.deployment import DeploymentReader


class ListingStatus(IntEnum):
    """
    Mirrors the Status enum in the Marketplace contract.
    Solidity enums are returned as integers by web3.py.
    """
    ACTIVE = 0
    FINALIZED = 1
    CANCELLED = 2


class MarketplaceService(BaseContractService):
    """
    Service for interacting with the Marketplace contract.
    Handles reading listings from the blockchain.
    Transactions (list, buy, cancel) are signed by the user from the frontend.
    """

    contract_name = "Marketplace"

    def __init__(self):
        address = DeploymentReader.get_addresses()["marketplace_address"]
        super().__init__(address=address)

    def _parse_listing(self, listing_id: int, raw: tuple) -> dict:
        """
        Converts the raw tuple returned by the contract into a dict.
        Contract struct order: (totalAmount, remainingAmount, pricePerToken, seller, status, token)
        """
        return {
            "id": listing_id,
            "total_amount": raw[0],
            "remaining_amount": raw[1],
            "price_per_token": raw[2],
            "seller": raw[3],
            "status": ListingStatus(raw[4]).name.lower(),  # "active" | "finalized" | "cancelled"
            "token": raw[5],
        }

    def listings_count(self) -> int:
        """Returns the total number of listings ever created (active or not)."""
        return self.call("listingsCount")

    def get_listing(self, listing_id: int) -> dict:
        """
        Returns a single listing by ID.
        Raises IndexError if listing_id is out of range.
        """
        count = self.listings_count()
        if listing_id < 0 or listing_id >= count:
            raise IndexError(f"Listing {listing_id} does not exist.")

        raw = self.call("listings", listing_id)
        return self._parse_listing(listing_id, raw)

    def get_all_listings(self, status: ListingStatus | None = ListingStatus.ACTIVE) -> list[dict]:
        """
        Returns all listings, optionally filtered by status.
        - status=ListingStatus.ACTIVE    → solo activos (default)
        - status=ListingStatus.FINALIZED → solo finalizados
        - status=ListingStatus.CANCELLED → solo cancelados
        - status=None                    → todos sin filtro
        """
        count = self.listings_count()
        listings = []

        for i in range(count):
            listing = self.get_listing(i)
            if status is not None and listing["status"] != status.name.lower():
                continue
            listings.append(listing)

        return listings

    def get_listings_by_seller(self, seller_address: str, status: ListingStatus | None = ListingStatus.ACTIVE) -> list[dict]:
        """Returns listings for a given seller address, filtered by status (default: active)."""
        all_listings = self.get_all_listings(status=status)
        seller = seller_address.lower()
        return [l for l in all_listings if l["seller"].lower() == seller]

    def get_listings_by_token(self, token_address: str, status: ListingStatus | None = ListingStatus.ACTIVE) -> list[dict]:
        """Returns listings for a given DPF token address, filtered by status (default: active)."""
        all_listings = self.get_all_listings(status=status)
        token = token_address.lower()
        return [l for l in all_listings if l["token"].lower() == token]