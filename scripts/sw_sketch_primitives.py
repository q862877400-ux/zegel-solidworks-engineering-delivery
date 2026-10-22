"""★ 草图图元包装（B1 批）：3点矩形 / 平行四边形 / 切线弧 / 3点圆弧 / 部分椭圆 / 抛物线 / 圆锥 / 周边圆。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力实现）
# 文件:   scripts/sw_sketch_primitives.py
# 定位:   ★ 2026-10-03（轮 464）★ `specs/201-toolbar-gaps` 的 **B1 批**。
# ★★ 起因：用户贴草图工具条截图逐条问「能/不能」，这 9 个当时全答「不能」（本仓无入口）
# ；
#     随后要求「把这些不能实现的都攻关好」。
#   ★★★ **签名三源互证（铁律 4）**：本模块每个成员的**精确签名**都取自
#     `C:\swapi\types\ISketchManager\<成员>.md`（★ 结构化官方源，逐条读过），
#     参数顺序与类型**照抄**，不凭记忆：
#     ```
#     Create3PointCornerRectangle(X1,Y1,Z1, X2,Y2,Z2, X3,Y3,Z3) -> object
#     Create3PointCenterRectangle(X1,Y1,Z1, X2,Y2,Z2, X3,Y3,Z3) -> object
#     CreateParallelogram       (X1,Y1,Z1, X2,Y2,Z2, X3,Y3,Z3) -> object
#     CreateTangentArc          (X1,Y1,Z1, X2,Y2,Z2, ArcType:int) -> SketchSegment
#     Create3PointArc           (X1,Y1,Z1, X2,Y2,Z2, X3,Y3,Z3) -> SketchSegment
#     CreateEllipticalArc       (XC,YC,Zc, XMajor,YMajor,ZMajor, XMinor,YMinor,ZMinor,
#                                X1,Y1,Z1, X2,Y2,Z2, Direction:short) -> SketchSegment
# CreateParabola            (XFocus,YFocus,ZFocus, XApex,YApex,ZApex, X1,Y1,Z1, X2,Y2,Z2
# ) -> SketchSegment
# CreateConic               (XFocus,YFocus,ZFocus, XApex,YApex,ZApex, X1,Y1,Z1, X2,Y2,Z2
# ) -> SketchSegment
#     PerimeterCircle           (X1,Y1, X2,Y2, X3,Y3) -> object     ★ 注意：**没有 Z**
#     ```
# ⚠ **单位**：一律**毫米**，与本仓 `sw_part.sketch_*` 那族一致（★ 不是官方文档里那个"米"
# ，
#     见已知事实 73 的实测）。★ 换算只在**工具层**边界做一次（规则 2）。
# ⚠ **返回值**：官方这族里 `Create3Point*` / `CreateParallelogram` / `PerimeterCircle`
# 声明回
#     `System.object`，其余回 `SketchSegment`。★ 本模块**对 `None` 一律抛** ——
# ★ 因为"建了但返回 None"与"没建"在调用方看来是同一种失败（事实 40 的教训：让失败可见）
# 。
# 官方依据: `C:\swapi\types\ISketchManager\*.md`（9 个成员，逐条读签名）。
# 许可:   本仓库 MIT。无第三方代码引入（★ 全部按官方签名自建）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 每个函数在**返回值非 None** 之外，还要由调用方回读**草图实体计数**（规则 6）
# 。

from __future__ import annotations

_MM_TO_M = 1.0 / 1000.0  #: ★ 毫米 → 米（事实 2 的换算口径）

import sys  # noqa: E402
from pathlib import Path  # noqa: E402

_HERE = Path(__file__).resolve()
for _p in (_HERE.parent, _HERE.parent.parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from sw_connect import get_com_member  # noqa: E402

#: ★ 长度换算助手：`_f(v)` = 先收窄成 float、再**毫米→米**（恰好一次）。
#: ★★ 依据（定案）：`output/probe-unit-decisive/decisive.json` —— 同文档同会话单变量：
#:   草图 40×40 回读 `[40,40,0]` ✓ 而 `extrude_boss(20.0)` 回读 Z = **20000 mm**
#:   ⇒ COM 吃**米**，用户传毫米 ⇒ 进 COM 前必须换算恰好一次。
#: ⚠ 用单 token 替换（`float(` → `_f(`）落地，避免括号配对出错（事实 61）。
_f = lambda v: v * _MM_TO_M  # noqa: E731


def _sm(model):
    """⇒ 当前文档的 `ISketchManager`；★ 拿不到就抛（不静默）。"""
    mgr = get_com_member(model, "SketchManager")
    if mgr is None:
        raise RuntimeError("取不到 ISketchManager（model 为 None 或文档不可用）")
    return mgr


def _need(seg, member: str, why: str = ""):
    """★ 官方回 `None` ⇒ **抛**（★ 事实 40 的教训：让失败可见，别让调用方以为是"建了但空"）。"""
    if seg is None:
        raise RuntimeError(
            "%s 返回 None ⇒ 图元没建出来（常见原因：当前不在草图编辑态%s）"
            % (member, ("；" + why) if why else "")
        )
    return seg


def sketch_3point_corner_rectangle(model, x1, y1, x2, y2, x3, y3):
    """★ 3 点边角矩形：`Create3PointCornerRectangle`（三点定一个**任意角度**的矩形）。"""
    return _need(
        get_com_member(
            _sm(model),
            "Create3PointCornerRectangle",
            _f(x1),
            _f(y1),
            0.0,
            _f(x2),
            _f(y2),
            0.0,
            _f(x3),
            _f(y3),
            0.0,
        ),
        "Create3PointCornerRectangle",
    )


def sketch_3point_center_rectangle(model, x1, y1, x2, y2, x3, y3):
    """★ 3 点中心矩形：`Create3PointCenterRectangle`（★ 第一点是**中心**）。"""
    return _need(
        get_com_member(
            _sm(model),
            "Create3PointCenterRectangle",
            _f(x1),
            _f(y1),
            0.0,
            _f(x2),
            _f(y2),
            0.0,
            _f(x3),
            _f(y3),
            0.0,
        ),
        "Create3PointCenterRectangle",
    )


def sketch_parallelogram(model, x1, y1, x2, y2, x3, y3):
    """★ 平行四边形：`CreateParallelogram`（三点：一角 + 两条邻边的端点）。"""
    return _need(
        get_com_member(
            _sm(model),
            "CreateParallelogram",
            _f(x1),
            _f(y1),
            0.0,
            _f(x2),
            _f(y2),
            0.0,
            _f(x3),
            _f(y3),
            0.0,
        ),
        "CreateParallelogram",
    )


def sketch_tangent_arc(model, x1, y1, x2, y2, arc_type=1):
    """★ 切线弧：`CreateTangentArc`（★ 与**上一条**草图线段相切）。

    :param arc_type: 官方的 `ArcType`（int）。★ 取值表在 `C:\\swapi` 里我没查到，
        ⇒ 默认 1（★ **标注为未核实**，按铁律 5 不假装知道）。
    """
    return _need(
        get_com_member(
            _sm(model),
            "CreateTangentArc",
            _f(x1),
            _f(y1),
            0.0,
            _f(x2),
            _f(y2),
            0.0,
            int(arc_type),
        ),
        "CreateTangentArc",
        "★ 切线弧要求草图上**已有**一条线段可供相切",
    )


def sketch_3point_arc(model, x1, y1, x2, y2, x3, y3):
    """★ 3 点圆弧：`Create3PointArc`（起点 / 终点 / 弧上一点）。"""
    return _need(
        get_com_member(
            _sm(model),
            "Create3PointArc",
            _f(x1),
            _f(y1),
            0.0,
            _f(x2),
            _f(y2),
            0.0,
            _f(x3),
            _f(y3),
            0.0,
        ),
        "Create3PointArc",
    )


def sketch_elliptical_arc(
    model, cx, cy, major_x, major_y, minor_x, minor_y, x1, y1, x2, y2, direction=1
):
    """★ 部分椭圆：`CreateEllipticalArc`（★ 中心 + 长短轴点 + 起终点 + 方向）。"""
    return _need(
        get_com_member(
            _sm(model),
            "CreateEllipticalArc",
            _f(cx),
            _f(cy),
            0.0,
            _f(major_x),
            _f(major_y),
            0.0,
            _f(minor_x),
            _f(minor_y),
            0.0,
            _f(x1),
            _f(y1),
            0.0,
            _f(x2),
            _f(y2),
            0.0,
            int(direction),
        ),
        "CreateEllipticalArc",
    )


def sketch_parabola(model, fx, fy, ax, ay, x1, y1, x2, y2):
    """★ 抛物线：`CreateParabola`（焦点 + 顶点 + 两点定端点）。"""
    return _need(
        get_com_member(
            _sm(model),
            "CreateParabola",
            _f(fx),
            _f(fy),
            0.0,
            _f(ax),
            _f(ay),
            0.0,
            _f(x1),
            _f(y1),
            0.0,
            _f(x2),
            _f(y2),
            0.0,
        ),
        "CreateParabola",
    )


def sketch_conic(model, fx, fy, ax, ay, x1, y1, x2, y2):
    """★ 圆锥曲线：`CreateConic`（★ 官方签名与 `CreateParabola` **同形**）。"""
    return _need(
        get_com_member(
            _sm(model),
            "CreateConic",
            _f(fx),
            _f(fy),
            0.0,
            _f(ax),
            _f(ay),
            0.0,
            _f(x1),
            _f(y1),
            0.0,
            _f(x2),
            _f(y2),
            0.0,
        ),
        "CreateConic",
    )


def sketch_perimeter_circle(model, x1, y1, x2, y2, x3, y3):
    """★ 周边圆：`PerimeterCircle`（★ 官方签名**只有 6 个参数 —— 没有 Z**）。"""
    return _need(
        get_com_member(
            _sm(model),
            "PerimeterCircle",
            _f(x1),
            _f(y1),
            _f(x2),
            _f(y2),
            _f(x3),
            _f(y3),
        ),
        "PerimeterCircle",
    )


#: ★ B1 批的成员清单（★ 供探针与门禁按名单跑，不遍历）
B1_MEMBERS = (
    "sketch_3point_corner_rectangle",
    "sketch_3point_center_rectangle",
    "sketch_parallelogram",
    "sketch_tangent_arc",
    "sketch_3point_arc",
    "sketch_elliptical_arc",
    "sketch_parabola",
    "sketch_conic",
    "sketch_perimeter_circle",
)
