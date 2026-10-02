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


# ── C2 三条：调用**前**先选好（`pre_call`）─────────────────────────
def _pre_edge_flange(params):
    _select(params, "EDGE")


def _pre_gusset(params):
    _select(params, "FACE")


def _pre_draft(params):
    _select(params, "FACE")


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
#:   `Select-String scripts/sw_sheet_metal.py -Pattern '^def create_(edge_flange|gusset|draft|swept_flange)'`
#:   `Select-String scripts/sw_sheet_metal.py -Pattern '^class (EdgeFlangeSpec|GussetSpec|DraftFeatureSpec|SweptFlangeSpec)'`
SPECS_BATCH4: list[ToolSpec] = [
    # 签名: def create_edge_flange(model, spec: EdgeFlangeSpec)
    ToolSpec(
        name="solidworks_sheet_metal_create_edge_flange",
        title="Create Sheet Metal Edge Flange",
        module="sw_sheet_metal", function="create_edge_flange",
        inject="model",
        # ⚠⚠ `selection` **不传给目标函数** —— 实现只收 `(model, spec)`，
        #   多传一个 kwarg 会 `TypeError`（**这个错是守卫测试抓到的**）。它由 `pre_call` 消费。
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
        doc=("Create a native edge flange on a SELECTED edge. The edge is selected for you from `selection` BEFORE the call (the implementation requires a pre-existing selection). *** NOT USABLE ON THE TEST MACHINE *** run 2026-10-01 on SW 2026 SP4.1 and it FAILED with: setting `ReverseDirection` gave `Property ... can not be set`. The correct call shape has not been determined yet - see scripts/sw_sheet_metal.py::SHEET_METAL_RUNTIME_STATUS. The tool is kept so the failure stays diagnosable, not because it works."),
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
        doc=("Create a native sheet-metal gusset on a SELECTED supporting face. The face is selected for you from `selection` BEFORE the call. *** NOT USABLE ON THE TEST MACHINE *** run 2026-10-01 on SW 2026 SP4.1 and it FAILED with: setting `Thickness` gave `Property ... can not be set`. The correct call shape has not been determined yet - see scripts/sw_sheet_metal.py::SHEET_METAL_RUNTIME_STATUS. The tool is kept so the failure stays diagnosable, not because it works."),
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
            {"selection": None},
            **_consumed("angle_deg", "depth_mm", "reverse_direction"),
        ),
        pre_call=_pre_draft,
        omitted_params=("face_ref",),
        derived_args=lambda p: {"spec": _draft_spec(p)},
        params=[
            Param("selection", str,
                  description="Declarative FACE selection: '__current_selection__' or 'index:<n>'."),
            Param("angle_deg", float, description="Draft angle in DEGREES."),
            Param("depth_mm", float, description="Draft depth in MILLIMETRES."),
            Param("reverse_direction", bool, default=False, description="Reverse the draft direction."),
        ],
        doc=("Create a native draft on a SELECTED face. NOTE: the implementation's own `face_ref` parameter is accepted but NEVER USED (verified by reading the body); this tool therefore omits it and selects from `selection` instead, matching the docstring ('on the already-selected face'). *** NOT USABLE ON THE TEST MACHINE *** run 2026-10-01 on SW 2026 SP4.1 and it FAILED with: CreateDefinition(3) returned None. The correct call shape has not been determined yet - see scripts/sw_sheet_metal.py::SHEET_METAL_RUNTIME_STATUS. The tool is kept so the failure stays diagnosable, not because it works."),
    ),
    # 签名: def create_swept_flange(model, path_ref, profile_ref, spec: SweptFlangeSpec)
    ToolSpec(
        name="solidworks_sheet_metal_create_swept_flange",
        title="Create Sheet Metal Swept Flange",
        module="sw_sheet_metal", function="create_swept_flange",
        inject="model",
        # ⚠ 两个 ref **都被真用了**（`data.Path` / `data.Profile`）⇒ 用 derived_args 解析成对象
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
