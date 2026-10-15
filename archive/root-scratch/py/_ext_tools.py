import re, io
from pathlib import Path
o = io.StringIO()
# (op, [(clone_dir, filename_hint)], tool_names_in_source)
JOBS = [
 ("bodies/sheet/edges/faces/vertices/point/view/mates  [Slacker-LLC]",
  Path(r"C:\swprojects\Slacker-LLC"),
  ["'bodies'","'sheet'","'edges'","'faces'","'vertices'","'point'","'view'","'mates'","'delete_feature'","'rename_feature'"]),
 ("hide_all_planes/show_all_planes/fold/projected_curve/select_entity/view_rotate  [Eduardof0nt]",
  Path(r"C:\swprojects\Eduardof0nt"),
  ["'hide_all_planes'","'show_all_planes'","'fold'","'projected_curve'","'select_entity'","'view_rotate'","'unsuppress_feature'","'gdt'","'composite_curve'"]),
 ("classify_feature_tree/execute_workflow/optimize_performance/update_title_block/units/load_part/file_properties/rename_feature  [andrewbartels1]",
  Path(r"C:\swprojects\andrewbartels1"),
  ["'classify_feature_tree'","'execute_workflow'","'optimize_performance'","'update_title_block'","'units'","'load_part'","'file_properties'","'rename_feature'","'model_info'"]),
 ("vespo92 vba_* + macro security + grayscale  [vespo92]",
  Path(r"C:\swprojects\SolidworksMCP-TS"),
  ["'vba_advanced_features'","'vba_api_automation'","'vba_error_handling'","'vba_custom_properties'","'vba_pdm_operations'","'macro_set_security'","'macro_get_security_info'","'set_view_grayscale_enhanced'","'update_sheet_format'","'solidworks_operations'"]),
]
for label, root, names in JOBS:
    o.write("\n"+"#"*95+"\n## %s\n" % label)
    for name in names:
        o.write("\n--- tool %s ---\n" % name)
        found = False
        for p in sorted(root.rglob("*")):
            if not p.is_file(): continue
            if p.suffix.lower() not in (".py",".ts",".js"): continue
            if "node_modules" in str(p) or ".git" in str(p) or "__tests__" in str(p): continue
            try: txt = p.read_text(encoding="utf-8", errors="ignore")
            except Exception: continue
            rx = re.compile(r"name\s*[:=]\s*" + re.escape(name))
            for m in rx.finditer(txt):
                found = True
                s = max(0, m.start()-200); e = min(len(txt), m.end()+900)
                o.write("  >>> %s\n%s\n" % (p.relative_to(root), txt[s:e].replace("\r","")))
                break
            if found: break
        if not found: o.write("  (NOT FOUND as a tool name literal)\n")
open(r"D:\AI\SW\_ext_tools.txt","w",encoding="utf-8").write(o.getvalue())
print("ok len=%d" % len(o.getvalue()))
