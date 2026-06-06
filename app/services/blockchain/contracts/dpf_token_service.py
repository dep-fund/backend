from app.services.blockchain.base_contract_service import BaseContractService
from app.services.blockchain.deployment import DeploymentReaderProduction
from app.core.config import settings


class DpfTokenService(BaseContractService):
    contract_name = "DpfFactory"

    def __init__(self):
        # address = DeploymentReader.get_addresses()["factory_address"]
        address = DeploymentReaderProduction.get_addresses()["factory_address"]
        super().__init__(address=address)

    def create_project_token(self, name: str, suffix: str, supply: int) -> str:
        # addresses = DeploymentReader.get_addresses()
        addresses = DeploymentReaderProduction.get_addresses()
        receipt = self.transact(
            "createProjectToken",
            name,
            suffix,
            supply * 10**18,
            settings.PLATFORM_ADDRESS,
            addresses["marketplace_address"],
        )
        logs = self.contract.events.TokenCreated().process_receipt(receipt)
        return logs[0]["args"]["token"]

    def tokens_count(self) -> int:
        return self.call("tokensCount")

    def set_offering(self, token_address: str, offering_address: str):
        self._contract = self.client.get_contract("DpfToken", token_address)
        self.transact("setOffering", offering_address)

    def transfer_to_offering(
        self, token_address: str, offering_address: str, amount: int
    ):
        self._contract = self.client.get_contract("DpfToken", token_address)
        self.transact("transfer", offering_address, amount * 10**18)
