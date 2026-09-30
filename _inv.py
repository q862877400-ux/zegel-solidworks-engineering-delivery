import ast, io, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
R = Path(r"C:\swprojects\sw-skill-fork\scripts")
MINE = ["sw_hubs","sw_drawing_annotations","sw_part_features","sw_sketch_sheetmetal",
        "sw_geometry","sw_simulation_registry","sw_simulation_full","sw_pdm_full",
        "sw_sldworks_remaining","sw_sldworks_lastgap","sw_routing_costing_full",
        "sw_sldworks_app","sw_model_doc_extension","sw_section_view",
        "sw_table_annotations","sw_document_core",
        "sw_api_sldworks","sw_api_cosworks","sw_api_swdocumentmgr",
        "sw_api_SWRoutingLib","sw_api_sldcostingapi","sw_api_fworks"]
print("=== 我新建模块里剩下的公开符号 ===")
for m in MINE:
    p = R/f"{m}.py"
    if not p.is_file(): continue
    t = ast.parse(p.read_text(encoding="utf-8"))
    fns = [n.name for n in t.body if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")]
    cls = [n.name for n in t.body if isinstance(n, ast.ClassDef)]
    if fns or cls: print("  %-24s 函数%s 类%s" % (m, fns, cls))
