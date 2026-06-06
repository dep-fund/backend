#!/usr/bin/env python3
"""
sync_abis.py
============
Copies the necessary Foundry artifacts from the blockchain repo to the backend.

Usage:
    python sync_abis.py [--blockchain-out ../blockchain/out]

Contracts that need the FULL artifact (ABI + bytecode) because the backend deploys them:
    - Offering
    - Dividends

Contracts that only need the ABI (already deployed, fixed addresses):
    - DpfFactory
    - Marketplace
"""

import argparse
import json
import shutil
from pathlib import Path

# Destination inside the backend project (relative to this script)
DEST_DIR = Path(__file__).parent / "app" / "services" / "blockchain" / "abis"

# Contracts that need the full artifact (ABI + bytecode) — backend deploys them
FULL_ARTIFACT_CONTRACTS = ["Offering", "Dividends"]

# Contracts that only need the ABI — already deployed, fixed addresses
ABI_ONLY_CONTRACTS = ["DpfFactory", "DpfToken", "Marketplace"]

ALL_CONTRACTS = FULL_ARTIFACT_CONTRACTS + ABI_ONLY_CONTRACTS


def sync(blockchain_out: Path) -> None:
    DEST_DIR.mkdir(parents=True, exist_ok=True)

    errors = []

    for contract in ALL_CONTRACTS:
        src = blockchain_out / f"{contract}.sol" / f"{contract}.json"

        if not src.exists():
            errors.append(f"  ✗ Not found: {src}")
            continue

        with open(src) as f:
            artifact = json.load(f)

        if contract in ABI_ONLY_CONTRACTS:
            output = {"abi": artifact["abi"]}
            dest = DEST_DIR / f"{contract}.json"
            with open(dest, "w") as f:
                json.dump(output, f, indent=2)
            print(
                f"  ✓ {contract} (ABI only) → {dest.relative_to(Path(__file__).parent)}"
            )
        else:
            dest = DEST_DIR / f"{contract}.json"
            shutil.copy2(src, dest)
            print(
                f"  ✓ {contract} (full artifact) → {dest.relative_to(Path(__file__).parent)}"
            )

    if errors:
        print("\nErrors:")
        for e in errors:
            print(e)
        raise SystemExit(1)

    print(
        f"\nDone. {len(ALL_CONTRACTS)} artifacts synced to {DEST_DIR.relative_to(Path(__file__).parent)}/"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Sync Foundry artifacts to the backend."
    )
    parser.add_argument(
        "--blockchain-out",
        type=Path,
        default=Path(__file__).parent.parent / "blockchain" / "out",
        help="Path to the Foundry 'out' directory (default: ../blockchain/out)",
    )
    args = parser.parse_args()

    blockchain_out = args.blockchain_out.resolve()
    print(f"Syncing from: {blockchain_out}\n")

    if not blockchain_out.exists():
        print(f"Error: blockchain 'out' directory not found at {blockchain_out}")
        print("Run 'forge build' first, or pass --blockchain-out <path>")
        raise SystemExit(1)

    sync(blockchain_out)


if __name__ == "__main__":
    main()
