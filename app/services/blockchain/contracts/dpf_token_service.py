import time
from app.services.blockchain.base_contract_service import BaseContractService
from app.services.blockchain.deployment import DeploymentReaderProduction
from app.core.config import settings


class DpfTokenService(BaseContractService):
    contract_name = "DpfFactory"

    def __init__(self):
        address = DeploymentReaderProduction.get_addresses()["factory_address"]
        super().__init__(address=address)

    def create_project_token(self, name: str, suffix: str, supply: int) -> str:
        print("SUPPLY", supply)
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
        print("SET OFFERING contract address:", self._contract.address)
        print("SET OFFERING to:", offering_address)
        receipt = self.transact("setOffering", offering_address)
        print("SET OFFERING receipt:", receipt)

    def set_dividends(self, token_address: str, dividends_address: str):
        self._contract = self.client.get_contract("DpfToken", token_address)
        print("SET DIVIDENDS contract address:", self._contract.address)
        print("SET DIVIDENDS to:", dividends_address)
        receipt = self.transact("setDividends", dividends_address)
        print("SET DIVIDENDS receipt:", receipt)

    def transfer_to_offering(
        self, token_address: str, offering_address: str, amount: int
    ):
        self._contract = self.client.get_contract("DpfToken", token_address)
        receipt = self.transact("transfer", offering_address, amount * 10**18)
        print("TRANSFER TO OFFERING receipt:", receipt)

    def wait_for_offering_set(
        self, token_address: str, offering_address: str, timeout: int = 30
    ):
        token_contract = self.client.get_contract("DpfToken", token_address)
        deadline = time.time() + timeout
        while time.time() < deadline:
            current = token_contract.functions.offering().call()
            if current.lower() == offering_address.lower():
                return
            time.sleep(1)
        raise TimeoutError(
            f"offering() never updated to {offering_address} after {timeout}s"
        )

    def wait_for_dividends_set(
        self, token_address: str, dividends_address: str, timeout: int = 30
    ):
        token_contract = self.client.get_contract("DpfToken", token_address)
        deadline = time.time() + timeout
        while time.time() < deadline:
            current = token_contract.functions.dividends().call()
            if current.lower() == dividends_address.lower():
                return
            time.sleep(1)
        raise TimeoutError(
            f"dividends() never updated to {dividends_address} after {timeout}s"
        )
