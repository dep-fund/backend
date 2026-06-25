from app.services.blockchain.base_contract_service import BaseContractService
from app.services.blockchain.deployment import DeploymentReaderProduction


class DividendsService(BaseContractService):
    """
    Service for deploying and operating Dividend contracts.
    One instance per project.
    """

    contract_name = "Dividends"

    def approve_usdc(self, dividend_address: str):
        usdc = self.client.get_contract(
            "MockUSDC", DeploymentReaderProduction.get_addresses()["usdc_address"]
        )

        tx = usdc.functions.approve(dividend_address, 2**256 - 1).build_transaction(
            {"from": self.client.deployer.address}
        )

        self.client.send_transaction(tx)

    def deploy(self, dpf_token: str, issuer: str, offering: str) -> str:
        """
        Deploy a new Dividends contract and return its address.
        """
        # addresses = DeploymentReader.get_addresses()
        addresses = DeploymentReaderProduction.get_addresses()

        address = self.client.deploy_contract(
            self.contract_name,
            dpf_token,
            addresses["usdc_address"],
            issuer,
            offering,
        )

        self._contract = self.client.get_contract(self.contract_name, address)
        self.approve_usdc(address)
        return address

    def distribute(self, usdc_amount: int) -> dict:
        """Distributes USDC dividends to all DPF token holders."""
        return self.transact("distribute", usdc_amount)
