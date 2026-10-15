import re, io
from pathlib import Path
ROOT = Path(r"D:\AI\SW")
KW = {
 "advanced_features": r"advanced_feature|advanced features",
 "api_automation": r"api_automation",
 "arc": r"sketch_add_arc|add_3point_arc|create_arc|sketch_arc",
 "bodies": r"def .*\bbodies\b|solid_bodies|get_bodies|body_count|list_bodies",
 "classify_feature_tree": r"classify",
 "composite_curve": r"composite_curve",
 "delete_feature": r"feature_delete|delete_feature",
 "edges": r"\"EDGE\"|'EDGE'|entities_on_body",
 "error_handling": r"error_handling|explain_hresult|hresult",
 "execute_workflow": r"execute_workflow|workflow",
 "faces": r"\"FACE\"|'FACE'",
 "features": r"feature_list_names|feature_present|iter_features",
 "file_properties": r"custom_propert|file_propert",
 "fold": r"\bfold\b|unfold|flat_pattern",
 "gdt": r"gtol|gdt",
 "hide_all_planes": r"hide_all_planes|hide_plane|show_all_planes|plane.*visib",
 "line": r"sketch_add_line|create_line",
 "load_part": r"open_document|open_model|load_part",
 "mate": r"add_mate|_mate\b|list_mates",
 "mates": r"list_mates|mates_count",
 "model_info": r"collect_model_summary|model_info",
 "operations": r"operations",
 "optimize_performance": r"optimize_performance|performance",
 "pdm_operations": r"pdm",
 "point": r"reference_point|insert_reference_point",
 "projected_curve": r"projected_curve|project_curve",
 "rename_feature": r"rename",
 "rib": r"\brib\b|part_rib",
 "security": r"macro_security|security_level|SecurityLevel",
 "security_info": r"security_info|security",
 "select_entity": r"select_by_selector|select_entity_by_index|selection_count",
 "sheet": r"sheet_metal|drawing_sheet|current_sheet",
 "show_all_planes": r"show_all_planes|plane.*visib",
 "suppress": r"feature_suppress|suppress_component|_suppress",
 "units": r"read_document_units|SetUnits|swUnitsLinear|GetUnits",
 "unsuppress_feature": r"unsuppress",
 "update_sheet_format": r"set_sheet_format|SetTemplateName|update_sheet_format",
 "update_title_block": r"title_block",
 "vertices": r"VERTEX|GetVertices",
 "view": r"set_standard_view|active_view|view_get_",
 "view_grayscale_enhanced": r"grayscale|grey_scale|gray_scale",
 "view_rotate": r"rotate_about_center|roll_view|view_rotate",
}
targets = []
for p in sorted((ROOT/"mcp-server").glob("tool_specs_*.py")):
    targets.append(p)
targets.append(ROOT/"mcp-server"/"server.py")
targets += sorted((ROOT/"scripts").glob("sw_*.py"))
o = io.StringIO()
for op, pat in KW.items():
    rx = re.compile(pat, re.IGNORECASE)
    hits = []
    for p in targets:
        if p is None or not p.is_file(): continue
        for i, ln in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if rx.search(ln):
                hits.append("%s:%d: %s" % (p.name, i, ln.strip()[:150]))
    o.write("\n" + "="*90 + "\n### %s  (pat=%s)  hits=%d\n" % (op, pat, len(hits)))
    for h in hits[:14]: o.write("  " + h + "\n")
    if len(hits) > 14: o.write("  ... (+%d more)\n" % (len(hits)-14))
open(r"D:\AI\SW\_inv_grep.txt","w",encoding="utf-8").write(o.getvalue())
print("ok")
