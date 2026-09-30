import re, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

def tool_names(path: Path, label: str) -> set:
    names = set()
    for f in path.rglob("*"):
        if not f.is_file() or f.suffix not in (".py", ".ts", ".cs"): continue
        if any(x in str(f) for x in (".venv","node_modules","site-packages",".git","__pycache__","test","dist","build")): continue
        try: t = f.read_text(encoding="utf-8", errors="ignore")
        except Exception: continue
        names |= set(re.findall(r'@mcp\.tool\(\s*\n?\s*name\s*=\s*"([^"]+)"', t))
        names |= set(re.findall(r'@mcp\.tool\s*\n\s*(?:async\s+)?def\s+([a-z]\w+)', t))
        names |= set(re.findall(r'\{\s*name:\s*[\'"]([a-z][a-z0-9_]{3,})[\'"]', t))
        names |= set(re.findall(r'name="([a-z][a-z0-9_]{3,})"\s*,?\s*\n\s*title=', t))
        names |= set(re.findall(r'@tool\(\s*[\'"]([a-z][a-z0-9_]{3,})[\'"]', t))
    return names

# Slacker 的 README 工具名（人工抄自其 README 的分段表）
slacker = set("""solidworks_status get_active_document_info create_new_document open_document save_document
save_active_document export_document rebuild_document set_appearance set_material list_reference_planes
create_plane create_axis create_sketch edit_sketch close_sketch list_sketches list_sketch_segments
get_sketch_status draw_line draw_centerline draw_circle draw_rectangle draw_arc draw_3point_arc
draw_ellipse draw_polygon draw_slot draw_point draw_spline sketch_fillet sketch_chamfer sketch_trim
sketch_offset sketch_mirror convert_entities set_construction_geometry add_relation add_dimension
set_dimension list_dimensions boss_extrude cut_extrude revolve fillet chamfer shell draft rib
simple_hole sweep loft linear_pattern circular_pattern mirror_feature delete_feature rename_feature
set_feature_suppression capture_screenshot list_faces list_edges list_vertices list_bodies
get_mass_properties get_bounding_box measure check_errors set_view list_components insert_component
add_mate list_mates set_component_fixed create_drawing list_sheets add_sheet activate_sheet
insert_standard_views insert_model_view insert_projected_view insert_section_view insert_detail_view
list_drawing_views activate_drawing_view create_drawing_sketch set_drawing_view insert_model_annotations
auto_dimension_view insert_center_marks insert_centerlines add_note""".split())

sets = {"Slacker-LLC(README)": slacker}
for label, p in [("vespo92 TS", r"C:\swprojects\SolidworksMCP-TS"),
                 ("SolidPilot", r"C:\swprojects\mcp-server-solidworks"),
                 ("alisamsam", r"C:\swprojects\Solidworks-MCP"),
                 ("q3ds", r"C:\swprojects\q3ds-solidworks-mcp"),
                 ("我们(上游 MCP)", r"C:\swprojects\sw-skill-fork\mcp-server")]:
    q = Path(p)
    if q.exists(): sets[label] = tool_names(q, label)

DOM = {
 "仿真": r"simulat|cosworks|fea|study|static|thermal|frequency|buckling",
 "动画/Motion": r"motion|animat|anim",
 "拓扑": r"topolog",
 "钣金": r"sheet|flange|bend|unfold|flat_?pattern",
 "焊件": r"weld|gusset|structural",
 "曲面": r"surface|loft|sweep|boundary",
 "方程/表": r"equation|design_?table|driving",
 "成本": r"cost",
 "PDM": r"pdm|vault|revision",
 "路由": r"routing|pipe|tube|harness|cable",
 "DFM": r"dfm|manufactur|machin",
 "公差": r"dimxpert|toleranc|gd_?t|fit",
 "阵列/模式": r"pattern|mirror|array",
}
print("%-18s %5s %s" % ("项目", "工具", " ".join("%-7s" % k for k in DOM)))
for label, names in sets.items():
    row = []
    for k, rx in DOM.items():
        hit = [n for n in names if re.search(rx, n, re.I)]
        row.append("%-7s" % ("✓%d" % len(hit) if hit else "·"))
    print("%-18s %5d %s" % (label, len(names), " ".join(row)))
print()
print("=== 各项目在「仿真/动画/拓扑」上的具体工具 ===")
for label, names in sets.items():
    hit = sorted(n for n in names if re.search(r"simulat|cosworks|fea|motion|animat|topolog|study", n, re.I))
    if hit: print("  %-18s %s" % (label, ", ".join(hit[:10])))