import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── 事实 120 ────────────────────────────────────────────────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 120 | " + "".join([
    "**31 条验收命令逐条跑：绿 15 · 红 3 · 探针 13 —— 其中**只有 1 条**是判据自身的问题** —— ",
    "2026-10-01（轮 180）。",
    "★ 缘起：轮 179 发现拓扑那条验收命令**变红**（环境）⇒ ★★ **那其余条目呢？**",
    "⇒ `tools/run_verified_acceptance_commands.py` 把 `capabilities.yaml` 里 `level == verified` 条目",
    "**声明的 31 条** `python tools/*.py` 逐条跑（顺序执行，COM 单实例，事实 24）。",
    "★★★ **最终分类（可一句话说清）**：",
    "```",
    "绿   **15**",
    "红   **3** —— 两条**已知**（`verify_gtol_smoke` 3/5 = 事实 166；",
    "                `verify_in_context_reference_smoke` 9/12 = 事实 162）",
    "              + 一条**本轮查清**：`verify_composite_curve_smoke` 6/7",
    "探针 **13** —— `probe_*` / `audit_*`：**不设 verdict 是它们的正常形态**",
    "```",
    "★★ **新发现（`composite_curve`）**：它失败的那条是「**前提未满足，属应然**」（草图数 = 2）⇒",
    "⚠ **是这条 smoke 把「应然的失败」当成了 `fail`**（**判据问题，不是退化**）——",
    "而它**被 `part_and_features` 当作 evidence** ⇒ ★ **那条 evidence 本身是红的**。",
    "⚠⚠⚠ **而我的跑器第一版判据太窄（如实记）**：本仓库的验收脚本有**三种**输出格式：",
    "```",
    "① `── 8/8 · verdict: pass ──`                （多数冒烟）",
    "② `── 15/15 项通过 · verdict: pass ──`        （`verify_dfm_e2e` / `verify_routing_e2e`）",
    "③ `verdict: pass`                            （`verify_costing_e2e`，**无 N/M 计数**）",
    "⇒ ★ 我只认 ① ⇒ **把 4 个 pass 误报成「无 verdict」**（11 → 15）",
    "```",
    "⇒ ★ 又一次「**判据要与实现的**实际形态**对齐**」（事实 51 那一族）—— ★ 而且**这已是本会话第 N 次**。",
    "★ 产出：**`docs/acceptance-status.md`**（31 条逐条 + 定性），并**注明它是快照** ——",
    "★ 因为事实 119（「曾经绿」≠「现在绿」）⇒ **每次改完都要重跑**。",
    " | `tools/run_verified_acceptance_commands.py`；`docs/acceptance-status.md`；",
    "`D:/AI/SW/output/verified-acceptance-run.json`；事实 51 / 119 / 162 / 166 |",
])
if "| 120 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 120")
else:
    print("  已有 120")

# ── Spec Kit 100 ────────────────────────────────────────────────────
S = Path(r"D:\AI\SW\specs\100-acceptance-status-swept")
S.mkdir(parents=True, exist_ok=True)
spec = """# 100 · 31 条验收命令逐条跑：绿 15 · 红 3 · 探针 13

**Status**: Implemented（轮 180）

## 一、缘起
轮 179 发现拓扑那条验收命令**变红**（环境）⇒ ★★ **那其余条目呢？**
⇒ `tools/run_verified_acceptance_commands.py` 把 `capabilities.yaml` 里 `level == verified` 条目
**声明的 31 条** `python tools/*.py` 逐条跑（顺序执行，COM 单实例，事实 24）。

## 二、★★★ 最终分类（可一句话说清）
```
绿   **15**
红   **3** —— 两条**已知**：
                · `verify_gtol_smoke` 3/5              = 事实 166
                · `verify_in_context_reference_smoke` 9/12 = 事实 162
              + 一条**本轮查清**：`verify_composite_curve_smoke` 6/7
探针 **13** —— `probe_*` / `audit_*`：**不设 verdict 是它们的正常形态**
```

## 三、★★ 新发现：`verify_composite_curve_smoke` 6/7
```
它失败的那条是「**前提未满足，属应然**」（草图数 = 2）
⇒ ⚠ **是这条 smoke 把「应然的失败」当成了 `fail`**（**判据问题，不是退化**）
⇒ 而它**被 `part_and_features` 当作 evidence** ⇒ ★ **那条 evidence 本身是红的**
```

## 四、⚠⚠⚠ 我的跑器第一版判据太窄（如实记）
```
本仓库的验收脚本有**三种**输出格式：
  ① `── 8/8 · verdict: pass ──`                （多数冒烟）
  ② `── 15/15 项通过 · verdict: pass ──`        （`verify_dfm_e2e` / `verify_routing_e2e`）
  ③ `verdict: pass`                            （`verify_costing_e2e`，**无 N/M 计数**）
★ 我只认 ① ⇒ **把 4 个 pass 误报成「无 verdict」**（11 → 15）
⇒ ★ 又一次「**判据要与实现的实际形态对齐**」（事实 51 那一族）——
  ★ 而且**这已是本会话第 N 次**（113/114/115/116/118/120 同一族）。
```

## 五、★ 产出
```
`docs/acceptance-status.md`：31 条逐条 + 结果 + 定性（已知的写出来处）
★ 并**注明它是快照** —— 因为事实 119（「曾经绿」≠「现在绿」）⇒ **每次改完都要重跑**。
```

## 六、判据
| ID | 判据 |
|---|---|
| SC-10001 | ★★ **逐条跑**那 31 条（不是抽样）|
| SC-10002 | ★★★ **分类**：绿 15 / 红 3 / 探针 13，且**每条红都能说出出处** |
| SC-10003 | ★★ **新发现** `composite_curve` 的判据问题（把「应然」当「失败」）|
| SC-10004 | ★★★ **如实记我跑器的判据太窄**（只认 1/3 种格式 ⇒ 误报 4 个）|
| SC-10005 | ★ 产出 `docs/acceptance-status.md` 并**注明是快照** |
| SC-10006 | 门禁 + 回归不退化 |

## ⚠ 明确记下的限度
* ⚠ 那 13 个探针**没跑出 verdict** ⇒ 它们**不构成"验收"**（本轮**没**改：探针本就不设 verdict）；
* ⚠ **三条红里的两条**（166/162）是**已知未解问题**，本轮**没有**解决它们；
* ⚠ `composite_curve` 的**判据问题本轮只查清、未修**；
* ⚠ 本表是**快照**；★ 而且**只覆盖 `verified` 条目声明的命令**，不覆盖 `stitched` 那 5 条。
"""
plan = """# 100 · Plan

## 步骤
1. 轮 179 发现拓扑验收红 ⇒ ★ **系统性重跑其余条目**
2. ★ 从 `capabilities.yaml` 抽出 `verified` 条目声明的 31 条命令
3. ★ 写跑器（顺序、独立子进程、记 verdict + exit）
4. ⚠ 第一版判据太窄（只认 1 种输出格式）⇒ 误报 4 个"无 verdict"
5. ★ 修成宽松判据（三种格式）⇒ **15 绿**
6. ★★ 分类：绿 15 / 红 3（两条已知 + 一条本轮查清）/ 探针 13
7. ★ 产出 `docs/acceptance-status.md`（注明是快照）
8. 事实 120 → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 抽样跑就下结论 | ★ **逐条跑 31 条** |
| 只看 verdict 不看 exit | ★ **两样都记** |
| 判据只认一种格式 | ⚠ **本轮犯了** ⇒ 修 + **记进事实表** |
| 把快照当永久结论 | ★ 表里**注明快照** + 与事实 119 挂钩 |
"""
tasks = """# 100 · Tasks（全部完成，轮 180）

- [x] T-10001 抽命令 + 写跑器
- [x] T-10002 ★★ 逐条跑 `→ 验收:` `python tools/run_verified_acceptance_commands.py`（**15 绿 / 3 红 / 13 探针**）
- [x] T-10003 修跑器的判据（三种格式都认）
- [x] T-10004 查清 `composite_curve` 的失败性质（**应然**，判据问题）
- [x] T-10005 产出 `docs/acceptance-status.md`
- [x] T-10006 事实 120
- [x] T-10007 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""
converge = """# 100 · Converge

**Converged**: 2026-10-01（轮 180）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-10001 逐条跑 | ✅ 31 条 |
| SC-10002 分类 + 出处 | ✅ 15/3/13 |
| SC-10003 新发现 | ✅ `composite_curve` |
| SC-10004 记我判据太窄 | ✅ 11 → 15 |
| SC-10005 产出表 | ✅ `docs/acceptance-status.md` |
| SC-10006 门禁 + 回归 | ✅ |

## 二、★★★ 「跑一遍」本身就有价值
```
轮 179 只跑了一条 ⇒ 发现它红
轮 180 跑全部 31 条 ⇒ ★ 分类清楚：**15 绿 · 3 红 · 13 探针**
⇒ ★ 而且发现了一条**此前不知道**的红的（`composite_curve`）
⇒ ★★ 若我一直"记得它是绿的"，就永远不会发现。
```

## 三、⚠ 而我的判据**又一次**与实现不匹配
```
本仓库验收脚本有**三种**输出格式，我只认第一种 ⇒ **4 个 pass 被误报成"无 verdict"**
★ 这与事实 51（分析范围要贴合代码组织单元）**同族**，而本会话已出现 6+ 次：
  113 兜底 IObject · 114 散文猜接口 · 115 长度倒序 · 116 变量名猜接口 · 118 错误的桩 · 120 正则太窄
⇒ ★★ 收敛成一句：**我的"判据/观测"比代码更容易错** —— 每次都要拿真跑对一遍。
```

## 四、未查证
* ⚠ 13 个探针**不构成验收**（本就不设 verdict）；
* ⚠ 三条红里的**两条已知**（166/162）**未解决**；
* ⚠ `composite_curve` 的**判据问题只查清、未修**；
* ⚠ 只覆盖 `verified` 条目声明的命令（**5 条 `stitched` 不在内**）。
"""
for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
