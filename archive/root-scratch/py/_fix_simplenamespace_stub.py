import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")

P = ROOT / "tests" / "test_sw_part_sketch_selection.py"
t = P.read_text(encoding="utf-8")
OLD = 'sys.modules["sw_connect"] = types.SimpleNamespace(get_com_member=fake_get_com_member)'
NEW = ('#: ⚠ 2026-10-01（轮 145）：桩要**跟着真模块走** —— 轮 145 给 `sw_connect`\n'
       '#:   加了 `call_com_member`（"故意要调"的显式名），桩里也得有，否则 `sw_part` 导入即失败。\n'
       'sys.modules["sw_connect"] = types.SimpleNamespace(\n'
       '    get_com_member=fake_get_com_member,\n'
       '    call_com_member=fake_get_com_member,\n'
       ')')
assert OLD in t, "桩锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ✓ test_sw_part_sketch_selection.py 的桩已补 call_com_member")

#: 顺带全局扫一遍还有没有 `SimpleNamespace(... get_com_member` 形态的桩
import re
for p in sorted((ROOT / "tests").glob("*.py")):
    s = p.read_text(encoding="utf-8")
    for m in re.finditer(r"(?m)^.*SimpleNamespace\(.*get_com_member.*$", s):
        if "call_com_member" not in m.group(0):
            ln = s[:m.start()].count("\n") + 1
            print("     ⚠ %s:%d 还有只含 get_com_member 的 SimpleNamespace 桩" % (p.name, ln))
