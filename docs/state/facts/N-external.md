# N 维度 · 仓库外来源与尚未触碰的目录

> 观测时间 **2026-10-24** · 观测方式：目录扫描 + 读 LICENSE 原文首行 + `git -C <dir> log -1`（只读）
> 复现总命令：
> ```powershell
> python docs\state\probes\probe_external.py --json docs/state/inventory-n.json
> ```

---

## 第一部分：仓库外来源 `C:\swprojects\`

### N-01 26 个目录：25 个是 git 检出，23 个有 LICENSE 文件

- **读数**：目录 **26** · 含 `.git` **25** · 有 LICENSE **23** · **无 LICENSE 3**
- **无 LICENSE 的 3 个（逐字）**：`_tmp_mcp`（且非 git 检出）· `offline-solidworks-api-docs` · `solidworks-build-mechanical-models`
- **未确认**：这 3 个的可用范围——本次只记「没有 LICENSE 文件」这一事实

### N-02 许可分布：MIT 18 · AGPL-3.0 2 · GPL-2.0 1 · Apache 1 · 无许可 3 · 自定义 1

| 许可首行（逐字摘录）| 个数 |
|---|---|
| `MIT License` | **18** |
| `<无 LICENSE>` | 3 |
| `GNU AFFERO GENERAL PUBLIC LICENSE Versio…` | **2** |
| `GNU GENERAL PUBLIC LICENSE Version 2, Ju…` | 1 |
| `Apache License` | 1 |
| `Copyright (c) 2026 walterkken` | 1 |

- **证据**：`inventory-n.json` 的 `swprojects.license_heads`
- **未确认**：那 1 个「自定义首行」(`ddeng-skills`) 的完整授权条款——本次只读了首两行

### N-03 非 MIT 克隆的逐个落位

| 目录 | 许可（首行摘录）| 最近提交 |
|---|---|---|
| `_tmp_mcp` | `<无 LICENSE>` | `<非 git 检出>` |
| `ddeng-skills` | `Copyright (c) 2026 walterkken` | 2026-09-11 |
| `mcp-server-solidworks` | `GNU AFFERO GENERAL PUBLIC LICENSE Version 3` | 2026-09-28 |
| `offline-solidworks-api-docs` | `<无 LICENSE>` | 2026-08-03 |
| `pySW` | `GNU GENERAL PUBLIC LICENSE Version 2, June 1991` | 2023-04-24 |
| `q3ds-solidworks-mcp` | `GNU AFFERO GENERAL PUBLIC LICENSE Version 3` | 2026-08-24 |
| `Slacker-LLC` | `Apache License` | 2026-08-16 |
| `solidworks-build-mechanical-models` | `<无 LICENSE>` | 2026-07-13 |

- **交叉核对（陈述）**：`AGENTS.md` §四 记的四家来源里，`Slacker-LLC` 是 Apache-2.0（与这里一致）；
  另两家 AGPL（`mcp-server-solidworks` / `q3ds-solidworks-mcp`）与一家 GPL-2.0（`pySW`）在 `AGENTS.md` 的许可判定表里**未见逐条登记**——
  本文件只指出「这两处清单的说法不一致」，不判断哪个对
- **未确认**：这 8 个非 MIT 目录各自被本仓引用的程度——未查 `tools/union-sources.json` 是否收录它们

---

## 第二部分：仓库内尚未触碰的 5 个目录

### N-04 五个目录的文件构成

| 目录 | 文件数 | 主要扩展名 |
|---|---|---|
| `apps/` | **652** | `.py` 447 · `.md` 54 · `.json` 33 |
| `dotnet/` | **7** | `.cs` 5 · `.base64` 1 · `.csproj` 1 |
| `ai_team/` | **8** | `.cjs` 6 · `.json` 1 · `.ps1` 1 |
| `subskills/` | **80** | `.py` 23 · `.md` 22 · **`.pyc` 12** · `.yaml` 8 · `.json` 7 |
| `references/` | **22** | `.md` 22（全 markdown）|

- **证据**：`inventory-n.json` 的 `untouched_dirs`
- **记录员注（陈述）**：`subskills/` 里有 **12 个 `.pyc`**（编译产物）在版本库目录内
- **未确认**：这些 `.pyc` 是否被打进 git——本次未 `git ls-files` 核对（A 维度只测了顶层目录）

### N-05 这五个目录在本记录里的覆盖情况

| 目录 | 第一轮是否覆盖 | 本文件新增 |
|---|---|---|
| `apps/` | 仅出现在 A-03 的目录体积表 | 文件数 + 扩展名构成 |
| `dotnet/` `ai_team/` `subskills/` `references/` | **完全未覆盖** | 文件数 + 扩展名构成 |
| 内容层面（这些目录里到底有什么实现）| **五个目录全部未覆盖** | 仍未覆盖（见下）|

- **未确认**：这五个目录的**内容**（`apps/` 的桌面端、`subskills/` 的 23 个 .py、`references/` 的 22 份知识文档）——本次只做规模与构成统计

---

## 证据索引

| 事实 | 证据载体 |
|---|---|
| N-01 | `swprojects.dirs` / `with_git` / `with_license` / `without_license` |
| N-02 | `swprojects.license_heads` |
| N-03 | `swprojects.rows[]`（逐目录 license 与 last_commit） |
| N-04 | `untouched_dirs`（五个目录的 files 与 ext_top） |
| N-05 | 本文件表格 + 第一轮 `facts/A-structure.md` A-03 |

---

## 本节未覆盖（留给后续补充）

- `C:\swprojects\` 各克隆与 `tools/union-sources.json` 的对应关系（哪些被正式列为来源）
- 五个仓库内目录的**内容**（实现、职责、与主链的关系）
- `subskills/` 里 `.pyc` 是否入库
- 仓库外克隆的代码是否被「逐行借鉴」进本仓（需 diff，不在本轮）
