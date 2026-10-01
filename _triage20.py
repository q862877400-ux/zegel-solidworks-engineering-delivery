import re
import sys
from collections import defaultdict
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
TYPES = Path(r"C:\swapi\types")
CALL = re.compile(r'get_com_member\(\s*([^,]+?)\s*,\s*"([A-Za-z_]\w*)"')

TARGETS = [
    "AdvancedGraphics", "AutoDimension2", "ExcludeFromBOM", "GetComponents",
    "GetDependencies2", "GetEdges", "GetErrorCode", "GetNext", "GetPolylines",
    "GetSplines", "GetType", "GetUserPreferenceToggle", "IsSuppressed", "KFactor",
    "MoldUndercutDetect", "ReferenceType", "SetUserPreferenceToggle", "SystemValue",
    "GetUserPoints", "GetSketchPoints",
]

# 我们的调用点：成员 → [(文件, 行号, 目标表达式, 整行)]
sites = defaultdict(list)
for p in sorted((ROOT / "scripts").glob("sw_*.py")):
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    for i, l in enumerate(lines, 1):
        for m in CALL.finditer(l):
            sites[m.group(2)].append((p.name, i, m.group(1).strip(), l.strip()[:96]))

# 官方文档：成员 → [(接口, 是否 Obsolete, 后继)]
docs = defaultdict(list)
for p in TYPES.rglob("*.md"):
    docs[p.stem].append(p)

for name in TARGETS:
    ss = sites.get(name) or []
    if not ss:
        continue
    print("── %s（%d 处调用）" % (name, len(ss)))
    for d in docs.get(name, []):
        head = d.read_text(encoding="utf-8", errors="replace")[:1200]
        obs = "Obsolete" in head
        m = re.search(r"Obsolete\.\s*(?:Superseded by\s*(.+?)\.)?", head)
        print("     文档: %-42s Obsolete=%s" % (d.parent.name, obs))
        if m and m.group(1):
            print("           后继: %s" % m.group(1)[:66])
    for f, i, tgt, line in ss[:3]:
        print("     调用: %s:%d  target=%r" % (f, i, tgt))
        print("           %s" % line)
    if len(ss) > 3:
        print("     …（还有 %d 处）" % (len(ss) - 3))
    print()
