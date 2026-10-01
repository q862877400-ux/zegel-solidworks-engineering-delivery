import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_part_sketch_selection.py")
t = P.read_text(encoding="utf-8")
OLD = '''        src = (ROOT / "scripts" / "sw_part.py").read_text(encoding="utf-8")
        i = src.index("def get_bounding_box")
        body = src[i:i + 2600]'''
NEW = '''        src = (ROOT / "scripts" / "sw_part.py").read_text(encoding="utf-8")
        i = src.index("def get_bounding_box")
        # ⚠ 往前多取一段 —— 官方的 "approximate" 原文在**来源块**里（在 def **之前**）
        body = src[max(0, i - 2200):i + 2600]'''
assert OLD in t, "锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 判据切片已往前扩（含来源块）")
