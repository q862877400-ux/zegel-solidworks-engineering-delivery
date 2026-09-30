import sys
sys.stdout.reconfigure(encoding="utf-8")
# Slacker-LLC README 里逐个域抄下来的工具（原文分段）
slacker = {
 "会话/文档": "solidworks_status get_active_document_info create_new_document open_document save_document save_active_document export_document rebuild_document set_appearance set_material",
 "参考几何": "list_reference_planes create_plane create_axis",
 "草图·几何": "draw_line draw_centerline draw_circle draw_rectangle draw_arc draw_3point_arc draw_ellipse draw_polygon draw_slot draw_point draw_spline",
 "草图·编辑": "sketch_fillet sketch_chamfer sketch_trim sketch_offset sketch_mirror convert_entities set_construction_geometry",
 "草图·参数": "add_relation add_dimension set_dimension list_dimensions",
 "实体特征": "boss_extrude cut_extrude revolve fillet chamfer shell draft rib simple_hole sweep loft linear_pattern circular_pattern mirror_feature delete_feature rename_feature set_feature_suppression",
 "检查/反馈": "capture_screenshot list_faces list_edges list_vertices list_bodies get_mass_properties get_bounding_box measure check_errors set_view",
 "装配": "list_components insert_component add_mate list_mates set_component_fixed",
 "工程图": "create_drawing list_sheets add_sheet activate_sheet insert_standard_views insert_model_view insert_projected_view insert_section_view insert_detail_view list_drawing_views activate_drawing_view create_drawing_sketch set_drawing_view insert_model_annotations auto_dimension_view insert_center_marks insert_centerlines add_note",
}
user_wants = {
 "装配体设计/装配关系": ["装配"],
 "参数化设计": ["草图·参数","草图·几何","草图·编辑"],
 "拓扑（拓扑优化）": [],
 "仿真": [],
 "动画": [],
 "钣金": [],
 "焊件": [],
 "曲面": [],
 "运动算例 Motion": [],
 "方程/设计表": [],
 "成本估算": [],
 "DFM": [],
}
allt = set()
for v in slacker.values(): allt |= set(v.split())
print("Slacker-LLC 实际工具数: %d" % len(allt))
print()
print("=== 对照你要的能力 ===")
for want, cover in user_wants.items():
    if cover:
        n = sum(len(slacker[c].split()) for c in cover)
        print("  ✅ %-22s 它有 %d 个工具（%s）" % (want, n, "+".join(cover)))
    else:
        print("  ❌ %-22s **它一个都没有**" % want)