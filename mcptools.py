import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
s = Path(r"C:\swprojects\sw-skill-fork\mcp-server\server.py").read_text(encoding="utf-8")
names = re.findall(r'@mcp\.tool\(\s*\n\s*name="([^"]+)"', s)
print("★ MCP 暴露的 tool 共 %d 个:" % len(names))
for i, n in enumerate(names, 1):
    print("   %2d. %s" % (i, n))