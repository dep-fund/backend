import json
from pathlib import Path
from web3 import Web3
from web3.contract import Contract
from app.core.config import settings


class BlockchainClient:
    """
    Base client for communicating with the blockchain.
    Handles the connection, ABI loading, and transaction signing.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.w3 = Web3(Web3.HTTPProvider(settings.RPC_URL))
        self.deployer = self.w3.eth.account.from_key(settings.DEPLOYER_PRIVATE_KEY)
        self._abi_cache: dict[str, list] = {}
        self._initialized = True

    def _load_abi(self, contract_name: str) -> list:
        """Load and cache the ABI from the artifacts compiled by Foundry."""
        if contract_name in self._abi_cache:
            return self._abi_cache[contract_name]

        abi_path = (
            Path(settings.BLOCKCHAIN_ARTIFACTS_PATH)
            / f"{contract_name}.sol"
            / f"{contract_name}.json"
        )

        with open(abi_path) as f:
            artifact = json.load(f)

        abi = artifact["abi"]
        self._abi_cache[contract_name] = abi
        return abi

    @property
    def is_connected(self) -> bool:
        return self.w3.is_connected()

    def get_contract(self, contract_name: str, address: str) -> Contract:
        """Returns an instance of the contract ready to interact."""
        abi = self._load_abi(contract_name)
        return self.w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)

    def send_transaction(self, tx) -> dict:
        """Sign and send a transaction, waiting for the receipt."""
        tx["nonce"] = self.w3.eth.get_transaction_count(self.deployer.address)
        tx["gas"] = self.w3.eth.estimate_gas(tx)

        if "gasPrice" in tx and ("maxFeePerGas" in tx or "maxPriorityFeePerGas" in tx):
            del tx["gasPrice"]

        signed = self.deployer.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)

    def deploy_contract(self, contract_name: str, *constructor_args) -> str:
        """Deploy a contract and return its address."""
        abi = self._load_abi(contract_name)

        with open(
            Path(settings.BLOCKCHAIN_ARTIFACTS_PATH)
            / f"{contract_name}.sol"
            / f"{contract_name}.json"
        ) as f:
            artifact = json.load(f)

        bytecode = artifact["bytecode"]["object"]

        contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)

        tx = contract.constructor(*constructor_args).build_transaction(
            {
                "from": self.deployer.address,
            }
        )

        receipt = self.send_transaction(tx)
        return receipt["contractAddress"]
