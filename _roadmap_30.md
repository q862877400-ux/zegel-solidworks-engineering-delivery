            ㉚ 🔴 **A5 的真实缺口被发现并修掉**（轮 55）：`docs/signature-audit.md` 的**逐模块调用点数**已失真
               —— 与 `harvest-report` **完全同型**的缺口（**只查存在、不查数字**），
               只是这一份**还能实跑复核**（它自己的「复跑方式」给了命令）：
               ```
               drawing_workflow.py   文档 140/137  →  实际 198/194（+1 查不到：GetModelViewManager）
               sw_simulation.py      文档  34/34   →  实际  44/44
               sw_topology.py        文档  45/45   →  实际  49/49  ← 轮 51 加了 4 个 COM 调用
               ⇒ **3/6 失真**
               ```
               ★ **这就是 A5 的缺口**：表在、数字失真 ⇒ 让人**以为覆盖是 45 个调用点**（实际 49）
            ㉛ ★ **新增 `scripts/check_signature_audit_freshness.py`（硬门禁）**：
               按文档表里的模块清单**逐个实跑** `audit_call_arity.py`（传全 `iface_*.txt`）并逐项比对
               ★ **便携性守卫**：拿不到 `D:\AI\SW\_raw` 或模块文件 ⇒ **SKIP 并 exit 0**
               ★★ **两个踩到并修的判据问题**：
                 ① 表里是**裸文件名**而它们在 `scripts/` 与 `subskills/**/` ⇒ 加 `resolve_module()`
                    （**首跑 6/6 全报「跑不了」⇒ 误 SKIP**）
                 ② **同名文件有两份**：`drawing_workflow.py` 的**源**与**桌面内嵌快照**
                    （`apps/*/resources/skill/**`，gitignore 构建产物）⇒ 解析器**排除 `resources`**
                    （否则判「不唯一」而白丢 1 个模块）
               ★ 口径写进门禁输出：**调用点数会随代码增长 ⇒ 这是应该的**；
                 门禁要的是「**文档跟得上代码**」，不是「数字永远不变」
               ⇒ 契约测试 **8 条**（含负例 + 两个假命中守卫）· 回归 **897 passed / 17 skipped / 0 failed**
            ㉜ ★ **两份「新鲜度」门禁已同型化**：`check_report_freshness.py`（harvest-report 的偏离数字）
               与 `check_signature_audit_freshness.py`（signature-audit 的逐模块数字）——
               **同一族缺口（「存在但数字失真」）的两份制品**，现在都有硬门禁守着。
               ★ **下一步**：这份文件里其余**历史性**数字（批次 1–4 的手工统计）**未纳入**门禁
                 （它们记录的是当时的查证动作，不是当前状态）—— 若将来要核，需先给它们一个可跑的定义。
