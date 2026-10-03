"""SolidWorks 草图高级能力：几何约束、样条曲线、槽。

能力域
    域 2 · 草图

补齐的接口族（见 docs/family-coverage.md 草图域 10/14）
    ISketchRelation        13 成员 —— 几何约束对象（查询/替换实体/抑制）
    ISketchRelationManager 10 成员 —— 约束的增删查
    ISketchSpline          34 成员 —— 样条曲线
    ISketchSlot             8 成员 —— 直槽/中心点弧槽

与既有 ``scripts/sw_part.py`` 的关系
-----------------------------------
``sw_part`` 已覆盖草图的**基础实体**（直线、圆、矩形等）与选中流程。
本模块只补**约束与参数化曲线**这一层，两者互补不重叠。

⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）。
"""
from __future__ import annotations

from typing import Any

try:
    from .sw_connect import get_com_member, set_com_member
except ImportError:
    from sw_connect import get_com_member, set_com_member

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sketch_relations.py —— 本文件自身
# 定位:   模块导出清单与枚举常量。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方各函数另附更精确的来源块。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "SKETCH_CONSTRAINT_TYPES",
    "SKETCH_SLOT_CREATION_TYPES",
    "SKETCH_SLOT_LENGTH_TYPES",
    "SKETCH_RELATION_ENTITY_TYPES",
    "add_relation",
    "list_relations",
    "get_allowed_relations",
    "suppress_relation",
    "create_spline",
    "create_spline_by_points",
    "set_slot_length",
    "set_slot_width",
    "collect_relation_evidence",
]


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 枚举定义（C:\swapi 收录的 swconst）
# 文件:   C:\swapi\enums\swConstraintType_e.md
# 定位:   ISketchRelationManager.AddRelation(Object Entities, Int32 Type) 第 2 参。
# ⚑ 名称查证过程: 我先按印象写 `swSketchRelation_e`，三路确认**该枚举不存在** ——
#   ① sw_know.py enum swSketchRelation_e → [SWK_NOT_FOUND]
#   ② sw_know.py suggest SketchRelation → 只有 swSketchRelationFilterType_e /
#      swSketchRelationEntityTypes_e / swSketchFullyDefineRelationType_e，均非
#   ③ 对 SolidWorks.Interop.swconst.dll 做纯元数据反射 → NO_ENUM，候选里也没有
#   真正的枚举是 **`swConstraintType_e`**（草图几何约束的类型）。
# 取值:   官方该枚举有 100+ 项（含 3D 与角度变体）。此处**只收录草图二维场景
#         常用的核心项**，未收录的不臆造数值。
# ⚠ 官方枚举全量清单见 C:\swapi\enums\swConstraintType_e.md，需要别的类型
#   请自行查该文件，不要沿用本表的默认值。
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
SKETCH_CONSTRAINT_TYPES = {
    "coincident": 1,        # swConstraintType_COINCIDENT
    "concentric": 6,        # swConstraintType_CONCENTRIC
    "coradial": 27,         # swConstraintType_CORADIAL
    "distance": 20,          # swConstraintType_DISTANCE
    "horizontal": 19,        # swConstraintType_HORIZONTAL
    "vertical": 18,          # swConstraintType_VERTICAL
    "parallel": 9,           # swConstraintType_PARALLEL
    "perpendicular": 10,     # swConstraintType_PERPENDICULAR
    "tangent": 21,           # swConstraintType_TANGENT
    "equal": 3,              # swConstraintType_EQUAL
    "midpoint": 26,          # swConstraintType_MIDPOINT
    "intersect": 24,         # swConstraintType_INTERSECT
    "symmetric": 28,         # swConstraintType_SYMMETRIC
    "angle": 2,              # swConstraintType_ANGLE
    "fix": 34,               # swConstraintType_FIX
    "pierce": 31,            # swConstraintType_PIERCE
    "collinear": 12,         # swConstraintType_COLLINEAR
    "block": 45,             # swConstraintType_BLOCK
    "snappoint": 33,         # swConstraintType_SNAPPOINT
}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 枚举定义（C:\swapi 收录的 swconst）
# 文件:   C:\swapi\enums\swSketchSlotCreationType_e.md
#         C:\swapi\enums\swSketchSlotLengthType_e.md
#         C:\swapi\enums\swSketchRelationEntityTypes_e.md
# 定位:   槽的创建方式、长度标注方式，以及关系对象的实体类型。
# 取值:   各枚举**全量照录**（分别 3 / 2 / 6 项），未增删改。
# ⚠ swSketchSlotCenterArcDirection_e 查不到（sw_know 报 [SWK_NOT_FOUND]），
#   故槽的弧方向参数不设默认值，由调用方显式传。
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
SKETCH_SLOT_CREATION_TYPES = {
    "center_line": 1,        # swSketchSlotCreationType_center_line
    "arc": 2,                # swSketchSlotCreationType_arc
    "three_point_arc": 3,    # swSketchSlotCreationType_3pointarc
}

SKETCH_SLOT_LENGTH_TYPES = {
    "center_center": 0,      # swSketchSlotLengthType_CenterCenter
    "full_length": 1,        # swSketchSlotLengthType_FullLength
}

SKETCH_RELATION_ENTITY_TYPES = {
    "line": 3,               # swSketchRelationEntityType_Line
    "arc": 4,                # swSketchRelationEntityType_Arc
    "ellipse": 5,            # swSketchRelationEntityType_Ellipse
    "hatch": 8,              # swSketchRelationEntityType_Hatch
    "cylinder": 11,          # swSketchRelationEntityType_Cylinder
    "dimension": 14,         # swSketchRelationEntityType_Dimension
}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（SolidWorks.Interop.sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt
#           → ISketchRelationManager 段
# 定位:   草图几何约束的增删查。官方签名：
#           SketchRelation AddRelation(Object Entities, Int32 Type)  ← 2 参
#           Boolean      DeleteRelation(SketchRelation)
#           Boolean      DeleteAllRelations()
#           Object       GetRelations(Int32)              ← 1 参（实体索引）
#           Int32        GetRelationsCount(Int32)         ← 1 参
#           Object       GetAllowedRelations(Object)      ← 1 参
# ⚠ GetRelations / GetRelationsCount 的 Int32 语义（草图实体下标？）两套官方源
#   都未说明，故本模块只透传不解释。
# ⚠ 返回的 SketchRelation 上可继续查 ISketchRelation 的成员
#   （GetRelationType / GetEntities / Suppressed / ReplaceEntity）。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def _dispatch_array(entities):
    """把实体序列包成 COM 要的 **SAFEARRAY of IDispatch**（`VARIANT(VT_ARRAY|VT_DISPATCH)`）。

    ⚠⚠ **不包就调不通**（轮 161 实测）：`list` / `tuple` 都报
    `com_error 0x80010105`（「服务器出现意外情况」），而包了之后计数**真的 +1**。
    ★ 已是 `VARIANT` 的直接原样返回（调用方自己包过就别再包一层）。
    """
    import pythoncom
    from win32com.client import VARIANT
    if hasattr(entities, "varianttype"):
        return entities
    return VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, list(entities))


def add_relation(sketch, entities, constraint_type: int):
    """给草图实体添加几何约束，返回 ISketchRelation。"""
    if entities is None:
        raise ValueError("entities 为 None：须先选中要约束的草图实体")
    manager = get_com_member(sketch, "RelationManager")
    if manager is None:
        raise RuntimeError("ISketch.RelationManager 为 None：不在草图编辑态？")
    #: ⚠⚠⚠ **实测（轮 161）**：`AddRelation` 官方有**两个重载**
    #: （`SketchRelation AddRelation(Object, Int32)` 与 `Void AddRelation(String)`）——
    #: 而那个 `Object` 是 **SAFEARRAY** ⇒ **直接传 Python `list` / `tuple` 都不行**：
    #: ```
    #:   list[0:2]  ⇒ com_error 0x80010105「服务器出现意外情况」  计数 3 → 3（**没加上**）
    #:   tuple(0,1) ⇒ 同上
    #:   VARIANT(VT_ARRAY | VT_DISPATCH, [实体…]) ⇒ 无错  计数 3 → **4**（**加上了**）
    #: ```
    #: ★★★ **所以本函数此前**从没在真机上跑通过** —— 契约测试用的是**假对象**，
    #: 而假对象测不出「实参要不要包 VARIANT」（已知事实 99/101 那一族）。
    #: ⚠ 另记：那个错误码 `0x80010105` 与已知事实 28/47 的「服务器出现意外情况」同一个码 ——
    #: 本轮的形态是「**数组实参没包 VARIANT**」，与那两条（`CreateBsplineSurface` /
    #: `AccessSelections`）**不同因同码**，报错本身看不出是哪一种。
    relation = get_com_member(manager, "AddRelation",
                              _dispatch_array(entities), int(constraint_type))
    if relation is None:
        raise RuntimeError(
            f"AddRelation({constraint_type}) 未返回约束对象："
            "常见原因为选区实体数与该约束类型不匹配"
        )
    return relation


def list_relations(sketch, entity_index: int = 0):
    """列出与指定实体相关的约束。"""
    manager = get_com_member(sketch, "RelationManager")
    if manager is None:
        return []
    return get_com_member(manager, "GetRelations", int(entity_index)) or []


def get_allowed_relations(sketch, entity):
    """查询官方允许对该实体施加哪些约束（用于避免盲目试错）。"""
    manager = get_com_member(sketch, "RelationManager")
    if manager is None:
        return []
    return get_com_member(manager, "GetAllowedRelations", entity) or []


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → ISketchRelation 段
# 定位:   约束对象的抑制开关。官方签名：``Boolean set_Suppressed(Boolean)``
#           —— 是**属性**（setter），不是方法。
# ⚠ 迟到绑定下 Suppressed 是属性，加括号调用会 TypeError
#   （见 AGENTS.md §六 事实 4）。故本函数用单参数赋值而不是 ``(True)``。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def suppress_relation(relation, suppressed: bool = True):
    """抑制 / 取消抑制一个约束。"""
    if relation is None:
        raise ValueError("relation 为 None")
    set_com_member(relation, "Suppressed", bool(suppressed))
    return relation


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → ISketchManager 段
# 定位:   样条曲线创建。官方签名（按参数个数从小到大）：
#           SketchSegment CreateSpline(Object Points)                     ← 1 参
#           SketchSegment CreateSpline2(Object Points, Boolean Simulate)  ← 2 参
#           Object        CreateSpline3(Object, Object, Object, Boolean, Object&)
#                         ← 4 参 + 1 个 by-ref 出参
#           SketchSpline  CreateEquationSpline(String, Double, Double,
#                         Boolean, Double, Double, Double, Boolean, Boolean)
#           SplineParamData CreateSplineParamData()
# ⚠ CreateSpline3 末位是 by-ref 出参，迟到绑定下不保证回写；
#   本模块只提供 1 参与 2 参版本，不碰带 by-ref 的 CreateSpline3。
# ⚠ CreateSpline 第一个参数的期望类型（点数组 SAFEARRAY）两套官方源都未细说，
#   按上游 sw_hole_features / sw_part 既有惯例由调用方构造 VARIANT SAFEARRAY。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_spline(sketch_manager, points, simulate: bool = False):
    """由点集创建样条曲线。

    :param points: 控制点 —— **两种写法都收**：
        · **扁平序列** `[x0,y0,z0, x1,y1,z1, …]`（官方 Remarks 的原话就是这种形态）
        · **点对序列** `[(x,y,z), (x,y,z), …]`（调用方更自然的写法，**本函数负责摊平**）
    :param simulate: 官方 `CreateSpline2` 的 `SimulateNaturalEnds`（模拟自然端）。
    :returns: 官方返回的 `SketchSegment`。

    ⚠⚠⚠ **2026-10-01（轮 183）修掉一处「实参形态」缺陷 —— 此前它**建不出样条****：
    ```
      tools/probe_spline_forms.py 在**新零件**上逐个形态试，**每次回读草图段数**：
        ① 扁平 list                    ⇒ 段数 0 → 0（没变）· 返回 None
        ② 扁平 tuple                   ⇒ 段数 0 → 0（没变）· 返回 None
        ③ **VARIANT(VT_ARRAY|VT_R8)**  ⇒ 段数 **0 → 1（变了 ✚）**  ★★★ **成了**
        ④ list of tuples（**本函数此前的写法**）⇒ 段数 0 → 0（没变）· 返回 None
    ```
    ⇒ ★★★ **官方 Remarks 只说 "array of X,Y,Z point coordinates"，没说「要包 VARIANT」**
      ⇒ 而我们传 list/tuple 时它**静默返回 `None`**（**不是报错**）。
    ⇒ ★★ 与**已知事实 167**（`ISketchRelationManager.AddRelation` 必须包
      `VARIANT(VT_ARRAY|VT_DISPATCH)`）**完全同一族**：**数组实参必须包 VARIANT**。
    ★ 所以本函数现在**自己摊平 + 包 `VARIANT(VT_ARRAY | VT_R8)`**。
    """
    if points is None:
        raise ValueError("points 为 None：须提供样条控制点数组")
    #: ★ 摊平：既收 [(x,y,z), …] 也收 [x,y,z, x,y,z, …]
    seq = list(points)
    if seq and isinstance(seq[0], (list, tuple)):
        flat: list = []
        for p in seq:
            flat.extend(float(v) for v in p)
    else:
        flat = [float(v) for v in seq]
    if len(flat) < 6:
        raise ValueError(
            "控制点太少：官方 Remarks 要求**至少两组 X,Y,Z**（6 个数），收到 %d 个" % len(flat))
    import pythoncom
    import win32com.client
    #: ★★★ **必须包 VARIANT(VT_ARRAY | VT_R8)** —— 裸 list/tuple 会**静默返回 None**（轮 183 实测）
    data = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, flat)
    #: ⚠⚠⚠ **2026-10-01（轮 183）再修一处**：**默认走 `CreateSpline2`，不碰 `CreateSpline`**。
    #: 理由（真机实测 + 官方）：
    #: ```
    #:   · 官方 md：`CreateSpline` **Obsolete. Superseded by ISketchManager::CreateSpline2.**
    #:   · 真机：`getattr(sketch_manager, "CreateSpline")` ⇒ **None**
    #:     ⇒ 走它会在 `get_com_member` 里报 `TypeError: 'NoneType' object is not callable`
    #:       （⚠ 错误信息**指不出真因** —— 又是"报错看不出病因"那一族）
    #:   · 而 `CreateSpline2` **取得到、也建得出**（段数 0 → 1）✓
    #: ```
    #: ⇒ ★ 因为 `CreateSpline` **用不了**，「不 simulate」也**只能**走 `CreateSpline2` + `False`。
    return get_com_member(sketch_manager, "CreateSpline2", data, bool(simulate))


def create_spline_by_points(sketch_manager, points, simulate: bool = False):
    """``create_spline`` 的别名入口，语义更明确（由点创建）。"""
    return create_spline(sketch_manager, points, simulate=simulate)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → ISketchSlot 段
# 定位:   槽的尺寸调整。官方签名（全部是**属性**）：
#           Void set_Length(Double) / get_Length()
#           Void set_Width(Double)  / get_Width()
#           Void set_LengthType(Int32) / get_LengthType()
#           Int32 get_CreationType() / get_CenterArcDirection()
#           MathPoint GetCenterPoint() / GetCenterPointHandle()
#           Object  GetSlotPoints()
# ⚑ 名称歧义提示: Length / Width / LengthType 都是**属性**（setter 形式），
#   不是方法。迟到绑定下 ``slot.Length(0.1)`` 会 TypeError。
# ⚠ 槽的创建入口是 ISketchManager.CreateSketchSlot，共 **14 个参数**
#   （2 个 Int32 类型位 + 11 个 Double + 1 个 Int32 + 1 个 Boolean），
#   官方未逐项说明各 Double 的语义，故本模块**不提供创建封装**，
#   只提供已建构槽的尺寸调整；创建请按官方 14 参签名自行组装。
# ⚠ swSketchSlotCenterArcDirection_e 查不到，故方向参数不设默认值。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def set_slot_length(slot, length: float, length_type: int | None = None):
    """设置槽长。``length_type`` 见 SKETCH_SLOT_LENGTH_TYPES。"""
    if slot is None:
        raise ValueError("slot 为 None：须先创建槽")
    set_com_member(slot, "Length", float(length))
    if length_type is not None:
        set_com_member(slot, "LengthType", int(length_type))
    return slot


def set_slot_width(slot, width: float):
    """设置槽宽。"""
    if slot is None:
        raise ValueError("slot 为 None：须先创建槽")
    set_com_member(slot, "Width", float(width))
    return slot


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（scripts/sw_review.py 的证据回读）
# 定位:   约束证据回读，沿用「只取已核实成员、不臆造方法」的写法。
#         读取的成员全部是 ISketchRelation 上确认为 Int32/Boolean 的那些。
# ⚠ GetRelationType() 的返回值**具体含义查不到**（取值域未在两套源里给全），
#   故原样透出为数字，不翻译成名字。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def collect_relation_evidence(sketch, entity_index: int = 0) -> dict[str, Any]:
    """回读草图约束情况，形成可审计证据。"""
    manager = get_com_member(sketch, "RelationManager")
    if manager is None:
        return {"has_relation_manager": False, "relations": []}
    relations = list_relations(sketch, entity_index) or []
    rows = []
    for relation in relations:
        rows.append({
            "type_id": int(get_com_member(relation, "GetRelationType") or -1),
            "entities_count": int(get_com_member(relation, "GetEntitiesCount") or 0),
            "suppressed": bool(get_com_member(relation, "Suppressed")),
        })
    return {
        "has_relation_manager": True,
        "total_relations": int(
            get_com_member(manager, "GetRelationsCount", int(entity_index)) or 0
        ),
        "relations": rows,
    }


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（SolidWorks.Interop.sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → ISketchSpline 段
# 定位:   样条曲线的查询与控制点编辑（草图域最后一个未触及族，42 成员）。
#         官方签名（本模块用到的部分）：
#             Int32        get_CurveDegree() / get_CurveType() / GetPointCount()
#             Object       GetPoints() / GetControlVertexWeights()
#             Boolean      DeletePoint(SketchPoint)
#             SplineHandle AddTangencyControl(Double, Double, Double)
#             SplineHandle AddCurvatureControl(Double, Double, Double)
#             Boolean      get_ShowSplineHandles() / get_ShowInflectionPoints() /
#                          get_ShowMinimumRadius() / get_ShowCurvatureCombs()
#         创建侧见本文件上方的 create_spline（ISketchManager.CreateSpline/2）。
# ⚠ GetEquationParameters / GetEquationParameters2 全部是 by-ref 出参
#   （前者 9 个、后者 12 个），迟到绑定下不保证回写，
#   故本模块**不提供**其封装，也不臆造输出缓冲的分配方式。
# ⚠ CurveType / CurveDegree 的取值含义未逐项说明，原样透出数字不翻译。
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_spline_points(spline):
    """取样条的控制点数组。"""
    if spline is None:
        raise ValueError("spline 为 None：须先由 create_spline 得到")
    return get_com_member(spline, "GetPoints")


def delete_spline_point(spline, point):
    """删除样条的一个控制点。"""
    if spline is None:
        raise ValueError("spline 为 None")
    return bool(get_com_member(spline, "DeletePoint", point))


def add_spline_tangency(spline, x: float, y: float, z: float):
    """给样条加相切控制。"""
    if spline is None:
        raise ValueError("spline 为 None")
    return get_com_member(spline, "AddTangencyControl",
                          float(x), float(y), float(z))


def add_spline_curvature(spline, x: float, y: float, z: float):
    """给样条加曲率控制。"""
    if spline is None:
        raise ValueError("spline is None")
    return get_com_member(spline, "AddCurvatureControl",
                          float(x), float(y), float(z))


def collect_spline_evidence(spline) -> dict[str, Any]:
    """回读样条曲线的结构信息，形成可审计证据。"""
    if spline is None:
        raise ValueError("spline 为 None")
    points = get_com_member(spline, "GetPoints")
    return {
        "curve_degree": int(get_com_member(spline, "CurveDegree") or -1),
        "curve_type": int(get_com_member(spline, "CurveType") or -1),
        "point_count": int(get_com_member(spline, "GetPointCount") or 0),
        "points_seen": len(points) if isinstance(points, (list, tuple)) else 0,
        "is_rational": bool(get_com_member(spline, "IsRationalCurve")),
        "is_style_spline": bool(get_com_member(spline, "IsStyleSpline")),
        "show_handles": bool(get_com_member(spline, "ShowSplineHandles")),
    }
