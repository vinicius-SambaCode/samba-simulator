# backend/tools/pyd_v2_scan.py
from __future__ import annotations
import sys
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]  # .../backend
INCLUDE_DIRS = ["app"]  # ajuste se houver mais pastas
PATTERN = re.compile(r"^\s*class\s+Config\s*:\s*$", re.MULTILINE)

def main() -> int:
    total = 0
    files = []
    for base in INCLUDE_DIRS:
        for py in (ROOT / base).rglob("*.py"):
            try:
                text = py.read_text(encoding="utf-8")
            except Exception:
                continue
            if PATTERN.search(text):
                files.append(py)
                total += 1
    if files:
        print("Encontradas ocorrências de 'class Config:' nestes arquivos:\n")
        for f in files:
            print("-", f.relative_to(ROOT))
        print(f"\nTotal: {total}")
        return 1
    else:
        print("Nenhuma ocorrência de 'class Config:' encontrada. ✅")
        return 0

if __name__ == "__main__":
    sys.exit(main())
