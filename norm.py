import json, re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
res = json.loads(Path(r"D:\AI\SW\toolsets.json").read_text(encoding="utf-8"))
PREFIX = re.compile(r'^(sw_|solidworks_|cadstudio_|automation_|vba_|macro_|sketch_|draw_|create_|add_|insert_|set_|get_|list_)')
SYN = {
 "note": "annotation", "annotations": "annotation", "text_note": "annotation",
 "round": "fillet", "corner_round": "fillet",
 "hole_wizard": "hole", "simple_hole": "hole", "threaded_hole": "hole",
 "boss_extrude": "extrude", "extrusion": "extrude", "cut_extrude": "extrude_cut",
 "revolve_boss": "revolve",
 "mate": "mate", "mates": "mate", "add_mate": "mate",
 "screenshot": "screenshot", "capture": "screenshot", "photoview_screenshot": "screenshot",
 "suppress_feature": "suppress", "set_feature_suppression": "suppress",
 "unsuppress_feature": "unsuppress",
 "reference_plane": "ref_plane", "refplane": "ref_plane", "create_plane": "ref_plane",
 "reference_axis": "ref_axis", "create_axis": "ref_axis",
 "centerline": "centerline", "centerlines": "centerline", "add_centerlines": "centerline",
 "center_mark": "center_mark", "center_marks": "center_mark",
 "bom": "bom", "bom_table": "bom",
 "flat_pattern": "flat_pattern", "flatten": "flat_pattern",
 "structural_member": "structural_member", "weldment": "structural_member",
 "motion_study": "motion_study", "simulation_study": "simulation_study",
 "mass_properties": "mass_props", "material_properties": "mass_props",
 "bounding_box": "bbox",
 "custom_property": "custom_prop", "custom_properties": "custom_prop",
 "global_variable": "global_var", "global_variables": "global_var",
 "design_table": "design_table", "equation": "equation", "equations": "equation",
 "dimension": "dimension", "dimensions": "dimension",
 "sketch_dimension": "dimension",
 "geometric_tolerance": "gdt", "datum_feature": "gdt", "surface_finish": "gdt",
 "interference": "interference", "check_interference": "interference",
 "explode": "explode", "exploded_view": "explode",
 "drawing_view": "drawing_view", "model_view": "drawing_view",
 "section_view": "section_view", "detail_view": "detail_view",
 "projected_view": "projected_view", "auxiliary_view": "auxiliary_view",
 "broken_view": "broken_view", "standard_views": "standard_views",
 "extrude_surface": "surface", "planar_surface": "surface", "loft": "loft",
 "sweep": "sweep", "knit": "surface", "thicken": "surface",
 "hole_feature": "hole",
 "structural": "structural_member",
}
def norm(n: str) -> str:
    s = n.lower()
    s = re.sub(r'^(sw_|solidworks_|cadstudio_|automation_|vba_|macro_)', '', s)
    if s in SYN: return SYN[s]
    s2 = re.sub(r'^(create_|add_|insert_|set_|get_|list_|draw_|start_|make_|build_)', '', s)
    if s2 in SYN: return SYN[s2]
    return s2 or s
buckets = {}
for proj, tools in res.items():
    for t in tools:
        buckets.setdefault(norm(t), set()).add(proj)
PROJS = list(res.keys())
multi = {k: v for k, v in buckets.items() if len(v) >= 2}
print("归一后共 %d 个不同操作" % len(buckets))
print("  其中 ≥2 家有: %d 个（真重叠，可择优抄）" % len(multi))
print("  只有 1 家有  : %d 个（真独有）" % (len(buckets) - len(multi)))
print()
print("=== 只有一家有的（别人都没做的）===")
for k, v in sorted(buckets.items()):
    if len(v) == 1:
        print("  %-34s %s" % (k, list(v)[0]))