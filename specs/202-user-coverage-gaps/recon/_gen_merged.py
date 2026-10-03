"""★ 生成合并总表：全部 277 条 ToolSpec × 档位 × 依据。"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
RECON = ROOT / "specs" / "202-user-coverage-gaps" / "recon"

# ── 档位覆盖表：只列非「无关」的条目；其余默认无关 ────────────────────────
SAFE = {
    "solidworks_sheet_metal_create_edge_flange": ("安全", "batch4 `pre_call=_pre_edge_flange` → `resolve_selection(..., \"EDGE\")`"),
    "solidworks_sheet_metal_create_gusset": ("安全", "batch4 `pre_call=_pre_gusset` → `resolve_selection(..., \"FACE\")`"),
    "solidworks_sheet_metal_create_draft": ("安全", "batch4 `pre_call=_pre_draft` → `resolve_selection(..., \"FACE\")`"),
    "solidworks_chamfer": ("安全", "batch23 `pre_call=_select_edge` → `resolve_selection(..., \"EDGE\")`"),
    "solidworks_fillet": ("安全", "batch23 `pre_call=_select_edge` → `resolve_selection(..., \"EDGE\")`"),
    "solidworks_simulation_apply_fixed_restraint": ("安全", "batch26 `pre_call=_select_face` + `derived_args=_derive_model`"),
    "solidworks_simulation_apply_normal_force": ("安全", "batch26 同上"),
    "solidworks_simulation_apply_pressure": ("安全", "batch29 `_spec` 工厂 `pre_call=_select_face`"),
    "solidworks_simulation_apply_torque": ("安全", "batch29 同上"),
    "solidworks_simulation_apply_gravity": ("安全", "batch29 同上"),
    "solidworks_simulation_apply_centrifugal_force": ("安全", "batch29 同上"),
    "solidworks_simulation_apply_convection": ("安全", "batch58 经 `tool_specs_batch29._spec` 工厂"),
    "solidworks_simulation_apply_heat_flux": ("安全", "batch58 同上"),
    "solidworks_simulation_apply_heat_power": ("安全", "batch58 同上"),
    "solidworks_simulation_apply_radiation": ("安全", "batch58 同上"),
    "solidworks_simulation_apply_elastic_connector": ("安全", "batch58 同上"),
    "solidworks_simulation_apply_temperature": ("安全", "batch58 同上（★ 文件头「不注册」的注释与代码不符，工具实际已注册）"),
    "solidworks_simulation_apply_distributed_mass": ("安全", "batch60 经 batch29 工厂"),
    "solidworks_simulation_apply_force": ("安全", "batch60 同上"),
    "solidworks_simulation_apply_remote_load": ("安全", "batch60 同上"),
    "solidworks_weldment_insert_end_cap": ("安全", "batch74 `pre_call=_select_faces_for(0, 1)`（按 mark 选 1 个面，回读计数，不够就抛）"),
    "solidworks_weldment_gusset_create": ("安全", "batch74 `pre_call=_select_faces_for(1, 2)`（官方 mark=1 · 两个面）"),
    "solidworks_sheet_metal_create_swept_flange": ("安全", "★ 非 `pre_call` 形态：batch4 `derived_args=_swept_refs_and_spec` 把选择器**解析成对象**塞进 `data.Path`/`data.Profile` ⇒ 选区不必活到第 4 步"),
}

# 真危险：名称 → (子类, 出处路, 依据, 待补依据?)
DANGER = {
    # ── 官方前置 · 静默失败 ──────────────────────────────────────────────
    "solidworks_mold_parting_line": ("真危险·官方前置", "A",
        "`C:\\swapi\\types\\IFeatureManager\\InsertMoldPartingLine.md` Remarks 逐字：「Before calling this method, you must select the direction of pull and the edges for the parting line by calling IModelDocExtension::SelectByID2 with the following Marks: Direction of pull **1** / Parting line edges **4**」；`sw_mold.py::insert_parting_line` 函数体只有 `InsertMoldPartingLine`，一个实体都不选", False),
    "solidworks_mold_parting_surface": ("真危险·官方前置（条件）", "A",
        "`InsertMoldPartingSurface.md` Remarks 逐字：「f a parting line feature does not yet exist in the model, you must first select the direction of pull and the edges for the parting line using IModelDocExtension::SelectByID2」⇒ ★ 仅当模型里还没有分型线时触发", False),
    "solidworks_add_sketch_relation": ("真危险·官方前置", "A",
        "`C:\\swapi\\types\\IModelDoc2\\SketchAddConstraints.md` **描述行**逐字：「Adds the specified constraint to the selected entities.」；`sw_part.py::add_sketch_relation` 函数体只有一句 `return model.SketchAddConstraints(relation_type)` ⇒ Python 体一个实体都不读，官方 API 隐式吃选区（★ 最隐蔽：没有任何报错线索）", False),
    "solidworks_part_insert_composite_curve": ("真危险·官方前置", "B",
        "`C:\\swapi\\types\\IModelDoc2\\InsertCompositeCurve.md` Remarks 逐字：「To use this method, select the entities by calling IModelDocExtension::SelectByID2 with a **mark number of 1**」", False),
    "solidworks_part_insert_dome": ("真危险·官方前置", "B",
        "`C:\\swapi\\types\\IModelDoc2\\InsertDome.md` Remarks 逐字：「Before using this method, you must select the face for the dome using a **selection mark of 1**.」", False),
    "solidworks_sketch_convert_entities": ("真危险·官方前置", "B",
        "`C:\\swapi\\types\\ISketchManager\\SketchUseEdge3.md` Remarks 逐字：「Specifying true for the Chain argument creates the **selected** sketch entity and any other sketch entities that belong to the same sketch contour or chain…」", False),
    "solidworks_sketch_create_chamfer": ("真危险·官方前置", "B",
        "`C:\\swapi\\types\\ISketchManager\\CreateChamfer.md` **描述行**逐字：「Creates a chamfer **between two selected sketch entities**.」（★ 该页无 `## Remarks` 段 ⇒ 证据在描述行）", False),
    "solidworks_sketch_mirror": ("真危险·官方前置", "B",
        "`C:\\swapi\\types\\IModelDoc2\\SketchMirror.md` Remarks 逐字：「If the entity to mirror is: a sketch segment, then use a **selection mark of 1**; a centerline, then use a **selection mark of 2**.」★ 复核改正：B 路写的路径 `ISketchManager/SketchMirror.md` **不存在**，正确路径是 `IModelDoc2/SketchMirror.md`", False),
    "solidworks_sketch_stretch_entities": ("真危险·官方前置", "C",
        "`C:\\swapi\\types\\IModelDocExtension\\Stretch.md` **描述行**逐字：「Stretch the **selected** entities.」（★ 该页无 `## Remarks` 段）", False),
    "solidworks_insert_planar_surface": ("真危险·官方前置", "C",
        "`C:\\swapi\\types\\IModelDoc2\\InsertPlanarRefSurface.md` Remarks 逐字：「Before calling this method, select the surface's boundary entities using IModelDocExtension::SelectByID2 with **Marks of 1**.」", False),
    "solidworks_insert_offset_surface": ("真危险·官方前置", "C",
        "`C:\\swapi\\types\\IModelDoc2\\InsertOffsetSurface.md` Remarks 逐字：「**Make the selections using IModelDocExtension::SelectByID2 before calling this method.**」★ **经复核改正**：能力层 docstring 写「★ 官方没写\"要不要先选面\"」**与官方页不符** —— 官方明写了；档位成立且证据应升到官方级", False),
    "solidworks_insert_ruled_surface": ("真危险·官方前置", "C",
        "`C:\\swapi\\types\\IFeatureManager\\InsertRuledSurfaceFromEdge2.md` Remarks 逐字：「If you select an edge with a **selection mark of 4**, the default face is used.」", False),
    "solidworks_insert_replace_face": ("真危险·官方前置", "C",
        "`C:\\swapi\\types\\IModelDoc2\\InsertFeatureReplaceFace.md` Remarks 逐字：「Before calling this method, select the faces to replace by calling IModelDocExtension::SelectByID2 with **Marks of 1** and select the replacement surfaces … with **Marks of 2**.」", False),
    "solidworks_insert_lofted_ref_surface": ("真危险·官方前置", "C",
        "`C:\\swapi\\types\\IModelDoc2\\InsertLoftRefSurface2.md` Remarks 逐字：「Use IModelDocExtension::SelectByID2 to select the profiles and guide curves. The mark for: **profile selections should be 1**」", False),
    "solidworks_create_revolved_surface": ("真危险·官方前置", "C",
        "`C:\\swapi\\types\\IFeatureManager\\InsertRevolvedRefSurface.md` Remarks 逐字：「**Make the selections using IModelDocExtension::SelectByID2 before calling this method.**」★ 官方**没给 mark** ⇒ 修的时候不能假定", False),
    "solidworks_insert_ref_plane": ("真危险·官方前置", "C",
        "`C:\\swapi\\types\\IFeatureManager\\InsertRefPlane.md` Remarks 逐字：「Before calling this method, you must have selected the reference entities using these marks with IModelDocExtension::SelectByID2: **0 = First reference entity · 1 = Second · 2 = Third**」", False),
    "solidworks_topology_create_preserved_region": ("真危险·官方前置", "A",
        "`sw_topology.py::create_preserved_region` docstring：「⚑ 调用方须**先选好要保留的面**再调本函数」；函数体只有 `CreatePreservedRegionControl` + `SetIncludeRegionDepth2`。★ **官方依据缺失**：`Get-ChildItem C:\\swapi -Recurse -Filter *.md | Select-String \"CreatePreservedRegionControl\"` ⇒ **0 命中**（复核已重跑）", True),
    "solidworks_topology_create_symmetry_control": ("真危险·官方前置", "A",
        "`sw_topology.py::create_symmetry_control` docstring：「调用方须先选好对称平面」；`tool_specs_batch12.py` doc 亦写「The caller must first select the symmetry plane(s)」★ **官方依据缺失**：`C:\\swapi` 检索 `CreateSymmetryControl` ⇒ **0 命中**（复核已重跑）", True),
    "solidworks_topology_create_demold_control": ("真危险·官方前置", "A",
        "`sw_topology.py::create_demold_control` docstring：「调用方须先选好拔模方向的面/边/基准面」；`tool_specs_batch12.py` doc 亦写「The caller must first select the pull-direction face/edge/plane」★ **官方依据缺失**：`C:\\swapi` 检索 `CreateDemoldControl` ⇒ **0 命中**（复核已重跑）", True),
    "solidworks_weldment_create_profile_center_mate": ("真危险·官方前置", "B",
        "`sw_weldment.py::create_profile_center_mate` docstring「在所选实体间创建型材中心配合」+ `raise ValueError(\"entities 为 None：须先选中要配合的实体\")` + `set_com_member(data, \"EntitiesToMate\", entities)`；而 `tool_specs_batch35.py` 的 `Param(\"entities\", str, default=\"__current_selection__\")` 是**字符串直传**（无 `param_alias` / 无 `pre_call` / 无 `derived_args`）⇒ 声明式选择根本没被解析。★ **官方依据缺失**：`IProfileCenterMateData` 在 `C:\\swapi` 下**无命中**（本轮实测）⇒ ★ 官方 mark 无法引用", True),
    # ── 真危险·显式拒（代码自己读计数并拒）─────────────────────────────────
    "solidworks_measure_selection": ("真危险·显式拒", "B",
        "`sw_measure.py::measure_selection_report`：`sel_n = int(_get(_get(model, \"SelectionManager\"), \"GetSelectedObjectCount2\", -1))` ＋ `if sel_n == 0: return {\"ok\": False, \"stage\": \"selection\", …}` ⇒ 经工具层**必然失败**", False),
    "solidworks_part_loft": ("真危险·显式拒", "B",
        "`sw_loft.py::create_loft_report`：`if use_selected_profiles and sel_n < 2: return {\"ok\": False, \"stage\": \"selection\", \"error\": \"放样至少要选 **2 个轮廓**（★ mark=1 —— 官方 Remarks）…\"}`", False),
    "solidworks_part_sweep": ("真危险·显式拒", "B",
        "`sw_sweep.py::create_sweep_report`：`for mark, label in ((1, \"profile\"), (4, \"path\"), (2, \"guide\"))` 回读 ＋ `if sel.get(\"profile\", 0) < 1 or sel.get(\"path\", 0) < 1: return {\"ok\": False, \"stage\": \"selection\", …}`", False),
    "solidworks_part_axis": ("真危险·显式拒", "B",
        "`sw_part.py::create_axis_report`：`if sel_n == 0: return {\"ok\": False, \"stage\": \"selection\", \"error\": \"建轴要先选中几何…\"}`", False),
    "solidworks_part_wrap": ("真危险·显式拒", "B",
        "`sw_wrap.py::create_wrap_report`：`for mark, label in ((4, \"sketch\"), (1, \"face\"))` ＋ `if sel.get(\"sketch\", 0) < 1 or sel.get(\"face\", 0) < 1: return {\"ok\": False, \"stage\": \"selection\", …}`", False),
    # ── 真危险·诊断型（恒回 0；是受害者链的源头，不是受害者本身）──────────────
    "solidworks_selection_count": ("真危险·诊断型", "C",
        "`sw_selection_spec.py::get_selection_count`：`get_com_member(sm, \"GetSelectedObjectCount2\", -1)`；spec 无 `pre_call`/`derived_args` ⇒ 经工具层**恒回 0**（事实 503：`RESOLVERS[\"model\"]` 会清空选区）", False),
    "solidworks_resolve_selection": ("真危险·诊断型", "C",
        "`sw_selection_spec.py::resolve_selection`：`count = get_selection_count(model)` ＋ `raise EntitySelectionError(\"选择器 %r 解析后**选区计数为 0**\")` ⇒ `__current_selection__` 路径必失败", False),
    "solidworks_selection_point": ("真危险·诊断型", "C",
        "`sw_selection_spec.py::selection_point`：`if not out[\"selection_count\"]: out[\"error\"] = \"当前**没有选中任何东西** ⇒ 读不到点。…\"`", False),
    "solidworks_resolve_entity": ("真危险·诊断型", "C",
        "`sw_selection_spec.py::resolve_entity_report`：`out[\"count\"] = int(get_selection_count(model))` ＋ `\"解析出了对象**而选区计数为 0** ⇒ 选择器是 __current_selection__ 时\"`", False),
    "solidworks_current_selection": ("真危险·诊断型", "A",
        "★ **经复核改正**：A 路判「无关（回读方向）」。按与其余 4 条**同一判据**（真的读选区 ＋ 无 `pre_call`）复核后改判。`sw_selection_spec.py::current_selection`：`count = get_selection_count(model)` ＋ `get_com_member(sm, \"GetSelectedObject6\", i, int(mark))` ⇒ **确实读选区**；`tool_specs_batch5.py` 的 spec **无 `pre_call`/`derived_args`**", False),
    # ── 真危险·条件 ──────────────────────────────────────────────────────
    "solidworks_insert_reference_point": ("真危险·条件", "C",
        "★ 依据链**比同表其它条弱一档**：`C:\\swapi\\types\\IFeatureManager\\InsertReferencePoint.md` 的 `## Remarks` **只写 NumberOfRefPoints 必须为 1、没有选区句**；唯一依据是 `tool_specs_batch70.py` 的 spec doc 真机记录「先选一个面（mark=0）+ `FaceCenter(4)` ⇒ 树新增 `点1`」「★★ 而选面**必须紧接着调用**」⇒ 仅对 `FaceCenter(4)`/`FaceVertexProjection(5)` 等部分 `ref_point_type` 成立", True),
    "solidworks_insert_global_bounding_box": ("真危险·条件", "C",
        "`InsertGlobalBoundingBox2.md` Remarks 逐字：「**If** BBoxType is set to swGlobalBoundingBoxFitOptions_e.swBoundingBoxType_**CustomPlane**, then select a face or plane using IModelDocExtension::SelectByRay … before calling this method.」⇒ ★ 仅 `bbox_type=2` 触发；默认 `BestFit(1)` 不需要", False),
    # ── 真危险·软失败（前置真，但代码不硬拒：只报 preconditions_held 后仍尝试）──
    "solidworks_drawing_create_auxiliary_view": ("真危险·软失败", "C",
        "`C:\\swapi\\types\\IDrawingDoc\\CreateAuxiliaryViewAt2.md` **描述行**逐字：「Creates an auxiliary view **based on a selected edge in a drawing view**.」（★ 该页无 `## Remarks`）；`sw_drawing_create_missing.py::create_auxiliary_view` 只把 `sel = _selection_count(model)` 写进 `preconditions_held`，**仍然调** `CreateAuxiliaryViewAt2`", False),
    "solidworks_drawing_insert_datum_tag": ("真危险·软失败", "C",
        "`C:\\swapi\\types\\IModelDoc2\\InsertDatumTag2.md` **描述行**逐字：「Inserts a datum tag symbol **at a selected location**.」（★ 该页无 `## Remarks`）；官方**零参数** ⇒ 落点完全由选区决定；函数只报 `preconditions_held` 后仍调 `InsertDatumTag2()`", False),
    "solidworks_drawing_insert_surface_finish_symbol": ("真危险·软失败", "C",
        "`C:\\swapi\\types\\IModelDocExtension\\InsertSurfaceFinishSymbol3.md` **描述行**逐字：「Creates a surface-finish symbol **based on the last selection**.」；函数只把 `sel = _selection_count(model)` 写进 `preconditions_held` 后仍调", False),
    "solidworks_drawing_create_section_view": ("真危险·软失败", "C",
        "`C:\\swapi\\types\\IDrawingDoc\\CreateSectionViewAt5.md` Remarks 逐字：「**Before calling this method, select the section line or lines to use as a section line.**」；`sw_drawing_expose.py::create_section_view` 只 `pre = _selection_count(drawing_model)` 写进 `pre_ok`，**仍然调**", False),
}

# ★ 经复核改正为「无关」的（原候选判真危险）
CORRECTED_OUT = {
    "solidworks_surface_fill": ("B",
        "★ **经复核改正**：原判「真危险」，实为**无关（可降级）**。依据 `scripts/sw_surface_features.py::insert_fill_surface_report`：声明式分支回读计数为 0 时 **不失败、而是回退**——`_selected_readback <= 0` ⇒ 设 `_fallback_note` 并把 `_declarative` 置 False ⇒ 走 `ext.SelectByID2(\"\", \"EDGE\", 中点, True, MARK_BOUNDARY, callout, 0)` 自动选边路径（★ 在 inject 之后执行 ⇒ 不受影响，**真机建成过**）⇒ 传 `selection` 也**不会失败**。注：官方前置本身是真的（`InsertFillSurface2.md` Remarks 逐字「You must use IModelDocExtension::SelectByID2 and the following Mark values … Boundary curves = 1」）"),
    "solidworks_drawing_create_hole_table": ("C",
        "★ **经复核改正**：原判「真危险」，实为**无关（告警后仍尝试）**。依据 `scripts/sw_drawing_expose.py::create_hole_table`：`if not pre:` 段（源码内注「★★ 2026-10-03（接手轮）**从\"硬失败\"改成\"告警后仍然尝试**」⇒ 记 `preconditions_held: False` + `attempted_without_precondition: True` 后**仍然调** `InsertHoleTable3`）⇒ 不因选区为空而必然失败。注：官方前置本身是真的（`InsertHoleTable3.md` Remarks 逐字「…**pre-selected** holes… datum origin that is also **pre-selected**…Before calling this method, call …」）"),
    "solidworks_helix_insert": ("B",
        "★ **经复核改正**：原判「真危险」，实为**无关**。官方示例 `C:\\swapi\\examples\\Create_Spiral_Example_VB.md` 在调 `InsertHelix` **之前**执行 `swModel.ClearSelection2 True` 且**并未选中圆**（只 `SelectByID2(\"Front Plane\",\"PLANE\",…)` 选基准面后建圆）⇒ ★ 前置是「**活动草图里有圆**」，**不是选区**。另：能力层 `sw_helix.py::insert_helix` docstring 写「官方示例显示要先**选中一个圆**（`SelectByID2` + `CreateCircle`）」**与示例不符**（把选基准面的 `SelectByID2` 与建圆混为一谈）。★ `tool_specs_batch39.py` 的 spec doc 自己写的才是对的：「Needs the document state the official API requires (a circular sketch to revolve about)」"),
    "solidworks_drawing_add_note": ("C",
        "★ **经复核改正**：原判「真危险」，实为**无关（官方明示降级）**。依据 `C:\\swapi\\types\\IModelDoc2\\InsertNote.md` Remarks 逐字：「The leader attachment points for the new note come from the selections made before calling this method. … **If there are no selections, the note: Does not have a leader / Is free standing / Is at the origin of the model or drawing**」⇒ 无选区也能建，只是没引线。spec doc 自己也记了真机证据「两格（选中 / 不选）都返回非 None」"),
}

# ★ 三路都漏报、但本轮扫出来的（真危险之外，仅补齐覆盖）
MISSED_NOTE = {
    "solidworks_hole_wizard": ("无关（自建选区）· ★ **三路均未出现在报告里**（batch72）",
        "`sw_hole_features.py::create_hole_wizard_at_selection_report` **自己建选区**：`model.ClearSelection2(True)` ＋ `ext.SelectByRay(sx, sy, sz, …, int(SW_SEL_FACES), False, 0, 0)` ⇒ 它只 `GetSelectedObjectCount2(-1)` **回读自己那条射线**的结果（`if not ok_ray or sel_n < 1: raise`）⇒ **不是**受害者。补录以保证总表覆盖 277 条"),
}

NEUTRAL_REASON = {
    "solidworks_clear_selection": "清选区（`ClearSelection2`）",
    "solidworks_clear_selection_for_preview": "清选区（`ClearSelection2`）",
    "solidworks_entities_on_body": "**不读选区**：走 `GetBodies2` + `IBody2.GetEdges/GetFaces/GetVertices` 按序号枚举（★ 与 `current_selection` 那一族不同，故 A 路判「无关」是对的）",
    "solidworks_select_by_selector": "**自建选区**：`select_object(...)` 按序号自己选",
    "solidworks_select_entity_by_index": "**自建选区**：按序号自己 `Select4`",
    "solidworks_select_face_selector": "**自建选区**：`resolve_face_selector(model, selection)`",
    "solidworks_surface_knit": "**自建选区**：`_select_all_surface_faces` 先 `ClearSelection2` 再按 mark 选全部面",
    "solidworks_surface_extend": "**自建选区**：复用 `_select_all_surface_faces`；spec doc 自记「不选面它也能成（★ 真机实测）」",
    "solidworks_gtol_insert": "**软依赖**：官方明说没选中时符号无引线、独立存在（降级不成失败）",
    "solidworks_part_shell": "**软依赖**：`faces_to_remove` 未暴露、函数体 `InsertFeatureShell(thickness, False)` 不读选区",
    "solidworks_sketch_fully_defined_status": "前置是「**必须有活动草图**」，不是选区前置",
    "solidworks_drawing_create_projected_view": "前置是「`part_path` 必须已存盘」，不是选区前置",
    "solidworks_drawing_create_detail_view": "前置是「图上有局部圆（草图圆）」，不是选区前置",
    "solidworks_drawing_create_broken_view": "源码自记「★ **零选区前置**」",
    "solidworks_mold_draft_analysis": "会弹模态框，但**不读选区**（另一类问题，非本族）",
    "solidworks_mold_undercut_detect": "方向由 `Dx/Dy/Dz` 显式给 ⇒ 不依赖选区（但会弹模态框，另一类问题）",
}


def main():
    specs = json.loads((RECON / "_all_specs.json").read_text(encoding="utf-8"))["specs"]
    specs.sort(key=lambda s: (int(re.search(r"batch(\d+)", s["file"]).group(1)), s["name"]))
    rows = []
    for s in specs:
        n = s["name"]
        if n in DANGER:
            sub, fam, ev, todo = DANGER[n]
            rows.append(dict(n=n, file=s["file"], mod=s["module"], fn=s["function"],
                             reads="是", pre="否", grade=sub, fam=fam, ev=ev, todo=todo))
        elif n in SAFE:
            g, ev = SAFE[n]
            rows.append(dict(n=n, file=s["file"], mod=s["module"], fn=s["function"],
                             reads="是", pre="是", grade=g, fam="-", ev=ev, todo=False))
        elif n in CORRECTED_OUT:
            fam, ev = CORRECTED_OUT[n]
            rows.append(dict(n=n, file=s["file"], mod=s["module"], fn=s["function"],
                             reads="是", pre="否", grade="无关（经复核改正）", fam=fam, ev=ev, todo=False))
        elif n in MISSED_NOTE:
            g, ev = MISSED_NOTE[n]
            rows.append(dict(n=n, file=s["file"], mod=s["module"], fn=s["function"],
                             reads="是（自建）", pre="否", grade=g, fam="—", ev=ev, todo=False))
        else:
            why = NEUTRAL_REASON.get(n, "目标函数不读选区（自选 / 按名选 / 清选区 / 只读遍历 / 纯数据）")
            rows.append(dict(n=n, file=s["file"], mod=s["module"], fn=s["function"],
                             reads="否", pre="否", grade="无关", fam="-", ev=why, todo=False))
    out = dict(rows=rows, n=len(rows))
    (RECON / "_merged_rows.json").write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                            encoding="utf-8")
    from collections import Counter
    c = Counter(r["grade"] for r in rows)
    for k, v in sorted(c.items(), key=lambda x: -x[1]):
        print(f"{v:4}  {k}")
    print("-" * 40)
    print("total:", len(rows))
    print("待补依据:", sum(1 for r in rows if r["todo"]))


if __name__ == "__main__":
    main()