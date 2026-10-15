import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
for f in ("sketch_relations.py", "sw_assembly_doc.py", "sw_sketch_edit.py"):
    p = R / "scripts" / f
    t = p.read_text(encoding="utf-8")
    tree = ast.parse(t)
    fns = [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    pub = [n for n in fns if not n.startswith("_")]
    print("── %-22s %4d 行 · 顶层函数 %d 个（公开 %d）" % (f, t.count(chr(10)), len(fns), len(pub)))
    for n in pub:
        print("      %s" % n)
    print()
