import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
t = (R / "scripts" / "sw_gtol.py").read_text(encoding="utf-8")
print("  ── sw_gtol.py 头 40 行 ──")
for l in t.splitlines()[:40]:
    print("    %s" % l[:100])
print()
print("  ── 公开函数 ──")
import ast
print("    %s" % [n.name for n in ast.parse(t).body if isinstance(n, ast.FunctionDef)])
