import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
p = R / "scripts" / "sw_toolbox_index.py"
print("  文件在: %s（%d 行）" % (p.is_file(), p.read_text(encoding='utf-8').count(chr(10)) if p.is_file() else 0))
t = p.read_text(encoding="utf-8")
tree = ast.parse(t)
fns = [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
print("  顶层函数 %d 个: %s" % (len(fns), ", ".join(fns)))
print()
print("  ── 模块头（看它自称是什么）──")
for l in t.splitlines()[:14]:
    print("    %s" % l[:100])
print()
print("  ── capabilities.yaml 里有没有 Toolbox/标准件 相关条目 ──")
d = (R / "capabilities.yaml").read_text(encoding="utf-8")
for kw in ("toolbox", "Toolbox", "标准件", "standard_part", "sw_toolbox_index"):
    print("    %-20s 出现 %d 次" % (kw, d.count(kw)))
print()
print("  ── 文档里有没有提过它 ──")
for doc in ("harvest-report.md", "union-coverage-matrix.md", "capability-matrix.md"):
    f = R / "docs" / doc
    if f.is_file():
        c = f.read_text(encoding="utf-8").count("toolbox") + f.read_text(encoding="utf-8").count("Toolbox")
        print("    %-28s 出现 %d 次" % (doc, c))
print()
print("  ── 它有没有被 MCP 工具暴露 ──")
hit = 0
for f in list((R / "mcp-server").glob("*.py")):
    s = f.read_text(encoding="utf-8", errors="replace")
    if "toolbox" in s.lower():
        hit += 1
        print("    %s 提到 toolbox" % f.name)
print("    （%d 个 mcp-server 文件提到）" % hit)
