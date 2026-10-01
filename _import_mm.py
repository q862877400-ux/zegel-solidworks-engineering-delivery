import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_part.py")
t = P.read_text(encoding="utf-8")

OLD = """try:
    from .sw_connect import get_com_member
    from .sw_preflight import import_com_dependencies"""
NEW = """try:
    #: ⚑ 轮 127：`mm()` 也一并导入 —— 此前 `mm(...)` 只出现在**文档串的示例**里，
    #: 真要用时才发现没导入（`get_bounding_box` 就栽在这）。
    from .sw_connect import get_com_member, mm
    from .sw_preflight import import_com_dependencies"""
if OLD in t:
    t = t.replace(OLD, NEW, 1)
    print("  ok 已导入 mm（相对导入那支）")
else:
    print("  ⚠ 相对导入锚点不符")
if "from sw_connect import get_com_member" in t:
    OLD2 = "    from sw_connect import get_com_member"
    NEW2 = "    from sw_connect import get_com_member, mm"
    t = t.replace(OLD2, NEW2, 1)
    print("  ok 已导入 mm（绝对导入那支）")
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  语法 OK")
