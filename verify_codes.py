import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import json
from pathlib import Path
d = json.loads(Path(r"C:\swprojects\sw-skill-fork\scripts\jlcfa_index.json").read_text(encoding="utf-8"))
print("抽查型号是否存在（用真实库验证，不凭记忆）:")
for kw in ("EGW35SA","BEW15SC","HSR25HAM","JAL","GT20","GT40","UK205","FK508","NK25"):
    hits = [p for p in d["parts"] if p["code"] == kw or kw in p["code"]]
    if hits:
        h = hits[0]
        print("  %-10s ✓ %-22s %s" % (kw, h["code"], h["product"][:40]))
    else:
        print("  %-10s ✗ 库里没有" % kw)
print()
print("按分类查备选:")
for cat in ("机床防护罩","传动零部件","轴承附件","直线运动零件"):
    hits = [p for p in d["parts"] if cat in (p["category"] or [])]
    print("  %-10s %d 个: %s" % (cat, len(hits), [h["code"] for h in hits[:4]]))