import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
targets = {
  "我们的上游 sw-skill-fork": r"C:\swprojects\sw-skill-fork\mcp-server\server.py",
  "alisamsam/Solidworks-MCP": r"C:\swprojects\Solidworks-MCP",
  "SolidPilot": r"C:\swprojects\mcp-server-solidworks",
  "q3ds-solidworks-mcp": r"C:\swprojects\q3ds-solidworks-mcp",
  "vespo92/SolidworksMCP-TS": r"C:\swprojects\SolidworksMCP-TS",
}
for name, path in targets.items():
    p = Path(path)
    files = [p] if p.is_file() else [f for f in p.rglob("*") if f.is_file()
             and f.suffix in (".py",".ts")
             and not any(x in str(f) for x in (".venv","site-packages","__pycache__","node_modules",".git","test"))]
    names = set()
    for f in files:
        try: t = f.read_text(encoding="utf-8", errors="ignore")
        except Exception: continue
        # 三种常见注册写法，都要取「工具名」
        names |= set(re.findall(r'@mcp\.tool\(\s*\n?\s*name\s*=\s*"([^"]+)"', t))
        names |= set(re.findall(r'@mcp\.tool\s*\n\s*(?:async\s+)?def\s+(\w+)', t))
        names |= set(re.findall(r'name:\s*"([a-z][a-z0-9_]{3,})"[^}]{0,200}?(?:inputSchema|description)', t, re.S))
        names |= set(re.findall(r'\{\s*name:\s*[\'"]([a-z][a-z0-9_]{3,})[\'"]', t))
    print("★ %-28s 识别到 %d 个工具名" % (name, len(names)))
    if names:
        s = sorted(names)
        print("     %s" % ", ".join(s[:14]))
        if len(s) > 14: print("     … 共 %d" % len(s))
    print()