import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\unattended_baseline.json")
d = json.loads(P.read_text(encoding="utf-8"))
print("  基线键: %s" % list(d.keys()))
allowed = list(d.get("allowed") or [])
print("  基线 allowed 条数 = %d" % len(allowed))
CID = "standard_parts_toolbox"
if CID in allowed:
    print("  已在基线里")
else:
    #: ★ **只加这一项**，保持排序 —— 不用整体重抓（那会掩盖别的意外变化）。
    #: 理由（写进提交信息与条目限度里）：它是**只读索引查询**（无 COM、无文件写入）⇒
    #: 适合无人值守；且门禁「R11 · 授权真源」**已 PASS**。
    allowed.append(CID)
    allowed = sorted(allowed)
    d["allowed"] = allowed
    P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ok 已把 %s 加进基线 allowed（共 %d 条）" % (CID, len(allowed)))
print()
print("  allowed 前 12 条: %s" % allowed[:12])
