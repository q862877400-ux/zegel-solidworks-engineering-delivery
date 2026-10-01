import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_part.py")
t = P.read_text(encoding="utf-8")

OLD = '''    :returns: `{"min": [x, y, z], "max": [...], "size": [dx, dy, dz]}` ——
        **全部是毫米**，`size` 是各轴方向的跨度。
    :raises RuntimeError: 拿不到实体，或 `GetBodyBox` 返回的元素不是 6 个。
    """'''
NEW = '''    ★★ **单位：毫米 —— 这是实测出来的，官方没写。**
    2026-10-01（轮 127）真机：建一个 **80 × 60 × 50 mm** 的盒子，`GetBodyBox` 原始返回
    `[0.0, 0.0, -50.0, 80.0, 60.0, 0.0]` ⇒ **原始值就是 80 / 60 / 50**。
    ⚠ 这与官方**其它**几何接口惯用的"米"**不同** ⇒ **不要再乘/除 1000**。
    ⚠ 第一版实现误用了 `sw_connect.mm()`（那是**输入方向**：毫米→米），
    结果把 0.08 又除了 1000 ⇒ 被本轮的**数值冒烟**当场抓住。

    :returns: `{"min": [x, y, z], "max": [...], "size": [dx, dy, dz]}` ——
        **全部是毫米**（见上），`size` 是各轴方向的跨度。
    :raises RuntimeError: 拿不到实体，或 `GetBodyBox` 返回的元素不是 6 个。
    """'''
assert OLD in t, "docstring 锚点不符"
t = t.replace(OLD, NEW, 1)

OLD2 = '''    b = [float(v) for v in box]
    mn, mx = b[:3], b[3:]
    return {
        "min": [mm(v) for v in mn],
        "max": [mm(v) for v in mx],
        "size": [mm(mx[i] - mn[i]) for i in range(3)],
    }'''
NEW2 = '''    b = [float(v) for v in box]
    mn, mx = b[:3], b[3:]
    #: ⚠ **不做单位换算** —— 实测 `GetBodyBox` 的原始值就是**毫米**
    #: （80 mm 的盒子返回 80.0，不是 0.08）。第一版误用 `mm()` ⇒ 被数值冒烟抓住。
    return {
        "min": list(mn),
        "max": list(mx),
        "size": [mx[i] - mn[i] for i in range(3)],
    }'''
assert OLD2 in t, "实现锚点不符"
t = t.replace(OLD2, NEW2, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已去掉错误的单位换算，并把实测结论写进 docstring")
