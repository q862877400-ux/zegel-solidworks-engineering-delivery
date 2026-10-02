# Tasks: `checked == 0` 的 SKIP 语义

**Input**: [spec.md](spec.md) · [plan.md](plan.md)

**格式**：`[ID] [P?] [Story] 描述` —— 每个任务带 `→ 验收:`

**状态**：**全部完成**（轮 84）。

---

## Phase 0: 论证必然性（**不猜**）

- [x] **T-401** 读上游：能走到 `checked == 0` 的前提是什么
  **✅** 上游 `if not refs: SKIP` ⇒ 走到 `checked == 0` 时 **`refs` 必然非空**。
  `→ 验收:` `Select-String scripts\check_signature_audit_freshness.py -Pattern 'if not refs'`

- [x] **T-402** 读 `resolve_module`，确认表里模块是**本仓库的**文件
  **✅** 解析顺序：① 带路径原样 ② `scripts/<name>` ③ `subskills/**/<name>` ④ 全仓 rglob（唯一命中）。
  ⚠ 它的 docstring **自己就记着轮 55 的误 SKIP**（6/6 全报「跑不了」）。
  `→ 验收:` `Select-String scripts\check_signature_audit_freshness.py -Pattern 'resolve_module'`

---

## Phase 1: 复现（**先复现，再改**）

- [x] **T-403** 写 `tools/probe_checked_zero_skip.py`
  **✅** `--repo` 指向空临时目录 + `--raw` 用真反射 ⇒ 逼出 `refs` 非空、`checked == 0`。
  ⚠ 第一版把**源码文本**（`Path(r"…")`）当路径传 ⇒ 走的是**另一条** SKIP 分支
  （「拿不到反射」那条），**根本没测到目标路径** ⇒ 改成抽引号里的真路径。
  `→ 验收:` `python tools/probe_checked_zero_skip.py`

- [x] **T-404** ★ **修前实测**：那条路径当前是 SKIP
  **✅** 输出「反射文件 **13** 份 · 6 个模块跑不了」+「**SKIP** —— 一个模块都没能实跑」
  + **exit=0** —— **与轮 55 的误 SKIP 形态一模一样**。
  `→ 验收:` 同上（**改之前**跑）

---

## Phase 2: 改（**一次性语义修正，理由写进注释**）

- [x] **T-405** `checked == 0` 分支：SKIP → **FAIL**
  **✅** 输出含「反射转储**在**（13 份），但表里 **6** 个模块**一个都解析不出来**」
  + 列出解析失败的模块名 + 指向 `resolve_module` 的解析顺序；返回 **1**。
  **理由写进代码注释**（让下一个人不必再推一遍"为什么这不是便携性"）。
  `→ 验收:` 见 [converge.md](converge.md) §2.1

---

## Phase 3: 两边都测

- [x] **T-406** 正例（真仓库 + 真反射）⇒ exit 0
  **✅** `[PASS] 6 个模块逐项相符`，exit 0。
  `→ 验收:` `python scripts/check_signature_audit_freshness.py`

- [x] **T-407** 负例（空仓库 + 真反射）⇒ **exit 1**
  **✅** exit 1（修前 0）。
  `→ 验收:` `python tools/probe_checked_zero_skip.py`

- [x] **T-408** 便携性（`--raw` 不存在）⇒ **仍 SKIP exit 0**
  **✅** `**SKIP** —— 拿不到 iface_*.txt（…）`，exit 0。
  `→ 验收:` 同 T-407 的探针 + 手工一条命令

---

## Phase 4: 修那个假用例（**回看 007 的产物**）

- [x] **T-409** `tools/probe_skip_semantics.py` 的「删表」正则**没匹配上**
  **✅** 产出的"坏文档"仍带完整的表 ⇒ 门禁照常 `[PASS]`，**而我当时当成了修好的证据**。
  ⇒ 改成**造一份只有标题、不含表的文档** ⇒ 实测 `exit=1`，用例这才成立。
  `→ 验收:` `python tools/probe_skip_semantics.py`（② 段应显示 **exit=1**）

---

## Phase 5: 收工

- [x] **T-410** [P] 13 道门禁 + 生成物刷新
  `→ 验收:` `python scripts/release_check.py`（exit 0）

- [x] **T-411** 全量回归
  `→ 验收:` `python -m pytest tests -q`（970 passed / 17 skipped / 0 failed）

- [x] **T-412** 两仓库各自 commit
  `→ 验收:` `git -C . log --oneline -1` + `git -C D:\AI\SW log --oneline -1`

---

## ⚑ 与已知事实 53 的对账

「同一处**连续修补 ≥3 次**就该停下」—— 本次改的是 `checked == 0`，
而轮 83 改的是「文档在但表读不出」（**另一个分支**）⇒ **不是反复改同一处**，
且本次是**查证后的一次性修正**，非试参数。
