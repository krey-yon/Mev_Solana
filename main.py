import asyncio

from solana.rpc.async_api import AsyncClient

from utils.detector_mev_pattern import analyze_mev_file
from utils.extract_transction_data import extract_program_transactions
from utils.check_wide_sandwich_attack import filter_mev_with_wide_sandwich_attack
from utils.get_block_data import get_block_data_by_slot
from utils.txns_to_json import write_txns_to_json
from constant import program_id, rpc_url
from simulation import Simulation

async def main():
    client = AsyncClient(rpc_url)
    
    latestBlock = await client.get_slot()
    startBlock = latestBlock.value - 10000
    blockToScan = 1000
    print(f"we are scaning {blockToScan} blocks so it will probably take a while")

    # Fetch n consecutive blocks
    grouped_data = []
    for i in range(blockToScan):
        slot = startBlock + i
        block_data = await get_block_data_by_slot(slot, rpc_url)
        transactions = extract_program_transactions(block_data, program_id)
        
        # Group by slot
        grouped_data.append({
            "slot": slot,
            "data": transactions
        })
    
    print(f"Grouped data for {len(grouped_data)} slots")
    write_txns_to_json(grouped_data, "allTxnsInBlock.json")
    analyze_mev_file("result/allTxnsInBlock.json", "txnsWithMevPattern.json")
    filter_mev_with_wide_sandwich_attack("result/txnsWithMevPattern.json")


    # simulation
    simulation = Simulation(block=startBlock)
    victim = await simulation.find_victim()
    attack = await simulation.attack_victim(victimTxn=victim)
    write_txns_to_json(attack, "simulation.json")

if __name__ == "__main__":
    asyncio.run(main())