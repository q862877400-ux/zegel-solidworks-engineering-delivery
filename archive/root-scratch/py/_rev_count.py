import sys, re, json
sys.path.insert(0, "mcp-server")
from pathlib import Path
src = Path("mcp-server/server.py").read_text(encoding="utf-8")
pat = re.compile(r'name\s*=\s*"((?:solidworks|cadstudio)_[a-z0-9_]+)"')
names = pat.findall(src)
print("server.py declared:", len(names), "unique:", len(set(names)))
import register_capabilities as rc
b = [s.name for s in rc.all_specs()]
print("batch declared:", len(b))
print("sum:", len(names) + len(b))
print("overlap:", sorted(set(names) & set(b)))
