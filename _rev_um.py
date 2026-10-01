import sys, re
sys.path.insert(0, "tools")
sys.path.insert(0, "mcp-server")
import build_union_map as bum
tools = bum._our_tools()
print("_our_tools() len =", len(tools))
import register_capabilities as rc
spec_names = {s.name for s in rc.all_specs()}
server = (bum.ROOT/"mcp-server"/"server.py").read_text(encoding="utf-8", errors="ignore")
server_names = set(re.findall(r'@mcp\.tool\(\s*\n?\s*name\s*=\s*"([^"]+)"', server))
print("from server.py decorators:", len(server_names))
extra = set(tools) - server_names - spec_names
print("names picked up from batch files that are NOT registered specs:", len(extra))
for n in sorted(extra)[:20]:
    print("   ", n)
ops = bum._our_operations()
print("operations (normalized) =", len(ops))
