import ast, io, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
REPO = Path(r"C:\swprojects\sw-skill-fork\scripts")
MINE = ["sw_sldworks_app","sw_model_doc_extension","sw_section_view",
        "sw_table_annotations","sw_document_core","sw_hubs",
        "sw_drawing_annotations","sw_part_features","sw_sketch_sheetmetal",
        "sw_geometry","sw_simulation_registry","sw_sldworks_lastgap"]
print("%-26s %6s %6s %6s" % ("模块", "函数", "纯别名", "带逻辑"))
print("-"*50)
ta=tl=0
for m in MINE:
    p = REPO / f"{m}.py"
    if not p.is_file(): continue
    tree = ast.parse(p.read_text(encoding="utf-8"))
    alias=[]; logic=[]
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef): continue
        body = [n for n in node.body if not isinstance(n, ast.Expr)
                or not isinstance(n.value, ast.Constant)]
        src = ast.dump(ast.Module(body=body, type_ignores=[]))
        # 纯别名：函数体只有一句 return/赋值，且只调用一个成员
        n_stmt = len(body)
        is_alias = n_stmt == 1 and "get_com_member" in src and "for" not in src and "if" not in src
        (alias if is_alias else logic).append(node.name)
    ta+=len(alias); tl+=len(logic)
    print("%-26s %6d %6d %6d" % (m, len(alias)+len(logic), len(alias), len(logic)))
print("-"*50)
print("%-26s %6d %6d %6d" % ("合计", ta+tl, ta, tl))
print()
print("带逻辑的（**不能删**）：")
for m in MINE:
    p = REPO / f"{m}.py"
    if not p.is_file(): continue
    tree = ast.parse(p.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef): continue
        body = [n for n in node.body if not isinstance(n, ast.Expr)
                or not isinstance(n.value, ast.Constant)]
        src = ast.dump(ast.Module(body=body, type_ignores=[]))
        is_alias = len(body)==1 and "get_com_member" in src and "for" not in src and "if" not in src
        if not is_alias:
            print("   %s.%s" % (m, node.name))
