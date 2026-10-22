"""第四批 MCP 工具声明（钣金 C2 + C3 —— 选择解析层解锁的那 4 条）。

## 本批的 4 条与它们各自需要的「选择」形态

| 函数 | 类 | 实现要求 | 本批怎么做 |
|---|---|---|---|
| `create_edge_flange(model, spec)` | C2 | 文档串：「调用前必须先用 `_select_by_id` 把目标**边**选入选区」 | `pre_call` → `resolve_selection(selection, "EDGE")` |
| `create_gusset(model, spec)` | C2 | 来源块：「**支撑面须由调用方先用 `SelectByID2` 选好**」 | `pre_call` → `resolve_selection(selection, "FACE")` |
| `create_draft(model, face_ref, spec)` | C2 | 文档串：「在**已选中**的面上创建」 | `pre_call` → 选面；⚠ **`face_ref` 显式省略**，见下 |
| `create_swept_flange(model, path_ref, profile_ref, spec)` | C3 | `path_ref` → `data.Path`、`profile_ref` → `data.Profile`（**真用了**） | `derived_args` 把两个选择器解析成**对象** |

## ⚠⚠ 一个**真实缺陷**：`create_draft` 的 `face_ref` 参数**从未被使用**
逐行读 `scripts/sw_sheet_metal.py` 的函数体（**不是猜**）：
```
def create_draft(model, face_ref, spec: DraftFeatureSpec):
    '''在已选中的面上创建原生拔模特征。'''
    spec.validate()
    def _apply(data):
        data.Angle = float(spec.angle)                  # 只用了 spec
        data.ReverseDirection = float(spec.reverse_direction)
    return _create_from_definition(model, SW_FM_DRAFT, _apply)
    # ↑ `face_ref` 从头到尾**没出现**
```
**⇒ 一个「看起来有意义、实际什么都不做」的参数** —— 正是本项目纪律要抓的**静默无效**。
**⇒ 本批的处理**：`omitted_params=("face_ref",)` **显式省略**它，并在工具描述里写明原因；
真正的选择由 `pre_call` 的 `selection` 承担（与文档串「在**已选中**的面上」一致）。
**⇒ 缺陷本身已记进 `docs/T-011-expose-capabilities-assessment.md`（不擅自改 `scripts/` 的既有签名）。**

## ⚠ 单位（照 spec 的 docstring，不猜）
`EdgeFlangeSpec` / `GussetSpec` / `SweptFlangeSpec` 的**长度都为米、角度为度**；
`DraftFeatureSpec` 是**角度为度、深度为米**。MCP 表面按规则 2 用 `_mm` / `_deg`
⇒ 长度在 `derived_args` 里 `/1000`，**角度原样传**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植）
# 文件:   mcp-server/tool_specs_batch4.py
# 定位:   `docs/T-011-expose-capabilities-assessment.md` §11.3 的 C2/C3 落地。
#         参数**逐条照真实签名与 dataclass 字段抄**（守卫测试用
#         `inspect.signature` + `dataclasses.fields` 核）。
# 官方签名依据: 不适用（只做参数搬运；被搬运函数的依据在其源码来源块里）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ **尚未接入 `mcp-server/server.py`**（单源原则，已知事实 24）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH4"]

_MM = 0.001


def _consumed(*names: str) -> dict:
    """构造 `param_alias`：**这些入参由 `derived_args` 消费，不传给目标函数**。

    ⚠ 为什么必须显式：注册器会把每个声明参数当 kwarg 传给目标函数，
    而 spec 字段（如 `thickness_mm`）目标函数**并不接受** ⇒ 不标记就 `TypeError`。
    **⇒ 显式，不靠猜**（本项目一贯纪律）。
    """
    return {n: None for n in names}




def _model():
    """取活动文档（`pre_call` / `derived_args` 里用）。"""
    from scripts.sw_connect import connect_solidworks

    _sw, model, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    if model is None:
        raise RuntimeError("没有活动文档 —— 请先打开一个零件")
    return model


def _select(params, kind: str):
    """按 `selection` 入参选中一个实体，返回**回读计数**（0 就报错，不静默）。"""
    from scripts.sw_selection_spec import resolve_selection

    return resolve_selection(_model(), params.selection, kind)


#: ★★★ 2026-10-03（接手轮）**"按名选草图、并给 mark"的共用帮手** —— 放在这里（★ 本模块就
#: 是选择帮手之家）。
#: ★★ **为什么必须共用**（事实 60 的定则④：「写了一个好用的工具函数，就要在**所有**同类
#: 场合用它」）：
#: 「显式拒」那一族（`part_sweep` / `part_loft` / `part_axis` / `part_wrap`）**都要**在 
#: `pre_call` 里
#:     按官方 mark 把**草图**选上 ⇒ ★ 帮手只写一份，★ 免得四条各写一遍、各错一遍。
#:   ★ 官方 mark 依据逐条见各 spec 自己的 doc（本仓已回查过）。
def _select_sketch_by_name(model, name: str, mark: int, append: bool) -> bool:
    """★ 按**名字**选一个草图，并给指定 `mark`（★ 选完以**回读计数**为准）。

    ★ **事实 32** 逐字：**「按名字选」只对特征成立**（`sw_part._ensure_sketch_selected` 走的就是那一路），
      ★ 对**实体（边/面）不成立** ⇒ ★ **草图是特征** ⇒ ★ 所以**按名字可以选**。
    ★ **事实 33** 逐字：`SelectByID2` 的 `Callout` **必须**传 `VARIANT(VT_DISPATCH, None)`
      （传 `None` 报「类型不匹配」，★ 而那个错误**看不出是 Callout 的问题**）。
    ★ **事实 8** 逐字：`SelectByID2` 的**布尔返回值不可信** ⇒ ★ 本函数**只把回读计数当判据**。
    """
    from scripts.sw_connect import create_empty_dispatch_variant, get_com_member

    return bool(get_com_member(
        get_com_member(model, "Extension"), "SelectByID2",
        str(name), "SKETCH", 0.0, 0.0, 0.0,
        bool(append), int(mark), create_empty_dispatch_variant(), 0))


def _mark_count(model, mark: int) -> int:
    """★ 回读某一档 `mark` 的选中数（★ 事实 8：只有计数算数）。"""
    from scripts.sw_connect import get_com_member

    try:
        return int(get_com_member(get_com_member(model, "SelectionManager"),
                                  "GetSelectedObjectCount2", int(mark)) or 0)
    except Exception:                                                     # noqa: BLE001
        return -1


def _select_sketches_in_order(model, names, mark: int, at_least: int, what: str):
    """★ **按给定顺序**把多个草图选上（同一个 `mark`），并**回读计数** ⇒ 不够就**抛**。

    ★★ 「**顺序**」在放样/扫描里是**语义的一部分**（官方 Remarks：轮廓要**按期望的顺序**选中）
      ⇒ ★ 所以这里**按传入列表的次序**逐个 `append`，★ 不排序、不去重。
    ★ 不够就抛（★ 不静默地把"前置未成立"当成"能力不成"）。
    """
    from scripts.sw_connect import get_com_member

    try:
        get_com_member(model, "ClearSelection2", True)
    except Exception:                                                     # noqa: BLE001
        pass
    picked = 0
    for i, nm in enumerate([n for n in (names or []) if str(n).strip()]):
        _select_sketch_by_name(model, nm, mark, append=(i > 0))
        got = _mark_count(model, mark)
        if got > picked:
            picked = got
    if picked < at_least:
        raise RuntimeError(
            "★ 前置未成立：%s 需要 **mark=%d 至少 %d 个**，选完回读只有 **%d**。"
            "★ 检查草图名是否与特征树里**逐字**一致（事实 32：草图是特征、按名字可以选）；"
            "★ 名字按**顺序**给（顺序在放样/扫描里是语义的一部分）。传入=%r"
            % (what, mark, at_least, picked, list(names or [])))
    return {"mark": mark, "picked": picked}


def _pre_sweep_sketches(params):
    """★ `pre_call`：轮廓 **mark=1** · 路径 **mark=4**（官方专文给的 mark）。"""
    model = _model()
    prof = str(getattr(params, "profile_sketch", "") or "").strip()
    path = str(getattr(params, "path_sketch", "") or "").strip()
    if not prof or not path:
        raise RuntimeError(
            "★ 前置未成立：`profile_sketch` 与 `path_sketch` 都必填"
            "（官方 mark：轮廓=1 · 路径=4）—— 扫描**不预选任何东西**，两个草图必须由这两个参数点名")
    _select_sketches_in_order(model, [prof], 1, 1, "扫描的轮廓")
    _select_sketch_by_name(model, path, 4, True)          #: ★ 路径在轮廓之后 append 上去
    n4 = _mark_count(model, 4)
    if n4 < 1:
        raise RuntimeError(
            "★ 前置未成立：路径草图 %r 没选上（mark=4 回读 %d）—— "
            "检查名字是否与特征树里逐字一致" % (path, n4))
    return {"mark1": _mark_count(model, 1), "mark4": n4}


def _pre_loft_profiles(params):
    """★ `pre_call`：放样轮廓**全部 mark=1、按给定顺序**（官方 Remarks：轮廓 mark 1、且按期望顺序）。"""
    names = getattr(params, "profile_sketches", None) or []
    return _select_sketches_in_order(_model(), names, 1, 2, "放样的轮廓")


# ── C2 三条：调用**前**先选好（`pre_call`）─────────────────────────
def _pre_edge_flange(params):
    _select(params, "EDGE")


def _pre_gusset(params):
    _select(params, "FACE")


#: ★★★★ 2026-10-10（规格 296）**`create_draft` 的 `pre_call` 必须建立**两个**选择** ——
#:   ★★ 起因：**283 的真机读数**逐字（`output/_probe283_draft_dir.txt`）：
#:     · **只给面**（6 面 × 3 标记 = **18 臂**）⇒ ★ **全失败**，★ 报文**恒定**
#:       「**此拔模方向尚未定义。**」⇒ ★★ 排除了「选错面 / 选错 mark」；
#:     · **`Front Plane`（mark 1）+ 面#0（mark 2）** ⇒ ★★ **成功**（新特征 **`拔模1`**）。
#:   ★★★ **⇒ 前置是**两个**选择**，而本模块原先**只给了一个**：
#:     ```python
#:     def _pre_draft(params):
#:         _select(params, "FACE")          # ★ 只有面 ⇒ 真机必报「方向尚未定义」
#:     ```
#:     ⇒ ★★ 于是「283 真机建成」这个结论**经工具层复现不了**（★ 事实 503 那一族：
#:       「代码里写了」≠「真机上前置真的上了」）。
#:   ★ 官方 mark 逐字（`C:\swapi\types\IFeatureManager\InsertMultiFaceDraft.md`）：
#:     「direction **mark 1**, faces to draft **mark 2**, draft edges **mark 4**」。
#:   ★ 方向项用**平面名**（★ 声明式，★ 规则 3：不收裸坐标）——
#: ★ 走 `SelectByID2(name, "PLANE", …, mark=1)`（★ 平面**是特征**，★ 事实 32 说按名字选
#: 只对特征成立 ⇒ 可行）。
#:   ★★ **前置没备齐就抛**（★ 不静默继续 —— 那会把「前置没上」记成「能力不成」）。
def _face_object(params):
    """★ 取「待拔模面」的 COM 对象（★ **只取对象、不选择** —— 选择由调用方按 mark 做）。

    ★ 为什么不能直接用 `_select(params, "FACE")`：★★ 它内部走 `resolve_selection`
      → `select_object(append=False)` ⇒ **会清空**刚选好的**方向项**
      （★ 296 真机实测：`mark1` 从 1 变 **0**，★ 而真机随即报 `InsertMultiFaceDraft 创建失败`）。
    ⇒ ★★ 所以「取对象」与「选择」**必须分开**：先选平面（mark 1），再 `append=True` + `mark=2` 选面。
    """
    from scripts.sw_connect import get_com_member
    from scripts.sw_selection_spec import current_selection, entities_on_body

    model = _model()
    sel = str(getattr(params, "selection", "") or "").strip()
    if sel == "__current_selection__":
        found = current_selection(model)
        if not found:
            raise RuntimeError("★ 前置未成立：`selection='__current_selection__'` 但当前**没有选中项**")
        return found[0]
    if sel.startswith("index:"):
        try:
            idx = int(sel.split(":", 1)[1])
        except ValueError:
            raise RuntimeError("★ 非法的 `selection`：%r（`index:` 后面要跟整数）" % sel)
        items = entities_on_body(model, "FACE", body_index=0)
        if idx < 0 or idx >= len(items):
            raise RuntimeError("★ 前置未成立：FACE 序号 %d 越界（共 %d 个）" % (idx, len(items)))
        return items[idx]
    raise RuntimeError(
        "★ 非法的 `selection`：%r（应为 `__current_selection__` 或 `index:<n>`）" % sel)


def _select_plane(params, mark: int) -> int:
    """按**平面名**选一个基准面并给 `mark`；★ 回读计数为准（★ 事实 8：布尔返回值不可信）。"""
    from scripts.sw_connect import get_com_member
    from scripts.sw_part import _empty_callout, _get_plane_name_candidates

    model = _model()
    ext = get_com_member(model, "Extension")
    name = str(getattr(params, "direction_plane", "") or "").strip()
    if not name:
        raise RuntimeError(
            "★ 前置未成立：`direction_plane` 是空的 —— "
            "★ `InsertMultiFaceDraft` 的官方 `## Remarks` 要求**方向项 mark 1**（283 真机：缺它必报"
            "「此拔模方向尚未定义。」）⇒ ★ 请给出一个基准面名（如 `Front Plane` / `前视基准面`）")
    for cand in _get_plane_name_candidates(name):
        if get_com_member(ext, "SelectByID2", cand, "PLANE", 0.0, 0.0, 0.0,
                          False, int(mark), _empty_callout(), 0):
            break
    sm = get_com_member(model, "SelectionManager")
    got = int(get_com_member(sm, "GetSelectedObjectCount2", int(mark)) or 0)
    if got < 1:
        raise RuntimeError(
            "★ 前置未成立：平面 %r（候选 %r）按 mark=%d **一个都没选上**"
            % (name, _get_plane_name_candidates(name), mark))
    return got


def _pre_draft(params):
    """★★ 283 的真机配方：**方向项（平面 · mark 1）** + **待拔模面（mark 2）**。

    ★★ **顺序与 `append` 都必须对**（★ 296 真机实测的坑，★ 见 `output/_probe296_draft_precall.txt`）：
      · 第一版写成 `_select_plane(mark=1)` 然后 `_select(params, "FACE")`
        —— ★★ `_select` 内部走 `resolve_selection` → `select_object(append=False)`
        ⇒ ★★ **把刚选好的方向项清掉了**（实测 `mark1` 由 1 → **0**，合计只剩 1）
        ⇒ ★ 真机报 `InsertMultiFaceDraft 创建失败`（★ 与 283 的「方向尚未定义」同一病灶）。
      · **正解** = ★ **先选平面（mark 1）**，★ **再以 `append=True` + `mark=2` 选面** ——
        ★ 走本仓既有的「按对象选 + 带 mark」那条路：`_select_com_object(obj, append, mark, model)`
        （★ 它内部用 `CreateSelectData().Mark` + `IEntity::Select4`，见 `MEMORY.md` 规则 37）。
      · ★★ **两个 mark 都要回读**（★ 事实 8：布尔返回值不可信）⇒ 缺任一个就**抛**。
    """
    from scripts.sw_connect import get_com_member
    from scripts.sw_part import _select_com_object

    model = _model()
    get_com_member(model, "ClearSelection2", True)      #: ★ 官方示例第 ① 步：先清选区
    _select_plane(params, mark=1)                       #: ★ 方向项 —— ★ 缺它真机必报「此拔模方向尚未定义。」
    face = _face_object(params)                         #: ★ 待拔模面（★ 只取对象，不选）
    if not _select_com_object(face, append=True, mark=2, model=model):
        raise RuntimeError("★ 前置未成立：待拔模面（mark 2）没选上")
    sm = get_com_member(model, "SelectionManager")
    got1 = int(get_com_member(sm, "GetSelectedObjectCount2", 1) or 0)
    got2 = int(get_com_member(sm, "GetSelectedObjectCount2", 2) or 0)
    if got1 < 1 or got2 < 1:
        raise RuntimeError(
            "★ 前置未成立：需要**两个**选择 —— 方向项(mark1)=%d · 待拔模面(mark2)=%d"
            "（283 真机：缺任一个必报「此拔模方向尚未定义。」）" % (got1, got2))
    return got1 + got2


# ── spec 装配（`derived_args`）─────────────────────────────────────
def _edge_flange_spec(p):
    from scripts.sw_sheet_metal import EdgeFlangeSpec

    return EdgeFlangeSpec(
        bend_radius=float(p.bend_radius_mm) * _MM,
        flange_length=float(p.flange_length_mm) * _MM,
        angle=float(p.angle_deg),
        use_default_radius=bool(p.use_default_radius),
        reverse_direction=bool(p.reverse_direction),
    )


def _gusset_spec(p):
    from scripts.sw_sheet_metal import GussetSpec

    return GussetSpec(
        thickness=float(p.thickness_mm) * _MM,
        profile_distance_1=float(p.profile_distance_1_mm) * _MM,
        profile_distance_2=float(p.profile_distance_2_mm) * _MM,
        profile_angle=float(p.profile_angle_deg),
    )


def _draft_spec(p):
    from scripts.sw_sheet_metal import DraftFeatureSpec

    return DraftFeatureSpec(
        angle=float(p.angle_deg),
        depth=float(p.depth_mm) * _MM,
        reverse_direction=bool(p.reverse_direction),
    )


def _swept_refs_and_spec(p):
    """C3：把两个**声明式选择器**解析成**对象**，并装回 spec。"""
    from scripts.sw_connect import connect_solidworks
    from scripts.sw_selection_spec import resolve_entity
    from scripts.sw_sheet_metal import SweptFlangeSpec

    _sw, model, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    if model is None:
        raise RuntimeError("没有活动文档 —— 请先打开一个零件")
    path_ref = resolve_entity(model, p.path_selection, "EDGE")
    profile_ref = resolve_entity(model, p.profile_selection, "SKETCH")
    # ⚠ `thickness_mm` 为 None ⇒ **不设** Thickness，走基体法兰继承（复现官方示例行为）
    return {
        "path_ref": path_ref,
        "profile_ref": profile_ref,
        "spec": SweptFlangeSpec(
            start_offset=float(p.start_offset_mm) * _MM,
            end_offset=float(p.end_offset_mm) * _MM,
            thickness=(None if p.thickness_mm is None else float(p.thickness_mm) * _MM),
            bend_radius=float(p.bend_radius_mm) * _MM,
            use_default_radius=bool(p.use_default_radius),
            flange_position=int(p.flange_position),
            flatten_along_path=bool(p.flatten_along_path),
            trim_side_bends=bool(p.trim_side_bends),
            use_default_bend_relief=bool(p.use_default_bend_relief),
            use_gauge_table=bool(p.use_gauge_table),
            use_material_parameters=bool(p.use_material_parameters),
            override_default_sheet_metal_parameters=bool(
                p.override_default_sheet_metal_parameters),
            reverse_direction=bool(p.reverse_direction),
        ),
    }


#: ⚠ 参数逐条照**真实签名 + dataclass 字段**抄，出处：
#: `Select-String scripts/sw_sheet_metal.py -Pattern '^def create_(edge_flange|gusset|dr
#: aft|swept_flange)'`
#: `Select-String scripts/sw_sheet_metal.py -Pattern '^class (EdgeFlangeSpec|GussetSpec|
#: DraftFeatureSpec|SweptFlangeSpec)'`
SPECS_BATCH4: list[ToolSpec] = [
    # 签名: def create_edge_flange(model, spec: EdgeFlangeSpec)
    ToolSpec(
        name="solidworks_sheet_metal_create_edge_flange",
        title="Create Sheet Metal Edge Flange",
        module="sw_sheet_metal", function="create_edge_flange",
        inject="model",
        # ⚠⚠ `selection` **不传给目标函数** —— 实现只收 `(model, spec)`，
        # 多传一个 kwarg 会 `TypeError`（**这个错是守卫测试抓到的**）。它由 `pre_call` 
        # 消费。
        param_alias=dict(
            {"selection": None},
            **_consumed("bend_radius_mm", "flange_length_mm", "angle_deg",
                        "use_default_radius", "reverse_direction"),
        ),
        pre_call=_pre_edge_flange,
        derived_args=lambda p: {"spec": _edge_flange_spec(p)},
        params=[
            Param("selection", str,
                  description="Declarative EDGE selection: '__current_selection__' "
                              "(use what is already selected) or 'index:<n>'."),
            Param("bend_radius_mm", float, description="Bend radius in MILLIMETRES."),
            Param("flange_length_mm", float, description="Flange length in MILLIMETRES."),
            Param("angle_deg", float, default=90.0, description="Flange angle in DEGREES."),
            Param("use_default_radius", bool, default=True,
                  description="Use the part default bend radius instead of bend_radius_mm."),
            Param("reverse_direction", bool, default=False, description="Reverse the flange direction."),
        ],
        doc=("★★ **本机（SW 2026 SP4.1 + pywin32）仍不可用**：`SetFixedFace` / `AccessSelections` 属**进程内指针族**，pywin32 迟到绑定下调不动（事实 47，20+ 形态已穷尽）。"
             "Create a native edge flange on a SELECTED edge. The edge is selected for you from `selection` BEFORE the call (the implementation requires a pre-existing selection). "
             "⚠ **仍不可用，但报错已前移**（2026-10-04 更正，★ 处置 JUDGE-C_D_E 🔴 #2 · E-1 #2）。"
             "★★ **旧描述（已作废）**：`setting \\`ReverseDirection\\` gave \\`Property ... can not be set\\`` ——"
             "★ 那条**属性层**的错**已修掉**：`ReverseDirection` **不属于** `IEdgeFlangeFeatureData`（★ 跨接口泄漏），"
             "★★ **代码里已删除**该设置（★ 原处只剩一条说明性注释）。"
             "★★★ **现在的事实**：★ 报错已从「属性设不上」**前移到** `CreateFeature(37) 创建失败` ⇒ **卡点在创建、不在属性**。"
             "⇒ ★ **以 `scripts/sw_sheet_metal.py::SHEET_METAL_RUNTIME_STATUS` 为准**（★ 第一现场）；"
             "★ 按旧描述排查会**停在一条已经不存在的死路上**。"),
    ),
    # 签名: def create_gusset(model, spec: GussetSpec)
    ToolSpec(
        name="solidworks_sheet_metal_create_gusset",
        title="Create Sheet Metal Gusset",
        module="sw_sheet_metal", function="create_gusset",
        inject="model",
        param_alias=dict(
            {"selection": None},
            **_consumed("thickness_mm", "profile_distance_1_mm",
                        "profile_distance_2_mm", "profile_angle_deg"),
        ),
        pre_call=_pre_gusset,
        derived_args=lambda p: {"spec": _gusset_spec(p)},
        params=[
            Param("selection", str,
                  description="Declarative FACE selection: '__current_selection__' or 'index:<n>'."),
            Param("thickness_mm", float, description="Gusset thickness in MILLIMETRES."),
            Param("profile_distance_1_mm", float,
                  description="Profile distance 1 in MILLIMETRES."),
            Param("profile_distance_2_mm", float, default=0.0,
                  description="Profile distance 2 in MILLIMETRES."),
            Param("profile_angle_deg", float, default=0.0,
                  description="Profile angle in DEGREES."),
        ],
        doc=("★★ **本机（SW 2026 SP4.1 + pywin32）仍不可用**：`ISMGussetFeatureData` 的 `AccessSelections` 属**进程内指针族**（事实 47）；★ 属性层已修好，但**特征建不出来**。"
             "Create a native sheet-metal gusset on a SELECTED supporting face. The face is selected for you from `selection` BEFORE the call. "
             "⚠ **仍不可用，但属性层已修好**（2026-10-04 更正，★ 处置 JUDGE-C_D_E 🔴 #2 · E-1 #3）。"
             "★★ **旧描述（已作废）**：`setting \\`Thickness\\` gave \\`Property ... can not be set\\`` ——"
             "★ **真因不是「属性只读」，是接口不对**：`Thickness` 是**焊件族**的名字，★ 本工具要走的是**钣金族**的 "
             "`ISMGussetFeatureData` ⇒ ★ 已改设 `GussetThickness`（★ 源码里注明「原 Thickness（焊件名）」）。"
             "★★★ **现在的事实**：★ 改用 `GussetThickness` / `ProfileHeightDim` / `ProfileLengthDim` / `ProfileAngleDim` 后"
             "**真机属性层读回全部成功**（0.002 / 0.01 / 0.01 / 45.0）；★ 报错已变为 `CreateFeature(118) 创建失败` ⇒ **卡点在创建、不在属性**。"
             "⇒ ★ **以 `scripts/sw_sheet_metal.py::SHEET_METAL_RUNTIME_STATUS` 为准**（★ 第一现场）；"
             "★ 按旧描述排查会**以为属性设不上而去找别的属性名**。"),
    ),
    # 签名: def create_draft(model, face_ref, spec: DraftFeatureSpec)
    # ⚠⚠ `face_ref` 在实现里**从未被使用**（见模块头）⇒ **显式省略**，
    #    真正的选择由 `pre_call` 的 `selection` 承担（与文档串「在已选中的面上」一致）。
    ToolSpec(
        name="solidworks_sheet_metal_create_draft",
        title="Create Sheet Metal Draft",
        module="sw_sheet_metal", function="create_draft",
        inject="model",
        param_alias=dict(
            #: ★★ `direction_plane` 由 `pre_call` 消费（★ 不传给目标函数 ——
            #:   `create_draft(model, face_ref, spec)` **没有**这个形参）。
            #:   ★ 这正是本仓既有形态（同段的 `selection` 也是 `None`）✓
            {"selection": None, "direction_plane": None},
            **_consumed("angle_deg", "depth_mm", "reverse_direction"),
        ),
        pre_call=_pre_draft,
        omitted_params=("face_ref",),
        derived_args=lambda p: {"spec": _draft_spec(p)},
        params=[
            Param("selection", str,
                  description="Declarative FACE selection: '__current_selection__' or 'index:<n>'."),
            Param("direction_plane", str, default="Front Plane",
                  description="★★ 方向项（官方 mark 1）。一个**基准面名**（如 `Front Plane` / `前视基准面`）"
                              "—— ★ 是**名字**不是坐标 ⇒ 不违反规则 3。"
                              "★★ 283 真机：**缺它必报「此拔模方向尚未定义。」**（18 臂全失败），"
                              "★ 给了它（`Front Plane`）+ 面 ⇒ **建成 `拔模1`**。"),
            Param("angle_deg", float, description="Draft angle in DEGREES."),
            Param("depth_mm", float, description="Draft depth in MILLIMETRES."),
            Param("reverse_direction", bool, default=False, description="Reverse the draft direction."),
        ],
        doc=("★★ **2026-10-09（规格 239）创建路径已按官方页改写**：**旧描述（已作废）** —— "
             "`CreateDefinition(3)`（`swFmDraft`）**不是合法类型** ⇒ 回 `None`；★ 那是**真机事实**，"
             "但**根因**是「`swFmDraft` 不在任何官方 `CreateDefinition` 宿主页的 `Type` 清单里」"
             "（规格 238 已证）⇒ **这条路径官方根本不支持**，不是参数没调对。"
             "★★ **现在的路径**：官方入口 **`IFeatureManager::InsertMultiFaceDraft`**"
             "（★ 其前代 `IModelDoc2::InsertMfDraft` / `InsertMfDraft2` 两页都写着 "
             "`Obsolete. Superseded by IFeatureManager::InsertMultifaceDraft`）。"
             "Create a native draft on a SELECTED face. The face is selected for you from `selection` "
             "BEFORE the call; per the official `## Remarks` the selections must be made with "
             "`IModelDocExtension::SelectByID2` (direction mark 1, faces to draft mark 2, draft edges mark 4). "
             "NOTE: the implementation's own `face_ref` parameter is accepted but NEVER USED (verified by "
             "reading the body); this tool therefore omits it and selects from `selection` instead, matching "
             "the docstring ('on the already-selected face'). *** NOT VERIFIED ON THE TEST MACHINE *** "
             "The path was rewritten from the official page in an OFFLINE slice (no COM run) - see "
             "scripts/sw_sheet_metal.py::SHEET_METAL_RUNTIME_STATUS (still `None` = untested)."),
    ),
    # 签名: def create_swept_flange(model, path_ref, profile_ref, spec: SweptFlangeSpec)
    ToolSpec(
        name="solidworks_sheet_metal_create_swept_flange",
        title="Create Sheet Metal Swept Flange",
        module="sw_sheet_metal", function="create_swept_flange",
        inject="model",
        # ⚠ 两个 ref **都被真用了**（`data.Path` / `data.Profile`）⇒ 用 derived_args 解
        # 析成对象
        param_alias=dict(
            {"path_selection": None, "profile_selection": None},
            **_consumed(
                "start_offset_mm", "end_offset_mm", "thickness_mm",
                "bend_radius_mm", "use_default_radius", "flange_position",
                "flatten_along_path", "trim_side_bends",
                "use_default_bend_relief", "use_gauge_table",
                "use_material_parameters", "override_default_sheet_metal_parameters",
                "reverse_direction",
            ),
        ),
        derived_args=_swept_refs_and_spec,
        params=[
            Param("path_selection", str,
                  description="Declarative EDGE selection for the sweep path: "
                              "'__current_selection__' or 'index:<n>'."),
            Param("profile_selection", str,
                  description="Declarative SKETCH selection for the sweep profile: "
                              "'__current_selection__' or 'index:<n>'."),
            Param("start_offset_mm", float, description="Start offset in MILLIMETRES."),
            Param("end_offset_mm", float, default=0.0, description="End offset in MILLIMETRES."),
            Param("thickness_mm", float, default=None,
                  description="Thickness in MILLIMETRES. Leave UNSET (null) to inherit from the "
                              "base flange - that reproduces the official example, which does not "
                              "set Thickness at all."),
            Param("bend_radius_mm", float, default=0.0, description="Bend radius in MILLIMETRES."),
            Param("use_default_radius", bool, default=True,
                  description="Use the default bend radius; when False, bend_radius_mm applies."),
            Param("flange_position", int, default=1,
                  description="swSweptFlangePositionTypes_e: 1=material inside, 2=material outside, "
                              "3=bend outside."),
            Param("flatten_along_path", bool, default=False, description="Flatten along the path."),
            Param("trim_side_bends", bool, default=False, description="Trim side bends."),
            Param("use_default_bend_relief", bool, default=True, description="Use the default bend relief."),
            Param("use_gauge_table", bool, default=False, description="Use the gauge table."),
            Param("use_material_parameters", bool, default=False,
                  description="Use material sheet-metal parameters."),
            Param("override_default_sheet_metal_parameters", bool, default=False,
                  description="Override the default sheet-metal parameters."),
            Param("reverse_direction", bool, default=False, description="Reverse the direction."),
        ],
        doc=("Create a native swept flange along a path. REQUIRES an existing base flange first (the official example builds one before the swept flange) - otherwise there is no thickness to inherit. NOT YET TESTED ON A REAL MACHINE: it needs both a sweep path and a profile selection, which the 2026-10-01 probe did not build. See scripts/sw_sheet_metal.py::SHEET_METAL_RUNTIME_STATUS before relying on it."),
    ),
]
