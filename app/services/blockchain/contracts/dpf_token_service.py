import logging
import time
from app.services.blockchain.base_contract_service import BaseContractService
from app.services.blockchain.deployment import DeploymentReaderProduction
from app.core.config import settings

logger = logging.getLogger(__name__)


class DpfTokenService(BaseContractService):
    contract_name = "DpfFactory"

    def __init__(self):
        address = DeploymentReaderProduction.get_addresses()["factory_address"]
        super().__init__(address=address)

    def create_project_token(self, name: str, suffix: str, supply: int) -> str:
        logger.info("SUPPLY %s", supply)
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
        logger.info("SET OFFERING contract address: %s", self._contract.address)
        logger.info("SET OFFERING to: %s", offering_address)
        receipt = self.transact("setOffering", offering_address)
        logger.info("SET OFFERING receipt: %s", receipt)

    def set_dividends(self, token_address: str, dividends_address: str):
        self._contract = self.client.get_contract("DpfToken", token_address)
        logger.info("SET DIVIDENDS contract address: %s", self._contract.address)
        logger.info("SET DIVIDENDS to: %s", dividends_address)
        receipt = self.transact("setDividends", dividends_address)
        logger.info("SET DIVIDENDS receipt: %s", receipt)

    def transfer_to_offering(
        self, token_address: str, offering_address: str, amount: int
    ):
        self._contract = self.client.get_contract("DpfToken", token_address)
        receipt = self.transact("transfer", offering_address, amount * 10**18)
        logger.info("TRANSFER TO OFFERING receipt: %s", receipt)

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
