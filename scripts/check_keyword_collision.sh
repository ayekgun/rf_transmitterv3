#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

python3 - << 'PY'
import glob, re, sys

py_kws = set()
for f in glob.glob("libraries/*.py"):
    with open(f, encoding="utf-8") as fp:
        for line in fp:
            m = re.search(r'@keyword\("([^"]+)"\)', line)
            if m:
                py_kws.add(m.group(1))

rf_kws = set()
for f in glob.glob("resources/keywords/*.robot"):
    with open(f, encoding="utf-8") as fp:
        in_kw = False
        for line in fp:
            s = line.strip()
            if s.startswith("*** Keywords ***"):
                in_kw = True
                continue
            elif s.startswith("***"):
                in_kw = False
                continue
            if in_kw and s and not line.startswith(" ") and not line.startswith("\t") and not s.startswith("[") and not s.startswith("#") and not s.startswith("***"):
                rf_kws.add(s)

collisions = py_kws.intersection(rf_kws)
print("==> Collision check (recursion risk):")
if collisions:
    for c in sorted(collisions):
        print(f"  ⚠  {c}")
    sys.exit(1)
else:
    print("==> OK (No collision)")
PY
