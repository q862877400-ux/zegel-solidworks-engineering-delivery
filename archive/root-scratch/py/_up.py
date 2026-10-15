import ast, io, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
src = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_hole_features.py").read_text(encoding="utf-8")
lines = src.splitlines()
tree = ast.parse(src)
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and len(node.body) > 3:
        print("\n".join(lines[node.lineno-1:node.end_lineno]))
        break
