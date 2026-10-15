import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")

# ── ① 就地更正事实 93 里那句（不是 mark 的问题）────────────────────
OLD93 = "⇒ ★★ **所以「前提已按官方要求满足」这句话本身也**没有**被证实。"
NEW93 = "".join([
    "⇒ ★★ **所以「前提已按官方要求满足」这句话本身也**没有**被证实。",
    "〔⚠⚠ **2026-10-01 轮 154 就地更正**：当时把原因**列为两个候选** ——",
    "「mark 没设上」**或**「`GetSelectedObjectCount2` 的读法不对」。",
    "轮 154 用**判别实验**把它们分开了：同一个 `SelectByID2` 选**已知能选中的草图**，",
    "`mark=1` ⇒ `GetSelectedObjectCount2(1)` = **1**、`mark=2` ⇒ `(2)` = **1**、`mark=0` ⇒ `(0)` = **1**",
    "⇒ ★★ **mark 能落上，且 `GetSelectedObjectCount2(mark)` 的语义完全符合预期**。",
    "⇒ **那两个候选都不是原因**：轮 153 那个 0 是「**棱根本没被选中**」——",
    "★★★ 而 `SelectByID2(\"\",\"EDGE\",…)` **返回了 `True` 却什么都没选中**",
    "⇒ **`SelectByID2` 的 bool 返回值同样不可信**（与事实 8：`AddSelectionListObject` 的 bool 不可信**同族**，",
    "而这条此前只被记在 `AddSelectionListObject` 名下）。〕 ",
])
if "轮 154 就地更正" not in tk and OLD93 in tk:
    tk = tk.replace(OLD93, NEW93, 1)
    K.write_text(tk, encoding="utf-8")
    print("  ok 事实 93 已就地更正（候选被判别实验分开）")
else:
    print("  事实 93：锚点在=%s 已更正=%s" % (OLD93 in tk, "轮 154 就地更正" in tk))

# ── ② 新事实 94：SelectByID2 的 bool 不可信 ─────────────────────────
tk = K.read_text(encoding="utf-8")
FACT = "| 94 | " + "".join([
    "**`SelectByID2` 返回 `True` **也不代表选中了** —— 判「选上没有」只能回读 mark 计数** —— ",
    "2026-10-01（轮 154）**判别实验**（`tools/probe_mark_semantics.py`）：同一个 `SelectByID2` 选**已知能选中的草图1**，",
    "**判别实验读数**（同一个 `SelectByID2` 选已知能选中的草图1）：",
    "`mark=0` ⇒ `GetSelectedObjectCount2`: `-1:1  0:1  1:0  2:0` · ",
    "`mark=1` ⇒ `-1:1  0:0  1:1  2:0`（★ 精确落在 mark=1）· ",
    "`mark=2` ⇒ `-1:1  0:0  1:0  2:1`（★ 精确落在 mark=2）。",
    "⇒ ★★ 两个结论：① **mark 能落上**（`mark=N` ⇒ `(N)` = 1）；",
    "② **`GetSelectedObjectCount2(mark)` 的语义符合预期**（`-1` = 全部，`0/1/2` = 各 mark）。",
    "★★★ 而轮 153 用 `SelectByID2(\"\", \"EDGE\", x, y, z, …, mark=1, …)` 选棱时**返回 `True`**、",
    "`GetSelectedObjectCount2(1)` 却是 **0** ⇒ **`True` 与「选中了」是两件事**。",
    "★ 与**事实 8**（`AddSelectionListObject` 的 bool 不可信，要回读计数）**同族** —— ",
    "而那条此前只记在 `AddSelectionListObject` 名下，**这次把 `SelectByID2` 也纳进来**。",
    "★ **可复用的判据**：判「选上没有」**一律回读** `GetSelectedObjectCount2(<mark>)`，",
    "**不要看 `SelectByID2` 的返回值**（它只表示「找到了那个名字/位置」）。",
    "⚑ 未查明：`InsertCompositeCurve` 的真因（但**失败点更清楚了**：得先**真的**选中 2 条边）。 | ",
    "`tools/probe_mark_semantics.py`；`D:\\AI\\SW\\output\\mark-semantics.json`；事实 8 / 32 / 93 |",
])
if "| 94 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 94")
else:
    print("  已有 94")

# ── ③ 能力条目：更正上轮那句 ───────────────────────────────────────
Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
OLD = "⇒ **「按点选边」那次并没把 mark 设成 1** ⇒ ★★ **「前提已按官方要求满足」这句话本身也没被证实**"
NEW = "".join([
    "★ **2026-10-01（轮 154）判别实验把它查清了**：`mark=1/2/0` 都能精确落到对应 mark 上",
    "（`GetSelectedObjectCount2(N)` = 1）⇒ **mark 与读法都没问题**；",
    "★★★ 真因是 **`SelectByID2` 返回 `True` 却什么都没选中**（事实 94）",
    "⇒ ★ **可复用判据**：判「选上没有」**一律回读** `GetSelectedObjectCount2(<mark>)`，",
    "**不要看 `SelectByID2` 的返回值**。",
])
n = 0
for c in d["capabilities"]:
    lim = c.get("limitations") or []
    for i, s in enumerate(lim):
        if OLD in str(s):
            lim[i] = str(s).replace(OLD, NEW)
            n += 1
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  ok capabilities 更正 %d 处" % n)
