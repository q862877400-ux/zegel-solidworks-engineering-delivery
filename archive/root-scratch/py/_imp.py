import re, io, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
REPO = Path(r"C:\swprojects\sw-skill-fork")
OLD = ["sw_hubs","sw_drawing_annotations","sw_part_features","sw_sketch_sheetmetal",
       "sw_geometry","sw_simulation_registry","sw_simulation_full","sw_pdm_full",
       "sw_sldworks_remaining","sw_sldworks_lastgap","sw_routing_costing_full",
       "sw_sldworks_app","sw_model_doc_extension","sw_section_view",
       "sw_table_annotations","sw_document_core"]
fns = set()
for m in OLD:
    p = REPO/"scripts"/f"{m}.py"
    if not p.is_file(): continue
    for x in re.finditer(r"^def (\w+)\s*\(", p.read_text(encoding="utf-8"), re.M):
        if not x.group(1).startswith("_"): fns.add(x.group(1))
# 谁还在被引用（测试 + 其它脚本 + 文档）
users = {}
for t in sorted((REPO/"tests").glob("test_*.py")):
    s = t.read_text(encoding="utf-8")
    u = sorted(f for f in fns if re.search(rf"\b{f}\b", s))
    if u: users[t.name] = u
for p in sorted((REPO/"scripts").glob("*.py")):
    if p.stem in OLD: continue
    s = p.read_text(encoding="utf-8")
    u = sorted(f for f in fns if re.search(rf"\b{f}\b", s))
    if u: users["scripts/"+p.name] = u
print("待删/待改名符号 %d 个: %s" % (len(fns), ", ".join(sorted(fns))))
print()
print("仍被引用的地方 %d 处:" % len(users))
for k, v in sorted(users.items()): print("  %-46s %s" % (k, v))
