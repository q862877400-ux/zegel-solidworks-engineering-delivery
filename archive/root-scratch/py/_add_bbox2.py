import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_part.py")
t = P.read_text(encoding="utf-8")

NEW = '''

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**不是**从四家外部 MCP 项目移植）。
# 文件:   scripts/sw_part.py —— 「边界框」这一段（2026-10-01 轮 127）。
# 定位:   补 `docs/union-gap-triage.md`「真缺」档里的 `bbox`。
# 官方依据: ① 出厂类型库反射 `iface_*.txt`：`Object GetBodyBox()`（在 `IBody2` 上）·
#             `Object GetBodies2(Int32, Boolean)`（在 `IPartDoc` 上）
#           ② `C:\\swapi\\types\\IBody2\\GetBodyBox.md`：
#             **返回 6 个 double** —— `[X1, Y1, Z1, X2, Y2, Z2]`（包围盒的**对角线两端**，
#             盒面**平行于 XYZ 轴**）。
#           ③ ⚠⚠ **同一份文档的 IMPORTANT 段**（**必须照抄给调用方看**）：
#             > The values returned are **approximate** and **should not be used for
#             > comparison or calculation purposes**. Furthermore, the bounding box
#             > **may vary after rebuilding the model**.
#           ④ 单位：与官方其它几何接口一致，是**米** ⇒ 本模块在边界处换成毫米。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件 —— ⚠ 追加在文件尾，前面已有来源块 ⇒ 用「全文件」最稳。
# ─────────────────────────────────────────────────────────────────────
def get_bounding_box(model, *, body_index: int = 0, include_hidden: bool = False):
    """取**第一个实体**的边界框（官方 `IBody2.GetBodyBox`）。

    ⚠⚠ **先把官方那句重话说在前面**（原文照抄在来源块里）：
    **返回值是「近似值」，官方明确说「不应用于比较或计算」**，
    而且**重建模型之后它可能变化**。
    ⇒ 所以本函数的返回值**只适合「给人看个大概」**，
      **不要**拿它当尺寸依据去驱动别的特征。

    :param model: 零件文档（`IPartDoc`）。
    :param body_index: 取第几个实体（0 基）。
    :param include_hidden: 是否含隐藏实体。
    :returns: `{"min": [x, y, z], "max": [...], "size": [dx, dy, dz]}` ——
        **全部是毫米**，`size` 是各轴方向的跨度。
    :raises RuntimeError: 拿不到实体，或 `GetBodyBox` 返回的元素不是 6 个。
    """
    bodies = get_com_member(model, "GetBodies2", int(body_index), bool(include_hidden))
    if not bodies:
        raise RuntimeError(
            "IPartDoc.GetBodies2(%r, %r) 没拿到实体 ⇒ 零件里可能没有实体"
            "（先建一个特征，或把 body_index 调小）" % (body_index, include_hidden)
        )
    body = bodies[0] if isinstance(bodies, (list, tuple)) else bodies
    box = get_com_member(body, "GetBodyBox")
    if box is None or len(box) != 6:
        raise RuntimeError(
            "IBody2.GetBodyBox 返回的元素不是 6 个（官方：`[X1, Y1, Z1, X2, Y2, Z2]`）"
            " ⇒ 实际 %r" % (None if box is None else len(box),)
        )
    b = [float(v) for v in box]
    mn, mx = b[:3], b[3:]
    return {
        "min": [mm(v) for v in mn],
        "max": [mm(v) for v in mx],
        "size": [mm(mx[i] - mn[i]) for i in range(3)],
    }
'''

if "def get_bounding_box" not in t:
    t = t.rstrip() + "\n" + NEW
    P.write_text(t, encoding="utf-8")
    print("  ok 已追加 get_bounding_box")
else:
    print("  已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
