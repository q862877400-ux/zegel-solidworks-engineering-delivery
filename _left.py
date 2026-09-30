import ast, io, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork\scripts")
MINE = ["sw_hubs","sw_drawing_annotations","sw_part_features","sw_sketch_sheetmetal",
        "sw_geometry","sw_simulation_registry","sw_simulation_full","sw_pdm_full",
        "sw_sldworks_remaining","sw_sldworks_lastgap","sw_routing_costing_full",
        "sw_sldworks_app","sw_model_doc_extension","sw_section_view",
        "sw_table_annotations","sw_document_core"]
for m in MINE:
    p = R/f"{m}.py"
    if not p.is_file(): continue
    t = ast.parse(p.read_text(encoding="utf-8"))
    pub = [n.name for n in t.body if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")]
    if pub: print("  %-26s %s" % (m, ", ".join(pub)))
