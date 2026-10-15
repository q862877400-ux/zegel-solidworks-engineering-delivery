"""找 GetCostingManager 挂在哪个接口上（只读反射 + 索引）。"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

for rel in (r"reflect_sldworks\iface_sldworks.txt", r"topo-sldworks\iface_sldworks.txt"):
    p = Path(r"D:\AI\SW\_raw") / rel
    t = p.read_text(encoding="utf-8", errors="replace").splitlines()
    cur = None
    hits = []
    for i, l in enumerate(t):
        if l.strip().startswith("## "):
            cur = l.strip()[3:]
        if "GetCostingManager" in l:
            hits.append((cur, i + 1, l.strip()))
    print("  ── %s ⇒ %d 处 ──" % (rel, len(hits)))
    for iface, ln, txt in hits:
        print("     [%s] L%d: %s" % (iface, ln, txt))

print()
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_api_sldworks.py")
t = p.read_text(encoding="utf-8").splitlines()
print("  索引里 L23425 往上找最近的族名：")
for i in range(23424, 0, -1):
    m = re.match(r"^\s*'?(I[A-Z]\w+)'?\s*:\s*[\(\{]", t[i - 1])
    if m:
        print("     族名 = %s  （L%d）" % (m.group(1), i))
        break
print("     命中行 = %s" % t[23424].strip())
print()
print("  另：L6685 那处（index 0）属于哪个族：")
for i in range(6684, 0, -1):
    m = re.match(r"^\s*'?(I[A-Z]\w+)'?\s*:\s*[\(\{]", t[i - 1])
    if m:
        print("     族名 = %s  （L%d）" % (m.group(1), i))
        break
