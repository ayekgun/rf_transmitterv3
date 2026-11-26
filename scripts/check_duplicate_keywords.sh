#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

python3 - << 'PY'
import glob, re, sys

seen = {}
dupes = 0

for f in glob.glob("resources/keywords/*.robot"):
    with open(f, encoding="utf-8") as fp:
        in_kw = False
        for lineno, line in enumerate(fp, 1):
            s = line.strip()
            if s.startswith("*** Keywords ***"):
                in_kw = True
                continue
            elif s.startswith("***"):
                in_kw = False
                continue
            if in_kw and s and not line.startswith(" ") and not line.startswith("\t") and not s.startswith("[") and not s.startswith("#") and not s.startswith("***"):
                kw = s
                if kw in seen:
                    print(f"  ⚠  '{kw}' di: {seen[kw]} + {f}:{lineno}")
                    dupes += 1
                else:
                    seen[kw] = f"{f}:{lineno}"

if dupes > 0:
    print(f"==> FAIL: Ditemukan {dupes} duplikat keyword.")
    sys.exit(1)
else:
    print("==> OK (No duplicate keywords across robot files)")
PY
