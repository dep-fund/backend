from app.services.blockchain.base_contract_service import BaseContractService
from app.core.config import settings


class MarketplaceService(BaseContractService):
    """
    Service for interacting with the P2P Marketplace.
    """

    contract_name = "Marketplace"

    def __init__(self):
        super().__init__(address=settings.MARKETPLACE_ADDRESS)

    def list_token(self, token: str, amount: int, price_usdc: int) -> int:
        """Publishes a sales offer. Returns the listingId."""
        receipt = self.transact("list", token, amount, price_usdc)
        logs = self.contract.events.Listed().process_receipt(receipt)
        return logs[0]["args"]["listingId"]

    def buy(self, listing_id: int) -> dict:
        """Purchase an active offer."""
        return self.transact("buy", listing_id)

    def cancel(self, listing_id: int) -> dict:
        """Cancel an active offer."""
        return self.transact("cancel", listing_id)

    def listings_count(self) -> int:
        return self.call("listingsCount")

    def get_listing(self, listing_id: int) -> dict:
        result = self.call("listings", listing_id)
        return {
            "seller": result[0],
            "token": result[1],
            "amount": result[2],
            "price_usdc": result[3],
            "active": result[4],
        }
