import re, subprocess, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
MINE = ["sw_hubs","sw_drawing_annotations","sw_part_features","sw_sketch_sheetmetal",
        "sw_geometry","sw_simulation_registry","sw_simulation_full","sw_pdm_full",
        "sw_sldworks_remaining","sw_sldworks_lastgap","sw_routing_costing_full",
        "sw_sldworks_app","sw_model_doc_extension","sw_section_view",
        "sw_table_annotations","sw_document_core"]
d = subprocess.run(["git","diff","origin/main","--"]+["scripts/%s.py"%m for m in MINE],
                   capture_output=True, text=True, encoding="utf-8").stdout
gone = set(re.findall(r"^-\s*(?:def|    def) (\w+)\s*\(", d, re.M))
gone = {g for g in gone if not g.startswith("_")}
print("从 git diff 取到已删短名 %d 个" % len(gone))
Path = __import__("pathlib").Path
Path(r"D:\AI\SW\_gone.txt").write_text("\n".join(sorted(gone)), encoding="utf-8")
print("样例:", ", ".join(sorted(gone)[:10]))
