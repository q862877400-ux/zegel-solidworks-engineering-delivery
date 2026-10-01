import ast
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_assembly_doc.py")
t = p.read_text(encoding="utf-8")
print("  导入块（找 try/except 与 from … import）:")
for m in re.finditer(r"(?m)^(try:|except ImportError:|    from \S+ import .*$|from \S+ import .*$)", t):
    print("    %s" % m.group(0).strip()[:104])
print()
for k in ("out_i4", "_select_by_id"):
    #: 看它是**导入**来的还是**本文件定义**的
    print("  %-16s 定义在本文件: %s" % (k, bool(re.search(r"(?m)^def %s\b" % k, t))))
