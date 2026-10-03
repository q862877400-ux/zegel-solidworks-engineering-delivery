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
        mod = f.stem.replace("tool_specs_batch", "batch")
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


# ── 三路候选的建议工具名 ─────────────────────────────────────────────
PROPOSED: dict[str, list[str]] = {
    "sketch_dimension_horizontal": ["solidworks_sketch_add_horizontal_dimension"],
    "sketch_dimension_vertical": ["solidworks_sketch_add_vertical_dimension"],
    "sketch_slot_types": ["solidworks_sketch_create_sketch_slot"],
    "sketch_line2": ["solidworks_sketch_create_line2"],
    "sketch_spline3_2d": ["solidworks_sketch_create_spline3"],
    "sketch_rotate_or_copy_3d": ["solidworks_sketch_rotate_or_copy_3d_sketch"],
    "sketch_equation_curve": ["solidworks_sketch_equation_spline"],
    "sketch_offset_on_surface": ["solidworks_sketch_offset_on_surface"],
    "curve_and_split": [
        "solidworks_insert_split_line_project",
        "solidworks_insert_split_line_silhouette",
        "solidworks_insert_mate_reference",
    ],
    "curve_through_xyz": ["solidworks_insert_curve_file"],
    "surface_untrim": ["solidworks_untrim_surface"],
    "surface_delete_hole": ["solidworks_delete_hole_surface"],
    "feature_revolve_cut": ["solidworks_revolve_cut"],
    "feature_loft_cut": ["solidworks_loft_cut"],
    "autocad_script_backend": ["cadstudio_acad_script_run_command"],
    "autocad_dotnet_backend": ["cadstudio_acad_dotnet_preflight"],
    "animation_export": ["solidworks_motion_export_avi"],
    "drawing_dimension_insertion": ["solidworks_drawing_dimension_insert"],
    "render_material_library": ["solidworks_render_material_create", "solidworks_render_material_delete"],
    "select_by_ray": ["solidworks_select_by_ray"],
}


def main() -> int:
    ours = tool_names()
    rows = checklist()
    print("工具名 %d 个 / CHECKLIST %d 项" % (len(ours), len(rows)))
    unhit = [(d, i, p) for d, i, p in rows if not hit(ours, p)]
    print("当前未命中行 %d 项：" % len(unhit))
    for d, i, p in unhit:
        print("  - (%s, %s) %s" % (d, i, p))
    print("\n逐条：建议工具名 → 命中的**当前未命中**行")
    for cid, names in PROPOSED.items():
        gains = []
        for n in names:
            for d, i, p in unhit:
                if any(pn in n for pn in p):
                    gains.append("%s ⇒ (%s, %s)" % (n, d, i))
        print("  %-28s %s" % (cid, "；".join(gains) if gains else "★ 净增 0 格"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())