            83 🎯 **门禁结果**全部进返回体** + `skipped` **显式可见**（同一问题的第五层，轮 74）：
               轮 71–73 解决了「接线了没 / 接线方式对不对 / 跳过时算不算数」；本轮问：
               **「跳过了」在结果里看得见吗？**
               ⚠ 实测 `release_check` 的返回体：
               ```python
               return {
                   "status": "pass",
                   "provenance": provenance,      # ← 只汇总了 **4 个**
                   "diff_markers": markers,
                   "member_names": member_names,
                   "interface_ownership": ownership,
                   "missing": [],
               }
               ```
               · 其余 **9 个门禁的状态根本没被汇总**；
               · **没有任何地方统计 `skipped`** ⇒ **「跳过了」是隐形的**。
               ★ **一个静默跳过的门禁，与没跑等价**（第三种面孔）。
               ⇒ **修两件**：① **13 个状态一次全列**（`_gate_results` → `gates`），
                 非 dict 的标 `unknown`（**不谎报 pass**）；② **`skipped` 显式列出**
                 （+ `skipped_count`），另附 `gates_passed` 与 `gates_diagnostic`。
               ⇒ 实测：`gates: 13 个（12 pass + interface_ownership=clean）` ·
                 **`skipped: []（0 个）`** · `diagnostic: ['interface_ownership']`。
               ⇒ **元门禁加第五层**「汇总完整性」：`aggregated_vars()` 从 AST 取
                 `_gate_results` 的 value 名集合，与 `run_release_check` 里所有 `_run_*` 赋值
                 逐一对照 ⇒ **少汇总一个就报**；反向也报。
               ★ 负例 3 条：真仓库 ≥13 ✓ · 假源码漏汇总一个能被发现 ✓ · 返回体必须有
                 `"skipped": skipped` / `skipped_count` / `gates` ✓。
            84 ⚑ **本轮被两道门禁各拦一次 —— 那是门禁在尽职的证据**：
               ① **报告数字不符** ⇒ raise（正常流程，同步即可）；
               ② **改了 `release_check.py` 没跑 `sync_bundled_skill.py`** ⇒
                  「桌面内嵌 Skill 与根 Skill 不一致: scripts/release_check.py」——
                  那正是**已知事实 55**，而**门禁帮我记着**
                  （该快照在 `.gitignore` 里 ⇒ `git status` **看不见它**，人容易忘）。
               ★ 这正是本轮主题的反面印证：**门禁的价值在于它记得人容易忘的事**。
