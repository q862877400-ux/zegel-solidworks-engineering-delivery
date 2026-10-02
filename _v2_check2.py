import importlib
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(r"D:\AI\SW")
R = Path(r"C:\swprojects\sw-skill-fork")

NEW = {
    "tool_specs_batch53": "SPECS_BATCH53", "tool_specs_batch54": "SPECS_BATCH54",
    "tool_specs_batch55": "SPECS_BATCH55", "tool_specs_batch56": "SPECS_BATCH56",
    "tool_specs_batch57": "SPECS_BATCH57", "tool_specs_batch58": "SPECS_BATCH58",
    "tool_specs_batch59": "SPECS_BATCH59", "tool_specs_batch60": "SPECS_BATCH60",
}
sys.path.insert(0, str(R / "mcp-server"))
names = []
for mod, attr in NEW.items():
    try:
        m = importlib.import_module(mod)
    except Exception:                                          # noqa: BLE001
        continue
    names += [s.name for s in (getattr(m, attr, []) or [])]

caps = json.loads((R / "capabilities.yaml").read_text(encoding="utf-8"))["capabilities"]
#: \u2605 \u6bcf\u6761\u80fd\u529b\u7684 evidence \u91cc\u63d0\u5230\u7684 `*-evidence.json` \u6587\u4ef6\u540d
cap_pat = {}
for c in caps:
    files = set(re.findall(r"([\w\-]+-evidence\.json)", json.dumps(c, ensure_ascii=False)))
    cap_pat[c.get("id")] = (set(c.get("mcp_tools") or []), files)

verdict = {}
for p in W.glob("output/*evidence*.json"):
    try:
        verdict[p.name] = json.loads(p.read_text(encoding="utf-8")).get("verdict")
    except Exception:                                          # noqa: BLE001
        pass

ok, miss = [], []
for nm in sorted(set(names)):
    owner = [cid for cid, (tools, _f) in cap_pat.items() if nm in tools]
    passed = []
    for cid in owner:
        for f in cap_pat[cid][1]:
            if verdict.get(f) == "pass":
                passed.append(f)
    (ok if passed else miss).append((nm, owner[:1], sorted(set(passed))[:1]))

print("  \u672c\u8ba1\u5212\u65b0\u589e\u5de5\u5177\uff1a**%d** \u4e2a" % len(set(names)))
print("  \u2605 \u6309\u300c\u80fd\u529b\u2192\u5de5\u5177 \u00d7 \u80fd\u529b\u2192\u8bc1\u636e\u6587\u4ef6\uff08\u4e14\u8be5\u6587\u4ef6 verdict=pass\uff09\u300d\u5224\uff1a")
print("     \u2605 **\u6ee1\u8db3\uff1a%d/%d**" % (len(ok), len(set(names))))
if miss:
    print("     \u2605 **\u4e0d\u6ee1\u8db3\uff1a%d**" % len(miss))
    for nm, ow, _ in miss:
        print("        %-50s \u80fd\u529b=%s" % (nm, ow or "\u2014"))
#: \u2605 \u53e6\u5916\u62a5\u4e00\u4e2a\u6570\uff1a\u5168\u4ed3 evidence \u7684 pass \u7387
allv = [v for v in verdict.values()]
print("  \u5168\u4ed3 evidence\uff1a%d \u4efd\uff0c\u5176\u4e2d pass %d \u4efd" % (len(allv), sum(1 for v in allv if v == "pass")))
