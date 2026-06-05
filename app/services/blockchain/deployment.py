import json
from pathlib import Path


class DeploymentReader:
    DEPLOY_PATH = Path(
        "/blockchain/broadcast/Deploy.s.sol/31337/run-latest.json"
    )

    USDC_DEPLOY_PATH = Path(
        "/blockchain/broadcast/DeployMockUSDC.s.sol/31337/run-latest.json"
    )

    @staticmethod
    def _load(path: Path) -> dict:
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def _find_contract(cls, data: dict, contract_name: str) -> str:
        for tx in data.get("transactions", []):
            if tx.get("contractName") == contract_name:
                return tx["contractAddress"]

        raise RuntimeError(f"Contract not found: {contract_name}")

    @classmethod
    def get_addresses(cls) -> dict:
        deploy_data = cls._load(cls.DEPLOY_PATH)
        usdc_data = cls._load(cls.USDC_DEPLOY_PATH)

        return {
            "factory_address": cls._find_contract(
                deploy_data,
                "DpfFactory.sol\\DpfFactory",
            ),
            "marketplace_address": cls._find_contract(
                deploy_data,
                "Marketplace",
            ),
            "usdc_address": cls._find_contract(
                usdc_data,
                "MockUSDC.sol\\MockUSDC",
            ),
            "offering_address": cls._find_contract(
                deploy_data,
                "Offering",
            ),
        }