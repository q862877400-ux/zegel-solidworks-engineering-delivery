# C 维度 · 能力台账（`capabilities.yaml`）现状

> 观测时间 **2026-10-24** · 观测方式：YAML 解析 + 与工具声明交叉引用（只读）
> 复现总命令：
> ```powershell
> python docs\state\probes\probe_capabilities.py --json docs/state/inventory-c.json
> ```

---

### C-01 140 条能力，`schema_version` 2.0，顶层 6 个键

- **读数**：`capabilities` **140** 条 · `schema_version` **2.0** · `backend_schema_version` 存在
- **顶层键（逐字）**：`backend_catalog` · `backend_schema_version` · `capabilities` · `operation_routes` · `schema_version` · `verified_versions`
- **未确认**：无

### C-02 `level` 分布：`verified` 100 · `stitched` 37 · `not_implemented` 3

- **读数**：100 / 37 / 3（合计 140）
- **`not_implemented` 的 3 条（逐字）**：`drawing_dimension_insertion` · `autocad_basic_drafting` · `pdm`
- **证据**：`capabilities.yaml`；`docs/state/inventory-c.json` 的 `level_histogram`
- **未确认**：无

### C-03 字段齐全度：7 个字段 140/140，另有 4 个字段缺项

| 字段 | 有值的条数 |
|---|---|
| `id` `label` `level` `backends` `limitations` `source` `source_evidence` | **140/140** |
| `evidence` | **137/140** |
| `verified_versions` | 132/140 |
| `dependencies` | 126/140 |
| `allowed_modes` | 109/140 |
| `mcp_tools` | **105/140**（35 条无该字段）|
| `provenance` | **1/140** |

- **无 `evidence` 的 3 条（逐字）**：`autocad_basic_drafting` · `surface_modeling` · `mold_tools`
- **带 `provenance` 的 1 条**：`mold_tools`
- **证据**：`inventory-c.json` 的 `field_presence`
- **未确认**：`mcp_tools` 那 35 条无值，是「确实没有工具」还是「字段未填」——本探测只统计字段有无，未与该能力是否可在工具层调用做交叉

### C-04 `verified` 的 100 条全部有 `evidence`，形态统一为「列表」

- **读数**：100 条 `evidence` 均为 **list**，元素数分布：1 项(8) · 2 项(32) · 3 项(28) · 4 项(18) · 5 项(5) · 6 项(3) · 7 项(3) · 9 项(2) · **23 项(1)**
- **读数**：`verified` 中 `evidence` 缺失 **0** 条
- **未确认**：列表元素的内容形态（是路径？命令？自由文本？）未逐条分类；`evidence` 是否**可复跑**本次未验证

### C-05 `limitations` 覆盖 140/140

- **读数**：**140/140** 条能力都有非空 `limitations`
- **交叉核对**：`AGENTS.md` §十三 把能力的 `limitations` 称作「第一现场」
- **未确认**：无

### C-06 出现 4 种非模板键（1~4 条各一）

| 键 | 条数 |
|---|---|
| `title` | 4 |
| `skills` | 1 |
| `★★_2026-10-04_降级说明` | 1 |
| `★_allowed_modes_说明` | 1 |

- **观测方式**：统计所有条目出现过的键名（值非空的才算）
- **未确认**：这些键是否被任何读取方（门禁/工具/文档生成器）使用——本次未查引用

### C-07 能力名与「工具名」按名称匹配命中 0/140；与「模块名」命中 140/140

- **观测方式**：把能力 `name` 规范成 slug（小写、非字母数字转 `_`），
  ① 是否作为子串出现在任一工具名里（`rc.all_specs()` 的 501 个 name）；
  ② 是否作为子串出现在任一 `ToolSpec.module` 里
- **读数**：工具名命中 **0/140** · 模块名命中 **140/140**
- **记录员注（陈述）**：工具名统一是 `solidworks_<域>_<动作>`（见 B-02），能力名是模块式短语（如 `surface_modeling`），
  两者命名体系不同 ⇒ 该 0 命中既是名称体系差异的直接结果，也可能受本探测的「子串匹配」口径影响
- **未确认**：是否存在其它字段（如 `mcp_tools`）建立了能力→工具的显式映射——未逐条比对 `mcp_tools` 的值

---

## 本节未覆盖（留给后续补充）

- 100 条 `verified` 的 `evidence` **逐条真实性**（本次只统计了字段形态与条数）
- `backend_catalog` / `operation_routes` / `verified_versions` 三个顶层块的结构与用途
- 37 条 `stitched` 各自缺什么证据
- `mcp_tools` 字段的值形态（是工具名列表还是计数）
