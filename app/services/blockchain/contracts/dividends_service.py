from app.services.blockchain.base_contract_service import BaseContractService
from app.services.blockchain.deployment import DeploymentReader


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
        addresses = DeploymentReader.get_addresses()

        address = self.client.deploy_contract(
            self.contract_name,
            dpf_token,
            addresses["usdc_address"],  
            issuer,
            offering,
        )

        self._contract = self.client.get_contract(self.contract_name, address)
        return address

    def distribute(self, usdc_amount: int) -> dict:
        """Distributes USDC dividends to all DPF token holders."""
        return self.transact("distribute", usdc_amount)