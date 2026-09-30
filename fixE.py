import sys
from pathlib import Path
p = Path(r"D:\AI\SW\_miss2.py")
s = p.read_text(encoding="utf-8")
s = s.replace('if not f or row.get("pct", 100) >= 100: continue',
              'pct = row.get("pct")\n    if not f or pct is None or pct >= 100: continue')
p.write_text(s, encoding="utf-8")
print("fixed")