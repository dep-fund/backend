import json
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
latest_block = w3.eth.get_block('latest')
if latest_block.transactions:
    tx_hash = latest_block.transactions[-1]
    receipt = w3.eth.get_transaction_receipt(tx_hash)
    print("Status:", receipt.status)
    print("Logs length:", len(receipt.logs))
    print("Logs:", receipt.logs)
else:
    print("No transactions found.")
