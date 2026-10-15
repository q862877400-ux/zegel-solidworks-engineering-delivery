import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_part.py")
t = P.read_text(encoding="utf-8")

NEW = '''

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**不是**从四家外部 MCP 项目移植）。
# 文件:   scripts/sw_part.py —— 「中心线」这一段（2026-10-01 轮 140）。
# 定位:   补 `docs/union-gap-triage.md`「真缺」档里的 `centerline`。
# 官方依据: ① 出厂类型库反射 `iface_*.txt`：
#             `SketchSegment CreateCenterLine(Double ×6)`（在 `ISketchManager` 上）
#           ② `C:\\swapi\\types\\ISketchManager\\CreateCenterLine.md`：
#             `SketchSegment CreateCenterLine(X1, Y1, Z1, X2, Y2, Z2)` —— **6 个 double**。
#             ⚠⚠ **官方文档写「in meters」，而实测是毫米**（见已知事实 73 与
#             `tools/verify_centerline_smoke.py` 的**再测**）—— 按实测来。
#             ★ 官方 Remarks 还给了**另一条路**：「`ISketchManager::CreateLine` +
#             `ISketchSegment::ConstructionGeometry`」—— 本函数**不走那条**，
#             因为 `CreateCenterLine` 是**现行入口**且直接就是中心线。
#           ③ ⚠ **两级废弃链**（本模块**不走前两级**）：
#             `IModelDoc2.CreateCenterLine(Object,Object)`
#               ⇒ `Obsolete. Superseded by ISketchManager::CreateCenterLine.`
#             `IModelDoc2.CreateCenterLineVB(Double ×6)` —— **Void** 返回，
#               是同一件事的 VB 变体（不取返回值）。
#             ⇒ **现行入口是 `ISketchManager.CreateCenterLine`**（本函数采用的那个）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块文档化 `sketch_centerline` 一个单元。
# ─────────────────────────────────────────────────────────────────────
def sketch_centerline(model, x1, y1, x2, y2, z=0.0):
    """在**当前草图**里画一条**中心线**（官方 `ISketchManager.CreateCenterLine`）。

    ★ **走的正是现行入口**：`IModelDoc2.CreateCenterLine` **已废弃**、
    `CreateCenterLineVB` 是它的 **VB 变体**（`Void` 返回）—— 现行是
    `ISketchManager.CreateCenterLine`（见来源块）。

    ⚠ **单位：毫米**（**实测**，不是照官方文档的「meters」）——
    依据 `tools/verify_centerline_smoke.py`。同模块其余助手同此（已知事实 73）。

    :param x1, y1: 端点 1 的坐标（毫米）。
    :param x2, y2: 端点 2 的坐标（毫米）。
    :param z: 草图平面内的 Z（2D 草图通常 0）。
    :returns: 中心线对应的**草图线段**（官方返回值）。
    :raises RuntimeError: 官方**返回 `None`**（没建出来）。
    """
    seg = get_com_member(
        get_com_member(model, "SketchManager"), "CreateCenterLine",
        float(x1), float(y1), float(z), float(x2), float(y2), float(z))
    if seg is None:
        raise RuntimeError(
            "ISketchManager.CreateCenterLine 返回 None ⇒ 中心线没建出来"
            "（常见原因：当前不在草图编辑态）"
        )
    return seg
'''

if "def sketch_centerline" not in t:
    t = t.rstrip() + "\n" + NEW
    P.write_text(t, encoding="utf-8")
    print("  ok 已追加 sketch_centerline")
else:
    print("  已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
