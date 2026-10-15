import ast
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

R = Path(r"C:\swprojects\sw-skill-fork")
P = R / "docs" / "acceptance-status.md"
t = P.read_text(encoding="utf-8")

OLD = ("★ **本轮（轮 180）查清**：失败那条是「**前提未满足，属应然**」（草图数 = 2）"
       "⇒ ⚠ **是这条 smoke 把「应然的失败」当成了 `fail`**（判据问题），**不是退化**；"
       "⚠ 它被 `part_and_features` 当 evidence ⇒ **那条 evidence 是红的**")
NEW = ("⚠ **轮 181 更正**：**它是真失败，不是"应然"** —— 该 smoke 的判据与它自己的文本**自相矛盾**"
       "（文本说"前提未满足"，而判据用的是"草图数 ≠ 2"），而 **实测前提是成立的**"
       "（2 个草图 + 两个都 `mark=1` 选中）⇒ ★ **前提成立而 `insert_composite_curve` 仍失败** ⇒ "
       "**一个真缺陷**（与轮 142/151 那族一致）。★ 判据已改成「前提成立才要求 True」⇒ 现在这条红**含义准确**。"
       "⚠ 它被 `part_and_features` 当 evidence ⇒ **那条 evidence 是红的**。")
assert OLD in t, "锚点不符（acceptance-status.md 的文字可能已变）"
t = t.replace(OLD, NEW, 1)

#: 顶部加一条更正提示
MARK = "> ⚠ 本表是 **2026-10-01（轮 180）** 的快照"
i = t.find(MARK)
assert i > 0
NOTE = ("> ⚠⚠ **轮 181 更正**：`verify_composite_curve_smoke` 那条**不是"判据把应然当失败"** ——\n"
        "> 它的判据**与自己的文本矛盾**，而**实测前提是成立的** ⇒ ★ **它是真失败**（真缺陷）。\n"
        "> 判据已改成「**前提成立才要求 True**」⇒ 现在这条红**含义准确**（仍是红，因为**确实失败**）。\n")
t = t[:i] + NOTE + t[i:]
P.write_text(t, encoding="utf-8")
ast.parse  # noqa: B018
print("  ok acceptance-status.md 已更正（%d 字节）" % len(t))
