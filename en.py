import sys, re
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
SW = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
seg = re.search(r"(?ms)^## ISldWorks\s*\r?\n(.*?)(?=\r?\n## |\Z)", SW).group(1)
print("=== ISldWorks 上与 CommandInProgress 相关的行 ===")
for l in seg.splitlines():
    if "CommandInProgress" in l: print("   " + l.strip())
print()
print("=== ISldWorks 上含 Notification / Error 的行 ===")
for l in seg.splitlines():
    if re.search(r"Notif|Error", l.strip()): print("   " + l.strip())
print()
print("=== 全程序集里含 ErrorNotification 的成员 ===")
for p in Path(r"D:\AI\SW\_raw").rglob("iface_*.txt"):
    cur=None
    for l in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if l.startswith("## "): cur=l[3:].strip()
        elif cur and "ErrorNotification" in l: print("   [%s] %s" % (p.name, l.strip()))