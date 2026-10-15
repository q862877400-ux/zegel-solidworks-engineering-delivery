import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
targets = {
  "sw-skill-fork (我们的上游)": r"C:\swprojects\sw-skill-fork\mcp-server",
  "Solidworks-MCP (alisamsam)": r"C:\swprojects\Solidworks-MCP",
  "mcp-server-solidworks (SolidPilot)": r"C:\swprojects\mcp-server-solidworks",
  "SolidworksMCP-TS (vespo92)": r"C:\swprojects\SolidworksMCP-TS",
  "q3ds-solidworks-mcp": r"C:\swprojects\q3ds-solidworks-mcp",
  "solidworks-com-automation-skill": r"C:\swprojects\solidworks-com-automation-skill",
  "sw-ai-bridge": r"C:\swprojects\sw-ai-bridge",
  "solidworks-api-skill": r"C:\swprojects\sw-api-skill",
}
print("%-38s %6s %6s %6s %6s" % ("项目", "tool", "py", "cs", "ts"))
for name, path in targets.items():
    p = Path(path)
    if not p.exists():
        print("%-38s   (不存在)" % name); continue
    tools = py = cs = ts = 0
    for f in p.rglob("*"):
        if not f.is_file(): continue
        if any(x in str(f) for x in (".venv","site-packages","__pycache__","node_modules",".git")): continue
        if f.suffix == ".py":
            py += 1
            try: tools += len(re.findall(r"@mcp\.tool|@server\.list_tools|tools\.append|Tool\(", f.read_text(encoding="utf-8", errors="ignore")))
            except Exception: pass
        elif f.suffix == ".cs": cs += 1
        elif f.suffix == ".ts": ts += 1
    print("%-38s %6d %6d %6d %6d" % (name, tools, py, cs, ts))