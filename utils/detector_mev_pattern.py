import json
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict


def detect_sandwich_mev(blocks: List[Dict[str, Any]]):
    """
    Detect real sandwich MEV:
    - front-run (A -> B) by attacker
    - victim trades in the middle (any swap)
    - back-run (B -> A) by same attacker

    Returns:
    {
      "total_mev_attacks": N,
      "mev_attacks": [
         {
            "attackSlots": [...],
            "frontRun": txn1,
            "victim": txn2,
            "backRun": txn3
         },
         ...
      ]
    }
    """

    # Flatten all txns sorted by slot
    all_txns = []
    for block in blocks:
        slot = block["slot"]
        for tx in block["data"]:
            s = tx["swapInfo"]
            all_txns.append({
                "slot": slot,
                "signature": tx["signature"],
                "signer": tx["signer"],
                "from": s.get("from"),
                "to": s.get("to"),
                "fromAmount": s.get("fromAmount", 0),
                "toAmount": s.get("toAmount", 0)
            })

    all_txns.sort(key=lambda x: x["slot"])

    mev_attacks = []

    # Index by slot to locate victims between attacks
    slot_groups = defaultdict(list)
    for t in all_txns:
        slot_groups[t["slot"]].append(t)
    sorted_slots = sorted(slot_groups.keys())

    # -----------------------------------------------------
    # Scan attacker round-trips for front/back run
    # -----------------------------------------------------
    # Build signer groups
    signer_groups = defaultdict(list)
    for t in all_txns:
        signer_groups[t["signer"]].append(t)

    for attacker, txs in signer_groups.items():
        if len(txs) < 2:
            continue

        txs = sorted(txs, key=lambda x: x["slot"])

        # Check every front-run / back-run pair
        for i in range(len(txs)):
            A = txs[i]  # frontrun
            for j in range(i+1, len(txs)):
                B = txs[j]  # backrun

                # Must be reverse token swap
                if not A["from"] or not A["to"] or not B["from"] or not B["to"]:
                    continue

                if not (A["from"] == B["to"] and A["to"] == B["from"]):
                    continue  # not a round-trip

                # -----------------------------------------
                # Now find victim(s) between their slots
                # -----------------------------------------
                victims = []

                for slot in sorted_slots:
                    if A["slot"] < slot < B["slot"]:
                        for tx in slot_groups[slot]:
                            if tx["signer"] != attacker:
                                victims.append(tx)

                if victims:
                    # For now take first victim only (can extend later)
                    victim = victims[0]

                    mev_attacks.append({
                        "attackSlots": [A["slot"], victim["slot"], B["slot"]],
                        "frontRun": A,
                        "victim": victim,
                        "backRun": B
                    })

    result = {
        "total_mev_attacks": len(mev_attacks),
        "mev_attacks": mev_attacks
    }

    return result


def analyze_mev_file(input_path: str, output_filename: str):
    """
    Load input JSON, run MEV detection, and save output inside 'result' folder.
    The result folder is created automatically if missing.
    """
    # Read input
    with open(input_path, "r") as f:
        blocks = json.load(f)

    result = detect_sandwich_mev(blocks)

    # Ensure result folder exists
    result_dir = Path("result")
    result_dir.mkdir(exist_ok=True)

    # Build full output path
    output_path = result_dir / output_filename

    # Write output file
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print("MEV detection complete!")
    print("Saved to:", output_path)
    print("Total attacks found:", result["total_mev_attacks"])

    return result
