# G 维度 · 文档层（markdown）现状

> 观测时间 **2026-10-24** · 观测方式：文件系统 + 内容哈希 + markdown 链接抽取 + `git log -1`（只读）
> 复现总命令：
> ```powershell
> python docs\state\probes\probe_docs.py --json docs/state/inventory-g.json
> python docs\state\probes\probe_doc_map.py      # 生成 docs/state/doc-map.md
> ```

---

### G-01 扫描到 **1,864** 份 md（已排除 `AI Solidworks`/`archive`/`output`/`node_modules`）

- **读数**：**1,864** 份 · 总体积 **19.2 MB** · 单文件 **255 B ~ 1,744,604 B**
- **最大 4 份（逐字）**：`docs/known-facts.md` 1,744,604 B · `output/audit-batch7/G04-roadmap-cursor.md` 1,371,419 B（在 output 内，本次排除）· `docs/ROADMAP.md` 1,254,575 B · `docs/recon/member-to-example-index.md` 668,274 B
- **交叉核对**：本轮早前的口径是「`.md` 1,849 个」（含 archive 等）⇒ **两个数字口径不同**（排除规则不同），不是同一测量
- **未确认**：无

### G-02 目录分布：`specs/` 占 1,452 份（78%）

| 目录 | 份数 |
|---|---|
| `specs` | **1,452** |
| `docs` | 219 |
| `apps` | 54 |
| `commit-messages` | 28 |
| `solidpilot-salvage` | 23 |
| `references` | 22 |
| `subskills` | 22 |
| `.specify` | 16 |
| 仓库根 | 12 |
| `.workbuddy-ai` | 8 |
| 其余（`_raw`/`.pytest_cache`/`examples`/`mcp-server`/`_proof`）| 各 1~3 |

- **证据**：`docs/state/inventory-g.json` 的 `per_dir`
- **未确认**：无

### G-03 逐字重复 **49 组**；`docs/`+根子集里 3 份有双胞胎

- **读数（全 md 语境）**：规范化后内容哈希相同的组 **49** 组
- **读数（`docs/`+仓库根 232 份子集）**：**3** 份存在逐字双胞胎，**3/3 都指向 `apps/workbench-ui/src-tauri/resources/skill/`**
- **样本（逐字）**：`README.md` ↔ `apps/workbench-ui/src-tauri/resources/skill/README.md`；`SKILL.md` ↔ 同目录 `SKILL.md`；`SUBSKILLS.md` ↔ 同目录 `SUBSKILLS.md`
- **交叉核对**：`AGENTS.md` 事实 55 记「改了运行时文件必须重跑 `sync_bundled_skill.py`——它比『仓库根的 Skill』与『桌面内嵌快照』」
- **未确认**：其余 46 组（非 `docs/`+根子集）的构成——本次只留了 6 组样本

### G-04 内部 `.md` 链接 453 条，断链 **110** 条

- **读数**：链接 **453** · 目标文件不存在 **110**（占 24.3%）
- **读数**：核心文档（`AGENTS.md` / `docs/ROADMAP.md` / `RESTART-HANDOFF.md`）的 `.md` 链接断链 **0**
- **断链样本（逐字）**：`docs/known-facts.md` → `simulation-performance-memory-gpu.md`（×2）· → `deployment-boundary.md`（×2）· `specs/201-toolbar-gaps/tasks.md` → `../docs/toolbar-gaps-backend-limits.md` · `specs/204-bunny-moat-batches/goal-bar.md` → `../docs/recon/multiway-agreement.md`
- **未确认**：110 条里有多少是「目标文档曾经存在、后被移动/删除」——未查 `git log --diff-filter=D`

### G-05 文档地图已生成：232 份（`docs/` 220 + 根 12）

- **产物**：`docs/state/doc-map.md`（人读表）+ `docs/state/inventory-g-map.json`（机读）
- **四个信号**：最后提交日期 · 被引用次数 · 是否逐字重复 · 体积
- **★ 引用计数的口径限制（已写进产物抬头）**：按**相对路径**在全体 md 文本里计数，因此**仓库根文件**（rel 路径就是文件名，如 `README.md`）会把别处同名文件的提及一起算进去 ⇒ **只有 `docs/` 下文件的该计数是精确的**
- **未确认**：无

### G-06 引用次数 top5（含上述口径限制）

| 文档 | 引用次数 |
|---|---|
| `README.md`（根）| 1,420 |
| `AGENTS.md` | 1,142 |
| `SKILL.md` | 306 |
| `docs/known-facts.md` | 232 |
| `docs/ROADMAP.md` | 182 |

- **记录员注（陈述）**：前三个都是仓库根文件，受 G-05 所述口径影响；后两个是 `docs/` 下文件，计数精确

---

## 本节未覆盖（留给后续补充）

- 46 组非 `docs/` 子集的重复组构成
- 110 条断链的成因分类（移动 / 删除 / 从未存在）
- 文档内容与实现的**一致性**（本次只做结构信号，未比对内容）
- `.md` 之外的知识载体（`.yaml`/`.json` 规则库、`references/` 下非 md 文件）
