import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_hole_features.py")
t = P.read_text(encoding="utf-8")
t = t.replace("sw_hole_features.list_hole_standards", "holes.list_hole_standards")
t = t.replace("sw_hole_features, \"list_hole_standards\"", "holes, \"list_hole_standards\"")
t = t.replace('hasattr(sw_hole_features,', 'hasattr(holes,')
t = t.replace("from scripts import sw_hole_features as holes", "from scripts import sw_hole_features as holes")
# REPO_ROOT：从 __file__ 推
if "REPO_ROOT = " not in t:
    t = t.replace(
        "from scripts import sw_hole_features as holes\n",
        "from pathlib import Path\n\n"
        "from scripts import sw_hole_features as holes\n\n"
        "REPO_ROOT = Path(__file__).resolve().parents[1]\n",
        1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已改用 holes 别名 + 补 REPO_ROOT")
print("  还剩 sw_hole_features 字样: %d" % t.count("sw_hole_features"))
