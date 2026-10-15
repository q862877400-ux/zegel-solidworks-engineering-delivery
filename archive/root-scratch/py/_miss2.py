import re, sys, io, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
REPO = Path(r"C:\swprojects\sw-skill-fork")
doc = json.loads((REPO/"docs"/"family-coverage.json").read_text(encoding="utf-8"))
# 收集仓库里出现的所有 API 成员名（登记表字面量）
known = set()
for p in (REPO/"scripts").glob("*.py"):
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip().startswith("#"): continue
        known |= set(re.findall(r"['\"]([A-Z]\w{2,})['\"]\s*[,:}]", line))
INTERNAL = re.compile(r"^I[A-Z][a-z]")
SWAPI = Path(r"C:\swapi\types")
missing = {}
for row in doc:
    f = row.get("family")
    pct = row.get("pct")
    if not f or pct is None or pct >= 100: continue
    d = SWAPI / f
    if not d.is_dir(): continue
    want = {p.stem for p in d.glob("*.md")
            if p.stem != "_overview" and not INTERNAL.match(p.stem)}
    miss = sorted(n for n in want if n not in known)
    if miss: missing[f] = miss
tot = sum(len(v) for v in missing.values())
print("缺 %d 个成员，分布在 %d 族" % (tot, len(missing)))
for f, v in sorted(missing.items())[:20]:
    print("  %-34s %s" % (f, ", ".join(v)))
