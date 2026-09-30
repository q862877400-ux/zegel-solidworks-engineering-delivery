import sys, io, re
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sw = Path(r"C:\swapi")
# 找 swUserPreference* 枚举的 markdown
hits = []
for pat in ("swUserPreferenceStringValue", "swUserPreferenceToggle", "swUserPreferenceIntegerValue"):
    for p in sw.rglob(pat + "*"):
        hits.append(p); break
for p in hits[:3]:
    print("### %s" % p.name)
    txt = p.read_text(encoding="utf-8", errors="replace")
    for l in txt.splitlines():
        if re.match(r"^\s*\|?\s*(sw|val)", l) or "=" in l:
            print("   ", l.strip()[:110])
    print()
