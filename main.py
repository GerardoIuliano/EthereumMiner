import concurrent.futures
import argparse
import traceback
from multiprocessing import Manager
from scripts.client_etherscan import EtherscanClient
from scripts.client_web3 import Web3Client
from scripts.dispatcher import save
from scripts.utils import * 
from threading import Lock



def process_block_range(start_block, end_block, file_counter, lock):
    clientEth = EtherscanClient()
    clientWeb3 = Web3Client()

    print(f"Scanning from block {start_block} to {end_block}")
    while start_block >= end_block:
        try:
            print("Scanning Block:", start_block)
            transactions = clientEth.get_transactions_from_block(start_block)
            try:
                for tx in transactions:
                    # Aggiungi protezione con Lock per l'accesso sicuro al file_counter
                    with lock:
                        if clientEth.isAContractDeployment(tx):
                            id_transaction = tx["hash"]
                            tx_receipt = clientEth.get_transaction_receipt(id_transaction)      
                            contract_address = tx_receipt["contractAddress"]
                            metadata = clientEth.get_contract_metadata(contract_address)

                            proxy = metadata["Proxy"]
                            source_code = metadata["SourceCode"]
                            optimization = metadata["OptimizationUsed"]
                            constructor_arguments = metadata["ConstructorArguments"]
                            abi = metadata["ABI"]
                            compiler_type = metadata["CompilerType"]
                            
                            creation_bytecode = tx["input"]
                            compiler_version = metadata["CompilerVersion"]
                            library = metadata["Library"]
                            version_to_skip = "0_8"
                            if (not skipVersion(version_to_skip, source_code)):
                                
                                runtime_bytecode = clientWeb3.get_bytecode(contract_address)

                                if proxy == "1":
                                    print(f"✗ Skipped {contract_address}: Proxy contract detected. Proxy:", {proxy})
                                    continue
                                if source_code.strip().startswith('{'):
                                    print(f"✗ Skipped {contract_address}: Source code import external file or library.")
                                    continue

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
                                    constructor_arguments_decoded = decode_constructor_args(abi, constructor_arguments)
                                    # Salva il contratto
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
                            else:
                                print(f"✗ Skipped version: {version_to_skip}") 
            except Exception as e:
                print(f"An error occurred in transaction {tx['hash']}: {traceback.print_exc()}") 
        except Exception as e:
            print(f"An error occurred in block {start_block}: {e}\n{traceback.print_exc()}") 
        except KeyboardInterrupt:
            print("Process interrupted by user.")
            break
        start_block -= 1


def parallel_process_blocks(start_block, end_block, num_threads):
    # Crea un manager per un dizionario condiviso tra i thread
    with Manager() as manager:
        file_counter = manager.dict({
            "0_4": 0,
            "0_5": 0,   
            "0_6": 0,
            "0_7": 0,
            "0_8": 0,
        })
        lock = Lock()  # Lock per sincronizzare l'accesso ai dati condivisi
        
        # Calcola la dimensione del sotto-intervallo per ogni thread
        step = (start_block - end_block + 1) // num_threads
        ranges = []
        
        # Crea i sotto-intervalli
        for i in range(num_threads):
            sub_start = start_block - i * step
            sub_end = sub_start - step + 1
            if i == num_threads - 1:
                sub_end = end_block  # Assicurati che l'ultimo blocco arrivi a end_block
            ranges.append((sub_start, sub_end))

        # Usa ThreadPoolExecutor per eseguire i calcoli in parallelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(process_block_range, r[0], r[1], file_counter, lock) for r in ranges
            ]
            # Aspetta che tutti i task siano completi
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"An error occurred: {e}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Analyze Ethereum contracts using Etherscan and Web3.")
    parser.add_argument(
        "--start-block",
        type=int,
        help="Start block number (default: latest block)",
        required=False,
        default=EtherscanClient().get_last_block()
    )
    parser.add_argument(
        "--end-block",
        type=int,
        help="End block number (default: 0)",
        required=False,
        default=0
    )
    parser.add_argument(
        "--threads",
        type=int,
        help="Number of threads for parallel execution (default: 4)",
        default=1,
        required=False
    )

    args = parser.parse_args()

    # Avvia l'esecuzione parallela
    parallel_process_blocks(args.start_block, args.end_block, num_threads=args.threads)
