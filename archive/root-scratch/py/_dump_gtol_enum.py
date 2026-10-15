import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
for f in Path(r"D:\AI\SW\_raw").rglob("enum_*.txt"):
    t = f.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"(?ms)^## swGtolGeomCharSymbol_e\s*\n(.*?)(?=\n## |\Z)", t)
    if m:
        rows = re.findall(r"^\s+(swGcs\w+)\s*=\s*(-?\d+)\s*$", m.group(1), re.M)
        print("  来源: %s" % f)
        print("  共 %d 项:" % len(rows))
        for n, v in rows:
            print("    %-24s %s" % (n, v))
        break
else:
    print("  没找到（换 swapi 的 md）")
    p = Path(r"C:\swapi\enums\swGtolGeomCharSymbol_e.md")
    if p.is_file():
        for l in p.read_text(encoding="utf-8").splitlines():
            if l.startswith("| sw"):
                print("   %s" % l.strip()[:60])
