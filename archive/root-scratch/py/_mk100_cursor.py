import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           565 🎯 **Spec Kit `100`：31 条验收命令逐条跑 —— 绿 15 · 红 3 · 探针 13**（轮 180）——
               缘起：轮 179 发现拓扑那条验收命令**变红**（环境）⇒ ★★ **那其余条目呢？**
               ⇒ `tools/run_verified_acceptance_commands.py` 把 `capabilities.yaml` 里 `level == verified`
               条目**声明的 31 条** `python tools/*.py` **逐条跑**（顺序执行，COM 单实例，事实 24）。
            566 ★★★ **最终分类（可一句话说清）**：
               ```
               绿   **15**
               红   **3** —— 两条**已知**（`verify_gtol_smoke` 3/5 = 事实 166；
                               `verify_in_context_reference_smoke` 9/12 = 事实 162）
                             + 一条**本轮查清**：`verify_composite_curve_smoke` 6/7
               探针 **13** —— `probe_*` / `audit_*`：**不设 verdict 是它们的正常形态**
               ```
            567 ★★ **新发现（`composite_curve`）**：它失败的那条是「**前提未满足，属应然**」（草图数 = 2）⇒
               ⚠ **是这条 smoke 把「应然的失败」当成了 `fail`**（**判据问题，不是退化**）——
               而它**被 `part_and_features` 当作 evidence** ⇒ ★ **那条 evidence 本身是红的**。
               ★★★ 若我一直"记得它是绿的"，就永远不会发现 —— **跑一遍本身就有价值**。
            568 ⚠⚠⚠ **而我的跑器第一版判据太窄（如实记）**：本仓库的验收脚本有**三种**输出格式：
               ```
               ① `── 8/8 · verdict: pass ──`           （多数冒烟）
               ② `── 15/15 项通过 · verdict: pass ──`   （`verify_dfm_e2e` / `verify_routing_e2e`）
               ③ `verdict: pass`                       （`verify_costing_e2e`，**无 N/M 计数**）
               ⇒ ★ 我只认 ① ⇒ **把 4 个 pass 误报成「无 verdict」**（11 → 15）
               ```
               ★★★ **本会话已出现 6+ 次同一族**（「我的判据/观测比代码更容易错」）：
                 `113` 兜底 `IObject` · `114` 散文猜接口 · `115` 长度倒序 · `116` 变量名猜接口 ·
                 `118` 错误的测试桩 · **`120` 正则太窄** ⇒ ★ 收敛成一句：
                 **判据要与实现的**实际形态**对齐**，且**每次都要拿真跑对一遍**。
            569 ★ **产出**：**`docs/acceptance-status.md`**（31 条逐条 + 结果 + 定性，已知的写出来处），
               ★ 并**注明它是快照** —— 因为事实 119（「曾经绿」≠「现在绿」）⇒ **每次改完都要重跑**。
               门禁 + `release_check` exit 0 · 回归 **1248 passed**。
               ⚑ **未查证**：⚠ 那 13 个探针**不构成"验收"**（本就不设 verdict，本轮**没**改）；
                 ⚠ 三条红里的**两条已知**（166/162）本轮**没有**解决；⚠ `composite_curve` 的**判据问题只查清、未修**；
                 ⚠ 本表只覆盖 `verified` 条目声明的命令 ⇒ **5 条 `stitched` 不在内**。
               下轮候选：① 修 `verify_composite_curve_smoke` 的判据（把「应然」与「失败」分开）；
               ② 把 `part_and_features` 里那条红 evidence 处理掉（换绿证据或改条目）；
               ③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+565 ", before, re.M):
    print("  游标 565 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+569 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 569 行已存在 ✓")
