import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
root = Path(r"C:\swprojects\sw-skill-fork")
# Slacker-LLC 的 92 个工具名（从它的 README 抄下来，用于覆盖判定）
slacker = set("""solidworks_status get_active_document_info create_new_document open_document
save_document save_active_document export_document rebuild_document set_appearance set_material
list_reference_planes create_plane create_axis
create_sketch edit_sketch close_sketch list_sketches list_sketch_segments get_sketch_status
draw_line draw_centerline draw_circle draw_rectangle draw_arc draw_3point_arc draw_ellipse
draw_polygon draw_slot draw_point draw_spline
sketch_fillet sketch_chamfer sketch_trim sketch_offset sketch_mirror convert_entities set_construction_geometry
add_relation add_dimension set_dimension list_dimensions
boss_extrude cut_extrude revolve fillet chamfer shell draft rib simple_hole sweep loft
linear_pattern circular_pattern mirror_feature delete_feature rename_feature set_feature_suppression
capture_screenshot list_faces list_edges list_vertices list_bodies
get_mass_properties get_bounding_box measure check_errors set_view
list_components insert_component add_mate list_mates set_component_fixed
create_drawing list_sheets add_sheet activate_sheet insert_standard_views insert_model_view
insert_projected_view insert_section_view insert_detail_view list_drawing_views activate_drawing_view
create_drawing_sketch set_drawing_view insert_model_annotations auto_dimension_view
insert_center_marks insert_centerlines add_note""".split())

# 我们 ⑥ 类里每个模块，对应的「操作域」
mapping = {
 "sw_sketch": "create_sketch/draw_*/edit_sketch",
 "sketch_relations": "add_relation/list_dimensions",
 "sw_drawing_view": "insert_*_view/add_drawing_view",
 "sw_view": "set_view",
 "sw_pattern": "linear_pattern/circular_pattern/mirror_feature",
 "sw_assembly_doc": "list_components/insert_component/add_mate",
 "sw_surface": "（Slacker 无曲面工具）",
 "sw_render_material": "set_appearance/set_material",
 "sw_simulation": "（Slacker 无仿真）",
 "sw_simulation_study": "（Slacker 无仿真）",
 "sw_simulation_study_options": "（Slacker 无仿真）",
 "sw_simulation_loads": "（Slacker 无仿真）",
 "sw_simulation_loadprops": "（Slacker 无仿真）",
 "sw_simulation_results": "（Slacker 无仿真）",
 "sw_routing": "（Slacker 无路由）",
 "sw_costing": "（Slacker 无 Costing）",
 "sw_pdm": "（Slacker 无 PDM）",
 "sw_featureworks": "（Slacker 无 FeatureWorks）",
}
overlap = nover = 0
print("%-30s %6s  %s" % ("模块", "行数", "Slacker 有对应吗"))
for s, desc in mapping.items():
    f = root / "scripts" / (s + ".py")
    n = len(f.read_text(encoding="utf-8", errors="ignore").splitlines()) if f.exists() else 0
    has = "无" not in desc
    if has: overlap += n
    else: nover += n
    print("%-30s %6d  %s  %s" % (s, n, "★ 有重叠" if has else "✅ 它没有", desc))
print()
print("⑥ 类里：与 Slacker 重叠 %d 行 / 它完全没有 %d 行" % (overlap, nover))