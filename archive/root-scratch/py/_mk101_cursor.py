import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           570 🎯 **Spec Kit `101`：`composite_curve` 那条红是****真失败**** —— 而轮 180 我****读反了******（轮 181）——
               轮 180 我看到它的失败文本写着「⚑ **前提未满足，属应然**」⇒ 就把它归成「**判据把应然当失败**」。⛔ **那是错的。**
            571 ★★★ **本轮读那条判据的源码 ⇒ 判据与它自己的文本**自相矛盾****：
               ```python
               try:
                   sw_part.insert_composite_curve(doc)
                   chk("insert_composite_curve 返回 True", n_sketch == 2, ...)
               except Exception as exc:
                   chk("insert_composite_curve", **n_sketch != 2**,
                       "返回 False —— ⚑ **前提未满足，属应然**（草图数 = %d）")   # ← 文本说「前提未满足」
               ```
               ⇒ ★ 判据用的是「**草图数 不为 2**」（= 前提未满足才通过），而 **实测 `n_sketch == 2`** ⇒ **判失败**
               ⇒ ★★★ **所以：前提**是成立的**（2 个草图 + 两个都 `mark=1` 选中），而它仍失败 ⇒ **真缺陷****
                 （与轮 142/151 那族一致：`composite_curve` 在这条后端上到不了）。
            572 ★ **修法**：把判据写成**语义清楚**的一条 —— 「**前提成立才要求 True**；前提不成立 ⇒ **不判**」
               ⇒ 改后那条红**含义准确**（仍是红，因为**确实失败**）：
               `✗ ★ insert_composite_curve（前提成立时要求 True） 前提成立 ⇒ 这是真失败 ⇒ RuntimeError`
               ★ 并更正了 `docs/acceptance-status.md`（表格行 + 顶部提示）。
            573 ★★★ **教训（本会话第 7 次同族，但**形状不同**）**：
               ```
               113~117 / 120：**判据/观测**与实现不匹配（兜底、猜、正则太窄…）
               121        ：★ **我读「文本」就下了结论，没读「判据的源码」**
               ⇒ ★★ 而那条文本**本身是错的**（它说「前提未满足」，
                  而判据要求「前提未满足」才通过 —— ★ **两个都错，且互相掩盖**）
               ⇒ 于是我把「**真失败**」读成了「**应然的失败**」。
               ```
               ⇒ ★ **可复用定则**：**看到「这是应然的」这种措辞，要去读判据本身** ——
                 **注释/文本可以写错，而判据决定了红绿**；两者不一致时，**以判据为准并修文本**。
               ★★★ 这**最危险**的一种错法：**注释替代码说谎，而我看的是注释** ——
                 差点把一个**真缺陷**洗成「应然」。
               门禁 + `release_check` exit 0 · 回归 **1248 passed**。
               ⚑ **未查证**：⚠ **`insert_composite_curve` 本身没修** —— 本轮只**改对了判据**并**更正了结论**；
                 ⚠ 它为什么在前提成立时仍失败（**未查明**）⇒ 与轮 142/151 属同一处**未解问题**；
                 ⚠ `part_and_features` 的 evidence 仍引用这条**红**的 smoke ⇒ **未处理**；
                 ⚠ 其余 **30 条**验收命令本轮未动。
               下轮候选：① 查 `insert_composite_curve` 为什么在前提成立时失败（或按事实 53 停手并记证据）；
               ② 处理 `part_and_features` 那条红 evidence；③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+570 ", before, re.M):
    print("  游标 570 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+573 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 573 行已存在 ✓")
