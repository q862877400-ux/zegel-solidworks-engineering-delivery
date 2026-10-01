import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           584 🎯 **Spec Kit `104`：样条修好后 `InsertCompositeCurve` ****仍失败**** —— 真因未查明，按事实 53 停手**（轮 184）——
               ★★★ **决定性测试**（把 smoke 的输入从**两条直线**改成**两条样条草图**，照官方样例）：
               ```
               ✓ 特征树里有 2 个草图
               ✓ 用 mark=1 各选一次（草图2=True · 草图1=True）
               ✓ ★★★ **上游前置：本机能建出样条吗 ⇒ 能建**（轮 183 修好的）⇒ **前置确实可达了**
               ✗ insert_composite_curve（前置可达时要求 True）⇒ **仍失败**（RuntimeError）
               ```
            585 ★★ **所以：官方要求的前置确实满足了，而它仍不成** ⇒ 这是**真失败**，**真因未查明**。
            586 ⚠⚠ **而我试图排除「选实体 vs 选特征」时，实验**本身无效****：
               ```
               官方 Remarks 原文："select the **entities** by calling SelectByID2 with a **mark number of 1**"
               ⇒ 差别候选：**实体（草图段）** vs **草图特征**（smoke 选的是后者）
               ★ 但我的探针三组**都没选中**（`选中 0`）⇒ 三组都返回 False
               ⇒ ★ **不能据此说任何结论** —— **实验无效**，不是「选实体不成」。
               ★ 与**事实 118**（用错误的观测下结论）同族：那次是桩错，这次是**选法没成**。
               ```
            587 ★★★ **按事实 53 停手**：`composite_curve` 已在 **142 / 151 / 182 / 183 / 184** 反复 ⇒
               **本轮到此为止**，如实记：
               * ★ **前置可达**（样条已修好）—— 这一步是**真实的进展**；
               * ★ 而它**仍失败** ⇒ **真因未查明**；
               * ⚠ 「选实体 vs 选特征」这条候选**未排除**（我的对照实验无效）；
               * ⚠ 官方三份样例的**代码主体在本机被截断** ⇒ 它具体怎么选**看不到**。
            588 ★★★ **三轮把一个问题「定位干净」了**：
               ```
               轮 182：前置不可达（样条建不出）⇒ 那条红**不算它的错**
               轮 183：样条修好 ⇒ 前置**可达**
               轮 184：前置可达而它**仍失败** ⇒ ★ **现在这条红是它自己的问题了**
               ⇒ ★ 这不是"没解决"，而是**把问题定位干净了** ——
                 下一个动它的人**不会再被"前置"误导**。
               ```
               门禁 + `release_check` exit 0 · 回归 **1248 passed**。
               ⚑ **未查证**：⚠ **`composite_curve` 仍不可用**（真因未查明）；
                 ⚠ 「选实体 vs 选特征」**未排除**；⚠ 官方样例代码**被截断**（真正的选法**看不到**）；
                 ⚠ 我的那个探针**无效**（选中 0）⇒ **不构成任何证据**。
               下轮候选：① **换题**（这处已按事实 53 停手）—— 如 `surface_modeling` / `mold_tools` 的拆条目，
                 或扫其它「返回 None 其实是形态不对」的地方；
               ② 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+584 ", before, re.M):
    print("  游标 584 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+588 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 588 行已存在 ✓")
