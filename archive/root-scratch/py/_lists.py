import sys, io, re
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
def families(path):
    cur, out = None, set()
    for raw in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        if raw.startswith("## "): cur = raw[3:].strip()
        elif cur and raw.strip() and re.match(r"^\S+\s+\w+\s*\(", raw.strip()):
            out.add(cur)
    return sorted(out)
cw = families(r"D:\AI\SW\_raw\reflect\iface_cosworks.txt")
rt = families(r"D:\AI\SW\_raw\reflect\iface_SWRoutingLib.txt")
pd = families(r"D:\AI\SW\_raw\reflect\iface_swdocumentmgr.txt")
co = families(r"D:\AI\SW\_raw\reflect\iface_sldcostingapi.txt")
print("cosworks 有成员族 =", len(cw))
print("SWRoutingLib =", len(rt), " sldcostingapi =", len(co), " swdocumentmgr =", len(pd))
print("SWRoutingLib 全部:", " ".join(rt))
print("sldcostingapi 全部:", " ".join(co))
Path(r"D:\AI\SW\_cw_all.txt").write_text(" ".join(cw), encoding="utf-8")
Path(r"D:\AI\SW\_hub_all.txt").write_text(" ".join(rt + co), encoding="utf-8")
print("名单已存")
