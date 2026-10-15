import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_sketch_edit_smoke.py")
t = P.read_text(encoding="utf-8")
n = 0
#: ⚠ 冒烟原来用默认的 `distance_angle`（=0）⇒ 实测**只有 `distance_equal`(2) 能成**
OLD1 = 'sw_sketch_edit.create_sketch_chamfer(doc, distance_mm=5.0)'
NEW1 = ('#: ⚠⚠⚠ **必须用 `distance_equal`(2)** —— 轮 164 实测（`tools/probe_chamfer_forms.py`）：\n'
        '            #: `type=0`(默认) / `type=1` ⇒ 段数**不变**且返回 None；\n'
        '            #: `type=2` ⇒ 段数 **2 → 3**（倒角真的建出来了）。\n'
        '            sw_sketch_edit.create_sketch_chamfer(\n'
        '                doc, chamfer_type=2, distance_mm=5.0)')
if OLD1 in t:
    t = t.replace(OLD1, NEW1, 1)
    n += 1
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  改了 %d 处" % n)
