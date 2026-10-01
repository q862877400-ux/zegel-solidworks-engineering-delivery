import json
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
d = json.loads((R / "capabilities.yaml").read_text(encoding="utf-8"))
cands: dict = {}
for c in d["capabilities"]:
    if c.get("level") != "verified":
        continue
    for s in (c.get("evidence") or []):
        for m in re.finditer(r"python\s+(tools[\\/][\w.]+\.py|-[^\s]*\s*tests[\w./\\-]+)", str(s)):
            cmd = m.group(0).replace("\\", "/").strip()
            cands.setdefault(cmd, set()).add(c["id"])
print("  `verified` 条目里出现的**可跑验收命令**（去重）: **%d** 条" % len(cands))
tools = [k for k in cands if k.startswith("python tools/")]
py = [k for k in cands if not k.startswith("python tools/")]
print()
print("  ── `python tools/*.py`（真机脚本，值得逐条跑）: %d 条 ──" % len(tools))
for k in sorted(tools):
    print("    %-58s ← %s" % (k, ", ".join(sorted(cands[k]))[:44]))
print()
print("  ── 其它（多含 pytest，已在回归里覆盖）: %d 条 ──" % len(py))
for k in sorted(py)[:10]:
    print("    %-58s ← %s" % (k[:58], ", ".join(sorted(cands[k]))[:36]))
