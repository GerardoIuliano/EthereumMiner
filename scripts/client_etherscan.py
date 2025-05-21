# etherscan_client.py

import time
import requests
from config import ETHERSCAN_API_URL, ETHERSCAN_API_KEY, ETHERSCAN_RATE_LIMIT_DELAY

class EtherscanClient:
    def __init__(self, api_key=ETHERSCAN_API_KEY):
        self.api_key = api_key

    def _make_request(self, module, action, params):
        time.sleep(ETHERSCAN_RATE_LIMIT_DELAY)
        payload = {
            "module": module,
            "action": action,
            "apikey": self.api_key,
            **params
        }
        response = requests.get(ETHERSCAN_API_URL, params=payload)
        return response.json()

    def get_contract_metadata(self, address):
        result = self._make_request("contract", "getsourcecode", {"address": address})
        if result.get("status") == "1":
            return result["result"][0]
        return None

    # def get_contract_creation_tx(self, address):
    #     result = self._make_request("contract", "getcontractcreation", {"contractaddresses": address})
    #     if result.get("status") == "1":
    #         return result["result"][0]
    #     return None

    # def get_contract_bytecode(self, address):
    #     result = self._make_request("proxy", "eth_getCode", {"address": address, "tag": "latest"})
    #     return result.get("result", None)
    
    def get_last_block(self):
        result = self._make_request("proxy", "eth_blockNumber", {})
        return int(result.get("result", None), 16) 
    
    def get_transactions_from_block(self, block_number):
        result = self._make_request("proxy", "eth_getBlockByNumber", {"tag": hex(block_number), "boolean": "true"})
        if result["result"]["transactions"] != []:
            return result["result"]["transactions"]
        else:
            print("Error:", "get_transactions_from_block: No transactions found in block", block_number)
            return None
    
    def get_transaction_receipt(self, tx_hash):
        result = self._make_request("proxy", "eth_getTransactionReceipt", {"txhash": tx_hash})
        if result["result"] is not None:        
            return result["result"]
        else:
            print("Error:", "get_transaction_receipt: Transaction not found", tx_hash)   
            return None
        
    def isAContractDeployment(self, tx):
        if tx["to"] is None:
            return True
        else:
            return False