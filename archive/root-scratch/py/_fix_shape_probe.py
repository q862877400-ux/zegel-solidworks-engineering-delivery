import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\probe_sketch_getter_shapes.py")
t = P.read_text(encoding="utf-8")

#: 去掉 point 那一档（`sw_part` 没有点构造函数；`ISketchManager.CreatePoint` 尚未包）
OLD = '''    ("spline", ["get_splines"], lambda part, i: _spline(part, i)),
    ("point", ["get_sketch_points"], lambda part, i: _point(part, i)),
]'''
NEW = '''    ("spline", ["get_splines"], lambda part, i: _spline(part, i)),
    #: ⚠ **`point` 那一档去掉了**：`sw_part` 没有点构造函数
    #: （反射里 `ISketchManager.CreatePoint(Double,Double,Double) -> SketchPoint` 存在，
    #:  但**本模块尚未包装**）⇒ 强行测会得到"画不出来"，**不是取法的问题**。
]'''
assert OLD in t, "CASES 锚点不符"
t = t.replace(OLD, NEW, 1)

#: 去掉 `_point` 定义
i = t.index("def _point(part, i):")
j = t.index("def modal_dialogs(")
t = t[:i] + t[j:]
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已去掉 point 那一档")
