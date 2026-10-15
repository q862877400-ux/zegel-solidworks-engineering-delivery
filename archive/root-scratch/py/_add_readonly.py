import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\mcp-server\tool_specs_batch10.py")
t = P.read_text(encoding="utf-8")
n = t.count("        inject=")
t = t.replace("        inject=", "        read_only=True,      # ⚑ 本批 4 条**都是查询**（不改几何、不改文档）\n        inject=")
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已给 %d 条加 read_only=True" % n)
