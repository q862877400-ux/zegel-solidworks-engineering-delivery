import ast, io, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_hole_features.py")
src = p.read_text(encoding="utf-8")
lines = src.splitlines()
tree = ast.parse(src)
best = None
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and 8 < len(node.body) < 40:
        if best is None or len(node.body) > len(best.body):
            best = node
print("\n".join(lines[best.lineno-1:best.end_lineno]))
