# D 维度 · `scripts/` 脚本层现状

> 观测时间 **2026-10-24** · 观测方式：AST 解析 + 与工具声明交叉 + 复用统一化门禁输出（只读，**不 import 任何 scripts 模块**，避免触发 COM）
> 复现总命令：
> ```powershell
> python docs\state\probes\probe_scripts.py --json docs/state/inventory-d.json
> ```

---

### D-01 `scripts/*.py` 213 个，语法错误 0，函数 2,078 · 类 55

- **读数**：顶层 `.py` **213** 个 · `ast.parse` 失败 **0** 个 · 函数 **2,078** · 类 **55**
- **交叉核对**：本轮早前记录的口径是「`scripts/*.py` 211 个」——本次实测 **213**（含本轮新增的 `check_survey_cards.py`、`gen_survey_matrix.py`）
- **未确认**：无

### D-02 来源块覆盖率 213/213；无 docstring 的 7 个

- **读数**：含 `# ── 来源` 的 **213/213** ⇒ AGENTS `§十八` 要求的来源块在**顶层 scripts 模块**里全覆盖
- **读数**：顶层模块缺模块级 docstring 的 **7** 个：`sw_loft.py` · `sw_measure.py` · `sw_sensor.py` · `sw_surface_features.py` · `sw_sweep.py` · `sw_units.py` · `sw_wrap.py`
- **未确认**：这 7 个是否在其它位置（如函数级 docstring）有等价说明——未逐个读文件

### D-03 被工具声明引用的模块 **75** 个

- **读数**：`ToolSpec.module` 的顶层名与 `scripts/*.py` 文件名取交集 ⇒ **75**
- **未确认**：`ToolSpec.module` 里出现 `scripts` 子包（如 `engineering.catalog`）的情况未纳入此交集——见 D-04

### D-04 `ToolSpec.module` 里出现一个**包目录**名（非单文件模块）

- **读数**：`ToolSpec.module` 的顶层名集合中，有一个在 `scripts/*.py` 里无同名文件：**`engineering`**
- **实测**：`scripts/engineering/` **是目录**（`Test-Path -PathType Container` = True），其下有 **48** 个 `.py`
- **记录员注（陈述）**：本探测的「同名文件」判据只看顶层 `*.py`，因此包目录会被算成「不存在」
- **未确认**：`engineering` 包里 48 个模块中，被 `ToolSpec` 实际引用的有几个——本次只见到 `engineering.catalog`（B-09 那 4 条）

### D-05 未被工具声明引用的模块 **138** 个

- **读数**：213 顶层模块中，未被任何 `ToolSpec.module` 引用 **138** 个（占 64.8%）
- **未确认**：这 138 个里有多少是**门禁脚本/生成器/一次性探针**（本来就不该被工具层引用）——本次未按用途分类

### D-06 在 `tools/` 与 `tests/` 的文本里也搜不到名字的模块 **34** 个

- **观测方式**：把 `tools/*.py` + `tests/*.py` 全文拼成一个语料，检查模块名是否作为子串出现
- **读数**：D-05 的 138 个中有 **34** 个在该语料里搜不到
- **前 12 个（逐字）**：`audit_acceptance_criteria` · `check_corpus_shape` · `check_repo_uniformity` · `check_survey_cards` · `gate_decl` · `gen_survey_matrix` · `headless_common` · `refresh_api_signatures` · `sw_api_dsgnchk` · `sw_api_fworks` · `sw_api_gtswutilities` · `sw_api_sldtoolboxconfigureaddin`
- **★ 本探测口径的边界（必须一起读）**：语料**只含 `tools/` 与 `tests/`**，**不含 `scripts/release_check.py` 与 `docs/`**。
  实测举例：`check_repo_uniformity` 在 `release_check.py` 里被引用 **3** 次、`check_survey_cards` 也有接线 ⇒
  这 34 个**不等于**「全仓无人引用」，只等于「不在 tools/tests 文本里」
- **未确认**：34 个里真正全仓零引用的有几个——需把 `release_check.py`、`docs/`、`apps/` 一起纳入语料重算

### D-07 统一化门禁的五项读数（复用门禁自身输出）

| 指标 | 读数 |
|---|---|
| ① ruff（E,F,I,N,UP）| **415**（上界 415）|
| ② pyscn 克隆组 | **2,315**（信息项）|
| ③ 缺来源块 | **0** |
| ④ 同名 `.py` | **0** |
| ⑤ 跨文件同函数体组 | **76**（豁免 4 组）|

- **证据**：`docs/state/inventory-d.json` 的 `uniformity_readings`（由本探测器调用 `check_repo_uniformity.py` 抓取）
- **未确认**：无

---

## 本节未覆盖（留给后续补充）

- 213 个模块的**实际可导入性**（本次只做 `ast.parse`，未 import；`scripts/` 大量模块会碰 COM）
- 每个模块的用途分类（门禁 / 生成器 / 工具实现 / 一次性探针）
- `scripts/engineering/` 48 个模块的逐一现状
- 未调用函数（`test_no_uncalled_helpers_in_gates_and_tools` 的对象）——本次未跑该测试
