# A 维度 · 顶层结构与产物落位现状

> 观测时间 **2026-10-24** · 观测方式：文件系统扫描 + `git ls-files` / `git check-ignore`（只读）
> 复现总命令：
> ```powershell
> python docs\state\probes\probe_structure.py --json docs/state/inventory-a.json
> ```

---

### A-01 顶层：42 个目录 + 29 个文件

- **读数**：目录 **42** 个（不含 `.git`）· 文件 **29** 个
- **交叉核对**：`AGENTS.md` 铁律 3 记「交付/缓存目录…归档后根只剩 **29** 个文件」⇒ **文件数一致**；同节记「磁盘顶层 = **39** 个仓库目录 + 3 个工具缓存」⇒ **39+3 = 42 也等于实测总数**
- **但三种口径的拆分互不自洽（陈述，不判断）**：
  - 白名单 14 个（`.github agents ai_team apps assets docs dotnet examples mcp-server references scripts subskills tests tools`）——实测**全部存在**
  - AGENTS 的「多出的 25 个」登记表——实测**全部存在**（含 `.pytest_cache`，而它在同一段文字里又被算作「工具缓存」）
  - 既不在白名单、也不在那 25 条登记里的：**`archive`**（另在「归档目录」小节单独说明）· **`.codebase-memory`** · **`.ruff_cache`**
- **未确认**：AGENTS 的「39」当初按哪种拆分算出——未查该数字的历史来源

### A-02 git 视角：跟踪 8,293 个文件，ignored 条目 2,696

- **读数**：`git ls-files` ⇒ **8,293**；`git status --ignored --porcelain` 中 `!!` 开头 ⇒ **2,696**
- **证据**：`docs/state/inventory-a.json` 的 `tracked_files` / `ignored_entries`
- **未确认**：无

### A-03 目录规模 top12（文件数）

| 目录 | 文件数 | 体积 | `git check-ignore <目录>` | `git ls-files <目录>` |
|---|---|---|---|---|
| `AI Solidworks` | 29,749 | 314.7 MB | **True** | **0** |
| `output` | 9,604 | 510.9 MB | False | **456** |
| `archive` | 2,841 | 76.8 MB | False | **2,835** |
| `specs` | 2,369 | 52.3 MB | False | 2,369 |
| `tools` | 1,281 | 11.5 MB | False | 637 |
| `tests` | 980 | 14.7 MB | False | 497 |
| `apps` | 652 | 30.3 MB | False | 102 |
| `scripts` | 526 | 25.8 MB | False | 266 |
| `docs` | 286 | 9.1 MB | False | 284 |
| `shots` | 273 | 49.9 MB | **True** | 0 |
| `mcp-server` | 245 | 2.3 MB | False | 125 |
| `solidpilot-salvage` | 241 | 11.0 MB | False | 241 |

- **观测方式**：两列分开测 ——「目录是否被 ignore 规则命中」与「目录里有多少文件已入库」**不是同一件事**
- **记录员注（陈述）**：`output` 目录本身未被 `check-ignore` 命中，且其中 **456 个文件已入库**（含 5 个 `.py`、326 个 `.log/.err/.json/.md/.xlsx`）；`AI Solidworks` 与 `shots` 目录命中 ignore 且入库 **0**
- **未确认**：`output` 里那 456 个入库文件是何时、按什么规则进来的——未查 `git log --diff-filter=A -- output`

### A-04 `archive/` 2,841 个文件里 2,835 个已入库

- **读数**：`git ls-files archive` = **2,835** / 磁盘 **2,841**
- **交叉核对**：`AGENTS.md` 铁律 3 记「`archive/root-scratch/{py,txt,md,json,logs,other}` 装的是仓库根曾经就地写的 2814 个草稿」「归档后根只剩 29 个文件」；实测根文件 **29** ✓
- **未确认**：2814 与实测 2841/2835 的差额构成（是否含子目录占位、是否后续又归入过文件）——未逐个比对

### A-05 忽略清单里的两种形态

- **读数**：`git check-ignore -q <dir>` 为 True 的顶层目录：**`AI Solidworks`** 与 **`shots`**（两者 `git ls-files` 均为 0）
- **读数**：其余 40 个顶层目录 `check-ignore` 为 False
- **未确认**：`.gitignore` 里各条规则的原始写法与生效顺序——未逐行读 `.gitignore`

### A-06 顶层 29 个文件的清单

- **读数（逐字）**：`AGENTS.md` `CONTRIBUTING.md` `INPUT-ANOMALY-INVESTIGATION.md` `README-workspace.md` `README.md` `REPORTING-STYLE-PROPOSAL.md` `RESTART-HANDOFF.md` `SECURITY.md` `SKILL.md` `SUBSKILLS.md` `THIRD-PARTY-NOTICES.md` `toolbox-research.md` + 其余 17 个（完整清单见 `inventory-a.json` 的 `top_files`）
- **未确认**：无

### A-07 三个工具缓存的落位

- **读数**：`.pytest_cache`（在 AGENTS「多出的 25 个」表内）· `.codebase-memory` · `.ruff_cache`（后两者**不在任何名单**）——三者均在磁盘存在
- **交叉核对**：`AGENTS.md` 同段文字把这三者并称「3 个工具缓存」
- **未确认**：后两者的 ignore 状态——本探测只对顶层目录做了 `check-ignore`，未单独测这两个

---

## 本节未覆盖（留给后续补充）

- 每个顶层目录的「目录用途」与 AGENTS 登记的用途是否一一对应（只比了存在性）
- `output` / `archive` / `_raw` / `_proof` 等产物的**归属规则**（哪些该入库、哪些该忽略）——属判断，留给读者
- 磁盘总体积与仓库体积的差额构成
