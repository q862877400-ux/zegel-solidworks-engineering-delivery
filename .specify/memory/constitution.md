# SolidWorks 自动化 · 集大成与护城河 — Constitution

> **本文件不重述六条铁律。** 它们在 [`AGENTS.md`](../../AGENTS.md) §二，是唯一真源。
> 本宪法只回答一件事：**SDD 流程（Specify → Plan → Tasks → Implement → Converge）
> 如何服从那些既有约定。**

**Version**: 1.0.0 | **Ratified**: 2026-10-01 | **Last Amended**: 2026-10-01

---

## Core Principles

### I. 缝合优先，不发明（AGENTS.md 铁律 1）

每个能力都要能指认出处。**spec.md 必须为每个需求写出「来源」**，
取值限于 AGENTS.md 铁律 1 的四种合法来源（官方文档 / 其它开源项目 /
四家外部 MCP 项目 / 本项目既有模式）。

**不可接受**：spec 里出现「需要一个功能来做 X」而不说它从哪来。

### II. 签名三源互证，冲突以出厂类型库为准（铁律 4）

**plan.md 必须列出本特性要查的官方源**（CHM 解包路径 / `C:\swapi` / interop 反射转储），
并写明冲突时的裁决顺序。

**不可接受**：plan 里出现 `FeatureManager.XXX(...)` 而不写它从哪个源核到。

### III. 查不到就写查不到（铁律 5）

spec / plan / tasks 里出现「应该有这样的成员」时，
**必须附一条实际查过的命令**。查不到就写「查不到」并停下换思路。

**可 grep 判据**：该特性的 plan.md 里每个「应该有」都有对应的核查命令。

### IV. 许可红线（铁律 6）

**任何来源引用都要带许可**，且 `plan.md` 要写明：
- MIT / Apache-2.0 ⇒ 可抄，义务是什么
- AGPL / GPL / 无许可 ⇒ **只读思想，不抄代码不抄文本**

**判据**：`specs/<feature>/plan.md` 里每个来源行都有 `license` 字样。

### V. 验收判据必须能跑（本项目一贯做法）

**tasks.md 的每个任务都要有「怎么验」**，且是一条**能跑出绿的命令**。
「我检查过了」「应该没问题」不算。

**判据**：tasks.md 里每条任务都带 `→ 验收:` 并给出命令。

---

## SDD 与本项目既有载体的接口

**这是本宪法唯一新增的东西** —— 把 SDD 的四种制品接到已有的状态载体上：

| SDD 制品 | 接到哪 | 规则 |
|---|---|---|
| `spec.md` 的需求 | — | 每条需求带「来源」与「验收场景」 |
| `plan.md` 的技术方案 | `docs/signature-audit.md` | 新涉及的 COM 调用要进签名审计 |
| `tasks.md` 的任务 | `docs/ROADMAP.md` 的阶段 | **一个 tasks.md 对应 ROADMAP 的一个阶段**，不另起体系 |
| 实现完成后 | **`capabilities.yaml`** | `level` 取自五级枚举；`verified` 必须有我们自己的运行证据（`evidence` + CAD 的 `verified_versions`） |

**⚠ 三处不许写**（会与既有载体重复，属「一个事实两个家」）：

1. **不写「当前进度」** —— 那在 `capabilities.yaml` 的 `level` 与 ROADMAP §一 游标
2. **不重述六条铁律** —— 引用 AGENTS.md §二
3. **不重述已知事实** —— 引用 AGENTS.md §六（那里有 27 条本机核实过的事实）

---

## Governance

**AGENTS.md 优先。** 本宪法与它冲突时，以 AGENTS.md 为准，并修正本文件。

**修订流程**：
- 改六条铁律 ⇒ **改 AGENTS.md**，本文件只更新 §I–§IV 的引用
- 改 SDD 接口（上方那张表）⇒ **改本文件**，并 bump 版本号
- 每次修订要在本文件的 `Last Amended` 留日期

**合规检查**：Spec Kit 的 `speckit.analyze` 会做跨制品一致性检查；
本宪法的 §I–§V 就是它要对齐的判据。**判据可跑性由 `tasks.md` 的 `→ 验收:` 行保证。**

---

## 与 `docs/ROADMAP.md` 的关系

```
ROADMAP.md              = 「现在在哪、下一步做什么」（长程游标）
specs/<NNN>-<feature>/  = 单个特性的四件制品（本宪法管的）
```

**一个特性的完整生命周期**：
```
ROADMAP 进入某阶段 → speckit.specify 写 spec → speckit.plan → speckit.tasks
→ speckit.implement（在代码副本落地）→ 更新 capabilities.yaml → 回写 ROADMAP 游标
```

---

## 规格老化模型：**Flow-forward**（沿用既有项目指南第 5 步的必答项）

Spec Kit 把「规格如何老化」留给团队定，给三个模型。**本项目选 Flow-forward**：

| 选择 | 规则 |
|---|---|
| **完成的特性目录视为不可变历史** | 需求变了 ⇒ **开新的 `specs/<NNN>-<slug>/`**，不改旧的 |
| 当前状态 | 不在 spec 里 —— 在 **`capabilities.yaml`** 的 `level` + ROADMAP §一 游标 |

**为什么选它**：本项目在 Flow-back 上栽过 —— 双方反复修改同一批文档，
产出 13 轮往返（见 ROADMAP §五 反模式）。**冻结完成的目录 ⇒ 没人能改它 ⇒ 没有漂移。**
代价是可能重复，靠**目录编号 + ROADMAP 引用**维持血缘。

---

## 如何在 DSH 里调用这些命令（**没有斜杠命令**）

DSH 没有 `/speckit.*` 斜杠命令机制。命令文件在 `.specify/commands/*.md`，
**是「过程定义」，不是终端命令**（Spec Kit 官方原话：*These are agent skills, not terminal commands*）。

**本项目的调用方式**：

```
读 .specify/commands/speckit.<名字>.md → 按它写的过程执行 → 产出落在 specs/<NNN>-<slug>/
```

**⇒ 执行者（我）就是那个 agent，命令文件是我的作业指导书。**
**不要**去 DSH 的 skill 目录里复制一份 —— 那会造出第二个家（Spec Kit 升级后两边不一致）。

**命令的顺序**（**只有 `specify` 是 `plan` 的硬前置**，其余是质量闸）：

| 短路径（小特性） | 全路径（生产特性，本项目默认） |
|---|---|
| specify → plan → tasks → implement → converge | **constitution**（每项目一次）→ **specify → clarify → plan → checklist → tasks → analyze** → implement → converge |

**本项目默认走全路径** —— 理由：我们的特性都涉及**官方签名核验与许可**，
clarify（消除歧义）与 analyze（跨制品一致性）恰好是挡住「凭印象写 API」的那两道。
