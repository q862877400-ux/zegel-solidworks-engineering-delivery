import re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
s = open(r"C:\swprojects\sw-skill-fork\mcp-server\server.py", encoding="utf-8").read()
static = set(re.findall(r'scripts\.([a-z_][a-z0-9_]*)', s))
dyn = set(re.findall(r'import_module\(\s*["\']scripts\.([a-z_][a-z0-9_]*)["\']', s))
refs = static | dyn
print("  上游 MCP 引用的 scripts 模块: %d 个（静态 %d + 动态 %d）" % (len(refs), len(static), len(dyn)))
new = subprocess.run(["git","-C",r"C:\swprojects\sw-skill-fork","diff","origin/main","--name-status","--diff-filter=A"],
                     capture_output=True, text=True, encoding="utf-8").stdout
ours = {p.split("/")[-1][:-3] for p in
        (l.split("\t")[-1] for l in new.splitlines())
        if p.startswith("scripts/") and p.endswith(".py")}
print("  我们新增的 scripts 模块: %d 个" % len(ours))
print("  交集: %d（AGENTS.md 事实 25 说 0）" % len(refs & ours))