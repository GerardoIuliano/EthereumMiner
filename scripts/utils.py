import re

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
    bytecode: str,      # Bytecode del contratto
    contract_address: str   # Indirizzo del contratto 
):
    """
    Controlla se il contratto è valido in base a criteri specifici.
    :param source_code: Codice sorgente del contratto
    :param bytecode: Bytecode del contratto
    :return: None
    """
    # Controlla che source code e bytecode non siano nulli o vuoti
    if source_code and bytecode:
        return True
    else:
        if source_code is None or source_code == "":
            print(f"✗ Skipped {contract_address}: source code missing. Source code: {source_code}")
        if bytecode is None or bytecode == "":    
            print(f"✗ Skipped {contract_address}: bytecode missing. Bytecode: {bytecode}")
        return False
    
def is_candidate(
    contract_address: str,  # Indirizzo del contratto
    source_code: str,   # Codice sorgente del contratto
    bytecode: str,      # Bytecode del contratto
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
    if check_source_and_byte(source_code, bytecode, contract_address):
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