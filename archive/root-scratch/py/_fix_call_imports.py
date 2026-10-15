import ast
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
FILES = ["scripts/sw_document_data.py", "scripts/sw_drawing_view.py",
         "scripts/sw_geometry_selectors.py", "scripts/sw_gtol.py", "scripts/sw_mold.py",
         "scripts/sw_selection.py", "scripts/sw_sheet_metal.py", "scripts/sw_simulation.py",
         "scripts/sw_topology.py", "scripts/sw_view.py", "scripts/sw_weldment.py"]

for f in FILES:
    p = ROOT / f
    t = p.read_text(encoding="utf-8")
    #: 找导入 get_com_member 的那一行
    m = re.search(r"(?m)^from sw_connect import (.+)$", t)
    if m:
        names = [x.strip() for x in m.group(1).split(",")]
        if "call_com_member" not in names:
            names.append("call_com_member")
            names = sorted(set(names), key=lambda s: (s != "get_com_member", s))
            t = t[:m.start()] + "from sw_connect import " + ", ".join(names) + t[m.end():]
            p.write_text(t, encoding="utf-8")
            print("  ✓ %-34s 已补 import" % f.split("/")[-1])
        else:
            print("  · %-34s 已有" % f.split("/")[-1])
    else:
        #: 别的导入形态
        m2 = re.search(r"(?m)^.*import.*\bget_com_member\b.*$", t)
        print("  ⚠ %-34s 导入形态不同: %s" % (f.split("/")[-1], m2.group(0).strip()[:70] if m2 else "找不到"))
    ast.parse(p.read_text(encoding="utf-8"))
print()
print("  语法全部 OK" if all(True for _ in FILES) else "")
