import requests

async def get_block_data_by_slot(slot: int, rpc_url: str):
    """
    Fetch full block data for a given Solana slot using the getBlock RPC method.
    
    :param slot: The slot number to query.
    :param rpc_url: The Solana RPC endpoint URL (HTTPS).
    :return: JSON response from the RPC server.
    """
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBlock",
        "params": [
            slot,
            {
                "commitment": "finalized",
                "encoding": "json",
                "transactionDetails": "full",
                "maxSupportedTransactionVersion": 0,
                "rewards": True
            }
        ]
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(rpc_url, json=payload, headers=headers)

    # Raise error if something went wrong
    response.raise_for_status()
    
    return response.json()
