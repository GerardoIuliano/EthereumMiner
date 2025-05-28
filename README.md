# 🧠 Ethereum Contract Miner

This tool mines Ethereum contracts starting from a given **start block** and going backwards down to an **end block**.  
It leverages **Etherscan API** and **Web3** to retrieve, decode, and save contract details deployed within the specified block range.

---

## Features

- Mines contract deployment transactions from a block range (start block → end block, going backwards).
- Retrieves contract metadata (source code, ABI, bytecode, ...) from Etherscan.
- Decodes constructor arguments automatically.
- Supports parallel execution using multiple threads for faster processing.
- Automatically skips proxy contracts and contracts importing external files or libraries.

---

## Metadata collected

- Source code
- Creation bytecode
- Runtime bytecode
- ABI
- Solidity pragma
- Compiler version
- Compiler type
- Compiler Optimization
- Constructor Arguments Bytecode
- Constructor Arguments Decoded

---

## Requirements

- Python 3.8 or higher
- An Etherscan API key (get it from [etherscan.io/apis](https://etherscan.io/apis))
- An Ethereum node provider URL (e.g., Infura)

Set your API in the config.py file

```bash
# config.py

ETHERSCAN_API_KEY = "your_etherscan_api_key"
ETHERSCAN_API_URL = "https://api.etherscan.io/api"
ETHERSCAN_RATE_LIMIT_DELAY = 0.1  # In secondi

INFURA_API_URL = "https://mainnet.infura.io/v3/"
INFURA_API_KEY = "your_infura_api_key"

COUNTER_LIMIT = {
    "0_4": your_treshold,
    "0_5": your_treshold,
    "0_6": your_treshold,
    "0_7": your_treshold,
    "0_8": your_treshold,
}

```
---

## Dependencies

```bash
pip install -r requirements.txt

```

---

## Usage

```bash
python main.py --start-block <start_block> --end-block <end_block> --threads <num_threads>
```
### Example with arguments
```bash
python main.py --start-block 22573318 --end-block 22573000 --threads 2
```
### Example without arguments
```bash
python main.py
```
By **default** the miner starts from the **last block** of the chain to the **first block** (0) using **0 thread**.

- It is recommended to use a maximum of **3 threads** due to API throughput limits to avoid rate limiting and ensure stable performance.

---

## Output
The tool saves validated contracts into folders organized by compiler version. 

#### Folder structure
```
📁 Version // e.g. 0_8
├── 📁 source_code
│   └── 📄contract_address_1.sol
│   └── 📄contract_address_2.sol
├── 📁 runtime_bytecode
│   └── 📄contract_address_1.hex
│   └── 📄contract_address_2.hex
├── 📁 creation_bytecode
│   └── 📄contract_address_1.hex
│   └── 📄contract_address_2.hex
├── 📄 logs.json
```
#### logs.json structure
```json
{
  "0x<contract_address>": {
    "pragma": "<solidity_version>",                // e.g. "0.8.23"
    "compiler version": "<full_compiler_version>", // e.g. "v0.8.23+commit.f704f362"
    "compiler type": "<compiler_name>",            // e.g. "solc"
    "optimization": "<0_or_1>",                    // "0" if disabled, "1" if enabled
    "abi": [
      {
        "internalType": "<solidity_type>",         // e.g. "uint256[]"
        "name": "<parameter_name>",                // e.g. "amounts"
        "type": "<abi_type>"                       // e.g. "uint256[]"
      },
      {
        "stateMutability": "<state>",              // e.g. "payable" or "nonpayable"
        "type": "<function_type>"                  // e.g. "receive", "fallback"
      }
      // ... additional ABI entries
    ],
    "constructor arguments": "<hex_encoded>",       // e.g. "0000000000..."
    "constructor arguments decoded": "<readable_values>" // e.g. "[100, 200]"
  }
}
```


