import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_part.py")
t = P.read_text(encoding="utf-8")

OLD = """try:
    #: ⚑ 轮 127：`mm()` 也一并导入 —— 此前 `mm(...)` 只出现在**文档串的示例**里，
    #: 真要用时才发现没导入（`get_bounding_box` 就栽在这）。
    from .sw_connect import get_com_member, mm
    from .sw_preflight import import_com_dependencies
except ImportError:
    from sw_connect import get_com_member, mm
    from sw_preflight import import_com_dependencies"""
NEW = """try:
    from .sw_connect import get_com_member
    from .sw_preflight import import_com_dependencies
except ImportError:
    from sw_connect import get_com_member
    from sw_preflight import import_com_dependencies"""
if OLD in t:
    t = t.replace(OLD, NEW, 1)
    P.write_text(t, encoding="utf-8")
    print("  ok 已撤回 mm 的导入（单位修正后不再需要它）")
else:
    print("  ⚠ 锚点不符")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
print("  文件里还有 mm( 的**代码**用法吗: %s"
      % [l.strip()[:70] for l in P.read_text(encoding='utf-8').splitlines()
         if "mm(" in l and not l.strip().startswith("#") and '"""' not in l][:3])
