import json
import os

def filter_mev_with_wide_sandwich_attack(input_filepath: str):
    """
    Filters MEV attacks based on rules:
    1) attackSlots[2] == attackSlots[0] + 2
    2) Adds profit, ROI, price impact calculations

    Saves: result/desiredoutput.json
    """

    # Load input file
    with open(input_filepath, "r") as f:
        data = json.load(f)

    mev_attacks = data.get("mev_attacks", [])

    filtered = []

    for attack in mev_attacks:
        slots = attack.get("attackSlots", [])

        # ---- Rule 1: slot spacing ----
        if len(slots) == 3 and slots[2] == slots[0] + 2:

            # ---------------------------------------------------
            # Extract frontrun / backrun data
            # ---------------------------------------------------
            fr = attack.get("frontRun", {})
            br = attack.get("backRun", {})

            fr_from_amt = fr.get("fromAmount", 0.0)
            fr_to_amt   = fr.get("toAmount", 0.0)

            br_from_amt = br.get("fromAmount", 0.0)
            br_to_amt   = br.get("toAmount", 0.0)

            # ---------------------------------------------------
            # Calculate bot profit (in SOL)
            # profit = backRun.toAmount - frontRun.fromAmount
            # ---------------------------------------------------
            bot_profit = br_to_amt - fr_from_amt

            # ---------------------------------------------------
            # ROI: backrun.sol_out / frontrun.sol_in
            # ---------------------------------------------------
            roi = None
            if fr_from_amt > 0:
                roi = br_to_amt / fr_from_amt

            # ---------------------------------------------------
            # Price impact
            # front_price = SOL_in / TOKEN_out
            # back_price  = SOL_out / TOKEN_in
            # ---------------------------------------------------
            front_price = None
            back_price = None
            price_impact = None

            if fr_to_amt > 0:
                front_price = fr_from_amt / fr_to_amt

            if br_from_amt > 0:
                back_price = br_to_amt / br_from_amt

            if front_price and back_price:
                price_impact = ((back_price - front_price) / front_price) * 100

            # ---------------------------------------------------
            # Add computed metrics into attack block
            # ---------------------------------------------------
            attack["analysis"] = {
                "botProfit_SOL": bot_profit,
                "ROI": roi,
                "frontPrice": front_price,
                "backPrice": back_price,
                "priceImpactPercent": price_impact
            }

            filtered.append(attack)

    # Final output structure
    output = {
        "total_mev_attacks": len(filtered),
        "mev_attacks": filtered
    }

    # Ensure result folder exists
    os.makedirs("result", exist_ok=True)

    # Save output
    output_path = "result/desiredoutput.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nFiltered & analyzed MEV attacks saved to: {output_path}")
    print(f"Total matched attacks: {len(filtered)}")
    return output_path
