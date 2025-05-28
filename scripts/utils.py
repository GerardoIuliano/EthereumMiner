import re, json
from eth_abi import decode
from scripts.client_web3 import Web3Client
from eth_utils import remove_0x_prefix

def get_pragma_from_code(source_code: str) -> str:
    """
    Estrae la versione del compilatore dal codice sorgente.
    :param
    source_code: Codice sorgente del contratto
    :return: Versione del compilatore
    """
    # Trova la dichiarazione pragma
    match = re.search(r"pragma\s+solidity\s+([^\s;]+)", source_code)
    if match:
        # Estrai la versione del compilatore
        version = match.group(1).strip()
        # Rimuovi eventuali caratteri non necessari
        version = re.sub(r"[^0-9a-zA-Z.+-]", "", version)
        return version
    return None

def get_compiler_version(compiler_version: str) -> str: 
    """
    Estrae la versione del compilatore escludendo il commit hash.
    :param compiler_version: Versione del compilatore
    :return: Versione del compilatore senza commit hash
    """
    # Esempio: "v0.8.17+commit.8df45f5f" → "0.8.17"
    match = re.match(r"v?(\d+\.\d+\.\d+)", compiler_version)
    if match:
        return match.group(1)
    return None

def isAbiAvailable(abi: str, contract_address) -> bool:
    """
    Controlla se l'ABI è disponibile.
    :param abi: ABI del contratto
    :return: True se l'ABI è disponibile, False altrimenti
    """
    if abi is None or abi == "":
        print(f"✗ Skipped {contract_address}: ABI not available. ABI: {abi}")
        return False
    else: 
        return True
    
def is_same_version(source_code: str, compiler_version: str, contract_address) -> str:
    """
    Controlla se la versione del compilatore corrisponde a quella del codice sorgente.
    :param source_code: Codice sorgente del contratto
    :param compiler_version: Versione del compilatore
    :return: True se le versioni corrispondono, False altrimenti
    """
    pragma_version = get_pragma_from_code(source_code)
    compiler_version = get_compiler_version(compiler_version)   
    # Esempio: "0.8" == "0.8, match della major version"
    match_pragma = re.match(r'^(\d+\.\d+)', pragma_version)  
    match_compiler = re.match(r'^(\d+\.\d+)', compiler_version)
    if match_pragma and match_compiler:
        pragma_major_minor = match_pragma.group(1)
        compiler_major_minor = match_compiler.group(1)

        if pragma_major_minor == compiler_major_minor:
            return True
        else:
            print(f"✗ Skipped {contract_address}: pragma version and compiler version do not match. Pragma: {pragma_major_minor}, Compiler: {compiler_major_minor}")
            return False
        

def isLibraryEmpty(library: str, contract_address) -> bool:
    """
    Controlla se la libreria è vuota.
    :param library: Versione della libreria
    :return: True se la libreria è vuota, False altrimenti
    """
    if library is None or library == "":
        return True
    else:
        print(f"✗ Skipped {contract_address}: library not empty. Library: {library}")
        return False
    
def check_source_and_byte(
    source_code: str,   # Codice sorgente del contratto
    runtime_bytecode: str,      # Bytecode del contratto
    creation_bytecode: str,  # Bytecode di creazione del contratto
    contract_address: str   # Indirizzo del contratto 
):
    """
    Controlla se il contratto è valido in base a criteri specifici.
    :param source_code: Codice sorgente del contratto
    :param bytecode: Bytecode del contratto
    :return: None
    """
    # Controlla che source code e bytecode non siano nulli o vuoti
    if source_code and runtime_bytecode:
        return True
    else:
        if source_code is None or source_code == "":
            print(f"✗ Skipped {contract_address}: source code missing. Source code: {source_code}")
        if runtime_bytecode is None or runtime_bytecode == "":    
            print(f"✗ Skipped {contract_address}: runtime bytecode missing. Runtime bytecode: {runtime_bytecode}")
        if creation_bytecode is None or creation_bytecode == "":
            print(f"✗ Skipped {contract_address}: creation bytecode missing. Creation bytecode: {creation_bytecode}")
        return False

def decode_constructor_args(abi, constructor_arguments_hex):
    """
    Decodifica i constructor arguments dati ABI e dati esadecimali.

    :param abi: la lista ABI completa (come JSON/dict)
    :param constructor_arguments_hex: stringa esadecimale dei parametri del costruttore (es. da bytecode)
    :return: dizionario {nome_parametro: valore_decodificato}
    """
    if constructor_arguments_hex is None or constructor_arguments_hex == '':
        return ""
    if isinstance(abi, str):
        abi = json.loads(abi)

    constructor = next((item for item in abi if item.get("type") == "constructor"), None)
    if constructor is None:
        raise ValueError("ABI does not contain a constructor")

    input_types = []

    def parse_type(input_item):
        if input_item["type"] == "tuple":
            component_types = [parse_type(c) for c in input_item["components"]]
            return f"({','.join(component_types)})"
        elif input_item["type"].startswith("tuple["):
            dimensions = input_item["type"][5:]  # es: "[3]" o "[]"
            component_types = [parse_type(c) for c in input_item["components"]]
            return f"({','.join(component_types)}){dimensions}"
        else:
            return input_item["type"]

    for item in constructor["inputs"]:
        input_types.append(parse_type(item))
    if constructor_arguments_hex.startswith("0x"):
        constructor_args_bytes = bytes.fromhex(remove_0x_prefix(constructor_arguments_hex))
    else:
        constructor_args_bytes = constructor_arguments_hex
    decoded_values = decode(input_types, constructor_args_bytes)

    # Associa ogni valore al nome
    named_values = {}
    for item, value in zip(constructor["inputs"], decoded_values):
        if item["type"].startswith("tuple"):
            # Se è una tupla, associare anche i nomi interni
            component_names = [c["name"] for c in item["components"]]
            named_values[item["name"]] = dict(zip(component_names, value))
        else:
            named_values[item["name"]] = value

    return named_values

def is_candidate(
    contract_address: str,  # Indirizzo del contratto
    source_code: str,   # Codice sorgente del contratto
    runtime_bytecode: str,      # Runtime_bytecode del contratto
    creation_bytecode: str,  # Creation_bytecode di creazione del contratto
    compiler_version: str,  # Versione del compilatore
    library: str    # Librerie
):
    """
    Controlla se il contratto è valido in base a criteri specifici.
    :param source_code: Codice sorgente del contratto
    :param bytecode: Bytecode del contratto
    :param compiler_version: Versione del compilatore
    :param library: Librerie
    :return: None
    """
    if check_source_and_byte(source_code, runtime_bytecode, creation_bytecode, contract_address):
        if is_same_version(source_code, compiler_version, contract_address):
            if isLibraryEmpty(library, contract_address):
                # Se tutte le condizioni sono soddisfatte, il contratto è valido
                return True
            else:
                return False
        else:
            return False
    else:
        return False
    
def skipVersion(skip_version, source_code):
    pragma_version = get_pragma_from_code(source_code)
    version = pragma_version.replace(".", "_")
    # From 0_8_30 to 0_8
    version_folder = "_".join(version.split("_")[:2])  # Es. 0_8
    if skip_version == version_folder:
        return True
    else:
        return False