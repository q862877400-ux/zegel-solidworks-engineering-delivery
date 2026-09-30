import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
RAW = Path(r"D:\AI\SW\_raw")
S = Path(r"C:\swprojects\sw-skill-fork\scripts")

mine = set()
for p in S.glob("sw_api_*.py"):
    c = p.read_text(encoding="utf-8")
    mine |= set(re.findall(r"^        '(\w+)': \d+,", c, re.M))
    mine |= set(re.findall(r"^        '(\w+)',", c, re.M))

rf = None
for f in RAW.rglob("iface_sldworks*.txt"):
    rf = f
    break
meth, prop, enu = set(), set(), {}
for line in rf.read_text(encoding="utf-8", errors="replace").splitlines():
    s = line.strip()
    m = re.match(r"^(\S+)\s+(\w+)\s*\(", s)
    if m:
        n = m.group(2)
        (prop if n.startswith(("get_", "set_")) else meth).add(re.sub(r"^(get|set)_", "", n))
        continue
    m = re.match(r"^(\w*_e)\.(\w+)\s*=", s)
    if m:
        enu[m.group(2)] = m.group(1)

cap = meth | prop
miss = sorted(cap - mine)
print("  sldworks 缺口 %d 个。前 50 个及其性质:" % len(miss))
enum_only = both = 0
for n in miss[:50]:
    tag = "枚举=" + enu[n] if n in enu else "★接口能力"
    print("    %-38s %s" % (n, tag))
e = sum(1 for n in miss if n in enu)
print()
print("  全部 %d 个缺口里：在枚举表中出现的 %d / 纯接口能力 %d"
      % (len(miss), e, len(miss) - e))
