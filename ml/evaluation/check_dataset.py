from __future__ import annotations
import json
import sys
from collections import Counter
from pathlib import Path

REQUIRED = {'text', 'label', 'category', 'language'}
VALID = {'scam', 'suspicious', 'low_risk'}

def validate(path: str) -> None:
    rows = [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]
    if not rows: raise SystemExit('Dataset is empty.')
    for i, row in enumerate(rows):
        missing = REQUIRED - set(row)
        if missing: raise SystemExit(f'Row {i} missing: {sorted(missing)}')
        if row['label'] not in VALID: raise SystemExit(f'Row {i} has invalid label: {row["label"]}')
    print('rows=', len(rows), 'labels=', dict(Counter(r['label'] for r in rows)))

if __name__ == '__main__':
    validate(sys.argv[1] if len(sys.argv) > 1 else 'data/train.jsonl')
