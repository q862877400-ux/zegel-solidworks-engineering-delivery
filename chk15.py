import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
off = set()
for f in Path(r"D:\AI\SW\_raw").rglob("iface_*.txt"):
    for l in f.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\s*(\S+)\s+(\w+)\s*\(", l.strip())
        if m: off.add(re.sub(r"^(get|set)_", "", m.group(2)))
idx = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_api_sldworks.py").read_text(encoding="utf-8")
# 扫新增的四张表
import importlib.util
for tbl in ("READONLY","WRITEONLY","HIDDEN"):
    m = re.search(tbl + r": dict\[str, tuple\[str, \.\.\.\]\] = \{(.*?)\n\}", idx, re.S)
    if not m: continue
    names = re.findall(r"^        '(\w+)',$", m.group(1), re.M)
    miss = [n for n in names if n not in off]
    print("  %-10s %4d 条，查不到 %d %s" % (tbl, len(names), len(miss), miss[:5]))