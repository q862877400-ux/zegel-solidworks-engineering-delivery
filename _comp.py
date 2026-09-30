import re, sys, io, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
doc = Path(r"C:\swprojects\sw-skill-fork\docs\family-coverage.md").read_text(encoding="utf-8")
rows = re.findall(r"(?m)^\| [^|]+ \| `(\w+)` \| (\d+) \|", doc)
mapped = {f for f, _ in rows}
print("覆盖表里的族 =", len(mapped), "/ 总成员 =", sum(int(n) for _, n in rows))
# 各程序集反射里全部族
SRC = {
 "sldworks":      r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt",
 "cosworks":      r"D:\AI\SW\_raw\reflect\iface_cosworks.txt",
 "swdocumentmgr": r"D:\AI\SW\_raw\reflect\iface_swdocumentmgr.txt",
 "SWRoutingLib":  r"D:\AI\SW\_raw\reflect\iface_SWRoutingLib.txt",
 "sldcostingapi": r"D:\AI\SW\_raw\reflect\iface_sldcostingapi.txt",
 "fworks":        r"D:\AI\SW\_raw\reflect\iface_fworks.txt",
}
SIG = re.compile(r"^\S+\s+\w+\s*\(")
allf = {}
for asm, p in SRC.items():
    f = set(); cur=None
    for l in Path(p).read_text(encoding="utf-8", errors="replace").splitlines():
        if l.startswith("## "): cur=l[3:].strip()
        elif cur and l.strip() and SIG.match(l.strip()): f.add(cur)
    allf[asm] = sorted(f)
    print("  %-14s %4d 族" % (asm, len(f)))
allfams = set().union(*allf.values())
print("全部程序集有成员的族 =", len(allfams))
print("覆盖表遗漏的族 =", len(allfams - mapped))
Path(r"D:\AI\SW\_complete_families.json").write_text(
    json.dumps({"by_asm": allf, "all": sorted(allfams)}, ensure_ascii=False, indent=2),
    encoding="utf-8")
