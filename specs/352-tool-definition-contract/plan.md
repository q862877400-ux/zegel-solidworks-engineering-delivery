# 规格 352 · 计划（顺序 / 依赖 / 写盘边界）

> 读 `spec.md` 的判据 K1–K9 与 A1–A8。本文件只定**做什么、按什么顺序、谁写哪些文件**。

---

## 一 · 五步走（★ 每步都有独立可验的产物）

| 步 | 内容 | 产物 | 依赖 |
|---|---|---|---|
| **P0** | **契约 + 门禁 + 基线**（不改任何一条工具描述） | `scripts/check_tool_contract.py` · `docs/tool-contract-baseline.json` · 接线 3 处 · 双侧负例测试 | — |
| **P1** | **证据字段 + 迁移器**（只加 `ToolSpec.evidence`，仍不改描述） | `mcp-server/tool_registry.py`（+字段）· `tools/migrate_tool_evidence.py`（`--dry-run/--apply/--verify`） | P0 |
| **P2** | **评测基线**（当前 498 条的真实读数） | `tools/eval_tool_selection.py` · `output/tool-selection-baseline.json` | P1（要读 `tools/list`） |
| **P3** | **试点 24 条**（中 × 英 × 现况，真实模型） | `output/pilot-352.json` + `specs/352-.../pilot.md` | P2 |
| **P4** | **全量改写 498 条**（并行，按批次文件切分） | `mcp-server/tool_specs_batch*.py` | P3 |
| **P5** | **收尾**：全量评测 + 门禁 + 文档 + 提交 | 各项读数落盘 | P4 |

★ **P0–P3 之间不许跳**：没有基线就没法说「变好了」；没有试点就可能把 498 条改成错的语言。

---

## 二 · 写盘边界（★ 并行时的唯一防冲突手段）

| 谁 | 只写这些路径 | 依据 |
|---|---|---|
| **Lead** | `scripts/check_tool_contract.py` · `mcp-server/tool_registry.py` · `tools/migrate_tool_evidence.py` · `tools/eval_tool_selection.py` · `docs/tool-contract-baseline.json` · `docs/gate-classification.json` · `scripts/release_check.py` · `specs/352-*/**` · `tests/test_tool_contract_gate.py` | 门禁与评测是**单一真源**，不许并行 |
| **执行者 A…H** | 各自分到的 `mcp-server/tool_specs_batchNNN.py`（**不相交**） | 117 个批次文件天然可切 |

★ 执行者**不许**碰：`tool_registry.py`、任何 `scripts/` 门禁、`docs/*.json`、其他批次文件。
★ 执行者**不许**自行 `git commit`（Lead 按批次/按组提交，避免 index 竞争）。

---

## 三 · 单条工具的改写流程（★ 执行者照此做，逐条）

1. **读三处**（缺一不可）：
   - 旧 `doc`（＝即将搬进 `evidence` 的那段）——**里面通常已经写着官方签名、真机读数、废弃链**
   - 被声明的目标函数（`scripts/<module>.py::<function>`）的 **signature + docstring + 来源块**
   - 官方页（若旧 `doc` 里的引用可以在 `C:\swapi\types\<接口>\<成员>.md` 找到，直接读它的 `## Remarks`）
2. **写 `doc`**：≤600 字符，英文，句式
   ```
   <动词> <对象> <关键限定>.              ← 首句 ≤120，含必填取值域 / 何时用 / 副作用
   <决策信息>.                            ← 1–2 句：前置、副作用、返回什么、何时别用
   ```
3. **写每个 `Param.description`**：`<它是什么>[; <范围/取值>][; defaults to <默认值>].`（句号必须）
4. **搬证据**：`evidence=<旧 doc 逐字>`（迁移器可代做，见 P1）
5. **自查**：`python scripts/check_tool_contract.py --only <工具名>` ⇒ 零违反

---

## 四 · 判据口径的一个坑（★ 已核实，写下来免得重踩）

`firstLine()` 的断句符是 **`。`（中文句号）与换行**，**ASCII `.` 不算**。
⇒ ★ 对**英文** doc，真正的失败条件是「首句超过 120 字符」；
★ 对**中文** doc 才是「关键结论不在第一个 `。` 之前」。
★ 本规格要求**英文**，所以 K1 的「无 `。`」是为了**中文残留**兜底，不是英文的断句需求。

---

## 五 · 命令（每条都能一字不差地重跑）

```powershell
# P0 基线（当前 498 条的读数）
python -B output\_audit_tool_docs.py
python -B scripts\check_tool_contract.py --report

# P1 迁移（先演算，再落盘，再回读证明零丢失）
python -B tools\migrate_tool_evidence.py --dry-run
python -B tools\migrate_tool_evidence.py --apply
python -B tools\migrate_tool_evidence.py --verify

# P2/P5 评测
python -B tools\eval_tool_selection.py --run --tag baseline
python -B tools\eval_tool_selection.py --run --tag after

# 体量
python -B tools\measure_lean_catalog.py

# 收尾
pwsh -File tools\round_chain.ps1 -Tests tests\test_tool_contract_gate.py
```

---

## 六 · 风险与对策

| 风险 | 对策 |
|---|---|
| 改写**编造**了官方没说的语义 | 铁律 1/5：每句要能指回三源之一；`evidence` 保留原文；抽检 ≥30 条与官方页逐字对照 |
| 498 条并行改写**风格漂移** | 先 P3 试点定「样板 24 条」，全量时把样板作为 in-context 范例发给每个执行者 |
| `doc` 变短后**丢掉决策信息**（如"本机不可用"） | K8 保证旧门禁仍绿（`仍不可用` 必须在首句）；另设抽检 |
| 改写**打断**其它门禁（`check_param_binding` / `check_preselect_family` 读 `doc`） | P0 先跑一遍全量 `release_check` 记下"改动前的绿"，每批改完再跑 |
| 评测**量不准**（模型受 DSH 自身工具污染） | 评测 prompt 明写「只能选清单内名字」；配 5 道**弃权题**做负例；记录原始输出 |
