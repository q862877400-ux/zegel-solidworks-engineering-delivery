import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
cand = [p for p in Path(r"D:\AI\SW\_raw").rglob("enum_*.txt")]
for p in cand:
    txt = p.read_text(encoding="utf-8", errors="replace")
    if "sldworks" not in p.name.lower() and "sldworks" not in str(p.parent).lower():
        continue
    names = re.findall(r"^## (\w+)", txt, re.M)
    print("  %s : %d 个枚举" % (p.name, len(names)))
    hit = [n for n in names if "UserPreference" in n]
    print("    swUserPreference*:", ", ".join(hit[:10]) if hit else "(无)")
    sw = [n for n in names if n.startswith("swSel") or "SelectionFilter" in n or n=="swSelectType_e"]
    print("    选择相关:", ", ".join(sw[:8]))
