# scripts/extract_prompts.py
import re, csv, json
from pathlib import Path

# Matches triple-quoted prompt assignments to a variable or inline prompt = """
PROMPT_PATTERN = re.compile(
    r'^(?P<var>[A-Z_]+)\s*=\s*"""(?P<body>.+?)"""|prompt\s*=\s*"""(?P<body2>.+?)"""',
    re.DOTALL | re.MULTILINE
)

rows = []
for py in Path(".").rglob("*.py"):
    if ".venv" in py.parts: 
        continue
    if not any(p in py.parts for p in ("app", "watcher")):
        continue
    text = py.read_text(encoding="utf-8")
    for m in PROMPT_PATTERN.finditer(text):
        body = m.group("body") or m.group("body2")
        rows.append({
            "id":        f"{py.relative_to('.')}:L{m.start()}",
            "variable":  m.group("var") or "",
            "purpose":   "",  # ← fill this next
            "prompt_text": body.strip().replace("\n", "\\n")
        })

# Write CSV & JSON
with open("prompt_inventory.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id","variable","purpose","prompt_text"])
    writer.writeheader()
    writer.writerows(rows)

Path("prompt_inventory.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
