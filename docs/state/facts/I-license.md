# I 维度 · 许可与来源现状

> 观测时间 **2026-10-24** · 观测方式：读 `tools/union-sources.json` / `THIRD-PARTY-NOTICES.md` / `LICENSE` + 代码头关键词扫描（只读）
> 复现总命令：
> ```powershell
> python docs\state\probes\probe_license.py --json docs/state/inventory-i.json
> ```

---

### I-01 `tools/union-sources.json` 登记 **4** 条来源：MIT ×3 + Apache-2.0 ×1

- **读数**：来源 **4** 条 · 许可分布 `MIT` **3** · `Apache-2.0` **1**
- **交叉核对**：`AGENTS.md` §四 记「四家与本项目重叠的外部 MCP 项目」及其许可（3 家 MIT + `Slacker-LLC` Apache-2.0）⇒ 数量与许可分布一致
- **未确认**：`declared_verified` 字段的取值分布——本探测有采集但未在摘要打印，值见 `inventory-i.json`

### I-02 `THIRD-PARTY-NOTICES.md` 169 行 / 8,981 B，含 JIALE 与 MIT/Apache 字样

- **读数**：**169 行** · **8,981 B** · 出现 `JIALE` ✓ · `MIT` 12 次 · `Apache` 5 次
- **交叉核对**：`AGENTS.md` §四 记该文件「153 行 / 6.5 KB，已入库」⇒ 行数与体积**均与现状不同**（现 169 行 / 8.8 KB）
- **未确认**：该文件是否覆盖了 `union-sources.json` 的全部 4 家——未逐家比对

### I-03 仓库自身 `LICENSE` = MIT

- **读数**：`LICENSE` 存在 · 首行逐字 `MIT License`
- **未确认**：无

### I-04 扫描 **1,530** 个代码文件；头部出现许可关键词的频次

| 关键词 | 出现在头部（前 40 行）的文件数 |
|---|---|
| `MIT` | **1,245** |
| `GPL` | 8 |
| `AGPL` | 6 |
| `Apache` | 5 |
| `Copyright` | 3 |

- **观测方式**：对 `scripts/` `tools/` `mcp-server/` `tests/` `subskills/` 下全部 `.py` 取前 40 行做不区分大小写的子串匹配（**同一文件可命中多个关键词**）
- **未确认**：`MIT` 的 1,245 次里有多少是「本仓自己的许可声明」、多少是「提到上游是 MIT」——未逐行分类

### I-05 头部含 GPL 族的文件 **6** 个，逐行看均为「只读思想」声明或门禁判据

| 文件 | 该行的性质（逐字摘录） |
|---|---|
| `scripts/check_license_redlines.py:4` | `> **A6** 许可无越界：AGPL / GPL / 无许可 / 全版权保留的代码**没被抄进来**；` |
| `scripts/engineering/reference_resolver.py:23` | `…（355★ · **AGPL-3.0**）⇒ ★★ **只读思想、绝不抄代…` |
| `tools/compare_geometry.py:9` | `⇒ ★ 本模块把那**判据**（★ 不是代码 —— 来源是 AGPL，铁律 6 只读思想）搬进来，` |
| `tools/ec00_drafts_audit.py:40` | `r"(?:MIT\|Apache-2\.0\|AGPL\|GPL\|本仓.{0,4}MIT\|license\|许可)",`（正则里的枚举） |
| `tests/test_license_redlines_gate.py:8` | `依据是 AGENTS.md §二 铁律 6 的许可表（AGPL/GPL/无许可/全版权保留 = 只读思想）。` |
| `tests/test_reference_resolver.py:11` | `（355★ · **AGPL-3.0**）⇒ ★★ **只读思想、绝不抄代码**（铁律 6）` |

- **记录员注（陈述）**：这 6 处**没有一处**把本仓文件本身声明为 GPL 族；内容分别指向铁律 6、
  某来源的许可事实、或门禁正则的枚举
- **未确认**：仓库里是否存在**未在头部注明**的 GPL 族代码——本探测只看文件头 40 行

---

## 本节未覆盖（留给后续补充）

- `union-sources.json` 里每条来源的 `repo`/`license`/`declared_verified`/`note` 四字段是否齐全（`check_union_conventions` 规则 5 的对象）
- 能力级 `provenance` 与来源级清单的对应（C 维度记 `provenance` 只有 1/140 条）
- 仓库外克隆（`C:\swprojects\` 26 个）的许可现状
- 是否存在从 AGPL 项目「代码级」搬运——需逐文件比对，本次未做

---

## 证据索引（每个事实号 → `inventory-i.json` 的键）

| 事实 | 证据载体 |
|---|---|
| I-01 | `inventory-i.json` 的 `union_sources.count` / `union_sources.licenses` |
| I-02 | `inventory-i.json` 的 `third_party_notices` |
| I-03 | `inventory-i.json` 的 `repo_license` |
| I-04 | `inventory-i.json` 的 `code_files_scanned` / `license_keywords_in_header` |
| I-05 | `inventory-i.json` 的 `files_with_gpl_family_header`（6 个）+ 逐行摘录 |
