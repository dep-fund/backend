from decimal import Decimal
from app.services.blockchain.base_contract_service import BaseContractService
from app.services.blockchain.deployment import DeploymentReaderProduction
from app.core.config import settings
import time


class OfferingService(BaseContractService):
    contract_name = "Offering"

    def deploy(
        self,
        dpf_token: str,
        soft_cap: int,
        hard_cap: int,
        token_price: Decimal,
        deadline_seconds: int,
    ) -> str:
        # addresses = DeploymentReader.get_addresses()
        addresses = DeploymentReaderProduction.get_addresses()
        deadline = int(time.time()) + deadline_seconds

        address = self.client.deploy_contract(
            self.contract_name,
            addresses["usdc_address"],
            dpf_token,
            int(soft_cap),
            int(hard_cap),
            int(token_price),
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
