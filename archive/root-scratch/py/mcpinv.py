import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
roots = [Path(r"C:\swprojects"), Path(r"D:\AI")]
rows = []
for r in roots:
    for d in r.iterdir():
        if not d.is_dir(): continue
        # 找 MCP server 特征
        tools = 0; files = 0; lang = {}
        for p in d.rglob("*.py"):
            if any(x in str(p) for x in (".venv", "site-packages", "__pycache__", "node_modules")): continue
            files += 1
            try: t = p.read_text(encoding="utf-8", errors="ignore")
            except Exception: continue
            tools += len(re.findall(r"@mcp\.tool", t)) + len(re.findall(r"@server\.(?:call_tool|list_tools)", t))
        ts = sum(1 for _ in d.rglob("*.ts")) if d.exists() else 0
        cs = sum(1 for _ in d.rglob("*.cs"))
        if tools or "mcp" in d.name.lower() or "MCP" in d.name:
            rows.append((d.name, tools, files, cs, ts))
print("%-38s %6s %6s %6s %6s" % ("项目", "tool", "py", "cs", "ts"))
for n, t, f, cs, ts in sorted(rows, key=lambda x: -x[1]):
    print("%-38s %6d %6d %6d %6d" % (n, t, f, cs, ts))