import re, os, json

from scripts.utils import (
    get_pragma_from_code,
    get_compiler_version,
    is_same_version,
    check_source_and_byte,  
    is_candidate
)
from config import COUNTER_LIMIT





def check_and_save(
    contract_address: str,  # Indirizzo del contratto
    source_code: str,       # Codice sorgente del contratto
    bytecode: str,          # Bytecode del contratto
    compiler_version: str,  # Versione del compilatore
    library: str,    # Versione della libreria
    file_counter: dict  # Contatore dei file salvati
):
    """
    Salva il codice sorgente in un file.
    :param contract_address: Indirizzo del contratto
    :param source_code: Codice sorgente del contratto
    :param compiler_version: Versione del compilatore
    :param library_version: Versione della libreria
    :return: None
    """
    if is_candidate(
        contract_address,
        source_code,
        bytecode,
        compiler_version,
        library
    ):  

        pragma_version = get_pragma_from_code(source_code)
        version = pragma_version.replace(".", "_")
        # From 0_8_30 to 0_8
        version_folder = "_".join(version.split("_")[:2])  # Es. 0_8
        if file_counter[version_folder] < COUNTER_LIMIT[version_folder]:
            file_counter[version_folder] += 1
            # Creazione delle cartelle se non esistono
            os.makedirs(f"contracts/{version_folder}/sourcecode", exist_ok=True)
            os.makedirs(f"contracts/{version_folder}/bytecode", exist_ok=True)

            source_path = f"contracts/{version_folder}/sourcecode/{contract_address}.sol"
            bytecode_path = f"contracts/{version_folder}/bytecode/{contract_address}.hex"

            # Salva il source code solo se non esiste
            if not os.path.exists(source_path) and not os.path.exists(bytecode_path):
                with open(source_path, "w") as file:
                    file.write(source_code)
                with open(bytecode_path, "w") as file:
                    file.write(bytecode)
                # Salvataggio su logs.json
                logs_path = f"contracts/{version_folder}/logs.json"
                if os.path.exists(logs_path):
                    with open(logs_path, "r") as file:
                        logs = json.load(file)
                else:
                    logs = {}

                logs[contract_address] = {
                    "pragma": pragma_version,
                    "compiler version": compiler_version
                }

                with open(logs_path, "w") as file:
                    json.dump(logs, file, indent=4)

                print("✓ Saved:", contract_address)
            else:
                print(f"✗ Skipped: Source file already exists for {contract_address}")
        else:
            print(f"✗ Skipped: Counter limit reached for {version_folder}. Max: {COUNTER_LIMIT[version_folder]}")