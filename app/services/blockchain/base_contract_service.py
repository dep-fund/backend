from abc import ABC
from web3.contract import Contract
from .base import BlockchainClient


class BaseContractService(ABC):
    """
    Base class for all contract services.
    Every contract in the ecosystem inherits from this class.
    """

    contract_name: str

    def __init__(self, address: str | None = None):
        self.client = BlockchainClient()
        self._contract: Contract | None = None

        if address:
            self._contract = self.client.get_contract(self.contract_name, address)

    @property
    def contract(self) -> Contract:
        if self._contract is None:
            raise RuntimeError(f"{self.contract_name} it has no assigned address.")
        return self._contract

    def call(self, function_name: str, *args):
        """It calls a read-only function (does not use gas)."""
        fn = getattr(self.contract.functions, function_name)
        return fn(*args).call()

    def transact(self, function_name: str, *args) -> dict:
        """It calls a function that writes to the blockchain."""
        fn = getattr(self.contract.functions, function_name)
        tx = fn(*args).build_transaction({"from": self.client.deployer.address})
        return self.client.send_transaction(tx)
