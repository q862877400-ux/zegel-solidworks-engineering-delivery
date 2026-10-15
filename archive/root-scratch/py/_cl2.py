import ast, io, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
REPO = Path(r"C:\swprojects\sw-skill-fork\scripts")
MINE = ["sw_sldworks_app","sw_model_doc_extension","sw_section_view",
        "sw_table_annotations","sw_document_core","sw_hubs",
        "sw_drawing_annotations","sw_part_features","sw_sketch_sheetmetal",
        "sw_geometry","sw_simulation_registry","sw_sldworks_lastgap"]
FORWARD = {"_checked", "_call", "get_com_member"}
def stmt_calls(node):
    """函数体里被调用的名字集合（去掉转发层）。"""
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name): out.add(f.id)
            elif isinstance(f, ast.Attribute): out.add(f.attr)
    return out
def real_calls(node):
    return {c for c in stmt_calls(node) if c not in FORWARD
            and c not in ("len","list","int","str","float","bool","tuple","set","dict")}
alias, logic = [], []
for m in MINE:
    p = REPO / f"{m}.py"
    if not p.is_file(): continue
    tree = ast.parse(p.read_text(encoding="utf-8"))
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef): continue
        if node.name.startswith("_") or node.name in ("call_hub","call_annotation","call_feature_data","call_entity","call_member","call_sim","call_sheet_metal","call_sketch"):
            continue
        body = [n for n in node.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
        # 纯别名：函数体只调用转发层 + 内置转换，且**不含**循环/条件/异常
        has_ctrl = any(isinstance(n, (ast.For, ast.While, ast.If, ast.Try, ast.With)) for n in ast.walk(node))
        rc = real_calls(node)
        is_alias = (not has_ctrl) and rc <= {"len","list","int","str","float","bool","tuple","set","dict","type"}
        (alias if is_alias else logic).append((m, node.name))
print("纯别名（删）：%d" % len(alias))
print("带逻辑（留）：%d" % len(logic))
print()
print("=== 带逻辑的，**保留** ===")
for m,n in logic: print("   %s.%s" % (m,n))
print()
print("=== 纯别名，**准备删** ===")
for m,n in alias: print("   %s.%s" % (m,n))
