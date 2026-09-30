import re, sys, subprocess
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
root = Path(r"C:\swprojects\sw-skill-fork")
s = (root / "mcp-server" / "server.py").read_text(encoding="utf-8")
# server.py 引用的所有 scripts.xxx
refs = set(re.findall(r'scripts\.([a-z_][a-z0-9_]*)', s))
# 我们新增的模块名
new = subprocess.run(["git","-C",str(root),"diff","origin/main","--name-status","--diff-filter=A"],
                     capture_output=True, text=True, encoding="utf-8").stdout
ours = set()
for line in new.splitlines():
    parts = line.split("\t")
    if len(parts) >= 2 and parts[-1].startswith("scripts/") and parts[-1].endswith(".py"):
        ours.add(Path(parts[-1]).stem)
print("server.py 引用的 scripts 模块: %d 个" % len(refs))
print("我们新增的 scripts 模块  : %d 个" % len(ours))
print()
inter = sorted(refs & ours)
print("★ 交集（我们新增的、且被 MCP 包进去的）: %d 个" % len(inter))
for m in inter: print("     %s" % m)
print()
miss = sorted(ours - refs)
print("★ 我们新增但 MCP **没包**的: %d 个" % len(miss))
for m in miss: print("     %s" % m)