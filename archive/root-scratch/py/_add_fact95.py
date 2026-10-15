import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 95 | " + "".join([
    "**`InsertCompositeCurve` 累计 6 种选法全失败；卡点是「选中」与「mark=1」没能同时满足** —— ",
    "2026-10-01（轮 155）**回读着 mark 计数**逐个试：",
    "① 草图**整体** × 2（**官方示例原样**，按名 + mark=1）⇒ False；",
    "② 实体**边** × 2（`Select4`，`(-1)`=2 但 **mark=0**）⇒ False；",
    "③ 实体边（**按点** + mark=1）⇒ `SelectByID2` 返回 `True` 但 `(1)`=**0**（事实 94）；",
    "④ **草图段** × 2（`Select4`，**`(-1)`=2 回读确认**）⇒ False；",
    "⑤ 草图段（按名 + mark=1）⇒ **命中 0**；⑥ 按名选边 ⇒ 0（事实 32）。",
    "★★★ **卡点（本轮查出来的）**：`IEntity.Select4(Append, Callout)` **没有 mark 参数** ⇒ 选完 mark 仍是 0；",
    "而 `SelectByID2` 需要**名字**，可是 **边与草图段都没有可用名字** —— ",
    "★ 实测草图段的 `GetID` 返回的是**端点对**（`'(0, 1)'` / `'(1, 2)'`），**不是** `Line1` 那样的名字。",
    "⇒ ★★ 所以「**选中 2 个实体 + mark=1**」这个官方要求的前提，**在这条后端上我没能同时满足**。",
    "★★ 按**事实 53 强停止**（6 种远超它说的「≥3 次」）：**候选解释一律列为未验证**，",
    "例如「该后端下 `InsertCompositeCurve` 结构性不可用」（与事实 47 那族**同类**）—— ",
    "⚠ **但这只是候选，本轮没有证据**，因此**不写进结论**，`composite_curve` **不升级**。",
    "★ 可复用的两条：① 草图段**没有名字**（`GetID` 是端点对）⇒ **按名选段不可能**；",
    "② **`Select4` 与 mark=1 二者不可兼得** ⇒ 凡官方要求 mark 的地方，**必须走 `SelectByID2` 那条路**。 | ",
    "`tools/probe_composite_curve_segments.py`；`D:\\AI\\SW\\output\\composite-curve-segments.json`；",
    "事实 32 / 47 / 53 / 93 / 94 |",
])
if "| 95 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 95")
else:
    print("  已有 95")

Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
ADD = "".join([
    "⚠⚠ **2026-10-01（轮 155）按事实 53 强停止**：累计 **6 种选法全部失败**（草图整体 / 实体边 / ",
    "草图段 × 各两种选法）⇒ ★★★ **卡点查明**：`IEntity.Select4` **没有 mark 参数**（选完 mark 仍是 0），",
    "而 `SelectByID2` 需要**名字**、**边与草图段都没有名字**（草图段的 `GetID` 是**端点对** `'(0, 1)'`）。",
    "⇒ **「选中 2 个实体 + mark=1」这个官方前提，在这条后端上我没能同时满足**。",
    "⚑ **候选解释列为未验证**（如「该后端下结构性不可用」，与事实 47 同类）—— **没有证据，不写进结论**；",
    "⇒ `composite_curve` **不升级**、`insert_composite_curve` **已写但未取证**。",
])
for c in d["capabilities"]:
    if c.get("id") == "part_and_features":
        c["limitations"].insert(0, ADD)
        print("  ok part_and_features 已更新")
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
