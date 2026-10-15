import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── ① 新事实 93：四种选法都不行 + mark 计数的观察 ────────────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 93 | " + "".join([
    "**`InsertCompositeCurve` 四种选法都返回 `False` —— 按事实 53 停止试，**只报症状、不猜根因**** —— ",
    "2026-10-01（轮 153）在 **50×50×20 方块（12 条边）** 上逐个试：",
    "① **整个草图 × 2**（**官方示例的原样形态**，`SelectByID2(\"草图1\",\"SKETCH\",…,mark=1,…)`）⇒ `False`；",
    "② **`IEntity.Select4(True, callout)` 选 2 条边**（选择集计数 **2**）⇒ `False`（⚠ 它**没有 mark 参数**）；",
    "③ **按面上的点 + mark=1** 选 2 条棱 ⇒ 命中 **1**、且 **`GetSelectedObjectCount2(1)` = 0** ⇒ `False`；",
    "④ ⚠ 连**按名字选边**都是 0（`SelectByID2(\"Edge1\",\"EDGE\")` —— **事实 32 复现**，不是新发现）。",
    "★ **可复用的观察**：`GetSelectedObjectCount2(-1)` = **2** 而 `GetSelectedObjectCount2(1)` = **0** ⇒ ",
    "**「按点选边」那次并没有把 mark 设成 1**（或该接口的 mark 语义与预期不同）—— ",
    "⇒ ★★ **所以「前提已按官方要求满足」这句话本身也**没有**被证实。",
    "★★ 这正是轮 152 那件事的**同一形状**：**在说「功能不行」之前，先证「前提真的满足了」** —— ",
    "而「mark 到底设上没有」用的是**读回来的计数**（`GetSelectedObjectCount2(1)`），不是**调用返回的 True**。",
    "⚠ 与事实 8 同族（`AddSelectionListObject` 的 bool 不可信，要回读计数）。",
    "⚑ **未查明**：真因（不是「整草图 vs 边」这个区分、也不是 mark 的**明显**用法）；",
    "⇒ `composite_curve` 能力**不升级**。 | `tools/probe_composite_curve_edges.py`；",
    "`D:\\AI\\SW\\output\\composite-curve-edges.json`；事实 8 / 32 / 53 / 91 / 92 |",
])
if "| 93 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 93")
else:
    print("  已有 93")

# ── ② 能力条目：补上"四种选法都失败" ───────────────────────────────
Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
ADD = "".join([
    "⚠ **2026-10-01（轮 153）又试了 3 种选法（合计 4 种）**：① 整个草图 × 2（**官方示例原样**）· ",
    "② `IEntity.Select4` 选 2 条边（计数 2）· ③ 按面上的点 + **mark=1** · ",
    "④ 按名字选边（0，事实 32）—— **全部返回 `False`** ⇒ 按事实 53 **停止试**。",
    "★ 另记一个观察：`GetSelectedObjectCount2(-1)` = 2 而 **`GetSelectedObjectCount2(1)` = 0**",
    "⇒ **「按点选边」那次并没把 mark 设成 1** ⇒ ★★ **「前提已按官方要求满足」这句话本身也没被证实**",
    "⇒ ⚑ **真因未查明**，`composite_curve` **不升级**。",
])
for c in d["capabilities"]:
    if c.get("id") == "part_and_features":
        c["limitations"].insert(0, ADD)
        print("  ok part_and_features 已更新")
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
