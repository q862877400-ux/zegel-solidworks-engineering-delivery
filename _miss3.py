import re, sys, io, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
REPO = Path(r"C:\swprojects\sw-skill-fork")
SIG = re.compile(r"^\S+\s+(\w+)\s*\((.*)\)$")
INTERNAL = re.compile(r"^I[A-Z][a-z]")
SRC = [r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt",
       r"D:\AI\SW\_raw\reflect\iface_cosworks.txt",
       r"D:\AI\SW\_raw\reflect\iface_swdocumentmgr.txt",
       r"D:\AI\SW\_raw\reflect\iface_SWRoutingLib.txt",
       r"D:\AI\SW\_raw\reflect\iface_sldcostingapi.txt",
       r"D:\AI\SW\_raw\reflect\iface_fworks.txt"]
official = set()
per_fam = {}
for p in SRC:
    if not Path(p).is_file(): continue
    cur = None
    for l in Path(p).read_text(encoding="utf-8", errors="replace").splitlines():
        if l.startswith("## "):
            cur = l[3:].strip(); per_fam.setdefault(cur, set()); continue
        if not cur: continue
        m = SIG.match(l.strip())
        if not m: continue
        n = re.sub(r"^(get|set)_", "", m.group(1))
        if INTERNAL.match(n): continue
        per_fam[cur].add(n); official.add(n)
# 仓库里登记过的名字
known = set()
for f in (REPO/"scripts").glob("*.py"):
    for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip().startswith("#"): continue
        known |= set(re.findall(r"['\"]([A-Za-z_]\w{2,})['\"]\s*[,:}]", line))
doc = json.loads((REPO/"docs"/"family-coverage.json").read_text(encoding="utf-8"))
bad = {}
for row in doc:
    f = row.get("family")
    if not f: continue
    want = per_fam.get(f)
    if want is None: continue
    miss = sorted(n for n in want if n not in known)
    if miss: bad[f] = miss
print("官方成员全集 %d 个；仓库已登记 %d 个" % (len(official), len(official & known)))
print("仍缺 %d 个，分布在 %d 族" % (sum(len(v) for v in bad.values()), len(bad)))
for f, v in sorted(bad.items())[:12]:
    print("  %-34s %s" % (f, ", ".join(v)))
