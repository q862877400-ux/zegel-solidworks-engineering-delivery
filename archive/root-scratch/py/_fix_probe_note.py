import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\probe_capability_coverage.py")
t = P.read_text(encoding="utf-8")
bad = "#   因为**能力条目是域级的**（\nouting / weldments / surface_modeling …），\n"
good = "#   因为**能力条目是域级的**（routing / weldments / surface_modeling …），\n"
if bad in t:
    t = t.replace(bad, good, 1)
    P.write_text(t, encoding="utf-8")
    print("  ok 已修复被回车吃掉的 `routing`")
else:
    print("  未找到该坏行；当前 48-56 行：")
    for i, l in enumerate(t.splitlines()[47:56], 48):
        print("    L%-4d %r" % (i, l[:80]))
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
