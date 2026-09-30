import re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
S = Path(r"C:\swprojects\sw-skill-fork\scripts")
for p in sorted(S.glob("sw_api_*.py")):
    m = re.search(r"ASSEMBLY = '(\w+)'", p.read_text(encoding="utf-8"))
    asm = m.group(1) if m else "?"
    hits = list(Path(r"D:\AI\SW\_raw").rglob("iface_%s.txt" % asm))
    if len(hits) != 1:
        print("  ⚠ %-30s asm=%-22s 命中 %d 个: %s" % (p.name, asm, len(hits), [h.parent.name for h in hits]))
print("  (只列出命中数不等于 1 的)")