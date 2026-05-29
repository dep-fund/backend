from app.services.blockchain.base_contract_service import BaseContractService
from app.core.config import settings
import time


class OfferingService(BaseContractService):
    """
    Service for deploying and operating Offering contracts.
    One instance is required per project.
    """

    contract_name = "Offering"

    def deploy(
        self,
        dpf_token: str,
        soft_cap: int,
        hard_cap: int,
        token_price: int,
        deadline_seconds: int,
    ) -> str:
        """
        Deploy a new Offering contract and return your address.
        """
        deadline = int(time.time()) + deadline_seconds

        address = self.client.deploy_contract(
            self.contract_name,
            settings.USDC_ADDRESS,
            dpf_token,
            soft_cap,
            hard_cap,
            token_price,
            deadline,
            settings.TREASURY_ADDRESS,
        )

        self._contract = self.client.get_contract(self.contract_name, address)
        return address

    def total_raised(self) -> int:
        return self.call("totalRaised")

    def soft_cap(self) -> int:
        return self.call("SOFT_CAP")

    def contributions(self, address: str) -> int:
        return self.call("contributions", address)

    def invest(self, usdc_amount: int) -> dict:
        return self.transact("invest", usdc_amount)

    def refund(self) -> dict:
        return self.transact("refund")

    def withdraw(self) -> dict:
        return self.transact("withdraw")
