import ast
import json
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")

# ── ① 分类表：把新检查器登记为 **diagnostic**（诊断，不是硬门禁）──────
P = R / "docs" / "gate-classification.json"
d = json.loads(P.read_text(encoding="utf-8"))
rows = d["classification"]
if not any(r.get("gate") == "check_member_owner_interface.py" for r in rows):
    rows.append({
        "gate": "check_member_owner_interface.py",
        "runner": None,
        "kind": "diagnostic",
        "reason": "⚠ **判据未证到能当门禁的程度**（轮 173，事实 113）：一是它**抓不到形参 owner**"
                  "（`mold_evidence` 那种，**正是写它的动机**）；二是 20 处命中里仍有需**逐条真机核**的"
                  "（如 `model` 到底是不是 `IModelDoc2`）。★ 与事实 53 同族：**证据进文档，不进工具**。",
    })
    P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ok ① 分类表已登记 diagnostic")

# ── ② 豁免表：登记"不接 release_check"（附理由与证据）────────────────
Q = R / "docs" / "gate-wiring-exemptions.json"
if Q.is_file() and Q.stat().st_size > 2:
    e = json.loads(Q.read_text(encoding="utf-8"))
else:
    e = {"_comment": "★ 未接进 `release_check.py` 的门禁及其理由（`check_gate_wiring.py` 读这张表）。",
         "exemptions": []}
exs = e.setdefault("exemptions", [])
if not any(x.get("gate") == "check_member_owner_interface.py" for x in exs):
    exs.append({
        "gate": "check_member_owner_interface.py",
        "reason": "★ **诊断工具，不接硬门禁** —— 本轮**没验过**它的判据够不够准（无法机验那 20 处），"
                  "且它**抓不到形参 owner**（含它的动机 `mold_evidence`）。接进去会变成"
                  "「看起来在查、实际乱报/漏报」的那种门禁（事实 53 / 62 同族）。",
        "evidence": ["D:/AI/SW/output/member-owner-interface.json",
                     "D:/AI/SW/specs/093-member-owner-interface-checker/spec.md"],
    })
    Q.write_text(json.dumps(e, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ok ② 豁免表已登记（含理由与证据）")

for f in (P, Q):
    ast.parse  # noqa: B018  （占位，提醒这两个是 JSON 不是 py）
print("  （两张表都是 JSON）")
