import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
caps = d["capabilities"]
if not any(c.get("id") == "gtol_insert" for c in caps):
    caps.append({
        "id": "gtol_insert",
        "label": "形位公差：新建 GTol（InsertGtol）",
        "level": "verified",
        "backends": ["solidworks-com-pywin32"],
        "verified_versions": ["2026 SP4.1"],
        "dependencies": ["python"],
        "limitations": [
            "⚠ 只覆盖「**新建一个 GTol 标注对象**」这一步（官方 `IModelDoc2.InsertGtol()`，**0 参**）",
            "★ **帧路径已通**（轮 165）：`CanConvertFormat()` → `ConvertFormat()` → `AddFrame()` ⇒ "
            "`GetFrameCount()` = 2 且 `GetFrame(1)/(2)` **拿到对象**。"
            "⚠ 顺序很重要：`AddFrame()` **必须先经过 `ConvertFormat()`**"
            "（官方 Remarks：只对 **2022 或更新**创建的 Gtol 有效）",
            "⚠ **不含**「加公差指示符」那一步 —— 它在**本机到不了**（见 `geometric_tolerance` 条目）",
            "⚠ 只证「拿到了 GTol 对象 / 帧对象」，**不证明公差标得对**（位置、数值、字形都没验）",
        ],
        "allowed_modes": ["interactive", "reviewed", "unattended"],
        "evidence": [
            "python tools/verify_gtol_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1："
            "新零件 → `insert_gtol()` **拿到 CDispatch**）",
            "python tools/probe_gtol_frame_order.py（**真机**：`ConvertFormat()` ⇒ 0 → "
            "**`AddFrame()` ⇒ True** → `GetFrameCount` ⇒ **2** → `GetFrame(1)/(2)` **有对象**）",
        ],
        "source": "original",
        "source_evidence": "scripts/sw_gtol.py 的 insert_gtol / add_gtol_frame / ensure_gtol_frame"
                            "（照官方 `InsertGtol()` / `IGtol.AddFrame()` / `ConvertFormat()` 签名自建）",
    })
    print("  ok 已拆出 gtol_insert（verified）")
for c in caps:
    if c.get("id") == "geometric_tolerance":
        lim = c.get("limitations") or []
        lim.insert(0, "".join([
            "★★★ **2026-10-01（轮 166）穷尽式结论**：`IGtolFrame.AddIndicator` 那半 —— "
            "`tools/probe_gtol_indicator_matrix.py` 把 `BorderType`(0..3) × `TolType`"
            "（官方 Remarks 允许的 **5 个**：20/22/21/25/13）= **20 组全试**，"
            "而**每一组的帧都拿到了**（`GetFrame(1)` 非 NULL）⇒ **20 组全返回 `False`**。",
            "⇒ ★ 不是「取值不对」（5 个 tol 都在官方允许清单里），"
            "而是**这条后端到不了这一个成员**（与事实 47 那族同类）。",
            "★ 所以拆出 `gtol_insert`（**verified**，覆盖「新建 GTol + 帧路径」）；"
            "本条目**仍为 `stitched`**（含「加指示符」那半，它在**本机到不了**）。",
        ]))
        c["limitations"] = lim
        print("  ok geometric_tolerance 已更正")
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  条目数:", len(caps))
