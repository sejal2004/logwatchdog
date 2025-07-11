# scripts/validate_prompts.py
import json
import glob
import sys
from jsonschema import validate, ValidationError

SCHEMA_DIR = "schemas"
PROMPT_DEFS = "prompt_inventory.json"  # or wherever you store your prompt definitions

def main():
    failed = False

    # Load your prompt definitions
    with open(PROMPT_DEFS, encoding="utf-8") as f:
        prompts = json.load(f)

    for p in prompts:
        purpose = p["purpose"]
        # Skip untagged prompts
        if not purpose:
            print(f"[WARN] Skipping untagged prompt {p['id']}")
            continue

        schema_path = f"{SCHEMA_DIR}/{purpose}.schema.json"
        try:
            schema = json.load(open(schema_path, encoding="utf-8"))
        except FileNotFoundError:
            print(f"[✗] No schema found for purpose '{purpose}' ({p['id']})")
            failed = True
            continue

        try:
            validate(instance=p, schema=schema)
        except ValidationError as e:
            print(f"[✗] {p['id']}: {e.message}")
            failed = True
        else:
            print(f"[✓] {p['id']}")

    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
