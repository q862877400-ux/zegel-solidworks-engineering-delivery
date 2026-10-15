import ast, io, re, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
REPO = Path(r"C:\swprojects\sw-skill-fork")
# ⚠ 只限本任务新建的模块（上游自有的 sw_part / sw_view / sw_sketch / sw_routing
#   / sw_selection / sw_hole_features 等**不动** —— 那是项目自己的 API）
MINE = ["sw_hubs","sw_drawing_annotations","sw_part_features","sw_sketch_sheetmetal",
        "sw_geometry","sw_simulation_registry","sw_simulation_full","sw_pdm_full",
        "sw_sldworks_remaining","sw_sldworks_lastgap","sw_routing_costing_full",
        "sw_sldworks_app","sw_model_doc_extension","sw_section_view",
        "sw_table_annotations","sw_document_core"]
KEEP = {
 # 通用入口（官方名的唯一通道）
 "call_hub","call_annotation","call_feature_data","call_entity","call_member",
 "call_sim","call_sheet_metal","call_sketch","call_geometry",
 # 带 try/finally 的选区事务（真行为）
 "edit_feature_selection","edit_sheet_metal_selection",
 # 转发上游 _select_by_id（带「面名随语言变」候选机制，复制会漂移）
 "select_by_id",
}
print("=== 本任务新建模块里的公开函数 ===")
mine_funcs = {}
total = 0
for m in MINE:
    p = REPO/"scripts"/f"{m}.py"
    if not p.is_file(): continue
    tree = ast.parse(p.read_text(encoding="utf-8"))
    pub = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)
           and not n.name.startswith("_") and n.name not in KEEP]
    if pub:
        mine_funcs[m] = pub
        total += len(pub)
        print("  %-26s %2d 个" % (m, len(pub)))
print("  合计 %d 个" % total)
print()
aff = {}
for t in sorted((REPO/"tests").glob("test_*.py")):
    s = t.read_text(encoding="utf-8")
    used = sorted({f for m in mine_funcs for f in mine_funcs[m]
                   if re.search(rf"\b{re.escape(f)}\b", s)})
    if used: aff[t.name] = used
print("=== 会受影响的测试文件 %d 个 ===" % len(aff))
for k,v in sorted(aff.items(), key=lambda x:-len(x[1])):
    print("  %-44s %d" % (k, len(v)))
