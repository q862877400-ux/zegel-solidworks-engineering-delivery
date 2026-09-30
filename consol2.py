import ast, re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
S = Path(r"C:\swprojects\sw-skill-fork\scripts")
# 删 6 份重复的 describe（调试助手，不是 API 通道）
n = 0
for p in sorted(S.glob("sw_api_*.py")):
    src = p.read_text(encoding="utf-8")
    m = re.search(r"\n\ndef describe\(.*\Z", src, re.S)
    if not m: continue
    p.write_text(src[:m.start()] + "\n", encoding="utf-8")
    ast.parse(p.read_text(encoding="utf-8"))
    n += 1
print("删掉 %d 份重复的 describe" % n)
# __all__ 同步
for p in sorted(S.glob("sw_api_*.py")):
    src = p.read_text(encoding="utf-8")
    src = src.replace('"call_index",\n           "describe"]', '"call_index"]')
    p.write_text(src, encoding="utf-8")
print("__all__ 已同步")
# 删掉只测已删模块的测试文件
T = Path(r"C:\swprojects\sw-skill-fork\tests")
GONE_MODULES = ["sw_hubs","sw_drawing_annotations","sw_part_features",
    "sw_sketch_sheetmetal","sw_geometry","sw_simulation_registry",
    "sw_simulation_full","sw_pdm_full","sw_sldworks_remaining",
    "sw_sldworks_lastgap","sw_routing_costing_full","sw_sldworks_app",
    "sw_model_doc_extension","sw_section_view","sw_table_annotations",
    "sw_document_core","sw_simulation_full","sw_pdm_full"]
d = 0
for t in sorted(T.glob("test_*.py")):
    s = t.read_text(encoding="utf-8")
    if any(re.search(rf"\b{m}\b", s) for m in GONE_MODULES):
        t.unlink(); d += 1
        print("  删测试", t.name)
print("删除 %d 个失效测试文件" % d)