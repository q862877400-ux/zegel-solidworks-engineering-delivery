import json, ast, re
from pathlib import Path
data = json.loads(Path(r"D:\AI\SW\output\orphan-capabilities.json").read_text(encoding="utf-8"))
rows = data["orphans"]
print("rows:", len(rows))
bad = [r for r in rows if any(((")" in p) or ("[" in p) or (p == "")) for p in r["params"])]
print("garbled param lists:", len(bad))
for r in bad[:12]:
    print("   ", r["module"], r["function"], r["params"])
# 用 AST 重新算真实签名
ROOT = Path(r"C:\swprojects\sw-skill-fork")
sigs = {}
for p in sorted((ROOT/"scripts").glob("sw_*.py")):
    try:
        tree = ast.parse(p.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError as e:
        print("PARSE FAIL", p.name, e); continue
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
            a = node.args
            names = [x.arg for x in a.posonlyargs + a.args + a.kwonlyargs]
            if a.vararg: names.append(a.vararg.arg)
            if a.kwarg: names.append(a.kwarg.arg)
            sigs.setdefault(node.name, names)
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            pass
def inj(names): return bool(names) and names[0] in ("model","sw_app","study")
def coord(names): return any(n in ("x","y","z") for n in names)
real_inj = [r for r in rows if inj(sigs.get(r["function"], []))]
real_coord = [r for r in rows if coord(sigs.get(r["function"], []))]
print()
print("AST recompute: injectable =", len(real_inj), " bare-coord =", len(real_coord))
print("JSON claims  : injectable =", sum(1 for r in rows if r["first_param_is_injectable"]),
      " bare-coord =", sum(1 for r in rows if r["has_bare_coord_param"]))
d1 = {r["function"] for r in rows if r["first_param_is_injectable"]} ^ {r["function"] for r in real_inj}
d2 = {r["function"] for r in rows if r["has_bare_coord_param"]} ^ {r["function"] for r in real_coord}
print("injectable disagreement:", sorted(d1))
print("bare-coord disagreement:", sorted(d2))
