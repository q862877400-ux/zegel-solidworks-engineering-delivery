import re, json, io, sys
from pathlib import Path
ROOT = Path(r"D:\AI\SW")
o = io.StringIO()
tools = set()
for spec in sorted((ROOT/"mcp-server").glob("tool_specs_*.py")):
    t = spec.read_text(encoding="utf-8", errors="ignore")
    tools |= set(re.findall(r'name="((?:solidworks|cadstudio)_[\w]+)"', t))
server = ROOT/"mcp-server"/"server.py"
if server.is_file():
    t = server.read_text(encoding="utf-8", errors="ignore")
    tools |= set(re.findall(r'@mcp\.tool\(\s*\n?\s*name\s*=\s*"([^"]+)"', t))
o.write("=== OUR MCP TOOLS: %d ===\n" % len(tools))
for x in sorted(tools): o.write(x+"\n")
funcs = {}
for p in sorted((ROOT/"scripts").glob("sw_*.py")):
    t = p.read_text(encoding="utf-8", errors="ignore")
    fs = re.findall(r"^def ([a-z_]\w*)\(", t, re.MULTILINE)
    funcs[p.name] = fs
o.write("\n=== SCRIPTS sw_*.py: %d files ===\n" % len(funcs))
for k in sorted(funcs): o.write("%-38s %d  %s\n" % (k, len(funcs[k]), ", ".join(funcs[k])))
open(r"D:\AI\SW\_inv_ours.txt","w",encoding="utf-8").write(o.getvalue())
print("ok tools=%d files=%d" % (len(tools), len(funcs)))
