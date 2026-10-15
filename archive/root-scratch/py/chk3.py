import re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
t = Path(r"D:\AI\SW\_raw\reflect\iface_dsgnchk.txt").read_text(encoding="utf-8", errors="replace")
for l in t.splitlines():
    if "CheckAgainstExistingFile" in l: print("  反射原文:", l.strip())
print()
# 门禁的反射清单列表
T = Path(r"C:\swprojects\sw-skill-fork\tests\test_official_names_only_contract.py")
print("  门禁列的反射清单:")
for m in re.findall(r'iface_(\w+)\.txt', T.read_text(encoding="utf-8")):
    print("    " + m)