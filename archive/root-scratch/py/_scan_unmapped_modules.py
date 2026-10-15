import ast
import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")

# ── ① capabilities.yaml 的结构与条目域 ──────────────────────────────
d = json.loads((R / "capabilities.yaml").read_text(encoding="utf-8"))
caps = d.get("capabilities") or []
print("  capabilities 条目数 = %d" % len(caps))
ids = [c.get("id") for c in caps]
print("  id 列表: %s" % ", ".join(str(i) for i in ids[:40]))
print()

# ── ② 每个条目声明了哪些模块 / files ────────────────────────────────
claimed: set = set()
for c in caps:
    for key in ("modules", "files", "module", "source_files"):
        v = c.get(key)
        if isinstance(v, str):
            claimed.add(v)
        elif isinstance(v, list):
            for x in v:
                if isinstance(x, str):
                    claimed.add(Path(x).name)
    #: evidence/limitations 里提到 .py 的也算
    for key in ("evidence", "limitations"):
        for s in (c.get(key) or []):
            for tok in str(s).replace("`", " ").replace("(", " ").split():
                if tok.endswith(".py"):
                    claimed.add(Path(tok).name)
print("  **被任何条目提到过**的 .py 文件名: %d 个" % len(claimed))
print()

# ── ③ scripts/ 下每个模块的公开函数数，找出「有实现但没被提到」的 ──
rows = []
for p in sorted((R / "scripts").glob("*.py")):
    try:
        tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        continue
    fns = [n.name for n in tree.body
           if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and not n.name.startswith("_")]
    if not fns:
        continue
    rows.append((p.name, len(fns), p.name in claimed))
rows.sort(key=lambda r: (-r[1]))
unmentioned = [r for r in rows if not r[2]]
print("  有公开函数的模块 %d 个 · 其中**没被任何条目提到**的 %d 个："
      % (len(rows), len(unmentioned)))
for name, n, _ in unmentioned[:26]:
    print("    %-30s 公开函数 %d 个" % (name, n))
print()
print("  （对照组）公开函数最多的几个模块，以及它们有没有条目：")
for name, n, ok in rows[:10]:
    print("    %-30s %2d 个  条目=%s" % (name, n, "有" if ok else "**没有**"))
