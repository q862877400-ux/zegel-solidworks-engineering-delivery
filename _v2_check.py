import importlib
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\mcp-server")
W = Path(r"D:\AI\SW")

NEW = {
    "tool_specs_batch53": "SPECS_BATCH53", "tool_specs_batch54": "SPECS_BATCH54",
    "tool_specs_batch55": "SPECS_BATCH55", "tool_specs_batch56": "SPECS_BATCH56",
    "tool_specs_batch57": "SPECS_BATCH57", "tool_specs_batch58": "SPECS_BATCH58",
    "tool_specs_batch59": "SPECS_BATCH59", "tool_specs_batch60": "SPECS_BATCH60",
}
names = []
for mod, attr in NEW.items():
    try:
        m = importlib.import_module(mod)
    except Exception as exc:                                   # noqa: BLE001
        print("  **%s \u5bfc\u5165\u5931\u8d25**: %s" % (mod, str(exc)[:70]))
        continue
    for s in (getattr(m, attr, []) or []):
        names.append((s.name, s.function))
print("  \u672c\u8ba1\u5212\u65b0\u589e\u5de5\u5177\uff08\u6309\u58f0\u660e\uff09\uff1a**%d** \u4e2a" % len(names))

ev = {}
for p in W.glob("output/*evidence*.json"):
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:                                          # noqa: BLE001
        continue
    ev[p.name] = (d.get("verdict"), json.dumps(d, ensure_ascii=False))

ok, miss = [], []
for nm, fn in names:
    hit = sorted(k for k, (v, body) in ev.items() if fn in body and v == "pass")
    (ok if hit else miss).append((nm, fn, hit[:1]))
print("  \u2605 \u6709 `verdict: pass` \u8bc1\u636e\u7684\uff1a**%d/%d**" % (len(ok), len(names)))
if miss:
    print("  \u2605 **\u65e0 pass \u8bc1\u636e\u7684\uff1a%d**" % len(miss))
    for nm, fn, _ in miss:
        print("      %-52s %s" % (nm, fn))
else:
    print("  \u2605\u2605 **V2 \u6ee1\u8db3\uff1a\u65b0\u589e\u5de5\u5177\u9010\u4e2a\u90fd\u6709 pass \u8bc1\u636e**\uff08\u2605 \u800c\u672a\u9a8c\u8fc7\u7684\u90a3\u51e0\u6761"
          "\u5df2\u6309\u786c\u7ea6\u675f\u2465 **\u4e0d\u6ce8\u518c** \u21d2 \u5b83\u4eec\u4e0d\u5728\u672c\u540d\u5355\u91cc\uff09")
