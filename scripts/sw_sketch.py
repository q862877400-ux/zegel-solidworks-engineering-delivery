"""SolidWorks 草图查询与设置：ISketch 完整封装。

能力域
    域 2 · 草图

与既有代码的关系
----------------
``scripts/sketch_relations.py``（本任务新增）已补齐**约束**那一层
（ISketchRelation / ISketchRelationManager）。
本模块补的是**草图对象本身**——遍历里面的线/弧/圆/样条/点/轮廓、
读写模型↔草图坐标变换、草图尺寸属性、3D 草图判定。

为什么值得单独做
----------------
上游代码要拿「草图里有哪些线」只能自己写循环去猜
（``GetSketchSegments`` 一把抓全部，然后按类型过滤）；
官方其实给了**按类型分列**的十余个取法（GetLines / GetArcs / GetEllipses /
GetSplines / GetSketchPoints / GetContourEdges …），直接用既快又不会漏。

签名来源
--------
    D:\\AI\\SW\\_raw\\reflect_sldworks\\iface_sldworks.txt → ISketch 段
      —— 对 SolidWorks.Interop.sldworks.dll 的**纯元数据反射**
         （AGENTS.md §四.1③）。该段共 108 个成员。

⚠ 刻意不提供的
--------------
1. **``I*`` 前缀的成员**（``IGetArcs`` 之类）—— COM 内部分发口，不给调用方。
2. **``GetSplineParams*``** —— 四个重载里三个返回 ``Object``（SAFEARRAY），
   一个返回 ``SplineParamData`` coclass；官方无文档说明各重载差别，
   而 SAFEARRAY 的构造/读取规则两套源都查不到 ⇒ **不封装**，
   只在文档里列出它们的存在。
3. **``SetWorkingPlaneOrientation``（12 个 Double）** —— 参数语义无文档，
   照封装等于猜 ⇒ 不封装。

⚠ 多数取法返回 ``Object``（SAFEARRAY），本模块**原样透传**，
  不代为转成 list（转换会丢失 pywin32 的类型信息，且官方未定义元素顺序保证）。
  需要 list 时用 :func:`as_sequence`。

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
# 文件:   scripts/sw_sketch.py —— 本文件自身
# 定位:   模块导出清单与分类型取法表。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方各函数另附更精确的来源块。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "SKETCH_GETTERS",
    "SKETCH_SIMPLE_METHODS",
    "SKETCH_UNWRAPPED",
    "as_sequence",
    "get_sketch_segments",
    "get_lines",
    "get_arcs",
    "get_ellipses",
    "get_parabolas",
    "get_polylines",
    "get_splines",
    "get_sketch_points",
    "get_user_points",
    "get_contour_edges",
    "get_sketch_contours",
    "get_sketch_regions",
    "get_sketch_hatches",
    "get_sketch_slots",
    "get_sketch_pictures",
    "get_sketch_paths",
    "get_sketch_block_instances",
    "get_relation_manager",
    "is_3d_sketch",
    "get_model_to_sketch_transform",
    "set_model_to_sketch_transform",
    "set_automatic_solve",
    "merge_points",
    "collect_sketch_evidence",
    #: ★ 2026-10-01 轮 222（砌墙 W1）：**只回读数的薄函数** + **按名取草图**。
    "sketch_by_name",
    "resolve_sketch",
    "count_lines",
    "count_arcs",
    "count_segments",
]

#: `swCrossHatchFilter_e` 的成员（**两源一致**：出厂反射 `enum_values_sldworks.txt`
#: + `C:\\swapi\\enums\\swCrossHatchFilter_e.md`）。
#: ⚠ swapi 只列了其中 3 个（`Include/Exclude/AndExplodeOnly`），**值相同**，无冲突。
#: 反射里还有 `swCrossHatchOnly = 2` · `swSolidHatchOnly = 4`。
SKETCH_CROSS_HATCH = {
    "include": 0,               # swCrossHatchInclude（**本模块默认**）
    "exclude": 1,               # swCrossHatchExclude
    "only": 2,                  # swCrossHatchOnly
    "and_explode_only": 3,      # swCrossHatchAndExplodeOnly
    "solid_hatch_only": 4,      # swSolidHatchOnly
}

#: ISketch 上「按类型分列」的取法 —— 官方给了十余个，比一把抓再过滤更可靠。
#: ⚠⚠ **2026-10-01（轮 111）改：元组里把官方**后继**排在前面**。
#:   起因：`029` 的废弃成员台账查出本模块在调 **6 个官方已标 `Obsolete`** 的取法
#:   （`GetLines` / `GetArcs` / `GetEllipses` / `GetParabolas` / `GetSketchPoints` / `GetUserPoints`）。
#:   ⇒ 改用后继；**旧名保留在元组里**（调用方需要时可自取，且便于对照）。
#:   ⚠ 5 个后继是**零参直接可换**；**只有 `GetLines2(Int16)` 多一个参数**
#:   （`swCrossHatchFilter_e`，见 `SKETCH_CROSS_HATCH`）。
SKETCH_GETTERS: dict[str, tuple[str, ...]] = {
    "segments": ("GetSketchSegments",),
    "lines": ("GetLines2", "GetLines"),
    "arcs": ("GetArcs2", "GetArcs"),
    "ellipses": ("GetEllipses3", "GetEllipses2", "GetEllipses"),
    "parabolas": ("GetParabolas2", "GetParabolas"),
    "polylines": ("GetPolylines",),
    "splines": ("GetSplines", "GetSplinesInterpolate"),
    "points": ("GetSketchPoints2", "GetSketchPoints"),
    "user_points": ("GetUserPoints2", "GetUserPoints"),
    "contours": ("GetSketchContours",),
    "regions": ("GetSketchRegions",),
    "hatches": ("GetSketchHatches",),
    "slots": ("GetSketchSlots",),
    "pictures": ("GetSketchPictures",),
    "paths": ("GetSketchPaths",),
    "blocks": ("GetSketchBlockInstances",),
    "text": ("GetSketchTextSegments",),
}

#: 少量非零参的便捷方法
SKETCH_SIMPLE_METHODS: dict[str, int] = {
    "MergePoints": 1,
    "SetAutomaticSolve": 1,
    "SetSketchEditable": 1,
    "SetDetachSegmentOnDrag": 1,
    "GetContourEdges": 1,
    "GetSplineParams3": 1,
}

#: 刻意**不封装**的成员（附理由，勿当成遗漏）
SKETCH_UNWRAPPED: dict[str, str] = {
    "GetSplineParams": "返回 SAFEARRAY，官方无文档说明元素顺序；"
                       "构造/读取规则两套源都查不到",
    "GetSplineParams2": "返回 SAFEARRAY，官方无文档说明与 1 号重载的差别；"
                        "构造/读取规则两套源都查不到",
    "GetSplineParams3": "返回 SAFEARRAY，且带一个语义未注明的 Boolean 参数",
    "GetSplineParams4": "返回 SplineParamData coclass；官方无文档说明与前三个的关系",
    "SetWorkingPlaneOrientation": "12 个 Double，参数语义无文档；照封装等于猜",
    "AutoTraceSketchPicture": "语义与前置条件无文档",
}


def _require(sketch):
    if sketch is None:
        raise ValueError("sketch 为 None")
    return sketch


def as_sequence(value) -> list[Any]:
    """把官方返回的 SAFEARRAY 转成 list。

    ⚠ 转换**只保证拿到元素**，不保证顺序 —— 官方未定义 SAFEARRAY 的顺序保证。
    需要按类型过滤请用 :data:`SKETCH_GETTERS` 里的分类型取法，别用这个。
    """
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    try:
        return list(value)
    except TypeError:
        return [value]


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks interop 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → ISketch 段
# 定位:   按类型分列的取法。官方签名逐条照抄（**全部是零参**，返回 Object）：
#     Object GetSketchSegments() / GetSketchContours() / GetSketchRegions() /
#            GetSketchHatches() / GetSketchSlots() / GetSketchPictures() /
#            GetSketchPaths() / GetSketchBlockInstances() / GetSketchTextSegments()
#     Object GetLines() / GetArcs() / GetArcs2() / GetEllipses() / GetEllipses2() /
#            GetEllipses3() / GetParabolas() / GetParabolas2() / GetPolylines() /
#            GetSplines() / GetSplinesInterpolate() /
#            GetSketchPoints() / GetSketchPoints2() /
#            GetUserPoints() / GetUserPoints2()
#     Object GetContourEdges(Object Contour)                    ← **1 参**
# ⚑ 同一类型常有 2–3 个重载（GetArcs / GetArcs2、GetEllipses{,2,3}），
#   官方未说明差别 ⇒ 本模块**默认取第一个**（最基础的那个），
#   其它重载留在 SKETCH_GETTERS 的元组里，调用方需要时可自取。
#   **不替调用方决定「哪个对」**。
# 覆盖:   后续同级定义
# ⚑ **本组已于 2026-10-01（轮 117）真机实测** —— python tools/verify_sketch_getters_smoke.py
#   （**17/17**）：新零件 → 进草图 → 画 **1 条线 + 1 段弧** → 逐个调取法 → 退草图 → 关件不保存。
#   ★ 交叉验证：get_sketch_segments 返回 **2**（线+弧）· get_lines 返回 **12** 个浮点 ·
#     get_arcs 返回 **16** · get_sketch_points 返回 **5**；**收尾无残留模态框**。
#   ★ 这也**验证了轮 111（030）那次替换**：6 个后继（含唯一带参的 GetLines2）真机可调。
#   ⚠ 只证「没抛异常 + 元素数合理」，**不证元素内容/顺序正确**。
# ────────────────────────────────────────────────────────────────────
def get_sketch_segments(sketch) -> list[Any]:
    """草图里全部线段。"""
    _require(sketch)
    return as_sequence(get_com_member(sketch, "GetSketchSegments"))


def get_lines(sketch) -> list[Any]:
    """⚠⚠ **返回的是「数值数组」，不是「线对象列表」** —— 实测（2026-10-01 轮 140）。

    ★★ **实测语义**（`tools/probe_getlines_count.py`，真机 SW 2026 SP4.1）：

        | 草图里有几条直线 | `get_sketch_segments` | `get_lines` |
        |---|---|---|
        | 1 | 1 | **12** 个 `float` |
        | 2 | 2 | **24** |
        | 3 | 3 | **36** |

    ⇒ **每条直线占 12 个 `float`**（`get_lines(...)[0]` 的类型是 `float`，不是 `Dispatch`）
    ⇒ **不能**把结果当线对象用（没有 `.X` / `.GetStartPoint2`）。
    ⚠ **要「几条线」用 `get_sketch_segments(sketch)` 再按类型筛**；
    要「线的几何」用 `ISketchSegment` 上的方法（本模块另有包装）。

    ⚑ 2026-10-01（轮 111）：改用**后继** `GetLines2(swCrossHatchFilter_e)` ——
    官方已把 `GetLines` 标 **Obsolete**（见 `docs/obsolete-member-candidates.md`）。
    ⚠ 它是**唯一多一个参数**的后继：默认 `swCrossHatchInclude`（含剖面线），
    与旧 `GetLines()` 的「都取」语义一致。
    ⚠ 这条「12 个 float / 条」是**实测**的，**官方文档没写**返回结构。
    """
    _require(sketch)
    return as_sequence(get_com_member(sketch, "GetLines2",
                                      int(SKETCH_CROSS_HATCH["include"])))


def get_arcs(sketch) -> list[Any]:
    """圆弧。

    ⚑ 2026-10-01（轮 111）：改用**后继** `GetArcs2()`（官方已标 `GetArcs` Obsolete）。
    ⚠ 后继是**零参**，形状与旧的一致（都是 `Object`）。
    
    ⚠⚠ **返回的是「数值数组」，不是「对象列表」** —— 实测（2026-10-01 轮 141，
    `tools/probe_sketch_getter_shapes.py`，真机 SW 2026 SP4.1）：

    | 取法 | 画 1 个 | 画 2 个 | 每个占几个 `float` |
    |---|---|---|---|
    | `get_lines` | 12 | 24 | **12** |
    | `get_arcs` | 16 | 32 | **16** |
    | `get_ellipses` | 22 | 44 | **22** |

    ⇒ ★ 这三条**都是数值数组**（元素类型 `float`）。
    ⚠⚠ **2026-10-01（轮 142）更正**：此处原写「`get_*` 系列**都**返回数值数组」——**那是错的**。
    实测 `get_sketch_slots`（**1**/个）与 `get_sketch_points`（**2**/线）返回的是**对象列表**
    （元素 `CDispatch`）⇒ ★ **两种形状都有**。★ 规律**候选**（⚠ n=5，当假设不当定则）：
    **曲线类 ⇒ 数值数组；点/实体类 ⇒ 对象列表**。
    ⚠ **要「几个实体」用 `get_sketch_segments(sketch)`**；⚠ 官方文档**没写**这个返回结构。
"""
    _require(sketch)
    return as_sequence(get_com_member(sketch, "GetArcs2"))


def get_ellipses(sketch) -> list[Any]:
    """椭圆 / 样条圆。

    ⚑ 2026-10-01（轮 111）：改用**后继** `GetEllipses3()`（旧名 `GetEllipses` 已 Obsolete）。
    
    ⚠⚠ **返回的是「数值数组」，不是「对象列表」** —— 实测（2026-10-01 轮 141，
    `tools/probe_sketch_getter_shapes.py`，真机 SW 2026 SP4.1）：

    | 取法 | 画 1 个 | 画 2 个 | 每个占几个 `float` |
    |---|---|---|---|
    | `get_lines` | 12 | 24 | **12** |
    | `get_arcs` | 16 | 32 | **16** |
    | `get_ellipses` | 22 | 44 | **22** |

    ⇒ ★ 这三条**都是数值数组**（元素类型 `float`）。
    ⚠⚠ **2026-10-01（轮 142）更正**：此处原写「`get_*` 系列**都**返回数值数组」——**那是错的**。
    实测 `get_sketch_slots`（**1**/个）与 `get_sketch_points`（**2**/线）返回的是**对象列表**
    （元素 `CDispatch`）⇒ ★ **两种形状都有**。★ 规律**候选**（⚠ n=5，当假设不当定则）：
    **曲线类 ⇒ 数值数组；点/实体类 ⇒ 对象列表**。
    ⚠ **要「几个实体」用 `get_sketch_segments(sketch)`**；⚠ 官方文档**没写**这个返回结构。
"""
    _require(sketch)
    return as_sequence(get_com_member(sketch, "GetEllipses3"))


def get_parabolas(sketch) -> list[Any]:
    """抛物线。

    ⚑ 2026-10-01（轮 111）：改用**后继** `GetParabolas2()`（旧名已 Obsolete）。
    """
    _require(sketch)
    return as_sequence(get_com_member(sketch, "GetParabolas2"))


def get_polylines(sketch) -> list[Any]:
    """多段线。"""
    _require(sketch)
    return as_sequence(get_com_member(sketch, "GetPolylines"))


def get_splines(sketch) -> list[Any]:
    """样条曲线。"""
    _require(sketch)
    return as_sequence(get_com_member(sketch, "GetSplines"))


def get_sketch_points(sketch) -> list[Any]:
    """草图点。

    ⚑ 2026-10-01（轮 111）：改用**后继** `GetSketchPoints2()`（旧名已 Obsolete）。
    
    ✅ **返回的是「对象列表」**（实测 2026-10-01 轮 142，`tools/probe_slot_and_point_shapes.py`，
    真机 SW 2026 SP4.1）：**一条直线**的**两个端点**本身就是草图点 ⇒
    画 **1 / 2** 条直线 ⇒ 返回 **2 / 4** 个元素（**每条线 2 个**），元素类型 **`CDispatch`**。
    ⚠ 与**曲线类**取法（返回数值数组）**不同** ⇒ ★ **两种形状都有**。
"""
    _require(sketch)
    return as_sequence(get_com_member(sketch, "GetSketchPoints2"))


def get_user_points(sketch) -> list[Any]:
    """用户点（区别于自动生成的草图点）。

    ⚑ 2026-10-01（轮 111）：改用**后继** `GetUserPoints2()`（旧名已 Obsolete）。
    """
    _require(sketch)
    return as_sequence(get_com_member(sketch, "GetUserPoints2"))


def get_contour_edges(sketch, contour) -> list[Any]:
    """取某个轮廓的边。⚠ 官方是 **1 参**（Contour 对象）。"""
    _require(sketch)
    if contour is None:
        raise ValueError("contour 为 None")
    return as_sequence(get_com_member(sketch, "GetContourEdges", contour))


def get_sketch_contours(sketch) -> list[Any]:
    """轮廓。"""
    _require(sketch)
    return as_sequence(get_com_member(sketch, "GetSketchContours"))


def get_sketch_regions(sketch) -> list[Any]:
    """封闭区域。"""
    _require(sketch)
    return as_sequence(get_com_member(sketch, "GetSketchRegions"))


def get_sketch_hatches(sketch) -> list[Any]:
    """填充图案。"""
    _require(sketch)
    return as_sequence(get_com_member(sketch, "GetSketchHatches"))


def get_sketch_slots(sketch) -> list[Any]:
    """槽。
    ✅ **返回的是「对象列表」**（实测 2026-10-01 轮 142，`tools/probe_slot_and_point_shapes.py`，
    真机 SW 2026 SP4.1）：画 **1 / 2** 个槽口 ⇒ 返回 **1 / 2** 个元素，元素类型 **`CDispatch`**。
    ⚠ 注意与**曲线类**取法（`get_lines` / `get_arcs` / `get_ellipses`）**不同** —— 那三条返回
    **数值数组**（每个实体 12 / 16 / 22 个 `float`）⇒ ★ **两种形状都有，不能一概而论**。
"""
    _require(sketch)
    return as_sequence(get_com_member(sketch, "GetSketchSlots"))


def get_sketch_pictures(sketch) -> list[Any]:
    """草图图片。"""
    _require(sketch)
    return as_sequence(get_com_member(sketch, "GetSketchPictures"))


def get_sketch_paths(sketch) -> list[Any]:
    """草图路径（3D 草图用）。"""
    _require(sketch)
    return as_sequence(get_com_member(sketch, "GetSketchPaths"))


def get_sketch_block_instances(sketch) -> list[Any]:
    """草图块引用。"""
    _require(sketch)
    return as_sequence(get_com_member(sketch, "GetSketchBlockInstances"))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（同上文件）
# 定位:   草图属性与坐标变换。官方签名逐条照抄：
#     SketchRelationManager get_RelationManager()   ← **属性**
#     Boolean Is3D()                              ← **零参**
#     MathTransform get_ModelToSketchTransform()  ← **属性**
#     Object         get_ModelToSketchXform()      ← **属性**（旧式）
#     Void  set_ModelToSketchTransform(MathTransform) / set_ModelToSketchXform(Object)
#     Boolean SetAutomaticSolve(Boolean) / SetSketchEditable(Boolean) /
#             SetDetachSegmentOnDrag(Boolean)     → 各 1 参
#     Boolean MergePoints(Double)                 → 1 参
#     Boolean GetAutomaticSolve() / GetDetachSegmentOnDrag()  ← **零参**
# ⚑ 三对「取/设」成员都有**新式（Transform）与旧式（Xform）**两套，
#   官方未说明取舍 ⇒ 新式为主、旧式在注释里点名，**不替调用方删掉一个**。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_relation_manager(sketch):
    """取约束管理器。⚑ 官方是**属性**。约束封装见 sketch_relations.py。"""
    if sketch is None:
        raise ValueError("sketch 为 None")
    return get_com_member(sketch, "RelationManager")


def is_3d_sketch(sketch) -> bool:
    """是否 3D 草图。**零参**。"""
    if sketch is None:
        raise ValueError("sketch 为 None")
    return bool(get_com_member(sketch, "Is3D"))


def get_model_to_sketch_transform(sketch):
    """取「模型坐标 → 草图坐标」变换。⚑ 官方是**属性**（新式 Transform）。"""
    if sketch is None:
        raise ValueError("sketch 为 None")
    return get_com_member(sketch, "ModelToSketchTransform")


def set_model_to_sketch_transform(sketch, transform) -> bool:
    """设「模型坐标 → 草图坐标」变换。⚑ 官方是**属性**（新式）。"""
    if sketch is None:
        raise ValueError("sketch 为 None")
    set_com_member(sketch, "ModelToSketchTransform", transform)
    return True


def set_automatic_solve(sketch, enabled: bool) -> bool:
    """开关自动求解。"""
    if sketch is None:
        raise ValueError("sketch 为 None")
    return bool(get_com_member(sketch, "SetAutomaticSolve", bool(enabled)))


def merge_points(sketch, tolerance: float) -> bool:
    """合并重合点。⚠ 容差单位官方无说明。"""
    if sketch is None:
        raise ValueError("sketch 为 None")
    return bool(get_com_member(sketch, "MergePoints", float(tolerance)))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（sw_simulation_study.py::collect_study_evidence）
# 定位:   草图状态证据回读，沿用「只取已核实成员」的写法。
# 覆盖:   后续同级定义
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def collect_sketch_evidence(sketch) -> dict[str, Any]:
    """回读草图的结构信息。"""
    if sketch is None:
        raise ValueError("sketch 为 None")
    counts = {}
    for label, members in SKETCH_GETTERS.items():
        counts[label] = len(as_sequence(get_com_member(sketch, members[0])))
    return {
        "is_3d": bool(get_com_member(sketch, "Is3D")),
        "automatic_solve": bool(get_com_member(sketch, "GetAutomaticSolve")),
        "detach_segment_on_drag": bool(
            get_com_member(sketch, "GetDetachSegmentOnDrag")),
        "has_relation_manager": get_com_member(sketch, "RelationManager") is not None,
        "has_model_to_sketch_transform": (
            get_com_member(sketch, "ModelToSketchTransform") is not None),
        "element_counts": counts,
    }


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（`sw_part._capture_sketch_ref` 的按名取法 + 本模块的 `get_*` 一族）
# 文件:   scripts/sw_sketch.py（**本组为追加**，2026-10-01 轮 222 / 砌墙 W1）
# 定位:   给「把 `sw_sketch` 的只读查询挂成 MCP 工具」提供**只回读数**的薄函数。
#         ★ 为什么需要它（**真机实测定的，不是猜的**）：
#           `get_lines` / `get_arcs` 返回的是 **数值数组**（每条线 12 个 float、每条弧 16 个），
#           ★ **不是**"线对象列表「 ⇒ AI 拿回 36 个浮点数**没法判断」有几条线"**。
#           薄函数把它翻译成**条数**，那才是调用方要的东西。
# 官方依据: `ISketch.GetLines2` / `GetArcs2` / `GetSketchSegments` / `Is3D`
#          （结构不在官方文档里 —— ★ 官方**没写**返回结构，见下「除数」的实测依据）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 除数的依据是**本机实测**，不是官方文档：
#   `D:\AI\SW\output\sketch-getter-shapes.json`（`tools/probe_sketch_getter_shapes.py`，轮 141）
#   记着 `drawn` / `segments` / `count` / `element_type` ⇒ 画 1 条线 = 12 个 float（1↔12、2↔24、3↔36）。
# 覆盖:   本组 4 个函数
# ────────────────────────────────────────────────────────────────────
#: 每「条」几何在官方返回的数值数组里占几个 `float`。
#: ★ **有真机证据**（`output/sketch-getter-shapes.json`：1↔12、2↔24；弧 1↔16、2↔32）。
#: ⚠ 这是**实测形状**，官方文档**没写**；若哪天长度不是它的整数倍 ⇒ `count_*` **会报错**，不静默圆整。
ELEMS_PER_LINE = 12
ELEMS_PER_ARC = 16


def sketch_by_name(model, name: str):
    """按**草图特征名**取到 `ISketch` 对象。

    ★★ 本函数的存在理由是**真机实测**（`tools/probe_sketch_object_routes.py`，轮 220）：
    ```
                       草图打开中      草图已关闭
      model.GetActiveSketch2   草图1      **None**
      SketchManager.ActiveSketch 草图1    **None**
      按名取（本函数）           草图1      **草图1**  ✓
    ```
    ⇒ ★ **草图一关，两个「活动草图」取法都是 None**；而调用方的实际用法恰恰是
      「草图建完了，看看里面有什么」—— **那时草图已经关闭**。
      ⇒ 所以取草图对象的**唯一可靠路径是按名取**。

    ⚠ 与 `sw_part._find_cached_sketch_ref` 的区别：那个走**进程内缓存**，
      **MCP 调用是独立进程、缓存是空的** ⇒ **不能用于工具层**。本函数**无状态**。

    :param model: `IModelDoc2`
    :param name: 草图特征名（如 `"Sketch1"` / `"草图1"`）
    :raises RuntimeError: 找不到该名字的轮廓 —— ★ **选不中要报错，不静默返回 None**
    """
    if model is None:
        raise ValueError("model 为 None")
    feature = get_com_member(model, "FeatureByName", str(name))
    if feature is None:
        raise RuntimeError("找不到名为 %r 的草图特征（用 list 特征或按语言取名字）" % name)
    sketch = get_com_member(feature, "GetSpecificFeature2")
    if sketch is None:
        raise RuntimeError("%r 不是草图特征（GetSpecificFeature2 回了 None）" % name)
    return sketch


def _count_by_divisor(sketch, raw_getter, per_element: int, label: str) -> int:
    """把「数值数组」按实测的每元素长度换算成**条数**；长度不是整数倍就报错。"""
    raw = raw_getter(sketch)
    n = len(raw) if raw is not None else 0
    if n % per_element:
        raise RuntimeError(
            "%s 的返回值长度 %d **不是 %d 的整数倍** —— 官方返回结构可能变了；"
            "★ 不要圆整，先查 `tools/probe_sketch_getter_shapes.py`" % (label, n, per_element)
        )
    return n // per_element


def count_lines(sketch) -> int:
    """草图里有**几条直线**（不是「几个 float」）。

    ★ 原始取法 `get_lines()` 返回的是**数值数组**（每条 12 个 `float`）——
      实测 1 条→12、2 条→24、3 条→36（`output/sketch-getter-shapes.json`）。
      ⇒ 本函数给出调用方真正要的那个数。
    """
    return _count_by_divisor(sketch, get_lines, ELEMS_PER_LINE, "get_lines")


def count_arcs(sketch) -> int:
    """草图里有**几条圆弧**（★ 每条 16 个 `float`，实测见 `output/sketch-getter-shapes.json`）。"""
    return _count_by_divisor(sketch, get_arcs, ELEMS_PER_ARC, "get_arcs")


def count_segments(sketch) -> int:
    """草图里**一共几段**（`GetSketchSegments` 的元素数）。

    ⚠ 与 `count_lines` **不是一个东西**：段是「几何单元」的总数，
      线的条数只是其中一类。★ 两者都会给出，让调用方自己判断。
    """
    return len(get_sketch_segments(sketch))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（`sw_part._get_sketch_name_candidates` 的中英文变体 + 本模块的按名取）
# 文件:   scripts/sw_sketch.py（**本组为追加**，2026-10-01 轮 222 / 砌墙 W1）
# 定位:   ★ **真机验证抓出来的 bug 的修法**：`sw_part.current_sketch_name` 在
#         **草图已关闭**时回**英文 fallback `"Sketch1"`**，而中文 UI 下真名是「草图1」
#         ⇒ 第一次真机调用就报「找不到名为 'Sketch1' 的草图特征」。
#         ★ 这个错**只有真机能暴露** —— 静态门禁、62 个工具全部挂载成功，全绿。
# 官方依据: `IModelDoc2.FeatureByName` / `IFeature.GetSpecificFeature2` / `IModelDoc2.Fe
#           atureByPositionReverse`
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 名字随 UI 语言变是本仓库的既有事实（见 `docs/known-facts.md` 第 9 条：
#   基准面名 `Front Plane` / `前视基准面` 同理）⇒ **一律走候选名，不写死一种**。
# 覆盖:   本组 1 个函数
# ────────────────────────────────────────────────────────────────────
def active_sketch(model):
    """★ 取**当前活动草图**对象 —— ★ 走**后继入口** `ISketchManager.ActiveSketch`。

    ★★ 2026-10-03（接手轮）**为「消解废弃成员」抽出来的共用帮手**
      （★ 事实 60 定则④：写了一个好用的工具函数，就要在**所有**同类场合用它）。

    ★ 为什么换成它：★ 官方 `types/IModelDoc2/GetActiveSketch2.md` 逐字：
      「**Obsolete. Superseded by [[ISketchManager::ActiveSketch]].**」
    ★ 而后继是**属性**（`Sketch ActiveSketch {get;}`），★ 不是方法 ⇒ ★ 调用形态变成取属性。

    ★★★ 真机已验证两者**行为等价**（`tools/probe_activesketch_successor.py` ·
      `output/activesketch-successor-evidence.json`）：
      | 场景 | `GetActiveSketch2` | `SketchManager.ActiveSketch` |
      |---|---|---|
      | 无活动草图 | `None` | `None` |
      | ★ 草图开着 | `<COMObject>` | `<COMObject>`（★ 且 `.Name = '草图1'`）|
      | 草图已关闭 | `None` | `None` |
      ⇒ ★ **PASS** ✓ 这也**独立复核了**本仓原先那句「两者都是 None」。

    ★ 取不到就回 `None`（★ **不猜、不兜底** —— 与本模块 `resolve_sketch` 的分工：
      ★ `resolve_sketch` 是「按名字稳健地找」，★ 本函数是「只问当前活动草图，★ 没有就是没有」）。
    """
    try:
        sketch_manager = get_com_member(model, "SketchManager")
        if sketch_manager is None:
            return None
        return get_com_member(sketch_manager, "ActiveSketch")
    except Exception:                                                     # noqa: BLE001
        return None


def resolve_sketch(model, name: str = ""):
    """★ **稳健地**取到一个 `ISketch`，中英文名都能用，留空则取「最后一个草图」。

    解决三件事（★ 都由真机暴露，不是设想出来的）：
    ```
    ① 草图**已关闭**时，`SketchManager.ActiveSketch` 与 `model.GetActiveSketch2` 都是 None
       （真机探针 `tools/probe_sketch_object_routes.py`）
    ② 中文 UI 下草图真名是「草图1」，而 `sw_part.current_sketch_name` 在取不到时
       回**英文 fallback** `"Sketch1"` ⇒ 直接按那个名字找**必然找不到**
    ③ 调用方常常**根本不知道该填什么名字**（"我就要刚才建的那个草图"）
    ```

    查找顺序（每一步都**真的去取**，取到才返回）：
    ```
    1. 给了 name            ⇒ 按 候选名（中英文变体）逐个 FeatureByName
    2. 没给 name            ⇒ current_sketch_name 的结果 + 候选名
    3. 都不行               ⇒ ★ 从特征树里找**最后一个草图特征**（语言无关）
    4. 还找不到             ⇒ **抛错**（选不中要报错，不静默）
    ```

    :param model: `IModelDoc2`
    :param name: 草图特征名（中英文皆可）；留空 ⇒ 自动找
    :raises RuntimeError: 四种路径都取不到
    """
    if model is None:
        raise ValueError("model 为 None")

    tried: list[str] = []

    def _try(candidate: str):
        if not candidate:
            return None
        tried.append(candidate)
        try:
            return sketch_by_name(model, candidate)
        except RuntimeError:
            return None

    #: 1+2 · 显式名，或"当前草图名"（★ 两者都试中英文变体）
    #: ★★ 2026-10-03（轮 470）：**统一导入口径** —— 本行原写 `from scripts.sw_part import …`
    #:   （★ 包内却用**绝对包路径**），而本模块别处走 `from .sw_connect import …`（相对）
    #:   ⇒ ★ 同一个包内混用两套口径 ⇒ `sys.modules` 里可能出现**同一模块两份实例**
    #:   ⇒ 那是 `cannot import name … from '<unknown module name>'` 的来源之一。
    #:   ★ 现改为**相对优先、绝对回退**（与本仓模块级 `try/except` 的写法一致）。
    try:
        from .sw_part import _get_sketch_name_candidates, current_sketch_name
    except ImportError:                                        # 顶层载入（脚本 / 探针）
        from scripts.sw_part import _get_sketch_name_candidates, current_sketch_name

    base = str(name or "").strip() or current_sketch_name(model)
    for cand in _get_sketch_name_candidates(base):
        sk = _try(cand)
        if sk is not None:
            return sk

    #: ★★ 2026-10-03（轮 398）**缺陷修正**：★ **非空的名字一个都没解出来 ⇒ 报错，不许回退**。
    #:   真因：先前 `resolve_sketch(model, "<错名字>")` 会**静默回退**到
    #:   "特征树里最后一个草图" ⇒ ★★ 调用方会在**另一个草图**上读 / 写！
    #:   ★ 而本函数的批头明写「**选不中要报错，不静默**」。
    #:   ★ 兜底**只对「没给名字」成立** —— 那才是它的本意（"我就要刚才建的那个草图"）。
    #:   ★ 真机证据：`tools/prove_sketch_primitives.py` 第一版把
    #:   "不存在的草图名" 当负例 ⇒ **它竟然也能解析** ⇒ 才发现这个缺陷。
    if str(name or "").strip():
        raise RuntimeError(
            "按名找不到草图 %r（试过：%r）—— ★ 非空名字不许回退到「特征树里最后一个草图」"
            % (name, tried))
    
    #: 3 · 从特征树里找**最后一个草图特征**（★ 语言无关的兜底）
    try:
        total = int(get_com_member(model, "GetFeatureCount"))
    except Exception:                                          # noqa: BLE001
        total = 0
    for i in range(1, total + 1):
        feature = get_com_member(model, "FeatureByPositionReverse", i)
        fname = str(get_com_member(feature, "Name") or "") if feature is not None else ""
        if fname.startswith(("Sketch", "草图")):
            sk = _try(fname)
            if sk is not None:
                return sk

    raise RuntimeError(
        "取不到草图：试过 %r；特征树里也没找到以 Sketch/草图 开头的特征"
        % (tried or [base])
    )


# ── 规格 209 · B2-4（idx 175 `blank_sketch`）────────────────────────────────────────────────
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力实现）· ★ 铁律 1「只缝合不发明」
# 文件:   scripts/sw_sketch.py —— 追加 `feature_visibility` / `set_sketch_blanked`
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B2-4** · 外部项目 idx **175 `hide_al
#           l_sketches`**。
#   ★★★ 裁决书的硬约束（§九）逐字：「官方 `BlankSketch` 逐字是「Hides the **selected** sketches」
#     ⇒ ★ **官方没有 "all" 这个语义**（是别家自己许的）⇒ 工具名**不许叫 `hide_all_sketches`**，
#     要照官方的「**隐藏选中的草图**」；★ 别家**零选区 + 返回常量** = **规则 6 的反例**」✓
#   ★★ 它点名的**真风险**：「怎么回读「隐藏了没有」」—— 官方 `BlankSketch` 回 `void`、
#     且那一页**既无 Returns 也无 Remarks** ⇒ ★ 本节就是去**真机定出那个回读入口** ✓
# 官方依据 （★ 铁律 4：`C:\swapi` 逐页读过）：
#   · `C:\swapi\types\IModelDoc2\BlankSketch.md` —— `void BlankSketch()`，摘要逐字
#     「Hides the **selected** sketches.」★ **无 Returns 段、无 Remarks 段**
#   · `C:\swapi\types\IModelDoc2\UnblankSketch.md` —— `void UnblankSketch()`，摘要逐字
#     「Shows a hidden sketch.」
#   · ★★ `C:\swapi\types\IFeature\Visible.md` —— `System.int Visible {get;}`，
#     回 **`swVisibilityState_e`** ⇒ ★★ **这就是「隐藏了没有」的官方回读入口**
#     （★ 官方示例里**只有肉眼**："Examine the graphics area"）
#   · `C:\swapi\enums\swVisibilityState_e.md` —— `swVisibilityStateHide=1` ·
#     `swVisibilityStateShown=2` · `swVisibilityStateUnknown=3`（★ **没有 0**）
#   · ★★ `C:\swapi\examples\Hide_and_Show_Sketches_Example_VB.md` —— 官方**调用序**（逐字）：
#     ```
#     ' Preconditions: … 3. **Select the sketches** in the FeatureManager design tree
#     '                    or graphics area that you want to hide.
#     swModel.BlankSketch                      ← ① 隐藏**选中的**草图
#     swModel.UnblankSketch                    ← ② 显示（也要先选中）
#     ```
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────
# ★★ **为什么工具名里没有 "all"**（★ 明写，免后人「顺手改回来」）：
#   官方语义是「**选中的**草图」；★ 别家把它叫 `hide_all_sketches` 是**自己许的语义**，
#   而它的实现是「**零选区 + 回一个常量**」—— ★★ 那既**没有实现"all"**、
#   也**没有实现"选中的"**（★ 规则 6 的反例：返回常量不是判据）✓
#   ⇒ ★ 本仓的名字 = **`set_sketch_blanked`**（动词用官方的 Blank，**不承诺 all**）✓

#: ★ 官方 `swVisibilityState_e`（★ 逐值抄自 `C:\swapi\enums\swVisibilityState_e.md`；★ **注意没有 0**）
VISIBILITY_STATES = {1: "hide", 2: "shown", 3: "unknown"}


def _selected_feature_objects(model) -> list:
    """★ 取**当前选区**里的对象（★ 供读 `IFeature::Visible` 用）。"""
    mgr = get_com_member(model, "SelectionManager")
    count = int(get_com_member(mgr, "GetSelectedObjectCount2", -1) or 0)
    out = []
    for i in range(1, count + 1):                              # ⚠ 官方 Index **从 1 开始**
        try:
            obj = get_com_member(mgr, "GetSelectedObject6", i, -1)
        except Exception:                                      # noqa: BLE001
            continue
        if obj is not None:
            out.append(obj)
    return out


def feature_visibility(feature) -> dict:
    """★ 读一个特征的**可见性**（官方 `IFeature::Visible` → `swVisibilityState_e`）。

    ★★ 这是「**隐藏了没有**」的**唯一官方回读入口**（★ 官方示例里只有肉眼）✓
    :returns: `{raw, state, readable}` —— ★ **读不到**回 `raw=None, readable=False`
        （★ **不拿 `unknown`(3) 冒充"读不到"**）✓
    """
    out = {"raw": None, "state": None, "readable": False}
    try:
        raw = int(get_com_member(feature, "Visible"))
        out["raw"] = raw
        out["state"] = VISIBILITY_STATES.get(raw, "not_in_enum_%d" % raw)
        out["readable"] = True
    except Exception:                                          # noqa: BLE001
        pass
    return out


def set_sketch_blanked(model, selection: str = "__current_selection__", *,
                       blank: bool = True) -> dict:
    """★ **隐藏 / 显示选中的草图**（★ 官方 `IModelDoc2::BlankSketch` / `UnblankSketch`，**都零参**）。

    :param selection: **声明式选择器**（★ 规则 3）：
        · `"__current_selection__"` —— 用当前选区（★ 官方示例的前置就是「先在树里选中」）；
        · 或**逗号分隔的草图特征名**（★ 事实 32：**特征可以按名字选**，草图段/实体不行）。
    :param blank: `True` ⇒ `BlankSketch()`（隐藏）· `False` ⇒ `UnblankSketch()`（显示）。
    :returns: `{ok, blank, entry_used, selection_count, before, after, changed, error}`

    ★★ **判据（规则 6）**：★ 它**回 `void`** ⇒ 只能回读 ⇒
      ① **选区计数**（事实 8：不许信返回值）；
      ② ★★ **`IFeature::Visible` 的前后读数**（`swVisibilityState_e`）—— ★ 要求**真的变了** ✓
    ⚠ **官方语义是"选中的草图"** —— ★ 本函数**不实现 "hide all"**（★ 那个语义官方没有）✓
    """
    from sw_part import _empty_callout                                 # noqa: E402
    out: dict = {
        "ok": False, "blank": bool(blank),
        "entry_used": ("IModelDoc2::BlankSketch()" if blank else "IModelDoc2::UnblankSketch()"),
        "selection": str(selection)[:80], "selection_count": None,
        "before": [], "after": [], "changed": [], "error": None,
        "★": "判据 = **选区计数** + **`IFeature::Visible` 的前后读数**（`swVisibilityState_e`）；"
             "★ 它回 `void`，只能回读；★★ **本工具不实现「hide all」**（官方语义是「选中的草图」）",
    }
    if model is None:
        out["error"] = "model 为 None"
        return out
    sel = str(selection or "").strip() or "__current_selection__"
    try:
        #: ★ 官方示例前置：**先选中草图** ⇒ 按名字选时自己先清选区再逐条选（Append）
        get_com_member(model, "ClearSelection2", True)
        if sel != "__current_selection__":
            names = [x.strip() for x in sel.split(",") if x.strip()]
            if not names:
                out["error"] = "selection 是空的名字清单"
                return out
            ext = get_com_member(model, "Extension")
            for k, name in enumerate(names):
                get_com_member(ext, "SelectByID2", name, "SKETCH", 0.0, 0.0, 0.0,
                               bool(k > 0), 0, _empty_callout(), 0)
        out["selection_count"] = int(
            get_com_member(get_com_member(model, "SelectionManager"),
                           "GetSelectedObjectCount2", -1) or 0)
        if out["selection_count"] <= 0:
            out["error"] = ("选完**回读计数为 0** ⇒ 没有草图在选区里（★ 事实 8）"
                            "—— ★ 官方示例的前置就是「先在树里选中要隐藏的草图」")
            return out
        targets = _selected_feature_objects(model)
        out["before"] = [{"name": str(get_com_member(f, "Name") or ""),
                          **feature_visibility(f)} for f in targets]
        get_com_member(model, "BlankSketch" if blank else "UnblankSketch")
        after = _selected_feature_objects(model)
        if not after:                                          # ★ 调用后选区可能被清掉 ⇒ 重新按名字取
            names = [b["name"] for b in out["before"] if b.get("name")]
            ext = get_com_member(model, "Extension")
            get_com_member(model, "ClearSelection2", True)
            for k, name in enumerate(names):
                get_com_member(ext, "SelectByID2", name, "SKETCH", 0.0, 0.0, 0.0,
                               bool(k > 0), 0, _empty_callout(), 0)
            after = _selected_feature_objects(model)
        out["after"] = [{"name": str(get_com_member(f, "Name") or ""),
                         **feature_visibility(f)} for f in after]
    except Exception as exc:                                   # noqa: BLE001
        out["error"] = "调用失败：%s: %s" % (type(exc).__name__, str(exc)[:200])
        return out
    #: ★ 判据：**逐条比对前后读数**（★ 名字对上、且 state 真的变了）
    before = {b["name"]: b for b in out["before"] if b.get("name")}
    changed = []
    for a in out["after"]:
        b = before.get(a["name"])
        if b and b.get("readable") and a.get("readable") and b["raw"] != a["raw"]:
            changed.append({"name": a["name"], "raw": [b["raw"], a["raw"]],
                            "state": [b["state"], a["state"]]})
    out["changed"] = changed
    want = "hide" if blank else "shown"
    matched = [c for c in changed if c["state"][1] == want]
    out["ok"] = bool(matched)
    if not out["ok"]:
        out["error"] = ("回读判据未过：**没有任何一条草图的 `Visible` 变成 %r** —— "
                        "前 %r / 后 %r（★ 它回 `void` ⇒ 只能靠回读；★ 读不到不等于没变）"
                        % (want, [b.get("state") for b in out["before"]],
                           [a.get("state") for a in out["after"]]))
    return out
