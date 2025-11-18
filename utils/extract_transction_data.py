import json

def extract_program_transactions(block_json: dict, program_ids: list[str]):
    """
    Extract only *proper swap* transactions:
      - signer MUST send a token
      - signer MUST receive a token
    Returns clean swap structured data.
    """

    results = []
    program_ids = [str(pid) for pid in program_ids]

    # block format check
    if "result" not in block_json or "transactions" not in block_json["result"]:
        return results

    tx_list = block_json["result"]["transactions"]

    for tx in tx_list:
        msg = tx["transaction"]["message"]
        meta = tx["meta"]
        account_keys = msg["accountKeys"]
        instructions = msg["instructions"]

        # -------------------------------
        # 1️⃣ check program usage
        # -------------------------------
        used_program = None
        for ix in instructions:
            pidx = ix["programIdIndex"]
            if pidx < len(account_keys):
                if account_keys[pidx] in program_ids:
                    used_program = account_keys[pidx]
                    break
        if not used_program:
            continue

        # -------------------------------
        # 2️⃣ signer detection
        # -------------------------------
        signer = account_keys[0]

        # -------------------------------
        # 3️⃣ token delta extraction
        # -------------------------------
        pre_tokens = { (b["accountIndex"], b["mint"]): b for b in meta.get("preTokenBalances", []) }
        post_tokens = { (b["accountIndex"], b["mint"]): b for b in meta.get("postTokenBalances", []) }

        user_changes = []

        for key, pre in pre_tokens.items():
            if key not in post_tokens:
                continue

            post = post_tokens[key]

            pre_amt = int(pre["uiTokenAmount"]["amount"])
            post_amt = int(post["uiTokenAmount"]["amount"])
            decimals = pre["uiTokenAmount"]["decimals"]
            delta = post_amt - pre_amt

            if delta != 0:
                # track ONLY user-owned SPL token accounts
                if pre["owner"] == signer:
                    user_changes.append({
                        "mint": key[1],
                        "delta": delta,
                        "decimals": decimals
                    })

        # -------------------------------
        # 4️⃣ identify real swap in/out
        # -------------------------------
        token_in_mint = None
        token_out_mint = None
        token_in_amount = 0
        token_out_amount = 0

        for c in user_changes:
            if c["delta"] < 0:
                token_in_mint = c["mint"]
                token_in_amount = abs(c["delta"]) / (10 ** c["decimals"])
            elif c["delta"] > 0:
                token_out_mint = c["mint"]
                token_out_amount = c["delta"] / (10 ** c["decimals"])

        # -------------------------------
        # 5️⃣ validation — only proper swaps
        # -------------------------------
        if not token_in_mint or not token_out_mint:
            # skip junk, ATA creation, SOL-only, fee payer only, etc.
            continue

        # -------------------------------
        # 6️⃣ add final result
        # -------------------------------
        results.append({
            "signature": tx["transaction"]["signatures"][0],
            "programId": used_program,
            "signer": signer,
            "swapInfo": {
                "from": token_in_mint,
                "to": token_out_mint,
                "fromAmount": token_in_amount,
                "toAmount": token_out_amount
            }
        })

    return results
