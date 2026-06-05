import json
from pathlib import Path
from web3 import Web3
from web3.contract import Contract
from app.core.config import settings

_BUNDLED_ABIS_DIR = Path(__file__).parent / "abis"


class BlockchainClient:
    """
    Base client for communicating with the blockchain.
    Handles the connection, ABI loading, and transaction signing.

    ABI resolution order:
      1. app/services/blockchain/abis/<ContractName>.json  (bundled, always preferred)
      2. BLOCKCHAIN_ARTIFACTS_PATH env var                 (legacy / local Anvil fallback)
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

    def _artifact_path(self, contract_name: str) -> Path:
        """
        Resolves the artifact JSON path.

        Prefers the bundled copy inside the backend repo so the service
        is self-contained and does not depend on the blockchain repo
        being mounted at runtime.
        """
        bundled = _BUNDLED_ABIS_DIR / f"{contract_name}.json"
        if bundled.exists():
            return bundled

        # Fallback: original Foundry output path (local dev / Anvil)
        legacy = (
            Path(settings.BLOCKCHAIN_ARTIFACTS_PATH)
            / f"{contract_name}.sol"
            / f"{contract_name}.json"
        )
        if legacy.exists():
            return legacy

        raise FileNotFoundError(
            f"ABI for '{contract_name}' not found.\n"
            f"  Looked in: {bundled}\n"
            f"  Fallback:  {legacy}\n"
            f"  Run 'make sync-abis' to populate the bundled ABIs."
        )

    def _load_abi(self, contract_name: str) -> list:
        """Load and cache the ABI for the given contract."""
        if contract_name in self._abi_cache:
            return self._abi_cache[contract_name]

        path = self._artifact_path(contract_name)
        with open(path) as f:
            artifact = json.load(f)

        # Support both full Foundry artifacts and ABI-only files
        abi = artifact["abi"] if "abi" in artifact else artifact
        self._abi_cache[contract_name] = abi
        return abi

    def _load_bytecode(self, contract_name: str) -> str:
        """Load the deployment bytecode (only available in full artifacts)."""
        path = self._artifact_path(contract_name)
        with open(path) as f:
            artifact = json.load(f)

        try:
            return artifact["bytecode"]["object"]
        except (KeyError, TypeError):
            raise RuntimeError(
                f"Bytecode not found for '{contract_name}'.\n"
                f"  The artifact at {path} is ABI-only.\n"
                f"  Re-run 'make sync-abis' — '{contract_name}' must be in "
                f"FULL_ARTIFACT_CONTRACTS."
            )

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
        bytecode = self._load_bytecode(contract_name)

        contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)

        tx = contract.constructor(*constructor_args).build_transaction(
            {
                "from": self.deployer.address,
            }
        )

        receipt = self.send_transaction(tx)
        return receipt["contractAddress"]
