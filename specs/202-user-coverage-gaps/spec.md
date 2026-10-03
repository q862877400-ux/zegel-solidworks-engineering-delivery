# Feature Specification: 用户视角能力覆盖 · 缺口攻关

**Feature Branch**: `202-user-coverage-gaps`
**Created**: 2026-10-03
**Status**: Draft
**Input**: 用户要求 —— 从 `docs/user-feature-coverage.md` 的视角，**提升本仓库的能力覆盖面**，按 spec 规范立计划并全自动执行。

## 一、要解决的问题

★ **本文不写「当前进度」**（宪法 §"三处不许写"第 1 条：进度在 `capabilities.yaml` 的 `level`
与 `docs/ROADMAP.md` §一 游标）。本文只说**要解决什么**。

`docs/user-feature-coverage.md`（★ **生成物，不要手改**，由仓外 `D:\SW-coverage-tool\` 现算）
按**用户 CommandManager 心智模型**量了 145 个功能，其中含：
① 一份**缺口清单**（该文 §八：只有四家有、我们没有的项）；
② 一份**「标了 ✅ 而 `level` 不是 `verified`」的名单**（该文 §五）。

⇒ ★★ **两个问题**：
1. 缺口清单里，**哪些真能做到、怎么做、怎么证明**（★ 做不到的**写明依据并单列**，不假装做到）；
2. 那份名单说明**「有入口」≠「能用」** ⇒ ★ **不许**拿覆盖率的百分数当能力承诺。

★ **要多少项、现是多少** —— 一律去 `docs/user-feature-coverage.md` **现算**，本文**不复述数字**
（复述就会腐坏：本仓已因此吃过「一个事实两个家」的亏）。

## 二、与既有规格 `specs/201-toolbar-gaps` 的关系（★ 不重复）

| | 201 | **202（本规格）** |
|---|---|---|
| 量的是什么 | 用户贴的**5 组工具栏截图**里那批条目 | 用户 CommandManager 心智模型下的 **145 个功能** |
| 需求原文 | `docs/toolbar-ledger.json` | `docs/user-feature-coverage.md` §八 + §五 |
| 交集 | ★ 两者**口径不同、交集不完全** —— 本规格**只处理 201 没覆盖的视角** |

★ 两规格**互不修改**（宪法 §Flow-forward：完成的特性目录是**不可变历史**）。

## 三、User Scenarios & Testing

### US1 - 出工程图：各类视图与标注（Priority: P1）

设计者要能建**投影 / 剖面 / 局部 / 断裂 / 辅助视图**，能插**注释 / 基准符号 / 表面粗糙度 / 中心符号线 / 气泡序号 / 孔表 / 修订表**，能用**图纸格式/模板**。

**Why this priority**：★ 这是**缺口清单里最大的一域**，且是四家**领先我们最多**的一域
（★ 具体数字去 `docs/user-feature-coverage.md` §四 现算，本文不复述）。

**Independent Test**：给一个零件，能建出其中**一个**视图并回读到视图对象；或能插入其中**一个**标注并回读到注解对象。

**Acceptance Scenarios**：

1. **Given** 一个已保存的零件，**When** 新建工程图并调投影视图入口，**Then** 视图数 **+1** 且能回读到视图对象（`Name` 非空）
2. **Given** 一张工程图，**When** 插入表面粗糙度符号，**Then** 注解数 **+1** 且回读到注解对象

---

### US2 - 特征与曲面的剩余工具（Priority: P2）

设计者要能用**组合/相交 · 缩放/变形 · 边界凸台 · 加厚**，以及**旋转曲面 / 剪裁曲面 / 中面**。

**Why this priority**：特征与曲面是缺口清单里**第二、第三大**的域；
★★ 其中**旋转曲面的实现已 `verified` 而未暴露成工具**（见 `docs/user-feature-coverage.md` §六）
⇒ **低成本高收益**。

**Independent Test**：能用其中**一项**并给出特征树/面数增量，或**写明它到不了并给出依据**。

**Acceptance Scenarios**：

1. **Given** 两个相交实体，**When** 调组合/相交，**Then** 实体数或面数发生可读的变化
2. **Given** 已有实现而未挂工具的项，**When** 补 ToolSpec，**Then** 它出现在 `all_specs()` 且覆盖率脚本命中

---

### US3 - 钣金与焊件的剩余工具（Priority: P3）

**Why this priority**：焊件与钣金是**占比最低**的两域（★ 数字见 coverage 文 §四）；
★ 但两者都有**已确证的指针族限制**（见 Edge Cases）⇒ 预期**部分只能单列**。

**Independent Test**：每项要么给出真机建成证据，要么写进后端到不了名单**并带依据**。

**Acceptance Scenarios**：

1. **Given** 一个有基体法兰的钣金件，**When** 调斜接法兰入口，**Then** 特征树增量**或**给出 `AccessSelections` 依据
2. **Given** 焊件，**When** 调顶端盖，**Then** 同上口径

---

### US4 - 草图/装配/其他的零星缺口（Priority: P4）

**样条曲线 · 完全定义检查 · 爆炸视图 · 宏/VBA · PDM**。

**Why this priority**：项数少且分散，但**样条曲线是草图的基本图元**、**完全定义检查是只读且便宜**。

**Independent Test**：逐项独立可测（各 1 格真机）。

**Acceptance Scenarios**：

1. **Given** 一个活动草图，**When** 画样条，**Then** 草图段数 **+1**
2. **Given** 一个草图，**When** 读完全定义状态，**Then** 回一个可解释的枚举/布尔，且**不报错**

---

### Edge Cases

- ★★ **官方入口是 `CreateDefinition` + `AccessSelections`（指针族）** ⇒ 本后端**到不了**（事实 47/474）⇒ 必须**单列并写明依据**，**不许假装做到**。
- ★★ **既有实现真机"静默不成"**（剪裁曲面三条入口 / 加厚曲面 / 直纹曲面 —— 事实 417–419）⇒ **不许把"有代码"记成"已能"**。
- ★ **官方源查不到入口** ⇒ 按铁律 5 写「查不到」并停下换思路，**不许用名字相近的凑**。
- ★ **判据只认"树增量"会误判**：分割线那一轮的实测证明**树会涨而几何没变**（事实 486）⇒ 判据要含**几何读数**。

## 四、Requirements

### Functional Requirements

★ 每条需求都写明**来源**（铁律 1 的四种合法来源之一）与**来源许可**。

- **FR-001**: 工程图**视图族**（投影/剖面/局部/断裂/辅助）MUST 有可调用入口。 来源=官方 API 文档（`C:\swapi\types\IView*.md` / `IDrawingDoc*.md`）+ 参照 `Eduardof0nt/Solidworks-MCP-Server`（**license: MIT**）。验收场景=US1-1。
- **FR-002**: 工程图**标注族**（注释/基准符号/表面粗糙度/中心符号线/气泡序号/孔表/修订表）MUST 有可调用入口。 来源=同上（**license: MIT**）。验收场景=US1-2。
- **FR-003**: **图纸格式/模板** MUST 可查可设。 来源=官方 API 文档 + `andrewbartels1/SolidworksMCP-python`（**license: MIT**）。
- **FR-004**: 特征域剩余的**组合/相交 · 缩放/变形 · 边界凸台 · 加厚** MUST 逐项给出「建成」或「带依据的到不了」。 来源=官方 API 文档 + `vespo92/SolidworksMCP-TS`（**license: MIT**）。验收场景=US2-1。
- **FR-005**: ★ **已 `verified` 而未挂工具的曲面能力** MUST 补上工具入口（★ 优先于新写实现）。 来源=**本项目自身既有模式**（`scripts/sw_surface.py`）。验收场景=US2-2。
- **FR-006**: 钣金/焊件剩余项 MUST 逐项给出「建成」或「带依据的到不了」。 来源=官方 API 文档 + `Slacker-LLC/solidworks-mcp`（**license: Apache-2.0**，义务：保留 `NOTICE`（`Copyright 2026 JIALE LIU`）+ 声明改动文件）。
- **FR-007**: 草图**样条曲线**与**完全定义检查** MUST 可用。 来源=官方 API 文档 + `Slacker-LLC/solidworks-mcp`（**license: Apache-2.0**）。
- **FR-008**: 装配**爆炸视图**与**宏/VBA 执行** MUST 可用。 来源=官方 API 文档 + `Slacker-LLC/solidworks-mcp`（**license: Apache-2.0**）。
- **FR-009**: ★ **本规格每一项都必须留下真机证据**，否则 `level` **不得**写 `verified`。 来源=AGENTS.md 铁律 2。
- **FR-010**: ★ 判为「后端到不了」的项 MUST 进 `docs/backend-limited-items.json` 且**每条带依据**。 来源=本项目既有约定。
- **FR-011**: ★ **不许手改** `docs/user-feature-coverage.md`（生成物） —— 覆盖率只能靠**补真入口**提升，不靠改表。 来源=该文件头部的自述。
- **FR-012**: PDM 项 MAY 判为 `[-] 不做` 并写明依据（需 PDM 服务器，本机无）。 来源=环境约束（**NEEDS CLARIFICATION: 本机是否装了 PDM？**）。

### Key Entities

- **缺口项**：`docs/user-feature-coverage.md` §八 的一行（域 + 功能 + 哪几家有）。
- **真机证据**：`output/*.json`，必须含**判据读数**与 `sw_alive`/`dialogs`。
- **能力条目**：`capabilities.yaml` 的一条（`level` + `evidence` + `limitations`）。

## 五、Success Criteria

- **SC-001**: 覆盖表**第一列** 本仓库升到 **≥110/145**（★ **当前值去 `docs/user-feature-coverage.md` §三 现算**，本文不复述）。
- **SC-002**: 本规格新做的每一项都**带真机证据**；`capabilities.yaml` 的 `level` **只升不降**。
- **SC-003**: 判为「后端到不了」的项 **100%** 进 `docs/backend-limited-items.json` 且每条带依据。
- **SC-004**: §五 那 13 条 `stitched` **至少转 `verified` 3 条**。
- **SC-005**: `scripts/release_check.py` 全程**退出 0**（门禁不许因本规格变红）。

⚠ **不设「100% 覆盖」目标** —— ★ 那会逼人把「有代码」当「能用」（本仓已栽过，见事实 420/486）。

## Assumptions

- ★ **单源运行时**（事实 24）：真机测试**串行**、由 Lead 亲自做；**不派给子智能体**（会死锁）。
- 本机 **SolidWorks 2026 SP4.1 · 中文 UI**。
- 官方离线源在本机：`C:\swapi\` 与 `D:\AI\SW\AI Solidworks\官方文档\`（CHM 解包）。
- 四家源码**已在本地克隆**（`C:\swprojects\`），**不联网**取。
- 便宜模型助手（`ninfer-sm89` / `qwen3.8-27b`）**不是多模态** ⇒ 只派**纯文本**静态活，**不派它看截图**。
