import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
d = json.loads(Path(r"C:\swprojects\sw-skill-fork\scripts\jlcfa_index.json").read_text(encoding="utf-8"))
parts = d["parts"]
print("  型号总数:", len(parts))
# 找机械传动类（导轨/丝杆/型材/轴承）
import re
KEYS = ["导轨","滑块","丝杆","铝型材","型材","直线","轴承","支撑","联轴器","直线模组","光轴"]
for k in KEYS:
    hits = [p for p in parts if k in p["product"] or k in p["name"]]
    if hits:
        print()
        print("  【%s】%d 个型号" % (k, len(hits)))
        for h in hits[:4]:
            print("     %-26s %-34s %s" % (h["code"][:24], h["product"][:32], (h["category"] or [""])[0][:12]))