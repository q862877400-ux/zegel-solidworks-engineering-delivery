import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sw = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
for n in ("GetMaterialPropertyValues","GetBodies2","GetSuppressions","GetComponentState"):
    hits = sorted(set(re.findall(r"\b(\w*%s\w*)\s*\(" % n, sw)))[:3]
    print("  %-28s -> %s" % (n, hits if hits else "反射里没有"))
