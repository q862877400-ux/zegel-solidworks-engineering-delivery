"""给 `sw_selection_spec.py` 补**点 / 方向**的声明式解析器（B 类的基础设施）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks 反射）+ 本项目真机实测结论
# 文件:   `IBody2.GetBodyBox()` → 6 个 Double（xmin ymin zmin xmax ymax zmax）
#         `IModelDocExtension.GetMassProperties2(...)` → 下标 0-2 质心（已知事实 5）
#         `IBody2.GetVertices()` / `IVertex.GetPoint()` → 顶点坐标
#         `IModeler.CreateCylindricalSurface(Object, Object, Double)` 等 —— 4 个**运行期可达**
#           的曲面创建器都收 `Object` 型的点/向量（已知事实 28：14 个里只有 5 个可达）
# 定位:   T-011 分类表里 **B 类（「需声明式选择解析」）** 的基础设施。
#         那一类的函数入参含**坐标/向量**，直接暴露会**违规则 3**
#         ⇒ 对外收**声明式选择器**，内部解析成坐标。
#
#  ⚠⚠ **规则 3 的红线**：本模块**绝不**接受裸坐标选择器。
#     合法选择器只有两类：
#       ① **从模型派生**的点：`origin` / `bbox:min` / `bbox:max` / `bbox:center` / `centroid`
#       ② **命名轴**的方向：`+x` / `-x` / `+y` / `-y` / `+z` / `-z`
#     **⇒ 想指定任意坐标？那说明该走「先建参照几何」的路，而不是让 API 收坐标。**
#
#  ⚠ 形状依据（已知事实 29，真机实测）：`Object` 型的点/向量**五种包装全可用**
#    （裸 list / 裸 tuple / `VT_ARRAY|VT_R8` / `VT_ARRAY|VT_VARIANT` / 逐元素 VARIANT）
#    ⇒ 本模块**返回裸 tuple**，由 pywin32 自己转 SAFEARRAY，**不强制调用方包 VARIANT**。
#
# 官方签名依据: `IBody2.GetBodyBox()` / `IVertex.GetPoint()` / `IMassProperty2.CenterOfMass`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠ **未在本机实测**（本模块的函数）；其消费者 `sw_surface` 的 4 个创建器
#   在 `probe_surface_array_shape.py` 里测过「返回非 None」。
# ────────────────────────────────────────────────────────────────────
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**沿上游与既有模式的写法**发展而来）。
# 文件:   scripts/sw_geometry_selectors.py —— 本文件（**轮 145 的命名迁移**）。
# 定位:   2026-10-01（轮 145）**只做了一件事**：把那些「**故意要调**」的零参调用
#         从 `get_com_member(...)` 改成 **`call_com_member(...)`**。
#         ★★ 起因：审计（`tools/audit_get_com_member_semantics.py`）发现
#         `get_com_member` 的语义是「**取或调**」—— **对 COM 成员，「取」可能等于「调」**；
#         而 471 个无实参调用点里有 193 处的成员在反射里**有零参重载**（会真的执行）。
#         ★ 逐条读过之后确认：**作者大多是故意的**（拿返回值当成败 / 要的就是那个动作），
#         但**代码里读不出来** ⇒ 本轮用 `call_com_member` **让名字表态**。
# 官方签名依据: 本次迁移**不改任何 COM 调用**（只是换个名字），
#         各调用的官方依据在原函数的来源块里。
# 许可:   本仓库 MIT（上游部分见 `THIRD-PARTY-NOTICES.md`）。无第三方代码引入。
# 覆盖:   全文件 —— ⚠ 本块是**轮 145 迁移这件事**的说明，
#         它**不替代**本文件里原有的、更精确的逐函数来源块。
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

from typing import Any

try:
    from .sw_connect import get_com_member, call_com_member
    from .sw_part import _empty_callout  # noqa: F401 —— 供同模块其它函数用
except ImportError:  # pragma: no cover
    from sw_connect import get_com_member, call_com_member
    from sw_part import _empty_callout  # noqa: F401

__all__ = [
    "POINT_SELECTORS",
    "DIRECTION_SELECTORS",
    "GeometrySelectorError",
    "resolve_point",
    "resolve_direction",
    "available_point_selectors",
    "available_direction_selectors",
]

#: 合法的**点**选择器（全部**从模型派生** —— 不接受裸坐标）
POINT_SELECTORS = (
    "origin",  # 模型原点 (0,0,0)
    "bbox:min",  # 体包围盒的最小角
    "bbox:max",  # 体包围盒的最大角
    "bbox:center",  # 体包围盒中心
    "centroid",  # 质心（质量属性）
)

#: 合法的**方向**选择器（**命名轴**，不是坐标）
DIRECTION_SELECTORS = ("+x", "-x", "+y", "-y", "+z", "-z")

_AXIS = {
    "+x": (1.0, 0.0, 0.0),
    "-x": (-1.0, 0.0, 0.0),
    "+y": (0.0, 1.0, 0.0),
    "-y": (0.0, -1.0, 0.0),
    "+z": (0.0, 0.0, 1.0),
    "-z": (0.0, 0.0, -1.0),
}


class GeometrySelectorError(RuntimeError):
    """点/方向选择器非法或解析不出 —— **报错，不静默返回原点**。"""


def available_point_selectors() -> list[str]:
    """列出合法的点选择器（供工具描述与错误信息引用）。"""
    return list(POINT_SELECTORS)


def available_direction_selectors() -> list[str]:
    """列出合法的方向选择器。"""
    return list(DIRECTION_SELECTORS)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks 反射）
# 文件:   `IBody2.GetBodyBox() -> Object`（6 个 Double）
#         `IPartDoc.GetBodies2(Int32 Type, Boolean VisibleOnly) -> Object`
#         `IMassProperty2.CenterOfMass`（经 `IModelDocExtension.CreateMassProperty2`）
# 定位:   把**声明式点选择器**解析成 `(x, y, z)` 三元组（米）。
#  ⚠ **只从模型派生**，不接受裸坐标（规则 3）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数整体（自本行至函数结束）
# ⚠ **未在本机实测**
# ────────────────────────────────────────────────────────────────────
def resolve_point(model, selector: str, *, body_index: int = 0) -> tuple:
    """把**声明式点选择器**解析成 ``(x, y, z)``（**米**）。

    :param selector: 见 :data:`POINT_SELECTORS`。
    :raises GeometrySelectorError: 选择器非法，或文档里没有实体/取不到包围盒。
    """
    key = str(selector).strip().lower()
    if key not in POINT_SELECTORS:
        raise GeometrySelectorError(
            "非法的点选择器 %r；合法值：%r。"
            "⚠ **不接受裸坐标**（并入规范规则 3）—— 需要任意坐标时，请先建参照几何再选它。"
            % (selector, list(POINT_SELECTORS))
        )
    if key == "origin":
        return (0.0, 0.0, 0.0)

    bodies = get_com_member(model, "GetBodies2", 0, True)  # 0 = swSolidBody
    if not bodies:
        raise GeometrySelectorError("活动文档里没有实体（swSolidBody）—— 先建几何")
    if body_index >= len(bodies):
        raise GeometrySelectorError(
            "body_index=%d 越界（共 %d 个体）" % (body_index, len(bodies))
        )
    body = bodies[body_index]

    if key.startswith("bbox:"):
        box = get_com_member(body, "GetBodyBox")
        if not box or len(box) < 6:
            raise GeometrySelectorError("GetBodyBox 没返回 6 个数")
        xmin, ymin, zmin, xmax, ymax, zmax = (float(box[i]) for i in range(6))
        if key == "bbox:min":
            return (xmin, ymin, zmin)
        if key == "bbox:max":
            return (xmax, ymax, zmax)
        return ((xmin + xmax) / 2.0, (ymin + ymax) / 2.0, (zmin + zmax) / 2.0)

    # centroid：走质量属性（已知事实 5：CreateMassProperty2 的 CenterOfMass）
    ext = get_com_member(model, "Extension")
    mp = call_com_member(ext, "CreateMassProperty2")
    if mp is None:
        raise GeometrySelectorError("CreateMassProperty2 返回 None ⇒ 取不到质心")
    com = get_com_member(mp, "CenterOfMass")
    if not com or len(com) < 3:
        raise GeometrySelectorError("CenterOfMass 没返回 3 个数")
    return (float(com[0]), float(com[1]), float(com[2]))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（沿用 `sw_simulation.FACE_SELECTORS` 的**外法向命名**约定）
# 文件:   scripts/sw_selection_spec.py 的 resolve_direction ——
#         与 `sw_simulation.FACE_SELECTORS`（`+x`/`-x`/…）**同一套命名**，
#         避免同一个概念在两处有不同写法。
# 定位:   把**命名轴**解析成单位向量 `(dx, dy, dz)`。
#  ⚠ 只认**轴名**，不认坐标（规则 3）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数整体（自本行至函数结束）
# ⚠ **未在本机实测**（纯算术，无 COM 调用 —— 这一条的风险很低）
# ────────────────────────────────────────────────────────────────────
def resolve_direction(selector: str) -> tuple:
    """把**命名轴**解析成单位向量 ``(dx, dy, dz)``。

    :param selector: 见 :data:`DIRECTION_SELECTORS`（与 `sw_simulation.FACE_SELECTORS`
        用**同一套外法向命名**，避免同一概念两种写法）。
    :raises GeometrySelectorError: 选择器非法。
    """
    key = str(selector).strip().lower()
    if key not in _AXIS:
        raise GeometrySelectorError(
            "非法的方向选择器 %r；合法值：%r。"
            "⚠ **不接受裸向量**（并入规范规则 3）。"
            % (selector, list(DIRECTION_SELECTORS))
        )
    return _AXIS[key]
