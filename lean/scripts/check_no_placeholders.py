#!/usr/bin/env python3
"""Reject Lean proof placeholders and declaration-level axioms."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BAD = {
    "sorry": re.compile(r"\bsorry\b"),
    "admit": re.compile(r"\badmit\b"),
    "axiom": re.compile(r"^\s*axiom\b", re.MULTILINE),
    "unsafe declaration": re.compile(r"^\s*unsafe\s+(?:def|theorem)\b", re.MULTILINE),
}
problems = []
EXCLUDED_DIRS = {".lake", "lake-packages", ".github"}
for path in sorted(ROOT.rglob("*.lean")):
    if EXCLUDED_DIRS & {part for part in path.relative_to(ROOT).parts}:
        continue
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/-.*?-/", "", text, flags=re.DOTALL)
    text = re.sub(r"--.*", "", text)
    for label, pattern in BAD.items():
        if pattern.search(text):
            problems.append(f"{path.relative_to(ROOT)}: contains {label}")
if problems:
    print("PLACEHOLDER CHECK FAILED")
    print("\n".join(problems))
    sys.exit(1)
print("PLACEHOLDER CHECK PASSED: no sorry/admit/axiom/unsafe theorem declarations")
