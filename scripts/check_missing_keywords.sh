#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

python3 - << 'PY'
import glob, re, sys

defined = set()
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
                defined.add(s)

# Also include BDD prefixes
bdd_prefixes = ["Given ", "When ", "Then ", "And ", "But "]

multi = sorted(defined, key=len, reverse=True)

missing = []
for path in glob.glob("tests/*.robot"):
    with open(path, encoding="utf-8") as fp:
        for lineno, line in enumerate(fp, 1):
            s = line.rstrip()
            if not re.match(r'^ {4}[A-Z]', s):
                continue
            body = s.strip()
            if body.startswith("#") or body.startswith("["):
                continue
            for pfx in bdd_prefixes:
                if body.startswith(pfx):
                    body = body[len(pfx):].strip()
                    break

            matched = False
            for kw in multi:
                if body == kw or body.startswith(kw + "    ") or body.startswith(kw + "  "):
                    matched = True
                    break
            if not matched:
                missing.append((path, lineno, body[:60]))

if missing:
    print("==> Keyword dipanggil tapi tidak terdefinisi:")
    for p, ln, txt in missing:
        print(f"  {p}:{ln}: {txt}")
    sys.exit(1)
else:
    print("==> OK (Semua keyword ter-resolve)")
PY
