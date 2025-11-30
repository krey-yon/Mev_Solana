from constant import program_id, rpc_url
from simulation_types import VictimTxn
from utils.extract_transction_data import extract_program_transactions
from utils.get_block_data import get_block_data_by_slot


class Simulation:
    def __init__(self, block) -> None:
        self.block = block

    async def find_victim(self):
        allTxnsInBlock = await get_block_data_by_slot(self.block, rpc_url=rpc_url)
        programTxns = extract_program_transactions(allTxnsInBlock, program_ids= program_id)
        raw = programTxns[0]
        victim: VictimTxn = {
            "signature": raw["signature"],
                "programId": raw["programId"],
                "signer": raw["signer"],
                "swapInfo": {
                    "from_": raw["swapInfo"]["from"],
                    "to": raw["swapInfo"]["to"],
                    "fromAmount": raw["swapInfo"]["fromAmount"],
                    "toAmount": raw["swapInfo"]["toAmount"],
                }
        }
        return victim

    async def attack_victim(self, victimTxn: VictimTxn):
        botPubkey = "B4XHtegFy3xhVyj4KUkqt3b8bT6uVrK9VAHZEhFbfMwW"

        v_from = victimTxn["swapInfo"]["from_"]
        v_to = victimTxn["swapInfo"]["to"]
        v_from_amount = victimTxn["swapInfo"]["fromAmount"]
        v_to_amount = victimTxn["swapInfo"]["toAmount"]

        front_run = {
            "slot": self.block - 1,
            "signature": "FAKE_FRONT_SIGNATURE",
            "signer": botPubkey,
            "from": v_from,
            "to": v_to,
            "fromAmount": 0.25 * v_from_amount,
            "toAmount": 0.25 * v_to_amount,
        }

        victim_json = {
            "slot": self.block,
            "signature": victimTxn["signature"],
            "signer": victimTxn["signer"],
            "from": v_from,
            "to": v_to,
            "fromAmount": v_from_amount,
            "toAmount": v_to_amount,
        }

        back_run = {
            "slot": self.block + 1,
            "signature": "FAKE_BACK_SIGNATURE",
            "signer": botPubkey,
            "from": v_to,
            "to": v_from,
            "fromAmount": 0.5 * v_to_amount,
            "toAmount": 0.5 * v_from_amount,
        }

        analysis = {
            "botProfit_SOL": 123.45,
            "ROI": 2.71,
            "frontPrice": 100.0,
            "backPrice": 98.0,
            "priceImpactPercent": -2.0,
        }

        json_output = {
            "attackSlots": [self.block - 1, self.block, self.block + 1],
            "frontRun": front_run,
            "victim": victim_json,
            "backRun": back_run,
            "analysis": analysis,
        }

        return json_output
