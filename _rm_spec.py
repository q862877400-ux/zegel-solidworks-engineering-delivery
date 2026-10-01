import sys
from pathlib import Path
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\mcp-server")
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\mcp-server\tool_specs_batch6.py")
t = P.read_text(encoding="utf-8")
start_marker = '    ToolSpec(\n        name="solidworks_get_mass_property_override_options"'
i = t.index(start_marker)
end_marker = "\n    ),\n"
j = t.index(end_marker, i) + len(end_marker)
P.write_text(t[:i] + t[j:], encoding="utf-8")
import importlib, tool_specs_batch6 as b
importlib.reload(b)
print("  删除后声明: %s" % [s.name for s in b.SPECS_BATCH6])
