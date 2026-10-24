# E 维度 · 门禁体系现状

> 观测时间 **2026-10-24** · 观测方式：静态解析 `scripts/check_*.py` + 读 `release_check.py` 源码 + 读 `docs/gate-classification.json`（只读）
> 复现总命令：
> ```powershell
> python docs\state\probes\probe_gates.py --json docs/state/inventory-e.json
> ```

---

### E-01 `scripts/check_*.py` 共 55 个，其中 52 个被 `release_check.py` 引用

- **读数**：文件 **55** · 在 `release_check.py` 里出现 `str(ROOT / "scripts" / "<名字>")` 的 **52** · 未出现的 **3**
- **未接的 3 个**：`check_fact_single_home.py` · `check_member_owner_interface.py` · `check_official_source_defects.py`
- **交叉核对**：这 3 个都在 `docs/gate-wiring-exemptions.json` 里（各带 `reason` 与 `evidence`）
- **未确认**：无

### E-02 `kind` 分布：`release_static` 51 · `diagnostic` 3 · **未登记 1**

- **读数**：`docs/gate-classification.json` 里 `kind=release_static` **51** · `diagnostic` **3** · 有文件但**不在分类表**的 **1**：`check_official_source_defects.py`
- **交叉核对**：`check_official_source_defects.py` **同时**出现在豁免清单（E-01）⇒「已豁免 + 未分类」并存
- **未确认**：分类表未登记是否会影响 `check_gate_wiring.py` 的判定——本次只读了该门禁的输出（PASS）

### E-03 分类表 59 条，其中 5 条在 `scripts/` 下找不到同名文件

| 分类表里的条目 | 实际位置 |
|---|---|
| `check_inject_binding.py` | `tools/check_inject_binding.py` |
| `check_judge_preflight.py` | `tools/check_judge_preflight.py` |
| `check_server_side_tools.py` | `tools/check_server_side_tools.py` |
| `check_typelib_tables.py` | `tools/check_typelib_tables.py` |
| `tests/test_inout_array_audit_contract.py` | `tests/` 下的**测试文件**（分类表 L275）|

- **读数**：分类表 **59** 条 · 与 `scripts/check_*.py` 同名匹配的 55 条中 54 条对上（差的那条见 E-02）
- **记录员注（陈述）**：分类表里有 4 条指向 `tools/` 下的文件、1 条指向 `tests/` 下的测试文件
- **未确认**：这 5 条是历史遗留还是有意登记（分类表本条目无「为什么放这条」的说明字段）

### E-04 只有 7/55 个门禁带 `selftest(`（负例自证）

- **读数**：含 `def selftest(` 的 **7** 个：`check_assumption_ledger.py` · `check_corpus_shape.py` · `check_fact_provenance.py` · `check_known_facts_triage.py` · `check_review_ids.py` · `check_sketch_definition.py` · `check_tools_index_fresh.py`
- **交叉核对**：`AGENTS.md` 与门禁文档里出现过「负例自证」的说法；本读数只统计**函数名**，不判断自证内容是否有效
- **未确认**：这 7 个的 `selftest()` 是否在 `main()` 里真被调用、是否在失败时影响退出码——未逐文件读调用点

### E-05 门禁文件体积跨度大：87 行 ~ 818 行

- **读数**：最小 `check_refuted_patterns.py` **87** 行 · 最大 `check_dispatch_entry_guard.py` **818** 行（次大 `check_interface_member_ownership.py` **808** 行，其 `kind=diagnostic`）
- **证据**：`docs/state/inventory-e.json` 的 `rows[].lines`
- **未确认**：行数与检查范围的对应关系——未逐门禁统计其检查对象数量

### E-06 `release_check.py` 自身规模与门禁数

- **读数**：`release_check.py` 报告 `gates` 字典登记项 —— 最近一次实跑输出 `status: pass`，门禁明细里含 `survey_cards`（本轮新增）
- **证据**：`output/_rc25.txt`（本轮实跑）；历史记录见 `docs/harvest-digest.md` 的「门禁 N 道」
- **未确认**：`release_check.py` 内 `gates` 字典的**精确项数**——本次未直接从源码计数，只从 JSON 输出读过 `status`

### E-07 「未接线」的判定口径

- **读数**：`check_gate_wiring.py` 用正则 `str\(\s*ROOT\s*/\s*"scripts"\s*/\s*"<名字>"\s*\)` 判「是否被 `release_check` 调用」（`scripts/check_gate_wiring.py:59-63`）
- **实测影响**：本轮（2026-10-24）曾出现「函数定义漏写但调用点已加」时，该门禁报的是「**未接线**」而不是 `NameError` ⇒ 判定只认那一行字符串
- **未确认**：除该正则外是否还有第二条判定路径——未逐行读该门禁全文

---

## 本节未覆盖（留给后续补充）

- 56 道门禁各自的**检查对象**与**判据来源**（本文件只记了首行 docstring、行数、接线、分类、selftest）
- `docs/gate-wiring-exemptions.json` 里 3 条豁免的 `reason` 与 `evidence` 是否与现状一致（只确认了存在）
- `release_check.py` 里各门禁的**执行顺序**与「先失败先抛」行为
- 门禁对**本仓之外**（如 `C:\swapi`、`AI Solidworks`）的依赖面
