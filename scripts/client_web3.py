from web3 import Web3
from config import INFURA_API_KEY

class Web3Client:
    # Connettiti a un provider Ethereum, ad esempio Infura
    def __init__(self, api_key=INFURA_API_KEY):
        self.w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/"+api_key))

    def get_bytecode(self, address):
        bytecode = self.w3.eth.get_code(Web3.to_checksum_address(address))
        return bytecode.hex()

