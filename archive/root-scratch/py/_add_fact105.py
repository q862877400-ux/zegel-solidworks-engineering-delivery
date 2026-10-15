import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── 事实 105 ────────────────────────────────────────────────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 105 | " + "".join([
    "**「顺序问题」第二次被误判成「做不到」 —— `ConvertFormat()` 必须先于 `AddFrame()`** —— ",
    "2026-10-01（轮 165）：轮 120 量到「2022 格式的帧路径**取不到帧**」（`AddFrame() -> False`、",
    "`GetFrame(0/1/2)` **全 None**）并按事实 53 停手 —— ⚠ **那个「停手」动作是规范的，但定性错了**。",
    "★★★ 轮 165 读官方 Remarks 读出真因：`IGtol.AddFrame` 的 Remarks 原文",
    "> This method is valid only if this Gtol was created in SOLIDWORKS **2022 or later**.",
    "⇒ 新建的 Gtol **默认是旧格式** ⇒ 而轮 120 的顺序是 `AddFrame()` **先于** `ConvertFormat()`",
    "⇒ **必然 False**。★ 实测（`tools/probe_gtol_frame_order.py`）：",
    "`ConvertFormat()` ⇒ 0（成功）→ **`AddFrame()` ⇒ True** → `GetFrameCount` ⇒ **2** → ",
    "**`GetFrame(1)/(2)` 拿到对象**（轮 120 时是 None）。",
    "★★ 与**事实 104**（`CreateChamfer` 被误判「架构性限制」）**同族** —— 两次都是",
    "「**把「形态/顺序不对」读成「做不到」**」。⇒ ★ 可复用的问句：**「我试的是这个 API 的哪一种用法？」**",
    "⚠ **仍未查明**：`IGtolFrame.AddIndicator(Int32, Int32, String)` **仍返回 `False`**",
    "（帧已拿到 ⇒ **不再是「帧路径取不到」**，而是**参数/前置未查明**）。",
    "★ 已修：`ensure_gtol_frame` 改为**先 `ConvertFormat()`、再 `AddFrame()`**；",
    "并把两句已过时的报错改掉（`GetFrame` 那句不再说「可能不是 2022 格式」；",
    "`AddIndicator` 那句不再说「不是 2022 格式」—— ⚠ **我们确实转换过了**）。",
    "⚠ `geometric_tolerance` **仍为 `stitched`**（3/5，指示符那一步未通）。",
    " | `tools/probe_gtol_frame_order.py`；`scripts/sw_gtol.py`；`C:/swapi/types/IGtol/AddFrame.md`；",
    "事实 53 / 104 |",
])
if "| 105 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 105")
else:
    print("  已有 105")

# ── 条目：更正「帧路径取不到」这句 ─────────────────────────────────
Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
ADD = "".join([
    "★★★ **2026-10-01（轮 165）更正「2022 格式的帧路径取不到帧」这句** —— 那是**顺序问题**：",
    "官方 `IGtol.AddFrame` 的 Remarks 说它只对 **2022 或更新**创建的 Gtol 有效，而新建的 Gtol **默认是旧格式**",
    "⇒ **必须先 `ConvertFormat()` 再 `AddFrame()`**；轮 120 的顺序是反的 ⇒ **必然 False**。",
    "★ 实测（`tools/probe_gtol_frame_order.py`）：`ConvertFormat()` ⇒ 0 → **`AddFrame()` ⇒ True** → ",
    "`GetFrameCount` ⇒ **2** → **`GetFrame(1)/(2)` 拿到对象** ✓ ⇒ **帧路径已通**。",
    "⚠ **仍未通**：`IGtolFrame.AddIndicator(Int32, Int32, String)` **返回 `False`**",
    "（帧已拿到 ⇒ 是**参数/前置未查明**，**不是**「帧取不到」）。",
    "★ 已修 `ensure_gtol_frame`（先转换再加帧）+ 改掉两句已过时的报错。",
])
for c in d["capabilities"]:
    if c.get("id") == "geometric_tolerance":
        c["limitations"].insert(0, ADD)
        print("  ok geometric_tolerance 已更正")
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
