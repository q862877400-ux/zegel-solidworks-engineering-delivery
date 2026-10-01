import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_assembly_doc.py")
t = p.read_text(encoding="utf-8")
lines = t.splitlines()
print("  前 34 行:")
for i, l in enumerate(lines[:34], 1):
    print("    L%-4d %s" % (i, l[:96]))
print()
for k in ("call_com_member", "out_i4", "_select_by_id", "safe_get_com_member"):
    print("  %-22s 在文件里: %s" % (k, k in t))
