from pathlib import Path
import json

def write_txns_to_json(txns, filename="txns.json"):
    """
    Writes your list of transaction dictionaries to a JSON file
    inside a 'result' folder. The folder is created if missing.
    """
    # Create "result" directory if it doesn't exist
    result_dir = Path("result")
    result_dir.mkdir(exist_ok=True)

    # Full path: result/<filename>
    path = result_dir / filename

    with path.open("w", encoding="utf-8") as f:
        json.dump(txns, f, indent=2)

    return path
