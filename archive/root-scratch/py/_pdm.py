import sys, io, re
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
cur, out = None, set()
for raw in Path(r"D:\AI\SW\_raw\reflect\iface_swdocumentmgr.txt").read_text(encoding="utf-8", errors="replace").splitlines():
    if raw.startswith("## "): cur = raw[3:].strip()
    elif cur and raw.strip() and re.match(r"^\S+\s+\w+\s*\(", raw.strip()): out.add(cur)
Path(r"D:\AI\SW\_pdm_all.txt").write_text(" ".join(sorted(out)), encoding="utf-8")
print("swdocumentmgr 族 =", len(out))
