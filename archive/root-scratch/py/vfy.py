import sys, re
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
off, enums = set(), set()
for f in Path(r"D:\AI\SW\_raw").rglob("iface_*.txt"):
    for l in f.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\s*(\S+)\s+(\w+)\s*\(", l.strip())
        if m: off.add(re.sub(r"^(get|set)_", "", m.group(2)))
for f in Path(r"D:\AI\SW\_raw").rglob("enum_*.txt"):
    for l in f.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\s*(\w+)\s*=", l.strip())
        if m: enums.add(m.group(1))
for f in Path(r"D:\AI\SW\_raw").rglob("enum_values_sldworks.txt"):
    for l in f.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\s*(\w+)\s*=", l.strip())
        if m: enums.add(m.group(1))
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_automation_knowledge.py")
s = p.read_text(encoding="utf-8")
claimed = set(re.findall(r'get_com_member\([^,]+,\s*"(\w+)"', s))
tbl = set(re.findall(r'^    "(\w+)": \d+,\s*$', s, re.M))
sup = set(re.findall(r'^    "(sw\w+)": \d+,\s*$', s, re.M))
allc = claimed | tbl | sup
bad = sorted(n for n in allc if n not in off and n not in enums)
print("  成员名 %d 个，查不到的: %s" % (len(allc), bad if bad else "无"))
print("  枚举项 %d 个 (swInputDimValOnCreate 在枚举里: %s)" % (len(sup), "swInputDimValOnCreate" in enums))