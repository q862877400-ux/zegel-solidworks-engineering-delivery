import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
EV = Path(r"D:\AI\SW\_undo_ev.txt").read_text(encoding="utf-8").strip()
c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
x = next(y for y in d["capabilities"] if y["id"] == "part_and_features")
tools = list(x.get("mcp_tools") or [])
if "solidworks_undo" not in tools:
    tools.append("solidworks_undo")
x["mcp_tools"] = tools
ev = list(x.get("evidence") or [])
if not any("undo_report" in s for s in ev):
    ev.insert(0, EV)
x["evidence"] = ev
c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  part_and_features tools=%d ev=%d" % (len(tools), len(ev)))
for t in tools:
    print("    " + t)
