from web3 import Web3
from config import INFURA_API_KEY, INFURA_API_URL
import json

class Web3Client:
    # Connettiti a un provider Ethereum, ad esempio Infura
    def __init__(self, api_key=INFURA_API_KEY):
        self.w3 = Web3(Web3.HTTPProvider(INFURA_API_URL+api_key))

    def get_bytecode(self, address):
        #runtime bytecode
        bytecode = self.w3.eth.get_code(Web3.to_checksum_address(address))
        return bytecode.hex()

    