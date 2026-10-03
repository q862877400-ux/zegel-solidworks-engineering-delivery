"""★ S2-b 合并：静态抽工具名 + 逐条算建议工具名对覆盖率表的净影响（只读，不碰 COM）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（合并裁判的临时核算脚本）
# 文件:   specs/202-user-coverage-gaps/recon/_s2b_merge_cov.py
# 定位:   ★ 照 scan-S2b-ledger-vs-tools.md §〇·② 的 AST 抽名法 + gen_user_feature_coverage.py
#          的 CHECKLIST / _hit 口径，算三路候选的建议工具名对覆盖率表的净影响。
# 依据:   mcp-server/tool_specs_batch*.py（AST）+ server.py（AST）+ register_capabilities.BATCH_MODULES
#         + D:\SW-coverage-tool\gen_user_feature_coverage.py 的 CHECKLIST/_hit/FALSE_POS
# 许可:   本仓库 MIT。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import re
from pathlib import Path

REPO = Path(r"D:\AI\SW")
MCP = REPO / "mcp-server"
NAME_RE = re.compile(r"^(solidworks|cadstudio)_[a-z0-9_]+$")


def batch_modules() -> set[str]:
    tree = ast.parse((MCP / "register_capabilities.py").read_text(encoding="utf-8", errors="replace"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "BATCH_MODULES":
                    return {e.value for e in node.value.elts if isinstance(e, ast.Constant)}
    return set()


def tool_names() -> set[str]:
    out: set[str] = set()
    batches = batch_modules()
    for f in sorted(MCP.glob("tool_specs_batch*.py")):
        mod = f.stem
        if batches and mod not in batches:
            continue
        tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = None
                if isinstance(node.func, ast.Name) and node.func.id == "ToolSpec":
                    for kw in node.keywords:
                        if kw.arg == "name" and isinstance(kw.value, ast.Constant):
                            name = kw.value.value
                elif isinstance(node.func, ast.Name) and node.func.id == "_spec" and node.args:
                    if isinstance(node.args[0], ast.Constant):
                        name = node.args[0].value
                if isinstance(name, str) and NAME_RE.match(name):
                    out.add(name.lower())
    server = (MCP / "server.py").read_text(encoding="utf-8", errors="replace")
    for node in ast.walk(ast.parse(server)):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Attribute) and fn.attr == "tool":
                for kw in node.keywords:
                    if kw.arg == "name" and isinstance(kw.value, ast.Constant):
                        v = kw.value.value
                        if isinstance(v, str) and NAME_RE.match(v):
                            out.add(v.lower())
    return out


def checklist() -> list[tuple[str, str, tuple[str, ...]]]:
    src = Path(r"D:\SW-coverage-tool\gen_user_feature_coverage.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", "") == "CHECKLIST":
            return [tuple(ast.literal_eval(e)) for e in node.value.elts]
    return []


def hit(names: set[str], pats: tuple[str, ...]) -> list[str]:
    return sorted(n for n in names if any(p in n for p in pats))


# ── 三路候选的「建议 / 已存在」工具名（★ 已存在者标 (已有)）─────────────
PROPOSED: dict[str, tuple[str, list[str]]] = {
    # —— 路 a ——
    "sketch_primitives_b1": ("已有", [
        "solidworks_sketch_add_3point_rectangle", "solidworks_sketch_add_3point_center_rectangle",
        "solidworks_sketch_add_parallelogram", "solidworks_sketch_add_tangent_arc",
        "solidworks_sketch_add_3point_arc", "solidworks_sketch_add_partial_ellipse",
        "solidworks_sketch_add_parabola", "solidworks_sketch_add_conic",
        "solidworks_sketch_add_perimeter_circle"]),
    "sketch_edit_ops_b3": ("已有", [
        "solidworks_sketch_trim", "solidworks_sketch_extend", "solidworks_sketch_offset",
        "solidworks_sketch_fillet", "solidworks_sketch_linear_pattern",
        "solidworks_sketch_circular_pattern"]),
    "sketch_modify_ops": ("已有", [
        "solidworks_sketch_move_entities", "solidworks_sketch_rotate_entities",
        "solidworks_sketch_scale_entities", "solidworks_sketch_stretch_entities",
        "solidworks_sketch_flip_entities"]),
    "sketch_dimension_horizontal": ("新", ["solidworks_sketch_add_horizontal_dimension"]),
    "sketch_dimension_vertical": ("新", ["solidworks_sketch_add_vertical_dimension"]),
    "sketch_slot_types": ("新", ["solidworks_sketch_create_sketch_slot"]),
    "sketch_line2": ("新", ["solidworks_sketch_create_line2"]),
    "sketch_spline": ("已有", ["solidworks_sketch_spline"]),
    "sketch_spline3_2d": ("新", ["solidworks_sketch_create_spline3"]),
    "sketch_rotate_or_copy_3d": ("新", ["solidworks_sketch_rotate_or_copy_3d_sketch"]),
    "sketch_equation_curve": ("新", ["solidworks_sketch_equation_spline"]),
    "sketch_offset_on_surface": ("新", ["solidworks_sketch_offset_on_surface"]),
    "curve_and_split": ("新", [
        "solidworks_insert_split_line_project", "solidworks_insert_split_line_silhouette",
        "solidworks_insert_mate_reference", "solidworks_insert_curve_through_points"]),
    "curve_through_xyz": ("新", [
        "solidworks_insert_curve_through_points", "solidworks_insert_curve_file"]),
    # —— 路 b ——
    "surface_modeling": ("已有", ["cadstudio_create_ocp_surface", "cadstudio_create_ocp_loft"]),
    "surface_edit_ops": ("已有", [
        "solidworks_insert_planar_surface", "solidworks_insert_offset_surface",
        "solidworks_insert_ruled_surface", "solidworks_insert_delete_face",
        "solidworks_insert_replace_face"]),
    "surface_ref_ops": ("已有", ["solidworks_insert_lofted_ref_surface"]),
    "surface_thicken_silent_noop": ("已有", ["solidworks_thicken"]),
    "surface_offset": ("已有", ["solidworks_insert_offset_surface"]),
    "surface_planar_region": ("已有", ["solidworks_insert_planar_surface"]),
    "surface_revolve": ("已有", ["solidworks_create_revolved_surface"]),
    "surface_flatten": ("已有", ["solidworks_flatten_surface"]),
    "surface_untrim": ("新", ["solidworks_untrim_surface"]),
    "surface_delete_hole": ("新", ["solidworks_delete_hole_surface"]),
    "feature_readback_criterion": ("新", ["solidworks_feature_readback_criterion"]),
    "feature_revolve_cut": ("新", ["solidworks_revolve_cut"]),
    "feature_loft_cut": ("新", ["solidworks_loft_cut"]),
    "feature_cosmetic_thread": ("已有", ["solidworks_feature_cosmetic_thread"]),
    "feature_hole_wizard5": ("已有", ["solidworks_hole_wizard"]),
    # —— 路 c ——
    "autocad_basic_drafting": ("新", ["cadstudio_autocad_draw_brief"]),
    "autocad_script_backend": ("新", ["cadstudio_acad_script_run_command"]),
    "autocad_dotnet_backend": ("新", ["cadstudio_acad_dotnet_preflight"]),
    "animation_export": ("新", ["solidworks_motion_export_avi"]),
    "coverage_gap_batch1": ("已有", [
        "solidworks_create_revolved_surface", "solidworks_hole_wizard",
        "solidworks_sketch_fully_defined_status", "solidworks_sketch_move_entities"]),
    "drawing_dimension_insertion": ("新", ["solidworks_drawing_dimension_insert"]),
    "geometric_tolerance": ("已有", ["solidworks_gtol_insert"]),
    "ref_geometry": ("已有", [
        "solidworks_insert_ref_plane", "solidworks_insert_coordinate_system",
        "solidworks_insert_reference_point", "solidworks_insert_center_of_mass",
        "solidworks_insert_global_bounding_box"]),
    "render_material_library": ("新", [
        "solidworks_render_material_create", "solidworks_render_material_delete",
        "solidworks_list_render_materials"]),
    "replace_face": ("已有", ["solidworks_insert_replace_face"]),
    "requirements_planning": ("新", []),
    "select_by_ray": ("新", ["solidworks_select_by_ray"]),
}


def main() -> int:
    ours = tool_names()
    rows = checklist()
    print("工具名 %d 个 / CHECKLIST %d 项" % (len(ours), len(rows)))
    unhit = [(d, i, p) for d, i, p in rows if not hit(ours, p)]
    print("当前未命中行 %d 项：" % len(unhit))
    for d, i, p in unhit:
        print("  - (%s, %s) %s" % (d, i, p))
    print("\n逐条：建议/已存在工具名 → 命中的 CHECKLIST 行（★=当前未命中 ❌）")
    rank = []
    for cid, (kind, names) in PROPOSED.items():
        gains, allrows = [], []
        for n in names:
            for d, i, p in rows:
                if any(pn in n for pn in p):
                    mark = "*" if not hit(ours, p) else " "
                    allrows.append("%s%s/%s" % (mark, d, i))
                    if mark == "*":
                        gains.append("%s => (%s, %s)" % (n, d, i))
        rank.append((len(gains), len(allrows), cid, kind, gains, allrows))
    for ng, na, cid, kind, gains, allrows in rank:
        print("  %-30s [%-2s] 行 %d · 新增 %d  %s" % (
            cid, kind, na, ng, "；".join(gains) if gains else ""))
        if allrows:
            print("        " + " | ".join(allrows))
    print("\n按「新增未命中行」排序前 8：")
    for ng, na, cid, kind, gains, allrows in sorted(rank, reverse=True)[:8]:
        print("  %d 新增 / %d 命中行  %s [%s]" % (ng, na, cid, kind))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())