import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
for p in Path(r"D:\AI\SW\_raw").rglob("*enum*.txt"):
    txt = p.read_text(encoding="utf-8", errors="replace")
    hits = sorted(set(re.findall(r"^## (swUserPreference\w*)", txt, re.M)))
    if hits:
        print(" ", p.name, "->", ", ".join(hits[:8]))
