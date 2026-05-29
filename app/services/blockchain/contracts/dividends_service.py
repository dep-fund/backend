from app.services.blockchain.base_contract_service import BaseContractService
from app.core.config import settings


class DividendsService(BaseContractService):
    """
    Service for deploying and operating Dividend contracts.
    One instance per project.
    """

    contract_name = "Dividends"

    def deploy(self, dpf_token: str, issuer: str, offering: str) -> str:
        """
        Deploy a new Dividends contract and return its address.
        """
        address = self.client.deploy_contract(
            self.contract_name,
            dpf_token,
            settings.USDC_ADDRESS,
            issuer,
            offering,
        )

        self._contract = self.client.get_contract(self.contract_name, address)
        return address

    def pending(self, holder: str) -> int:
        return self.call("pending", holder)

    def distribute(self, usdc_amount: int) -> dict:
        return self.transact("distribute", usdc_amount)

    def claim(self) -> dict:
        return self.transact("claim")
