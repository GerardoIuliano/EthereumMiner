from scripts.client_etherscan import EtherscanClient
from scripts.client_web3 import Web3Client
from scripts.dispatcher import save
from scripts.utils import * 

import argparse, traceback

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
                        #print("Metadata:", metadata)
                        proxy = metadata["Proxy"]
                        if proxy == "1":
                            print(f"✗ Skipped {contract_address}: Proxy contract detected. Proxy:", {proxy})
                            continue
                        source_code = metadata["SourceCode"]
                        if source_code.strip().startswith('{'):
                            print(f"✗ Skipped {contract_address}: Source code import external file or library.")
                            continue

                        optimization = metadata["OptimizationUsed"]
                        constructor_arguments = metadata["ConstructorArguments"]
                        abi = metadata["ABI"]
                        compiler_type = metadata["CompilerType"]
                        #print("ABI:", abi)
                        #OptimizationUsed
                        #print("OptimizationUsed:", metadata["OptimizationUsed"])
                        #ConstructorArguments
                        #print("ConstructorArguments:", metadata["ConstructorArguments"])
                        runtime_bytecode = clientWeb3.get_bytecode(contract_address)
                        #print("Runtime bytecode:", runtime_bytecode)
                        creation_bytecode = tx["input"]
                        #print("Creation bytecode:", creation_bytecode)

                        compiler_version = metadata["CompilerVersion"]
                        
                        library = metadata["Library"]
                        is_code_ok = check_source_and_byte(
                            source_code,
                            runtime_bytecode,
                            creation_bytecode,
                            contract_address)
                        if is_code_ok:
                            are_versions_match = is_same_version(
                                source_code, 
                                compiler_version, 
                                contract_address)
                        is_library_empty = isLibraryEmpty(
                            library, 
                            contract_address)
                        is_abi_ok = isAbiAvailable(
                            abi, 
                            contract_address)
                        if is_code_ok and are_versions_match and is_library_empty and is_abi_ok:
                            # Salva il contratto
                            print("constructor args:", constructor_arguments)
                            print("abi:", abi)
                            constructor_arguments_decoded = decode_constructor_args(abi, constructor_arguments)
                            
                            print("decoded constructor args:", constructor_arguments_decoded)
                            save(
                                contract_address,
                                source_code,
                                runtime_bytecode,
                                creation_bytecode,
                                compiler_version,
                                compiler_type,
                                optimization,
                                abi,
                                constructor_arguments,
                                constructor_arguments_decoded,
                                file_counter
                            )
            except Exception as e:
                print(f"An error occurred in transaction {tx["hash"]}: {traceback.print_exc()}") 
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

    
    
