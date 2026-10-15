import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

R = Path(r"C:\swprojects\sw-skill-fork")
P = R / "docs" / "acceptance-status.md"
t = P.read_text(encoding="utf-8")

OLD = ("★ **本轮（轮 180）查清**：失败那条是「**前提未满足，属应然**」（草图数 = 2）"
       "⇒ ⚠ **是这条 smoke 把「应然的失败」当成了 `fail`**（判据问题），**不是退化**；"
       "⚠ 它被 `part_and_features` 当 evidence ⇒ **那条 evidence 是红的**")
NEW = ("⚠ **轮 181 更正：它是真失败，不是「应然」** —— 该 smoke 的判据与它自己的文本**自相矛盾**"
       "（文本说「前提未满足」，而判据用的是「草图数 不为 2」），而 **实测前提是成立的**"
       "（2 个草图 + 两个都 `mark=1` 选中）⇒ ★ **前提成立而 `insert_composite_curve` 仍失败** ⇒ "
       "**一个真缺陷**（与轮 142/151 那族一致）。★ 判据已改成「前提成立才要求 True」⇒ 现在这条红**含义准确**。"
       "⚠ 它被 `part_and_features` 当 evidence ⇒ **那条 evidence 是红的**。")
if OLD in t:
    t = t.replace(OLD, NEW, 1)
    print("  ok 表格行已更正")
else:
    print("  ⚠ 锚点不符（可能已改过）")

MARK = "> ⚠ 本表是 **2026-10-01（轮 180）** 的快照"
i = t.find(MARK)
if i > 0 and "轮 181 更正" not in t[:i] + t[i:i + 200]:
    NOTE = ("> ⚠⚠ **轮 181 更正**：`verify_composite_curve_smoke` 那条**不是「判据把应然当失败」** ——\n"
            "> 它的判据**与自己的文本矛盾**，而**实测前提是成立的** ⇒ ★ **它是真失败**（真缺陷）。\n"
            "> 判据已改成「**前提成立才要求 True**」⇒ 现在这条红**含义准确**（仍是红，因为**确实失败**）。\n")
    t = t[:i] + NOTE + t[i:]
    print("  ok 顶部提示已加")
P.write_text(t, encoding="utf-8")
print("  最终 %d 字节" % len(t))
