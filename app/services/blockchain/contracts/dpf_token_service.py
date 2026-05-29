from app.services.blockchain.base_contract_service import BaseContractService
from app.core.config import settings


class DpfTokenService(BaseContractService):
    """
    Service for interacting with DpfFactory.
    Creates DPF tokens for each approved project.
    """

    contract_name = "DpfFactory"

    def __init__(self):
        super().__init__(address=settings.FACTORY_ADDRESS)

    def create_project_token(
        self,
        name: str,
        suffix: str,
        supply: int,
    ) -> str:
        """
        Creates a DPF token for a project and returns its address.
        The supply is expressed in base units (18 decimal places).
        """
        receipt = self.transact(
            "createProjectToken",
            name,
            suffix,
            supply,
            settings.PLATFORM_ADDRESS,
            settings.MARKETPLACE_ADDRESS,
        )

        logs = self.contract.events.TokenCreated().process_receipt(receipt)
        return logs[0]["args"]["token"]

    def tokens_count(self) -> int:
        return self.call("tokensCount")
