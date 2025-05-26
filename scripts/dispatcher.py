import re, os, json

from scripts.utils import (
    get_pragma_from_code,
)
from config import COUNTER_LIMIT





def save(
    contract_address: str,  # Indirizzo del contratto
    source_code: str,       # Codice sorgente del contratto
    runtime_bytecode: str,          # Bytecode del contratto
    creation_bytecode: str,  # Bytecode di creazione del contratto
    compiler_version: str,  # Versione del compilatore
    compiler_type: str,  # Tipo di compilatore
    optimization: str,  # Ottimizzazione
    abi: str,  # ABI
    constructor_arguments: str,  # Argomenti del costruttore
    constructor_arguments_decoded: str,  # Argomenti del costruttore decodificati
    file_counter: dict  # Contatore dei file salvati
):
    """
    Salva le infor in un file con relativo logs.
    """
    # if is_candidate(
    #     contract_address,
    #     source_code,
    #     runtime_bytecode,
    #     creation_bytecode,
    #     compiler_version,
    #     library
    # ):  

    pragma_version = get_pragma_from_code(source_code)
    version = pragma_version.replace(".", "_")
    # From 0_8_30 to 0_8
    version_folder = "_".join(version.split("_")[:2])  # Es. 0_8
    if file_counter[version_folder] < COUNTER_LIMIT[version_folder]:
        file_counter[version_folder] += 1
        # Creazione delle cartelle se non esistono
        os.makedirs(f"contracts/{version_folder}/sourcecode", exist_ok=True)
        os.makedirs(f"contracts/{version_folder}/runtime_bytecode", exist_ok=True)
        os.makedirs(f"contracts/{version_folder}/creation_bytecode", exist_ok=True)

        source_path = f"contracts/{version_folder}/sourcecode/{contract_address}.sol"
        runtime_bytecode_path = f"contracts/{version_folder}/runtime_bytecode/{contract_address}.hex"
        creation_bytecode_path = f"contracts/{version_folder}/creation_bytecode/{contract_address}.hex"

        # Salva il source code solo se non esiste
        if not os.path.exists(source_path) and not os.path.exists(runtime_bytecode_path) and not os.path.exists(creation_bytecode_path):
            with open(source_path, "w") as file:
                file.write(source_code)
            with open(runtime_bytecode_path, "w") as file:
                file.write(runtime_bytecode)
            with open(creation_bytecode_path, "w") as file:
                file.write(creation_bytecode)
            # Salvataggio su logs.json
            logs_path = f"contracts/{version_folder}/logs.json"
            if os.path.exists(logs_path):
                with open(logs_path, "r") as file:
                    logs = json.load(file)
            else:
                logs = {}
            
            try:
                abi = json.loads(abi)
            except json.JSONDecodeError:
                print("ABI non è un JSON valido.")
                abi = []
            
            logs[contract_address] = {
                "pragma": pragma_version,
                "compiler version": compiler_version,
                "compiler type": compiler_type,
                "optimization": optimization,
                "abi": abi,
                "constructor arguments": constructor_arguments,
                "constructor arguments decoded": constructor_arguments_decoded,
            }

            with open(logs_path, "w") as file:
                json.dump(logs, file, indent=4)

            print("✓ Saved:", contract_address)
        else:
            print(f"✗ Skipped: Source file already exists for {contract_address}")
    else:
        print(f"✗ Skipped: Counter limit reached for {version_folder}. Max: {COUNTER_LIMIT[version_folder]}")