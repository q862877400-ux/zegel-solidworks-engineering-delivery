import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_part.py")
t = P.read_text(encoding="utf-8")

NEW = '''

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**不是**从四家外部 MCP 项目移植）。
# 文件:   scripts/sw_part.py —— 「椭圆」这一段（2026-10-01 轮 132）。
# 定位:   补 `docs/union-gap-triage.md`「真缺」档里的 `ellipse`。
# 官方依据: ① 出厂类型库反射 `iface_*.txt`：
#             `SketchSegment CreateEllipse(Double ×9)`（在 `ISketchManager` 上）
#           ② `C:\\swapi\\types\\ISketchManager\\CreateEllipse.md`：
#             `SketchSegment CreateEllipse(XC, YC, Zc, XMajor, YMajor, ZMajor,
#              XMinor, YMinor, ZMinor)` —— **9 个 double**，返回草图线段。
#           ③ ⚠ **两级废弃链**（本模块**不走前两级**）：
#             `IModelDoc2.CreateEllipse(Object,Object,Object)`
#               ⇒ `Obsolete. Superseded by IModelDoc2::CreateEllipse2.`
#             `IModelDoc2.CreateEllipse2(Double ×9)`
#               ⇒ `Obsolete. Superseded by ISketchManager::CreateEllipse.`
#             ⇒ **现行入口是 `ISketchManager.CreateEllipse`**（本模块采用的那个）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块文档化 `sketch_ellipse` 一个单元。
# ─────────────────────────────────────────────────────────────────────
def sketch_ellipse(model, cx, cy, major_x, major_y, minor_x, minor_y, z=0.0):
    """在**当前草图**里画一个**整椭圆**（官方 `ISketchManager.CreateEllipse`）。

    ★ **走的正是现行入口**：`IModelDoc2.CreateEllipse` 与 `CreateEllipse2`
    **两级都已废弃**，现行是 `ISketchManager.CreateEllipse`（见来源块）。

    ⚠ **单位：毫米** —— 与同模块的 `sketch_circle` / `sketch_corner_rectangle` 一致，
    而**不是**它们 docstring 里写的"米"（那几处 docstring 与实际不符，
    见已知事实 73 的实测）。本函数按**实测**来，并在 docstring 里写明。

    :param cx, cy: 椭圆**中心**的坐标（毫米）。
    :param major_x, major_y: **长轴**上一点的坐标（毫米）—— 它到中心的距离就是长半轴。
    :param minor_x, minor_y: **短轴**上一点的坐标（毫米）—— 它到中心的距离就是短半轴。
    :param z: 草图平面内的 Z（2D 草图通常 0）。
    :returns: 椭圆对应的**草图线段**（官方返回值）。
    :raises RuntimeError: 官方**返回 `None`**（没建出来）。
    """
    seg = get_com_member(
        get_com_member(model, "SketchManager"), "CreateEllipse",
        float(cx), float(cy), float(z),
        float(major_x), float(major_y), float(z),
        float(minor_x), float(minor_y), float(z))
    if seg is None:
        raise RuntimeError(
            "ISketchManager.CreateEllipse 返回 None ⇒ 椭圆没建出来"
            "（常见原因：当前不在草图编辑态；官方说「若无活动草图则新建一个」）"
        )
    return seg
'''

if "def sketch_ellipse" not in t:
    t = t.rstrip() + "\n" + NEW
    P.write_text(t, encoding="utf-8")
    print("  ok 已追加 sketch_ellipse")
else:
    print("  已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
