import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\SolidworksMCP-TS")
names = set()
for f in p.rglob("*"):
    if not f.is_file() or f.suffix not in (".ts",): continue
    if any(x in str(f) for x in ("node_modules",".git","test","dist")): continue
    try: t = f.read_text(encoding="utf-8", errors="ignore")
    except Exception: continue
    names |= set(re.findall(r'\{\s*name:\s*[\'"]([a-z][a-z0-9_]{3,})[\'"]', t))
s = sorted(names)
print("  共 %d 个" % len(s))
for i, n in enumerate(s, 1):
    print("   %3d. %s" % (i, n))