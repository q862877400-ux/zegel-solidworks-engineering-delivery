"""★ 独立复核 41 条「真危险」候选：spec 侧（有无 pre_call/derived_args）+ 函数侧（是否读选区）。"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
MCP = ROOT / "mcp-server"
SCR = ROOT / "scripts"

CANDIDATES = [
    # family A
    "solidworks_mold_parting_line", "solidworks_mold_parting_surface",
    "solidworks_topology_create_preserved_region", "solidworks_topology_create_symmetry_control",
    "solidworks_topology_create_demold_control", "solidworks_add_sketch_relation",
    # family B
    "solidworks_part_insert_composite_curve", "solidworks_part_insert_dome",
    "solidworks_weldment_create_profile_center_mate", "solidworks_helix_insert",
    "solidworks_sketch_convert_entities", "solidworks_sketch_create_chamfer",
    "solidworks_sketch_mirror", "solidworks_surface_fill", "solidworks_measure_selection",
    "solidworks_part_loft", "solidworks_part_sweep", "solidworks_part_axis", "solidworks_part_wrap",
    # family C
    "solidworks_selection_count", "solidworks_resolve_selection", "solidworks_selection_point",
    "solidworks_resolve_entity", "solidworks_sketch_stretch_entities",
    "solidworks_insert_planar_surface", "solidworks_insert_offset_surface",
    "solidworks_insert_ruled_surface", "solidworks_insert_replace_face",
    "solidworks_insert_lofted_ref_surface", "solidworks_create_revolved_surface",
    "solidworks_insert_ref_plane", "solidworks_insert_reference_point",
    "solidworks_insert_global_bounding_box", "solidworks_drawing_create_auxiliary_view",
    "solidworks_drawing_insert_surface_finish_symbol", "solidworks_drawing_insert_datum_tag",
    "solidworks_sheet_metal_insert_miter_flange", "solidworks_sheet_metal_insert_closed_corner",
    "solidworks_drawing_create_section_view", "solidworks_drawing_create_hole_table",
    "solidworks_drawing_add_note",
]

SEL_TOKENS = ("GetSelectedObjectCount2", "GetSelectedObject6", "GetSelectionPoint",
              "SelectionManager", "resolve_selection", "resolve_entity",
              "_selection_count", "_selection_marks", "get_selection_count",
              "_get_selection_count", "select_selection")


def batch_of(name):
    m = re.search(r"batch(\d+)", name)
    return int(m.group(1)) if m else None


def find_spec_source(tool_name):
    """Return (file, source_text_of_enclosing_call, has_pre_call, has_derived, params)."""
    for f in MCP.glob("tool_specs_batch*.py"):
        txt = f.read_text(encoding="utf-8")
        if f'"{tool_name}"' not in txt:
            continue
        tree = ast.parse(txt)
        lines = txt.splitlines()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = ""
            n = node.func
            if isinstance(n, ast.Name):
                fn = n.id
            elif isinstance(n, ast.Attribute):
                fn = n.attr
            if fn not in ("ToolSpec", "_spec"):
                continue
            lits = []
            try:
                for a in list(node.args) + [k.value for k in node.keywords]:
                    v = ast.literal_eval(a)
                    if isinstance(v, str):
                        lits.append(v)
            except Exception:
                pass
            if tool_name not in lits:
                continue
            seg = "\n".join(lines[node.lineno - 1:node.end_lineno])
            has_pre = "pre_call" in seg
            has_der = "derived_args" in seg
            return f.name, seg, has_pre, has_der, tool_name
    return None, None, None, None, None


def func_source(module, function):
    p = SCR / f"{module}.py"
    if not p.exists():
        p2 = SCR / module / "__init__.py"
        if p2.exists():
            p = p2
        else:
            return None, None
    txt = p.read_text(encoding="utf-8")
    tree = ast.parse(txt)
    lines = txt.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function:
            seg = "\n".join(lines[node.lineno - 1:node.end_lineno])
            return seg, p.name
    return None, p.name


def main():
    allspecs = json.load(open(ROOT / "specs" / "202-user-coverage-gaps" / "recon" / "_all_specs.json",
                              encoding="utf-8"))["specs"]
    by_name = {s["name"]: s for s in allspecs}
    rows = []
    for t in CANDIDATES:
        s = by_name.get(t)
        f_name, seg, has_pre, has_der, _ = find_spec_source(t)
        fsrc, fname = (None, None)
        hits = []
        doc_has = {}
        if s and s["module"] and s["function"]:
            fsrc, fname = func_source(s["module"], s["function"])
            if fsrc:
                hits = sorted({tok for tok in SEL_TOKENS if tok in fsrc})
        doc = (s or {}).get("doc") or ""
        rows.append(dict(
            tool=t, batch=batch_of(f_name or ""), file=f_name,
            module=(s or {}).get("module"), function=(s or {}).get("function"),
            spec_pre_call=(s or {}).get("pre_call"), spec_derived=(s or {}).get("derived_args"),
            spec_inject=(s or {}).get("inject"),
            grep_pre_call_in_segment=has_pre, grep_derived_in_segment=has_der,
            func_file=fname, func_sel_tokens=hits,
            func_reads_sel=bool(hits),
            doc_mentions_sel=bool(re.search(r"select|selection|选中|选区|选好", doc, re.I)),
            has_selection_param=any(p.get("name") in ("selection", "entities", "path_selection",
                                                       "profile_selection", "sketch_name", "sketch_ref")
                                    for p in ((s or {}).get("params") or [])),
        ))
    out = ROOT / "specs" / "202-user-coverage-gaps" / "recon" / "_verify_41.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{'tool':52} {'b':>3} {'pre':>4} {'der':>4} {'selTok':>7} {'selParam':>8}")
    for r in rows:
        print(f"{r['tool'][:52]:52} {str(r['batch']):>3} "
              f"{str(bool(r['spec_pre_call'])):>4} {str(bool(r['spec_derived'])):>4} "
              f"{str(r['func_reads_sel']):>7} {str(r['has_selection_param']):>8}  "
              f"{r['func_file']}:{r['function']}  {r['func_sel_tokens']}")
    print()
    print("no func source found:", [r["tool"] for r in rows if r["func_file"] is None])
    print("no sel token:", [r["tool"] for r in rows if r["func_reads_sel"] is False])


if __name__ == "__main__":
    main()