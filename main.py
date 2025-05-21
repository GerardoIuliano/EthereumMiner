from scripts.client_etherscan import EtherscanClient
from scripts.client_web3 import Web3Client
from scripts.dispatcher import check_and_save
from scripts.utils import get_pragma_from_code, get_compiler_version

import argparse

def main(start_block, end_block):
    
    clientEth = EtherscanClient()
    clientWeb3 = Web3Client()

    print(f"Scanning from block {start_block} to {end_block}")
    file_counter = {
        "0_4": 0,
        "0_5": 0,   
        "0_6": 0,
        "0_7": 0,
        "0_8": 0,
    }
    while(start_block > end_block):
        try:
            print("Scanning Block:", start_block)
            transactions = clientEth.get_transactions_from_block(start_block)
            try:
                #print("Transactions in Last Block:", transactions)
                for tx in transactions:
                    if clientEth.isAContractDeployment(tx):
                        id_transaction = tx["hash"]
                        tx_receipt = clientEth.get_transaction_receipt(id_transaction)
                        contract_address = tx_receipt["contractAddress"]
                        metadata = clientEth.get_contract_metadata(contract_address)
                        proxy = metadata["Proxy"]
                        if proxy == "1":
                            print(f"✗ Skipped {contract_address}: Proxy contract detected. Proxy:", {proxy})
                            continue
                        source_code = metadata["SourceCode"]
                        if source_code.strip().startswith('{'):
                            print(f"✗ Skipped {contract_address}: Source code import external file or library. Source code:", {source_code})
                            continue
                        bytecode = clientWeb3.get_bytecode(contract_address)
                        compiler_version = metadata["CompilerVersion"]
                        library = metadata["Library"]
                        check_and_save(
                            contract_address,
                            source_code,
                            bytecode,
                            compiler_version,
                            library,
                            file_counter
                        )
            except Exception as e:
                print(f"An error occurred in transaction {tx}: {e}") 
        except Exception as e:
            print(f"An error occurred in block {start_block}: {e}") 
        except KeyboardInterrupt:
            print("Process interrupted by user.")
            break
        start_block -= 1    
   
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Ethereum contracts using Etherscan and Web3.")
    parser.add_argument(
        "--start-block",
        type=int,
        help="Start block number (default: latest block)",
        required=False
    )
    parser.add_argument(
        "--end-block",
        type=int,
        help="End block number (default: 0)",
        default=0
    )

    args = parser.parse_args()

    client = EtherscanClient()
    start_block = args.start_block or client.get_last_block()

    main(start_block, args.end_block)

    
    
