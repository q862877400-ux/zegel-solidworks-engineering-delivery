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

#: ★★ 先量**真名字在不在**（`import` 成功 ≠ 名字存在）
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import importlib
print("  ── 修之前：调用点用的名字在模块里存在吗 ──")
for f in FILES:
    mod = "scripts." + Path(f).stem
    m = importlib.import_module(mod)
    print("     %-34s call_com_member 存在=%s" % (Path(f).stem, hasattr(m, "call_com_member")))

print()
print("  ── 补相对导入 ──")
for f in FILES:
    p = ROOT / f
    t = p.read_text(encoding="utf-8")
    m = re.search(r"(?m)^from \.sw_connect import (.+)$", t)
    if not m:
        print("     ⚠ %-32s 找不到相对导入行" % Path(f).stem)
        continue
    names = sorted({x.strip() for x in m.group(1).split(",")} | {"call_com_member"})
    new = "from .sw_connect import " + ", ".join(names)
    t = t[:m.start()] + new + t[m.end():]
    p.write_text(t, encoding="utf-8")
    ast.parse(t)
    print("     ✓ %-32s %s" % (Path(f).stem, new[:70]))
