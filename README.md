# Solana MEV Sandwich Attack Detector

A Python tool for detecting and analyzing MEV (Maximal Extractable Value) sandwich attacks on Solana DEXs. This project scans Solana blocks, identifies potential sandwich attacks, and provides detailed profit analysis.

## Overview

This tool identifies sandwich attacks by:
1. Fetching recent Solana blocks via RPC
2. Extracting swap transactions from major DEX programs
3. Detecting sandwich patterns (front-run → victim → back-run)
4. Filtering attacks based on slot spacing criteria
5. Computing profit, ROI, and price impact metrics

## Features

- ✅ Multi-DEX support (Raydium, Orca, Meteora, etc.)
- ✅ Real-time block scanning
- ✅ Sandwich attack pattern detection
- ✅ Wide sandwich attack filtering (slot spacing analysis)
- ✅ Profit and ROI calculations
- ✅ Price impact analysis
- ✅ JSON output for further analysis

## Prerequisites

- Python 3.11 or higher
- Solana RPC endpoint (mainnet-beta)
- UV package manager (recommended) or pip

## Installation

### Using UV (Recommended)

```bash
# Clone the repository
git clone https://github.com/krey-yon/Mev_Solana
cd Mev_Solana

# Install dependencies
uv sync
```

### Using Pip

```bash
# Clone the repository
git clone https://github.com/krey-yon/Mev_Solana
cd Mev_Solana

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install solana solders requests base58
```

## Configuration

Before running the tool, you need to configure your RPC endpoint:

1. Open `constant.py`
2. Replace `"your_rpc_url_here"` with your Solana RPC URL:

```python
rpc_url = "https://your-rpc-endpoint.com"
```

### Supported DEX Programs

The tool monitors these DEX programs (configured in `constant.py`):
- **Raydium V4**: `675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8`
- **Raydium CLMM**: `6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P`
- **Raydium CPMM**: `cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG`
- **Orca Whirlpool**: `whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc`
- **Meteora**: `pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA`
- **Raydium CAMM**: `CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK`

## Usage

Run the main script:

```bash
# With UV
uv run python main.py

# With standard Python
python main.py
```

### What Happens

1. **Block Fetching**: Scans n consecutive blocks starting 10,000 slots before the latest block
2. **Transaction Extraction**: Filters swap transactions from monitored DEX programs
3. **MEV Detection**: Identifies sandwich attack patterns
4. **Analysis**: Filters and analyzes wide sandwich attacks (2-slot spacing)

### Output Files

All output files are saved in the `result/` directory:

#### 1. `allTxnsInBlock.json`
Raw swap transactions grouped by slot.

```json
[
  {
    "slot": 123456789,
    "data": [
      {
        "signature": "...",
        "programId": "...",
        "signer": "...",
        "swapInfo": {
          "from": "token_mint_1",
          "to": "token_mint_2",
          "fromAmount": 1.5,
          "toAmount": 1500.0
        }
      }
    ]
  }
]
```

#### 2. `txnsWithMevPattern.json`
Detected sandwich attacks with front-run, victim, and back-run transactions.

```json
{
  "total_mev_attacks": 26,
  "mev_attacks": [
    {
      "attackSlots": [123456789, 123456790, 123456791],
      "frontRun": { /* transaction details */ },
      "victim": { /* transaction details */ },
      "backRun": { /* transaction details */ }
    }
  ]
}
```

#### 3. `desiredoutput.json`
Filtered and analyzed attacks with profit metrics.

```json
{
  "total_mev_attacks": 10,
  "mev_attacks": [
    {
      "attackSlots": [123456789, 123456790, 123456791],
      "frontRun": { /* ... */ },
      "victim": { /* ... */ },
      "backRun": { /* ... */ },
      "analysis": {
        "botProfit_SOL": 0.05,
        "ROI": 1.025,
        "frontPrice": 0.001,
        "backPrice": 0.00102,
        "priceImpactPercent": 2.0
      }
    }
  ]
}
```

## How It Works

### 1. Sandwich Attack Detection

The tool identifies attacks where:
- **Front-run**: Bot swaps Token A → Token B
- **Victim**: User trades (any pair)
- **Back-run**: Same bot swaps Token B → Token A

### 2. Wide Sandwich Filtering

Filters attacks where `attackSlots[2] == attackSlots[0] + 2` (exactly 2-slot spacing).

### 3. Profit Analysis

For each attack, calculates:

- **Bot Profit (SOL)**: `backRun.toAmount - frontRun.fromAmount`
- **ROI**: `backRun.toAmount / frontRun.fromAmount`
- **Front Price**: `frontRun.fromAmount / frontRun.toAmount`
- **Back Price**: `backRun.toAmount / backRun.fromAmount`
- **Price Impact %**: `((backPrice - frontPrice) / frontPrice) * 100`

## Project Structure

```
mev_1/
├── main.py                          # Entry point
├── constant.py                      # Configuration (RPC URL, program IDs)
├── utils/
│   ├── get_block_data.py           # Fetch block data via RPC
│   ├── extract_transction_data.py  # Parse swap transactions
│   ├── txns_to_json.py             # JSON file writer
│   ├── detector_mev_pattern.py     # Sandwich attack detection logic
│   └── check_wide_sandwich_attack.py # Filter & analyze attacks
├── result/                          # Output directory
├── pyproject.toml                   # Dependencies
└── README.md
```

## Dependencies

- `solana>=0.36.9` - Solana Python SDK
- `solders>=0.26.0` - Solana types and utilities
- `requests>=2.32.5` - HTTP library for RPC calls
- `base58>=2.1.1` - Base58 encoding

## Customization

### Adjust Block Range

Edit `main.py` to change the number of blocks scanned:

```python
# Scan 1000 blocks instead of 100
for i in range(1000):
    slot = startBlock + i
    # ...
```

### Change Slot Offset

```python
# Scan more recent blocks (5000 slots back instead of 10000)
startBlock = latestBlock.value - 5000
```

### Modify Attack Criteria

Edit `check_wide_sandwich_attack.py` to change filtering rules:

```python
# Allow 3-slot spacing instead of 2
if len(slots) == 3 and slots[2] == slots[0] + 3:
    # ...
```

## Troubleshooting

### `FileNotFoundError: txnsWithMevPattern.json`
- Ensure the file path includes the `result/` prefix
- Check that previous steps completed successfully

### RPC Rate Limiting
- Use a premium RPC endpoint (Helius, QuickNode, Alchemy)
- Add rate limiting/delays between requests
- Reduce the number of blocks scanned

### No MEV Attacks Found
- Try scanning different block ranges
- MEV activity varies based on market conditions
- Check that program IDs are correct and active

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - feel free to use this project for research and educational purposes.

## Disclaimer

This tool is for educational and research purposes only. MEV extraction may be subject to legal and ethical considerations. Use responsibly.