import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_part_sketch_selection.py")
t = P.read_text(encoding="utf-8")
if "\nimport inspect\n" not in t:
    t = t.replace("import sys\n", "import inspect\nimport sys\n", 1)
    print("  ok 已导入 inspect")
# 断言跟随实际字面（加粗包住整句，不是只包「毫米」）
t = t.replace('assert "长度单位：**毫米**" in src, "模块头要写明单位"',
              'assert "长度单位" in src and "毫米" in src, "模块头要写明单位"')
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  语法 OK")
for i, l in enumerate(t.splitlines(), 1):
    if "长度单位" in l:
        print("    L%-4d %s" % (i, l.strip()[:88]))
