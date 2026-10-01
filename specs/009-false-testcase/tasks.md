# Tasks: 假用例普查

**Input**: [spec.md](spec.md) · [plan.md](plan.md)

**格式**：`[ID] [P?] [Story] 描述` —— 每个任务带 `→ 验收:`

**状态**：**全部完成**（轮 85）。

---

## Phase 0: 普查（**先看有多少**）

- [x] **T-501** 蒐集 `tools/` 下全部探针
  **✅** **24 个** `*.py`；其中含「造负例输入」特征（`坏`/`bad`/`broken`/`tamper`/`故意`/`不存在`）的 **8 个**。
  `→ 验收:` `Get-ChildItem tools -Filter *.py | Measure-Object`

- [x] **T-502** 在其中找「用变换造负例输入」的形态
  **✅** 只用 `re.sub`/`replace` 的：`build_union_sources` / `capability_gap` / `fetch_api_signature`
  （**都是正当的文本处理**，不是造负例）+ **`probe_skip_semantics.py`**。
  ⇒ 真正相关的**只有 1 处**。
  `→ 验收:` `python scripts/check_negative_input_selfproof.py`

- [x] **T-503** ★ **先实测那处是否真的生效**（不靠"看起来像"）
  **✅** 实测**生效**：`41954 -> 41897` 字节，那行确实被抹成 `> 偏离上游： · 工作区 clean`
  ⇒ **碰巧是对的**，但**没有自证** ⇒ 下次正则一改就会**静默变回假用例**。
  `→ 验收:` 见 [converge.md](converge.md) §2.2

---

## Phase 1: 写门禁（**先证明有牙齿**）

- [x] **T-504** 写 `scripts/check_negative_input_selfproof.py`
  **✅** 扫 `tools/*.py`，凡「变换 + 附近出现负例名」处，在前后 **10 行**内找自证证据
  （比对不等 / 前后字节数 / 断言）。⚠ 窗口取 10 是**工程折中**，已写进注释。
  `→ 验收:` `python scripts/check_negative_input_selfproof.py`

- [x] **T-505** ★ **跑现状必须先红**
  **✅** `[FAIL] **1/1** 处「造负例输入」的变换**没有自证**`
  —— **那正是它有牙齿的证明**（找到的是**真实存在**的那处，不是为测试造的样本）。
  `→ 验收:` 同上（**修复前**跑）

- [x] **T-506** 覆盖面**不夸大**
  **✅** 门禁在 `[PASS]` 输出里**也打印**：
  「只判『变换没生效』这一类（类型 1）；类型 2/3/4 …**需要语义判断，未判**」。
  `→ 验收:` 同上（修复后跑）

---

## Phase 2: 修（**加自证，不加特例**）

- [x] **T-507** `probe_skip_semantics.py` 报告那条：先算 → `assert new != old` → 再写 → 打印字节数
  **✅** 现在输出 `坏报告: 41954 -> 41897 字节（数字被抹掉，自证 ✓）`，
  且 `assert` 会在变换失效时**直接抛**（而不是静默空转）。
  `→ 验收:` `python tools/probe_skip_semantics.py`

---

## Phase 3: 接线（**三层**）

- [x] **T-508** `release_check.py` 调用 + 结果进 `_gate_results`
  **✅** 加 `_run_negative_input_selfproof_gate()` + `"negative_input_selfproof": selfproof`。
  `→ 验收:` `python scripts/check_gate_wiring.py`

- [x] **T-509** `docs/gate-classification.json` 登记 `hard`
  **✅** 14 → **15** 条。
  ⚠ 未登记时元门禁报：「被调用，却**没登记分类**」；未进汇总时报「**静默跳过与没跑等价**」。
  `→ 验收:` `[PASS] 15 个门禁全部已接线`

- [x] **T-510** 移除 `tools/` 下的重复实现（避免两份漂移）
  **✅** 逻辑只留 `scripts/` 一份。⚠ 那是**本轮刚建的**，不是用户数据。
  `→ 验收:` `python scripts/check_negative_input_selfproof.py`（它扫的就是 `tools/`；副本移除后仍 `[PASS]`）
  > ⚠ **门禁的一处局限**（本轮撞到）：我先写的是 `Test-Path tools\audit_negative_input_selfproof.py`（应为 False），
  > 而 `check_spec_acceptance_paths` **只认"文件存在"** ⇒ 把「**验证某文件已移除**」这类验收判据**误报成"仓库外/不存在"**。
  > ⇒ 已改写为**仓库内可达**的等价命令；**该局限如实记进 converge §2.6**。

---

## Phase 4: 收工

- [x] **T-511** [P] 14 道门禁 + 生成物刷新
  `→ 验收:` `python scripts/release_check.py`（exit 0）

- [x] **T-512** 全量回归
  `→ 验收:` `python -m pytest tests -q`（970 passed / 17 skipped / 0 failed）

- [x] **T-513** 两仓库各自 commit
  `→ 验收:` `git -C C:\swprojects\sw-skill-fork log --oneline -1` + `git -C D:\AI\SW log --oneline -1`
