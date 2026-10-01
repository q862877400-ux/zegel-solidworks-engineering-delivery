            ㊳ ★★ **A2 的「**能力级出处**」落地**（轮 58）—— 此前**只有来源级**（`union-sources.json`），
               「能力级」这一层 schema **没有** `source`/`origin` 字段
               ⇒ 29 条里**无法区分「并入来的」与「本项目自研的」**
               （例：`requirements_planning` 的 backend 是 `local-agent`，**显然是自研**，
                 却**没有地方这么说** —— 这正是 A2 明写的「两条线不该混」）
               ⇒ 29 条**全部**加 `source` + `source_evidence`：
               ```
               source: upstream=17 · mixed=7 · original=3 · undetermined=2
               level : verified=22 · stitched=6 · not_implemented=1
               ```
               ★ **证据两级**：① `tools/propose_capability_sources.py` 的关键词提案（21/29）；
                 ② ★★ **我逐条按能力语义点名候选模块，再用硬证据
                    `git cat-file -e origin/main:<path>` 判定**（**事实 49** 的方法，**比关键词硬**）
                 ⇒ 8 条 `undetermined` **全部**用 ② 复核 ⇒ **7 条定为 upstream**、
                   **1 条如实留 `undetermined`**（`configurations_and_design_tables` ——
                   origin/main 与工作树里**都没找到**明确实现模块）
               ⚠ **为什么必须留 `undetermined` 而不是硬填**：`THIRD-PARTY-NOTICES.md` 自己写着
                 「把**未并入**的东西写成**已并入**，是**归属造假**，比遗漏更严重」
            ㊴ ★ **R12 门禁**（加在**既有** `check_union_conventions` 的「清单形状」段，**不重造新文件**）：
               · `source` 必须在枚举内（`original`/`merged`/`upstream`/`mixed`/`undetermined`）
               · **`source_evidence` 必须非空** —— 一个没有依据的分类等于没分类
               · ★ 负例已测：种入 `source=BOGUS` ⇒ 门禁**精确点名**并 exit 1；还原后 PASS
            ㊵ ⚠ **排查中发现一个**方法学问题**（已记）**：我本想从测试的 import 反查实现模块，
               但 `tests/test_cad_reliability.py` 是**宽泛集成测试** ⇒ import 出一堆**无关**模块
               ⇒ **推不出该能力的实现** —— 正是**事实 51**（分析范围与**组织单元**不匹配）。
               ⇒ **一个测试文件的 import 不等于一个能力的实现清单。**
            ㊶ ★ **A2 的两条线现在都机器可查了**：
               `level: verified` 说的是「**有我们自己的运行证据**」，
               `source: upstream` 说的是「**代码/广度来自上游**」—— **交叉表可见两者独立**
               （`upstream × verified = 14` 正是「上游的代码 + 我们的证据」这一最常见的组合）
               ⇒ 回归 **909 passed / 17 skipped / 0 failed**
