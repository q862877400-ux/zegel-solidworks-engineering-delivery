# 项目现状记录（State Dossier）· 计划与入口

> **这份文件的定位**：让任何一个 Agent **不读整个项目**（55 万行 Python / 1,849 个 md）就能定位到任意一块的**现状**，
> 并拿到可复核的证据与复现命令。
>
> **记录员的边界（写死在本文件里，防止越界）**：
> - 只写**观察到的事实**与**可复核的读数**；
> - **不判断**对错、好坏、该不该改；**不给**修复建议、优先级、严重度；
> - 遇到「A 与 B 不一致」只陈述两边的原文与位置，**由读的人裁决**；
> - 查不到就写「查不到 + 已经查过什么」，不推测、不补全。

---

## 一、这份记录要解决的问题

| 现状 | 后果 |
|---|---|
| `.py` 2,063 个 / 553,615 行；`.md` 1,849 个；`specs` 281 份；`scripts/check_*.py` 56 道门 | 任何 Agent 想弄清一块都得先通读，成本极高 |
| 同一件事在多个地方各有一份说法（AGENTS / ROADMAP / known-facts / union-conventions / capabilities.yaml / digest） | 读的人不知道该信哪份，也不知道哪份与代码同步 |
| 部分「声明」与「实现」不在一处（工具声明 vs 函数签名 vs 能力台账 vs 测试） | 只看一侧会得出相反结论 |

⇒ 本记录用**按维度的事实清单**替代「通读」，每条事实自带证据与复现命令。

---

## 二、记录格式（固定字段，缺一不可）

```markdown
### <维度>-<序号> <一句话事实（描述性，不评判）>

- **观测方式**：<命令 / 探测器 / 抽样方式与样本量>
- **读数**：<数字 / 枚举 / 分布>
- **证据**：<`path:line` 或命令输出摘要>
- **复现**：<可直接粘贴运行的一条命令>
- **未确认**：<没查到的部分 + 已尝试过的查法；没有就写「无」>
```

★ 三条写法纪律：
1. **描述句不带判断词**：写「`A` 与 `B` 的值不同」，不写「`A` 是错的」；
2. **数字必须能重算**：给出命令，而不是「大约」「多数」；
3. **抽样必须标样本量**：写「抽 10/140」，不写「抽样显示普遍」。

---

## 三、十个维度（每个维度一份事实文件）

| 维度 | 记录文件 | 覆盖什么 | 主要观测手段 |
|---|---|---|---|
| **A 结构** | `facts/A-structure.md` | 顶层目录、白名单、产物落位、gitignore、目录体积 | `Get-ChildItem` / `git check-ignore` |
| **B 工具声明** | `facts/B-tools.md` | 501 条 `ToolSpec`：命名、单位后缀、`inject` 取值、doc、`read_only`、`writes`、重名、一实现多名 | 探测器读 `rc.all_specs()` |
| **C 能力台账** | `facts/C-capabilities.md` | `capabilities.yaml` 140 条：`level` 分布、每条的工具/脚本/测试落点、`evidence` 字段形态 | YAML 解析 + 交叉引用 |
| **D 脚本层** | `facts/D-scripts.md` | `scripts/` 211 个模块：可导入性、未定义名、未调用函数、ruff/克隆读数 | `compileall` / `check_undefined_names` / `check_repo_uniformity` |
| **E 门禁层** | `facts/E-gates.md` | 56 道 `check_*.py` + `release_check` 57 道：各自查什么、是否在 `release_check` 内、豁免清单、负例自证 | 读门禁源码 + `check_gate_wiring` 输出 |
| **F 测试层** | `facts/F-tests.md` | 496 个测试：能否收集、失败/跳过分类、钉死数字、断言形态 | `pytest --collect-only` / 逐文件抽样 |
| **G 文档层** | `facts/G-docs.md` | 1,849 个 md：哪些是权威、哪些过期、互相引用是否可达、与实现是否一致 | 引用抽取 + 抽样比对 |
| **H 规格层** | `facts/H-specs.md` | 281 份 spec：状态字段、`→ 验收:` 行、孤立/重复 | 目录扫描 + 行抽取 |
| **I 许可来源** | `facts/I-license.md` | 来源清单 vs 入库代码 vs NOTICE 义务 | `union-sources.json` + LICENSE 扫描 |
| **J 运行装配** | `facts/J-runtime.md` | `server.py` 装配链、`sw_connect`、`mcp.json`、单实例、护栏 | 读装配入口 + 配置 |

---

## 四、自动化（探测器）

**放哪**：`docs/state/probes/`（**刻意不进 `tools/`／`scripts/`**）。
理由：它们是**一次性观测器**，不是产品工具；放进 `tools/` 会触发 `check_tools_index_fresh`（索引必须登记每个工具）
与 `§十八 来源块` 义务，把「记录现状」变成「改产品」，与本角色不符。

| 探测器 | 产出 |
|---|---|
| `probe_all_specs.py` | `facts/` 里 B 维度的全部读数（JSON + 摘要） |
| `probe_capabilities.py` | C 维度：level 分布 + 每条落点 |
| `probe_gates.py` | E 维度：门禁 → 是否接入 / 是否豁免 |
| `probe_tests.py` | F 维度：收集期状态 + 失败/跳过清单 |
| `run_all.py` | 顺序跑全部探测器，把结果写成 `docs/state/inventory.json` |

★ 探测器自身纪律：**只读**，不装包、不连 SolidWorks、不改仓库任何文件（除写 `docs/state/` 下的输出）。

---

## 五、执行顺序与进度（每轮一个维度，做完即提交）

| 轮 | 维度 | 状态 |
|---|---|---|
| S1 | 计划 + **B 工具声明** | ✅ 已提交（`53990b15`）|
| S2 | **A 结构** + **E 门禁** | ✅ 已提交（事实见 `facts/A-structure.md`、`facts/E-gates.md`）|
| S3 | **C 能力台账** + **J 运行装配** | ✅ 已提交（事实见 `facts/C-capabilities.md`、`facts/J-runtime.md`）|
| S4 | **D 脚本层** + **F 测试层** | ✅ 已提交（事实见 `facts/D-scripts.md`、`facts/F-tests.md`）|
| S5 | **G 文档层** + **H 规格层** + **文档地图** | ✅ 已提交（`facts/G-docs.md`、`facts/H-specs.md`、`doc-map.md`）|
| S6 | **I 许可来源** + **跨维度索引** | ✅ 已提交（`facts/I-license.md`、`INDEX.md`）|

**收工状态（第一轮）**：A–J **十个维度全部落盘**；跨维度索引见 [`INDEX.md`](INDEX.md)；文档地图见 [`doc-map.md`](doc-map.md)。
探测器 **11 个**（`probes/`），全部只读、可重跑；机器可读读数 `inventory-a..j.json` + `inventory-g-map.json`。

---

## 六之补、第二轮：深度对应关系（规格 347）

第一轮记的是**结构信号**（多少条、多大、断没断）；第二轮只记**可证伪的对应关系**。
规格：`specs/347-state-dossier-round2/spec.md`

| 轮 | 维度 | 状态 |
|---|---|---|
| S7 | **K 声明 ↔ 实现签名** | ✅ 已提交（`facts/K-signature.md`）|
| S8 | **L 能力 evidence 核验** | ✅ 已提交（`facts/L-evidence.md`）|
| S9 | M 测试执行期结果 | ⬜ 下一轮 |
| S10 | N 仓库外来源 + 未触碰目录 | ⬜ |
| S11 | O 文档归并 | ⬜ |

**每轮收工**：① 事实写入对应 `facts/*.md`；② 更新本文件进度表；③ `python tools/commit_mine.py` 提交；
④ 跑 `release_check` 确认没有把仓库弄红。

---

## 六、旧文档怎么处置（记录员口径）

**只做「文档地图」，不擅自删**。理由：删文档是判断，超出本角色边界。

- 在 `facts/G-docs.md` 里给每个文档标一行：**权威 / 部分过期 / 已被 X 取代 / 纯历史**；
- 若两份文档**逐字重复同一段事实**，记「重复」并指向唯一保留处（**只记，不删**）；
- 后续 agent 拿到这张地图后自行决定删/并——那时它是「判断者」，不是记录员。

---

## 七、已知的入口（给后续 agent 的跳板）

| 想知道 | 去哪 |
|---|---|
| 工具层现在是什么状态 | `docs/state/facts/B-tools.md` |
| 能力台账的原始文件 | `capabilities.yaml`（140 条，`level` 五级）|
| 门禁体系入口 | `scripts/release_check.py`（57 道）· `docs/gate-classification.json`（每道门的分类与理由）|
| 长程计划与游标 | `docs/ROADMAP.md` §一（2026-10-22 第 32 轮收口为最后一条）|
| 项目规矩 | `AGENTS.md`（六条铁律 + A1–A10 + 已知事实速查 21 条）|
| 已知死路 | `docs/dead-ends.md`（由 `tools/gen_dead_ends.py` 生成）|
