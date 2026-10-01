import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_part_sketch_selection.py")
t = P.read_text(encoding="utf-8")
print("  现有导入行:")
for i, l in enumerate(t.splitlines()[:16], 1):
    if l.startswith(("import ", "from ")):
        print("    L%-3d %s" % (i, l[:90]))
