# L 维度 · 100 条 `verified` 的 `evidence` 可核验性

> 观测时间 **2026-10-24** · 观测方式：YAML 解析 + 路径记号解析（仓库内 / 仓库外官方源 / 名字回退）+ `Path.exists()`（只读，**不执行任何 evidence 命令**）
> 复现总命令：
> ```powershell
> python docs\state\probes\probe_evidence.py --json docs/state/inventory-l.json
> ```

---

### L-01 100 条 `verified` 共 **333** 个 evidence 元素

- **读数**：能力 **100** 条 · evidence 元素 **333** 个（平均 3.3 个/条）
- **元素个数分布**：见 `inventory-c.json` 的 `verified_evidence.kind_histogram`（1 项 8 · 2 项 32 · 3 项 28 · 4 项 18 · 5 项 5 · 6 项 3 · 7 项 3 · 9 项 2 · 23 项 1）
- **未确认**：无

### L-02 元素分三类：文件路径 **235** · 自由文本 **78** · 命令 **20**

| 类型 | 个数 | 能否独立核验 |
|---|---|---|
| 文件路径（含 `.py/.json/.md/...` 记号）| **235** | 可（本文件 L-03 逐条解析）|
| 命令（含 `python/pytest/pwsh/git/npm/uv`）| 20 | 部分（本文件只核命令里出现的文件记号，**不执行**）|
| 自由文本（无路径无命令）| **78** | 不可（本次不做语义判断）|

- **证据**：`inventory-l.json` 的 `item_kinds`
- **未确认**：那 78 条自由文本各自陈述了什么——本文件不评价内容

### L-03 235 个路径记号中，**222 个可达**、**13 个不可达**

- **读数**：可达 **222**（其中含指向仓库外官方源 `C:\swapi\` 的引用，见 L-05）· 不可达 **13**
- **不可达分类**：`移到仓库内他处`（按文件名在仓库里找得到）**9** · `全仓与外部源都找不到` **4**
- **未确认**：`output/` 那 3 个属于「按设计不入库的构建产物」（见 L-04），是否算「不可达」取决于读者口径——本文件只报分类

### L-04 不可达 13 条的完整明细

| # | 判定 | 能力 | 记号 | 在仓库内他处找到 |
|---|---|---|---|---|
| 1 | elsewhere | `part_and_features` | `JUDGE-A_B.md` | `specs/202-user-coverage-gaps/recon/verify50/JUDGE-A_B.md` |
| 2 | elsewhere | `sheet_metal` | `JUDGE-C_D_E.md` | `specs/202-user-coverage-gaps/recon/verify50/JUDGE-C_D_E.md` |
| 3 | elsewhere | `simulation_and_fea` | `tests/test_fea_analysis.py` | `archive/inherited-methods/tests/test_fea_analysis.py` |
| 4 | **missing** | `simulation_and_fea` | `output/simulation-evidence.json` | 无 |
| 5 | **missing** | `topology_optimization` | `output/topology-evidence.json` | 无 |
| 6 | elsewhere | `chamfer_fillet_on_selection` | `tests/test_sw_chamfer_geometry.py` | `archive/inherited-methods/tests/test_sw_chamfer_geometry.py` |
| 7 | **missing** | `mesh_size_sanity_gate` | `output/simulation-evidence.json` | 无 |
| 8 | elsewhere | `selection_helpers` | `probe_selection_spec_e2e.py` | `archive/root-scratch/py/probe_selection_spec_e2e.py` |
| 9 | elsewhere | `selection_helpers` | `sw_selection_spec.py` | `scripts/sw_selection_spec.py` |
| 10 | elsewhere | `costing_templates_and_defaults` | `iface_sldcostingapi.txt` | `_raw/reflect/iface_sldcostingapi.txt` |
| 11 | **missing** | `pattern_and_mirror` | `InsertMirrorFeature2.md` | 无（`C:\swapi\types\IFeatureManager\InsertMirrorFeature2.md` **存在**，但 evidence 只写了裸文件名，无法判定指向）|
| 12 | elsewhere | `drawing_view_operations` | `capture_drawing_query_evidence.py` | `tools/capture_drawing_query_evidence.py` |
| 13 | elsewhere | `drawing_bom_balloons` | `spec.md` | `specs/001-topology-result-readout/spec.md` |

- **记录员注（陈述）**：9 条 `elsewhere` 的共同形态是 **evidence 只写了文件名或旧路径**，文件本身在仓库里（`archive/` `specs/` `_raw/` `scripts/` `tools/`）；3 条 `missing` 指向 `output/`（构建产物目录，A-03 记该目录部分内容入库、`inventory-a.json` 可复核）
- **未确认**：`InsertMirrorFeature2.md` 的裸文件名是否本意指向 `C:\swapi\...`——本文件不推断

### L-05 evidence 里有 **11 条指向仓库外官方源 `C:\swapi\`**

- **读数**：`\swapi\types\...` / `\swapi\enums\...` 形式的引用 **11** 条；`C:\swapi` 目录存在（`Test-Path` = True），抽查 4 条全部存在
- **★ 本探测的口径修正（记录）**：第一版把这类引用按「仓库相对路径」判，误报成「全仓找不到 11 条」；
  修正为「先把 `swapi` 前缀解析到 `C:\swapi`」后，这 11 条**全部可达**
- **未确认**：`C:\swapi` 是**本机**离线源，换机器不成立——它在仓库之外

### L-06 每条 `verified` 能力都至少有一个「路径类」证据

- **读数**：没有任何路径类证据的能力 **0** 条；证据全为自由文本的能力 **0** 条
- **记录员注（陈述）**：这是「字段形态」层面的读数，**不表示**每个路径都指向正确的文件（不可达 13 条见 L-03）

---

## 证据索引（每个事实号 → `inventory-l.json` 的键）

| 事实 | 证据载体 |
|---|---|
| L-01 | `verified_capabilities` / `evidence_items` + `inventory-c.json` 的 `verified_evidence` |
| L-02 | `item_kinds` |
| L-03 | `path_tokens_checked` / `path_tokens_unreachable` / `classification` |
| L-04 | `missing_all`（13 条全量） |
| L-05 | `missing_all` 中 `verdict=external` 的条目 + `C:\swapi` 的存在性（本机 `Test-Path`） |
| L-06 | `caps_without_path_evidence` / `caps_evidence_all_free_text`（均为空） |

---

## 本节未覆盖（留给后续补充）

- **执行** evidence 里的 20 条命令（本次刻意不执行，避免触发 COM/SolidWorks）
- 78 条自由文本证据的语义核验
- 每条 `verified` 的**运行证据是否真的支撑该能力**（本次只核「指向物是否存在」）
- `output/` 那 3 个缺失产物是否曾在某次运行中产生（未查 `git log`）
