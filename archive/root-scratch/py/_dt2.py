import ast, io, re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
REPO = Path(r"C:\swprojects\sw-skill-fork")
gone = set(Path(r"D:\AI\SW\_gone.txt").read_text(encoding="utf-8").split())
n = 0
for t in sorted((REPO/"tests").glob("test_*.py")):
    src = t.read_text(encoding="utf-8")
    tree = ast.parse(src)
    lines = src.splitlines()
    spans, drop = [], []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef): continue
        body = ast.dump(ast.Module(body=node.body, type_ignores=[]))
        if any(re.search(rf"\b{re.escape(f)}\b", body) for f in gone):
            spans.append((node.lineno-1, node.end_lineno)); drop.append(node.name)
    if not drop: continue
    for s, e in sorted(spans, reverse=True): del lines[s:e]
    t.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ast.parse(t.read_text(encoding="utf-8"))
    n += len(drop)
    print("  %-44s 删 %2d" % (t.name, len(drop)))
print("合计删 %d 个失效测试" % n)
