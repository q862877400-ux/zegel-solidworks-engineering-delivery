import json
from pathlib import Path

c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
x = next(y for y in d["capabilities"] if y["id"] == "simulation_load_family_breadth")
#: \u2605\u2605 \u771f\u673a\u7248\u672c\uff1a\u672c\u673a SW 2026 SP4.1\uff08\u4e2d\u6587 UI\uff09\u2014\u2014 \u2605 \u4e0e\u522b\u7684 verified \u6761\u76ee\u540c\u53e3\u5f84
x["verified_versions"] = ["2026"]
#: \u2605 \u540c\u65f6\u628a\u7248\u672c\u4e8b\u5b9e\u5199\u8fdb limitations\uff08\u2605 \u4f9b\u4eba\u770b\uff09
lim = list(x.get("limitations") or [])
note = ("\u2605 \u771f\u673a\u7248\u672c\uff1a**SolidWorks 2026 SP4.1**\uff08\u4e2d\u6587 UI\uff09\u00b7 Python 3.14.7 "
        "\u00b7 \u2605 \u8bc1\u636e `output/loadfamily-evidence.json`\uff08PASS 5/5\uff09\u3002")
if not any("SP4.1" in s for s in lim):
    lim.insert(0, note)
x["limitations"] = lim
c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  ok \u00b7 verified_versions=%s" % x["verified_versions"])
