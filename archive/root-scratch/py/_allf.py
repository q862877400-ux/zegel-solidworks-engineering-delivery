import sys, io, re
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
srcs = {
  "sldworks":   r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt",
  "cosworks":   r"D:\AI\SW\_raw\reflect\iface_cosworks.txt",
  "swdocumentmgr": r"D:\AI\SW\_raw\reflect\iface_swdocumentmgr.txt",
  "SWRoutingLib":  r"D:\AI\SW\_raw\reflect\iface_SWRoutingLib.txt",
  "sldcostingapi": r"D:\AI\SW\_raw\reflect\iface_sldcostingapi.txt",
  "fworks":     r"D:\AI\SW\_raw\reflect\iface_fworks.txt",
}
def fams(path):
    cur, out = None, set()
    for raw in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        if raw.startswith("## "): cur = raw[3:].strip()
        elif cur and raw.strip() and re.match(r"^\S+\s+\w+\s*\(", raw.strip()): out.add(cur)
    return out
allf = {}
for asm, p in srcs.items():
    f = fams(p)
    allf[asm] = sorted(f)
    print("  %-16s %4d 族" % (asm, len(f)))
# swapi 侧的族（从 docs/family-coverage 的域表）
import json
doc = Path(r"C:\swprojects\sw-skill-fork\docs\family-coverage.md").read_text(encoding="utf-8")
swapi_fams = set(re.findall(r"\| `(\w+)` \| \d+ \|", doc))
allf["swapi_scoped"] = sorted(swapi_fams)
print("  覆盖表里出现的族 =", len(swapi_fams))
Path(r"D:\AI\SW\_all_families.json").write_text(json.dumps(allf, ensure_ascii=False, indent=2), encoding="utf-8")
print("已存 D:\\AI\\SW\\_all_families.json")
