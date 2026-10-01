# Tasks: 交付报告的判据编号与 `AGENTS.md §一` 对齐

**Input**: [spec.md](spec.md) · [plan.md](plan.md)

**格式**：`[ID] [P?] [Story] 描述` —— 每个任务带 `→ 验收:`

**状态**：**全部完成**（轮 82）。

---

## Phase 0: 对照两套编号（**先查证，不假定偏移**）

- [x] **T-201** 从 `AGENTS.md §一` 抽权威判据表
  **✅** 10 条（A1–A10）；A5 = **COM 签名对齐**、A8 = **报告写明补齐/空缺/原因**。
  `→ 验收:` `Select-String D:\AI\SW\AGENTS.md -Pattern '^\| A\d+ \|'`

- [x] **T-202** 解析报告 §四 的表，**逐行对照**
  **✅** 得出**错位表**（报告「A5」实为 A6、报告「A7」实为 A8、报告「A8」是 fork 且非 A 判据…）。
  ⚠ **证伪了"整体偏移一位"**：报告「A4 目录结构与上游一致」在 `AGENTS.md` 里**没有**对应判据
  （那是**铁律 3**，不是 A 判据）。
  `→ 验收:` 见 `spec.md §背景` 的错位表

---

## Phase 1: 写门禁（**先证明有牙齿**）

- [x] **T-203** 写 `scripts/check_report_criteria_alignment.py`
  **✅** 抽两套集合 + **单列非 `A\d+` 的编号行**；两者必须相同。
  `→ 验收:` `python scripts/check_report_criteria_alignment.py`

- [x] **T-204** ★ **跑现状必须先红**（有牙齿的证明）
  **✅** 实测输出：
  ```
  `AGENTS.md §一` 定义了 **10** 条：['A1'…'A10']
  报告自评表里出现 **7** 条：['A2'…'A8']
  [FAIL] 缺：['A1', 'A9', 'A10']
  [FAIL] 混入非 A 编号的行：['官方 API 覆盖']
  ```
  `→ 验收:` 同上（**修复前**运行 ⇒ 退出码 1）

- [x] **T-205** 修判据的**粗体盲区**
  **✅** 第一版 `^\|\s*(A\d+)\s*\|` **匹配不到** `| **A1** |`（表格惯用粗体）⇒ 改成
  `^\|\s*\*{0,2}(A\d+)\*{0,2}\s*\|`。★ 又一次「判据要贴合实际产物」。
  `→ 验收:` 修复后 `[PASS] … 逐条一致（10 条）`

---

## Phase 2: 重写 §四

- [x] **T-206** 重写 `harvest-report.md §四` 为 10 行逐条对齐（每行带可复跑依据）
  **✅** 15 行 → 24 行；**不沿用**任何旧编号。
  `→ 验收:` 门禁 `[PASS]`；`Select-String docs\harvest-report.md -Pattern 'A10'`

---

## Phase 3: 接线（**两层 + 汇总，缺一不可**）

- [x] **T-207** `release_check.py` 里调用它
  **✅** 加 `_run_report_criteria_alignment_gate()` + 失败即 `raise AssertionError`。
  `→ 验收:` `python scripts/check_gate_wiring.py`（14 个门禁全接线）

- [x] **T-208** `docs/gate-classification.json` 登记 `hard`
  **✅** 13 → **14** 条。
  ⚠ 未登记时元门禁报：「被调用，却**没登记分类**（登记表必须覆盖每一个调用点）」。
  `→ 验收:` 同上

- [x] **T-209** 结果进 `_gate_results`
  **✅** 加 `"report_criteria_alignment": crit_align`。
  ⚠ 未加时元门禁报：「`crit_align` 的结果**没有进返回体** ⇒ **静默跳过与没跑等价**」。
  `→ 验收:` 同上

---

## Phase 4: 加固 `check_report_freshness`（**撞见的假绿**）

- [x] **T-210** 把「报告在、但读不出那行」从 **SKIP** 改成 **FAIL**
  **✅** 保留「报告不存在 ⇒ SKIP」（便携性）。
  **负例实测**：拿**数字被抹掉**的报告当输入 ⇒ **exit 1**（修前是 exit 0 SKIP）。
  `→ 验收:` 见 [converge.md](converge.md) §2.2

- [x] **T-211** 加固"同步报告数字"的脚本：**修法行为空 ⇒ 直接退出不写**
  **✅** 那正是本轮写坏报告行的直接原因（空值被写进去）。
  `→ 验收:` 本次同步脚本含该守卫且通过

---

## Phase 5: 收工

- [x] **T-212** [P] 十三道硬门禁 + 生成物刷新
  `→ 验收:` `python scripts/release_check.py`（exit 0）

- [x] **T-213** 全量回归
  `→ 验收:` `python -m pytest tests -q`（970 passed / 17 skipped / 0 failed）

- [x] **T-214** 两仓库各自 commit
  `→ 验收:` `git -C C:\swprojects\sw-skill-fork log --oneline -1` + `git -C D:\AI\SW log --oneline -1`
