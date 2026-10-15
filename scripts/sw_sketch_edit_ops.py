"""★ 草图编辑包装（B3 批）：剪裁 / 延伸 / 等距 / 圆角 / 线性阵列 / 圆周阵列 / 交叉曲线。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力实现）
# 文件:   scripts/sw_sketch_edit_ops.py
# 定位:   ★ 2026-10-03（轮 465）★ `specs/201-toolbar-gaps` 的 **B3 批**（草图编辑 7 条）。
#   ★★ 起因：用户贴草图工具条截图逐条问「能/不能」，这 7 个当时全答「不能」（本仓无入口）；
#     随后要求「把这些不能实现的都攻关好」。
#   ★★★ **签名与枚举三源互证（铁律 4）**：全部逐条读自 `C:\\swapi\\`：
#     ```
#     C:\\swapi\\types\\ISketchManager\\SketchTrim.md
#       System.bool SketchTrim(int Option, double X, double Y, double Z)
#     C:\\swapi\\types\\ISketchManager\\SketchExtend.md
#       System.bool SketchExtend(double X, double Y, double Z)
#     C:\\swapi\\types\\ISketchManager\\SketchOffset2.md
#       System.bool SketchOffset2(double Offset, bool BothDirections, bool Chain,
#                                 int CapEnds, int MakeConstruction, bool AddDimensions)
#     C:\\swapi\\types\\ISketchManager\\CreateFillet.md
#       SketchSegment CreateFillet(double Radius, int ConstrainedCorners)
#     C:\\swapi\\types\\ISketchManager\\CreateLinearSketchStepAndRepeat.md
#       System.bool CreateLinearSketchStepAndRepeat(int NumX, int NumY, double SpacingX,
#         double SpacingY, double AngleX, double AngleY, string DeleteInstances, bool XSpacingDim,
#         bool YSpacingDim, bool AngleDim, bool CreateNumOfInstancesDimInXDir,
#         bool CreateNumOfInstancesDimInYDir)
#     C:\\swapi\\types\\ISketchManager\\CreateCircularSketchStepAndRepeat.md
#       System.bool CreateCircularSketchStepAndRepeat(double ArcRadius, double ArcAngle,
#         int PatternNum, double PatternSpacing, bool PatternRotate, string DeleteInstances,
#         bool RadiusDim, bool AngleDim, bool CreateNumOfInstancesDim)
#     C:\\swapi\\types\\ISketchManager\\IntersectCurves.md
#       void IntersectCurves()
#     C:\\swapi\\enums\\swSketchTrimChoice_e.md
#       Closest 0 · Corner 1 · TwoEntities 2 · EntityPoint 3 · Entities 4 · Outside 5 · Inside 6
#     C:\\swapi\\enums\\swSkOffsetCapEndType_e.md
#       NoCaps 0 · ArcCaps 1 · LineCaps 2
#     C:\\swapi\\enums\\swSkOffsetMakeConstructionType_e.md
#       Dont 0 · MakeOrig 1 · MakeOffs 2 · MakeBoth 3
#     ```
#   ★★★ **选择怎么做的（★ 本模块的核心设计）**：官方这族**全部要求"先选中草图实体"**，
#     而**事实 32** 说得很清楚 —— **按名字选只对特征成立**，对**实体（边/面/草图段）不成立**。
#     ⇒ ★ 故本模块走**按对象选**：`get_sketch_segments` 取到段对象，再 `Select4(append, callout)` ✓
#     ★★ 对外的参数是**声明式下标**（`selection="index:0"` / `"index:0,index:1"` / `"__current_selection__"`），
#       **不收裸坐标**（规则 3）✓
#   ⚠ **单位**：长度**毫米**、角度**度** —— 换算在工具层边界做一次（规则 2）。
#     ★ 官方这两个阵列成员的 `AngleX`/`AngleY`/`ArcAngle` 是**弧度**（COM 惯例）⇒ 本模块**收度**、
#       在边界乘 `pi/180` ✓
# 官方依据: 见上（`C:\\swapi\\` 的 7 个成员 + 3 个枚举）。
# 许可:   本仓库 MIT。无第三方代码引入（★ 全部按官方签名自建）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 建/改后由调用方回读**草图实体段数**或**几何坐标**（规则 6）。

from __future__ import annotations

_MM_TO_M = 1.0 / 1000.0      #: ★ 毫米 → 米（事实 2 的换算口径）

import math
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
for _p in (_HERE.parent, _HERE.parent.parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import sw_sketch as _SK  # noqa: E402
from sw_connect import get_com_member, set_com_member as _set_com_member  # noqa: E402
from sw_part import _empty_callout  # noqa: E402

#: ★ 长度换算助手：`_mm(v)` = **毫米→米**（恰好一次）。
#:   依据：本仓定案 `output/probe-unit-decisive/decisive.json`。
try:
    from sw_connect import mm as _mm          # noqa: F401
except Exception:                             # noqa: BLE001
    _mm = lambda v: float(v) / 1000.0         # noqa: E731


#: ★ 长度换算助手：`_f(v)` = 先收窄成 float、再**毫米→米**（恰好一次）。
#: ★★ 依据（定案）：`output/probe-unit-decisive/decisive.json` —— 同文档同会话单变量：
#:   草图 40×40 回读 `[40,40,0]` ✓ 而 `extrude_boss(20.0)` 回读 Z = **20000 mm**
#:   ⇒ COM 吃**米**，用户传毫米 ⇒ 进 COM 前必须换算恰好一次。
#: ⚠ 用单 token 替换（`float(` → `_f(`）落地，避免括号配对出错（事实 61）。
_f = lambda v: v * _MM_TO_M          # noqa: E731


#: ★ 官方 `swSketchTrimChoice_e`（★ 逐值抄自 `C:\swapi\enums\`）
#: enum-gate: enum swSketchTrimChoice_e
TRIM_CHOICES = {
    "closest": 0, "corner": 1, "two_entities": 2, "entity_point": 3,
    "entities": 4, "outside": 5, "inside": 6,
}
#: ★ 官方 `swSkOffsetCapEndType_e`
#: enum-gate: enum swSkOffsetCapEndType_e
OFFSET_CAPS = {"none": 0, "arc": 1, "line": 2}
#: ★ 官方 `swSkOffsetMakeConstructionType_e`
#: enum-gate: enum swSkOffsetMakeConstructionType_e
OFFSET_CONSTRUCTION = {"dont": 0, "orig": 1, "offs": 2, "both": 3}


def _sketch(model):
    sk = _SK.resolve_sketch(model, "")
    if sk is None:
        raise RuntimeError("没有活动草图（先 solidworks_sketch_start）")
    return sk


def select_sketch_segment(model, index: int, *, append: bool = False) -> int:
    """★ **按对象**选中草图里第 `index` 段（0 基）—— 事实 32：草图段**按名字选不中**。

    :returns: ★ 回读到的**选区计数**（★ 不是 `Select4` 的返回值 —— 事实 8）。
    """
    segs = _SK.get_sketch_segments(_sketch(model))
    if not segs:
        raise RuntimeError("草图里没有线段可选中")
    if index < 0 or index >= len(segs):
        raise RuntimeError("草图段下标 %d 越界（共 %d 段）" % (index, len(segs)))
    seg = segs[index]
    ok = get_com_member(seg, "Select4", bool(append), _empty_callout())
    if not ok and not append:
        #: \u2605 Select4 \u7684\u8fd4\u56de\u503c\u4e0d\u53ef\u4fe1\uff08\u4e8b\u5b9e 8\uff09\u21d2 \u7528\u56de\u8bfb\u8ba1\u6570\u5b9a\u8bba
        pass
    mgr = get_com_member(model, "SelectionManager")
    return int(get_com_member(mgr, "GetSelectedObjectCount2", -1) or 0)


def _select_spec(model, selection: str, *, mark: int = 0) -> int:
    """★ 解析声明式选择：`__current_selection__` / `index:0` / `index:0,index:1`。

    ★ 收**下标**、不收坐标（规则 3）✓
    """
    sel = (selection or "").strip()
    if sel in ("", "__current_selection__"):
        mgr = get_com_member(model, "SelectionManager")
        return int(get_com_member(mgr, "GetSelectedObjectCount2", -1) or 0)
    idxs = []
    for part in sel.split(","):
        part = part.strip()
        if not part.startswith("index:"):
            raise ValueError(
                "非法的草图段选择器 %r；合法形式：'__current_selection__' 或 'index:0' / 'index:0,index:1'" % part)
        idxs.append(int(part.split(":", 1)[1]))
    n = 0
    for k, i in enumerate(idxs):
        n = select_sketch_segment(model, i, append=(k > 0))
    return n


def sketch_trim(model, selection: str, option: str = "closest", x: float = 0.0, y: float = 0.0):
    """★ 剪裁实体：`SketchTrim(Option, X, Y, Z)`（★ `option` 逐值抄自官方枚举）。

    ⚠ ★ 官方 Remarks 对**每个选项**都写了"调用前必须先选几条段" ——
      ★ 本函数**按选择器先选好**再调；★ 而"该选几条"由 `option` 决定（见下），
      ★ **选错条数官方会失败**（★ 本模块如实抛，不静默）：
      ```
      closest(0)     ★ 一条且仅一条
      corner(1)      ★ 两条且仅两条
      two_entities(2)/entities(4)/entity_point(3)  ★ Power trim —— 官方要求先用
                     IModelDocExtension::SelectByID2 等方式选，形态不同
      outside(5)/inside(6)  ★ 至少……
      ```
    """
    key = str(option).strip().lower()
    if key not in TRIM_CHOICES:
        raise ValueError("未知的剪裁选项 %r；合法：%s" % (option, ", ".join(sorted(TRIM_CHOICES))))
    _select_spec(model, selection)
    return get_com_member(_sketch(model) and get_com_member(model, "SketchManager"),
                          "SketchTrim", TRIM_CHOICES[key], _f(x), _f(y), 0.0)


def sketch_extend(model, selection: str, x: float = 0.0, y: float = 0.0):
    """★ 延伸实体：`SketchExtend(X, Y, Z)`（★ 延伸**选中的**草图段到最近的实体）。"""
    _select_spec(model, selection)
    return get_com_member(get_com_member(model, "SketchManager"),
                          "SketchExtend", float(x), float(y), 0.0)


def sketch_offset(model, selection: str, offset_mm: float, *, both_directions: bool = False,
                  chain: bool = True, cap_ends: str = "none", make_construction: str = "dont",
                  add_dimensions: bool = False):
    """★ 等距实体：`SketchOffset2(Offset, BothDirections, Chain, CapEnds, MakeConstruction, AddDimensions)`。"""
    if cap_ends not in OFFSET_CAPS:
        raise ValueError("未知的 cap_ends %r；合法：%s" % (cap_ends, ", ".join(sorted(OFFSET_CAPS))))
    if make_construction not in OFFSET_CONSTRUCTION:
        raise ValueError("未知的 make_construction %r；合法：%s"
                         % (make_construction, ", ".join(sorted(OFFSET_CONSTRUCTION))))
    _select_spec(model, selection)
    return get_com_member(get_com_member(model, "SketchManager"), "SketchOffset2",
                          _f(offset_mm), bool(both_directions), bool(chain),
                          OFFSET_CAPS[cap_ends], OFFSET_CONSTRUCTION[make_construction],
                          bool(add_dimensions))


def sketch_fillet(model, selection: str, radius_mm: float, constrained_corners: int = 0):
    """★ 绘制圆角：`CreateFillet(Radius, ConstrainedCorners)`（★ 用**选中的两条**草图段）。"""
    _select_spec(model, selection)
    seg = get_com_member(get_com_member(model, "SketchManager"), "CreateFillet",
                         _f(radius_mm), int(constrained_corners))
    if seg is None:
        raise RuntimeError("CreateFillet 返回 None ⇒ 草图圆角没建出来"
                           "（★ 官方要求两条草图段**相交**且都已选中）")
    return seg


def sketch_linear_pattern(model, selection: str, num_x: int = 2, num_y: int = 1,
                          spacing_x_mm: float = 10.0, spacing_y_mm: float = 0.0,
                          angle_x_deg: float = 0.0, angle_y_deg: float = 0.0,
                          delete_instances: str = "", *, spacing_dim_x: bool = False,
                          spacing_dim_y: bool = False, angle_dim: bool = False,
                          count_dim_x: bool = False, count_dim_y: bool = False):
    """★ 线性草图阵列：`CreateLinearSketchStepAndRepeat(...)`（★ 12 参，逐条照抄）。"""
    _select_spec(model, selection)
    return get_com_member(get_com_member(model, "SketchManager"),
                          "CreateLinearSketchStepAndRepeat",
                          int(num_x), int(num_y), _f(spacing_x_mm), _f(spacing_y_mm),
                          math.radians(float(angle_x_deg)), math.radians(float(angle_y_deg)),
                          str(delete_instances or ""),
                          bool(spacing_dim_x), bool(spacing_dim_y), bool(angle_dim),
                          bool(count_dim_x), bool(count_dim_y))


def sketch_circular_pattern(model, selection: str, arc_radius_mm: float = 20.0,
                            arc_angle_deg: float = 360.0, pattern_num: int = 4,
                            pattern_spacing_deg: float = 0.0, pattern_rotate: bool = True,
                            delete_instances: str = "", *, radius_dim: bool = False,
                            angle_dim: bool = False, count_dim: bool = False):
    """★ 圆周草图阵列：`CreateCircularSketchStepAndRepeat(...)`（★ 9 参）。"""
    _select_spec(model, selection)
    return get_com_member(get_com_member(model, "SketchManager"),
                          "CreateCircularSketchStepAndRepeat",
                          _f(arc_radius_mm), math.radians(float(arc_angle_deg)),
                          int(pattern_num), math.radians(float(pattern_spacing_deg)),
                          bool(pattern_rotate), str(delete_instances or ""),
                          bool(radius_dim), bool(angle_dim), bool(count_dim))


def sketch_intersect_curves(model):
    """★ 交叉曲线：`IntersectCurves()`（★ 零参数）。"""
    return get_com_member(get_com_member(model, "SketchManager"), "IntersectCurves")


#: ★ B3 批的成员清单（★ 供探针与门禁按名单跑，不遍历）
B3_MEMBERS = (
    "sketch_trim", "sketch_extend", "sketch_offset", "sketch_fillet",
    "sketch_linear_pattern", "sketch_circular_pattern", "sketch_intersect_curves",
)


# ── 规格 209（规格 207 的 18 条采纳候选 · B1 批）：**构造几何** ─────────────────────────────
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_sketch_edit_ops.py —— 追加 `sketch_set_construction_geometry`
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B1 批** · 外部项目 idx **79 `construction_geometry`**。
#   ★★ 裁决书的强制约束（`docs/recon-207/adjudication.md` §一）：「零参 + 普通 dispinterface ⇒
#   后端可达性最高。落 `sw_sketch_edit_ops.py`，**复用**该文件已有的声明式选段包装」✓
# 官方依据 （★ 铁律 4：`C:\swapi` 逐页读过）：
#   · `C:\swapi\types\ISketchManager\CreateConstructionGeometry.md` —— `void CreateConstructionGeometry()`
#     ★ 摘要逐字：「**Sets** selected sketch segments **to be construction geometry instead of
#       sketch geometry**.」（★ 是**置位**、不是 toggle —— 措辞是 "Sets … instead of"，★ 不是 "toggles"）
#     ★ `## Remarks` 逐字：「This method supports **all document types**, unlike
#       `IDrawingDoc::CreateConstructionGeometry`, which only supports drawing documents.」
#   · `C:\swapi\types\ISketchSegment\ConstructionGeometry.md` —— `System.bool ConstructionGeometry {get; set;}`
#     ★ 摘要逐字：「Gets **or sets** whether this sketch segment is construction geometry」
#     ⇒ ★★ **往回变（构造线 → 实体线）官方只有这条属性通道**（`CreateConstructionGeometry` 是单向置位）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────
# ★★ **裁决书点名的、必须先定的那个开源问题（dp1）**：
#   「官方摘要**没说**"再调一次是**切换**还是**置位**" ⇒ ★ **必须先定这个，否则会做出
#    "第二次调用把构造线变回实体"的工具**（静默的语义错）」
#   ⇒ ★★ 本函数的**设计**（既做对、又可证）：**置位方向走官方零参入口**
#     （`CreateConstructionGeometry`），**复位方向走属性 setter**（★ 官方唯一的回程）✓
#   ★ 而"再调一次会怎样"由**真机探针**单独回答（`tools/probe_union_adopt_b1.py` 的 T2-c），
#     ★★ **不把 toggle 语义烘进工具**（★ 无论答案是哪一种，本工具的语义都是"我要它**是/不是**构造线"）
#   ★★★ **已知事实 32** 在这里照旧成立：草图段**按名字选不中** ⇒ 本函数走**按对象选**（`Select4`）✓


def _selection_segments(model, selection: str):
    """★ 把**声明式选择器**解析成**草图段对象清单**（★ 与 :func:`_select_spec` 同一套语法）。

    ★ 支持 ``"__current_selection__"`` / ``""``（用当前选区）与 ``"index:0,index:1"``。
    ★ 返回 `(segments, readback_count)` —— ★ **回读计数**才是判据（事实 8：`Select4` 的返回值不可信）。
    """
    sk = _sketch(model)
    sel = (selection or "").strip()
    if sel in ("", "__current_selection__"):
        mgr = get_com_member(model, "SelectionManager")
        count = int(get_com_member(mgr, "GetSelectedObjectCount2", -1) or 0)
        objs = []
        for i in range(1, count + 1):            # ⚠ 官方 Index **从 1 开始**
            try:
                objs.append(get_com_member(mgr, "GetSelectedObject6", i, -1))
            except Exception:                    # noqa: BLE001
                continue
        return [o for o in objs if o is not None], count
    idxs = []
    for part in sel.split(","):
        part = part.strip()
        if not part.startswith("index:"):
            raise ValueError(
                "非法的草图段选择器 %r；合法形式：'__current_selection__' 或 'index:0' / 'index:0,index:1'"
                % part)
        idxs.append(int(part.split(":", 1)[1]))
    segs = _SK.get_sketch_segments(sk)
    picked = []
    for i in idxs:
        if i < 0 or i >= len(segs):
            raise ValueError("草图段下标 %d 越界（共 %d 段）" % (i, len(segs)))
        picked.append(segs[i])
    for k, seg in enumerate(picked):
        get_com_member(seg, "Select4", bool(k > 0), _empty_callout())
    mgr = get_com_member(model, "SelectionManager")
    n = int(get_com_member(mgr, "GetSelectedObjectCount2", -1) or 0)
    return picked, n


def _construction_flags(model) -> list[bool]:
    """★ 回读**整张草图**每段的 `ISketchSegment.ConstructionGeometry` 属性（★ 官方 get/set）。"""
    flags = []
    for seg in _SK.get_sketch_segments(_sketch(model)) or []:
        try:
            flags.append(bool(get_com_member(seg, "ConstructionGeometry")))
        except Exception:                        # noqa: BLE001
            flags.append(None)
    return flags


def sketch_set_construction_geometry(model, selection: str, *,
                                     construction: bool = True) -> dict:
    """★ **把选中的草图段置为 / 复位为构造几何**（★ 规则 3：只收声明式选择器，不收坐标）。

    :param selection: ``"__current_selection__"`` 或 ``"index:0"`` / ``"index:0,index:1"``。
    :param construction: `True` ⇒ 变成**构造几何**（走官方零参入口 `CreateConstructionGeometry()`）；
        `False` ⇒ **变回实体线**（★ 官方唯一的回程是 `ISketchSegment::ConstructionGeometry` 属性
        setter —— `CreateConstructionGeometry` 是**单向置位**，官方摘要逐字 "Sets … instead of"）。
    :returns: `{ok, requested, entry_used, selection_count, segments_before, segments_after,
        construction_count_after, error}`

    ★★ **判据 = 回读属性**（★ 规则 6）：调用后逐段读 `ConstructionGeometry`，
      并要求**目标段的读数 == 请求的 `construction`**；★ 读回**不等于**请求 ⇒ `ok=False`
      并**如实报**哪几段没对上（★ 不静默 —— 这正是"toggle 还是置位"那件事会暴露的地方）。
    """
    out: dict = {
        "ok": False, "requested": bool(construction), "entry_used": None,
        "selection_count": None, "segments_before": None, "segments_after": None,
        "target_before": None, "target_after": None, "construction_count_after": None,
        "error": None,
        "★": "判据是**回读 `ISketchSegment.ConstructionGeometry`**；"
             "★ 置位方向用官方零参 `ISketchManager.CreateConstructionGeometry()`、"
             "复位方向用属性 setter（★ 官方唯一的回程）",
    }
    if model is None:
        out["error"] = "model 为 None"
        return out
    try:
        segs, count = _selection_segments(model, selection)
    except Exception as exc:                                   # noqa: BLE001
        out["error"] = "解析选择器失败：%s: %s" % (type(exc).__name__, str(exc)[:150])
        return out
    out["selection_count"] = count
    if not segs:
        out["error"] = ("选择器 %r 没给出任何草图段（★ 事实 32：草图段按名字选不中 ⇒ "
                        "请用 'index:<n>' 或先在界面上选中）" % str(selection)[:50])
        return out

    def _flag(seg):
        try:
            return bool(get_com_member(seg, "ConstructionGeometry"))
        except Exception:                                      # noqa: BLE001
            return None

    out["target_before"] = [_flag(s) for s in segs]
    out["segments_before"] = sum(1 for f in _construction_flags(model) if f)
    try:
        if construction:
            out["entry_used"] = "ISketchManager::CreateConstructionGeometry()"
            get_com_member(get_com_member(model, "SketchManager"), "CreateConstructionGeometry")
        else:
            out["entry_used"] = "ISketchSegment::ConstructionGeometry (setter = False)"
            for seg in segs:
                _set_com_member(seg, "ConstructionGeometry", False)
    except Exception as exc:                                   # noqa: BLE001
        out["error"] = "调用失败：%s: %s" % (type(exc).__name__, str(exc)[:200])
        return out
    out["target_after"] = [_flag(s) for s in segs]
    out["segments_after"] = sum(1 for f in _construction_flags(model) if f)
    out["construction_count_after"] = out["segments_after"]
    mismatched = [i for i, f in enumerate(out["target_after"]) if f is not bool(construction)]
    out["ok"] = not mismatched
    if mismatched:
        out["error"] = ("回读不对：第 %r 段没达到请求的状态（★ 请求 %r，回读 %r）—— "
                        "★ 这正是「再调一次是切换还是置位」那件事会暴露的地方"
                        % (mismatched, bool(construction),
                           [out["target_after"][i] for i in mismatched]))
    return out
