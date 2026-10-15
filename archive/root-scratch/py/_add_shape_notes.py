import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_sketch.py")
t = P.read_text(encoding="utf-8")

NOTE = '''
    ⚠⚠ **返回的是「数值数组」，不是「对象列表」** —— 实测（2026-10-01 轮 141，
    `tools/probe_sketch_getter_shapes.py`，真机 SW 2026 SP4.1）：

    | 取法 | 画 1 个 | 画 2 个 | 每个占几个 `float` |
    |---|---|---|---|
    | `get_lines` | 12 | 24 | **12** |
    | `get_arcs` | 16 | 32 | **16** |
    | `get_ellipses` | 22 | 44 | **22** |

    ⇒ ★ **这是通例，不是孤例**：`get_*` 系列都返回**数值数组**（元素类型是 `float`）。
    ⚠ **要「几个实体」用 `get_sketch_segments(sketch)`**；⚠ 官方文档**没写**这个返回结构。
'''

#: 给 get_arcs / get_ellipses 各加一段同样的说明（它们此前没有）
for fn in ("get_arcs", "get_ellipses"):
    i = t.index("def %s(" % fn)
    j = t.index('"""', i + 1)              # 开头三引号
    k = t.index('"""', j + 3)              # 结尾三引号
    body = t[j + 3:k]
    if "数值数组" in body:
        print("  %s 已有说明" % fn)
        continue
    t = t[:k] + NOTE + t[k:]
    print("  ok %s 已加「数值数组」说明" % fn)

P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  语法 OK")
