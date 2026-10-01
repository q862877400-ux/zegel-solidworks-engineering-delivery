import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\tools\probe_unit_declarations.py")
t = p.read_text(encoding="utf-8")
OLD = 'print("⚠ **不下"该接门禁"的结论** —— 这份清单要**人工逐条看**：")'
NEW = 'print("⚠ **不下「该接门禁」的结论** —— 这份清单要**人工逐条看**：")'
if OLD in t:
    p.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
    print("  ok 已修")
else:
    for i, l in enumerate(t.splitlines(), 1):
        if "不下" in l:
            print("  L%-4d %s" % (i, l[:100]))
ast.parse(p.read_text(encoding="utf-8"))
print("  语法 OK")
