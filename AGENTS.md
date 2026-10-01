# AGENTS.md

本文件是 SolidWorks Automation Skill「集大成 + 建护城河」任务的常驻指令；工作区 `D:\AI\SW\`（已是 git 仓库），代码工作副本 `C:\swprojects\sw-skill-fork\`。跨项目的通用纪律在 `~/.dsh/AGENTS.md`（用户全局层，每轮自动注入）—— 缝合优先、签名以官方源为准、查不到就说查不到、许可红线、把验证责任转移到静态比对、验收判据写成可 grep 项；本文件只留 SolidWorks 专属的事实与规矩。

## 工作区（第一件事，先确认你在哪）

| 路径 | 是什么 | 能改吗 |
|---|---|---|
| `D:\AI\SW\` | 本文件所在 · DSH 工作区根 · 任务产物（草稿 / 日志 / 报告 / 证据） | 放产物 |
| `C:\swprojects\sw-skill-fork\` | 代码工作副本（独立 git 仓库） | 唯一改代码的地方 |
| `C:\swprojects\<owner>\` | 四家外部 MCP 项目的克隆 | 只读对照 |
| `C:\swprojects\sw-automation-skill\` | 上游的另一份克隆 | 只读对照 |
| `D:\AI\SW\AI Solidworks\` | SolidWorks 工作区（官方文档 / 手册 / 模型 / 截图） | 只读 |
| `D:\AI\SW\docs\` | 本文件里 `docs/...` 相对 AGENTS.md 解析到这里（上游结构 / 素材 / 来源标注 / 团队分工 / 资源速查 / 开工模板 6 份）；任务产出（`union-conventions.md` 等）在代码副本的 `C:\swprojects\sw-skill-fork\docs\` | 可改 |

`D:\AI\SW\` 现已是 git 仓库（提交 `1f86c5d` 起），收草稿脚本、运行日志、报告与证据；`.gitignore` 排除了 398 MB（官方文档 / 反射转储 / 探索截图 / CAD 保真数据）。

任务报告放 `D:\AI\SW\` 下，代码放 `C:\swprojects\sw-skill-fork\`。`D:\AI\SW\AI Solidworks\` 是模型 / 截图 / 手册，不是代码落点。

## 〇、一句话任务

> 自建仓库，把 SolidWorks 自动化做到「官方 SolidWorks API 全覆盖 + 集四家 MIT/Apache MCP 项目之广度 + 业界空白域护城河」；交付形态是我们自己的仓库，上游 `wzyn20051216/solidworks-automation-skill`（1010 星, MIT）与四家外部项目同为来源，一件一件搬、搬一件过一遍并入六条规则。

- 集大成：把四家外部 MCP 项目的能力广度并入本仓库，使单一项目即可替代四家之和，每一步可指认出处（铁律 1）。
- 建护城河：攻业界空白域 —— 经核实真正全网空白的只有拓扑优化、动画导出（AVI）、Costing 三个。
- 正规军：不搞大杂烩，命名 / 单位 / 选择 / 验证等级 / 出处五统一，并挂机器门禁（`docs/union-conventions.md` + `scripts/check_union_conventions.py`）。
- 单源交付：运行时只能有一个 SolidWorks MCP —— 多个进程抢同一 COM 连接会死锁（已知事实 24）。

选按需搬取、不整体继承的理由：整体继承会把上游的目录结构、命名与验证口径整套带进来，与同时要并入的四家外部项目在同一批文件里打架；搬一件过一遍六条规则，冲突在搬的那一刻解决，不留给后面。

「引用各家」不等于不用上游代码：上游 `mcp-server/server.py`（104 KB，45 个工具的现成实现，我们一行没改）与 49 个 `scripts/*.py` 是要用的，只是身份从「本仓库的历史基底」降为来源之一，与四家同等，MIT 版权声明照留。

这仍是缝合项目，不是从零写：能力来自官方文档、外部开源项目与本仓库既有模式。

## 一、验收标准（做完这几条才算完成）

| # | 判据 | 怎么验 |
|---|---|---|
| A1 | 四家的能力广度已并入：域覆盖矩阵里本仓库每一格都有来源，或写明「不做 + 原因」 | `docs/union-coverage-matrix.md` 可重新生成且无空白格 |
| A2 | **两层 provenance 都要**：① **来源级** —— `tools/union-sources.json` 的每个来源带 `owner/repo` 全名 + 许可（白名单内）+ `declared_verified` + `note`；② **能力级** —— `capabilities[].provenance` 对**来源派生**的条目（`level: source_verified`）必须齐 `repo`/`license`/`files`/`upstream_verified` 四字段。⚠ ①与②**不是同一件事**：① 说的是「哪几家、什么许可、他们自己声明跑过什么」；② 说的是「这一条能力是从哪条来源派生的」。**`level: verified` 只表示「有我们自己的运行证据」，不表示「代码是我们写的」—— 两条线不该混。** | ① `python scripts/check_union_conventions.py` 的「规则 5 · 出处与许可」段；② 同门禁的「清单形状」段（现 `source_verified` 条目数为 **0**，故②**空满足**；一旦新增 `source_verified` 条目，②即强制生效）|
| A3 | 五统一门禁通过：命名 / 单位 / 选择 / 验证等级 / 出处 | `scripts/check_union_conventions.py` 退出码 0，且已接进 `release_check.py` |
| A4 | 每个条目的 `level` 取自五级枚举；`verified` 必须有我们自己的运行证据 | 逐条核对 `capabilities.yaml` |
| A5 | 每个新增文件里每个 COM 调用的参数顺序与类型与官方签名对齐 | `docs/signature-audit.md` |
| A6 | 许可无越界：AGPL / GPL / 无许可 / 全版权保留的代码没被抄进来；Apache-2.0 来源带 NOTICE 义务 | 逐文件对照「许可判定表」 |
| A7 | 全文没有一处把 `source_verified` 或 `stitched` 写成 `verified` | grep 全文，禁词 0 命中 |
| A8 | 报告写明并入了什么、仍空缺什么、为什么空缺 | `docs/harvest-report.md` |
| A9 | 空白域护城河有可跑的工程实现（拓扑优化优先），不是只有文档 | 对应 `scripts/` 模块 + `tests/` |
| A10 | 按需搬取：每一件搬进来的东西都过一遍「并入六条规则」，冲突在搬进来的当时解决 | `scripts/check_union_conventions.py` 退出码 0 + 并入清单逐条核对 |

> A1–A10 是交付判据，不是每轮都要全绿：A3（门禁）是可执行的不变量，任何时候都该绿；其余随并入逐条满足。

进度与下一步看 `capabilities.yaml`（能力清单：每条带 `level`，`verified` 另带 `evidence`）—— 状态由清单承载，不写进本文件。`docs/union-coverage-matrix.md` 第五节的「并入清单」是缺口地图（每域缺什么、从哪抄、该来源声明跑过没有），不是进度。

## 二、六条铁律

### 铁律 1 · 只做「缝合」，不做「发明」

每加一个能力，要能指认出处。四种合法来源：
| 来源 | 怎么用 | 例 |
|---|---|---|
| 官方 API 文档 | 决定接口选型与参数顺序 | Simulation 域（外部无人提供，只能照官方签名建） |
| 其它开源项目 | 直接移植 / 改写，保留来源头注释 | 建视图 ← codestack；VBScript ← pengxiaoan |
| 四家外部 MCP 项目 | 移植其能力广度，按 `provenance` 标注来源与许可 | `andrewbartels1` 的草图完全定义探针；`Slacker-LLC` 的声明式 selection |
| 本项目自身既有模式 | 沿用 `sw_part.py` / `sw_hole_features.py` 的写法与命名 | 新 `sw_xxx.py` 沿用 `_select_by_id` / `get_com_member` |

不可接受：凭印象写一个 `FeatureManager.XXX(...)` 然后「看着像对的」。

### 铁律 2 · 可以实测，但必须先关弹窗、必须有超时

验证顺序：静态签名比对（前置筛查）→ 本机实测（真跑，用 `mcp__solidworks__*` 或直接调 COM）→ 两关都过，才允许在文档里写「已验证 / 实测 / 跑通」。实测的三条安全约束：

- 先置 `ISldWorks.CommandInProgress = True` —— 未抑制的模态对话框会把会话永久挂起，这是无人值守挂起的头号原因。
- 每个 COM 调用设超时 —— COM 是 STA 且线程亲和，调用一旦开始无法强制中止；超时只救「等待」，救不了线程，超时后不要重试同一进程。
- 收尾必做 —— `CommandInProgress = False`、释放 COM 引用、关掉自己开的文档。

红线：破解相关（SolidWorks-CAD / Solidworks-Crack 类投递页、破解指南）零接触；不动注册表 / 全局环境变量 / 系统层；未经确认不 `git push` / 不建目标远端仓库 / 不发 release；不删用户数据。

### 铁律 3 · 结构按顶层白名单，不临时起目录

**结构目录**只允许这 14 个：`.github` `agents` `ai_team` `apps` `assets` `docs` `dotnet` `examples` `mcp-server` `references` `scripts` `subskills` `tests` `tools`（前 13 个上游就有，`tools` 是我们加的）。新增白名单外的顶层目录，要在本节登记它是什么、为什么放不进已有目录，再动手。

**产物 / 缓存目录**允许存在于工作树，但必须 gitignore、不入库：`.api-signatures`（签名索引）、`output`（构建产物）、`.pytest_cache`（pytest 缓存，须 ignore）。

新文件落进已有位置：能力实现进 `scripts/`，知识文档进 `references/`，测试进 `tests/`，说明与生成物进 `docs/`。上游目录树与新增模块的硬性要求见 [docs/upstream-layout.md](docs/upstream-layout.md)（对照参考，不是约束来源）。

### 铁律 4 · 签名三源互证，冲突以出厂类型库为准

本机有两套官方离线源，各有长短，都要查：`D:\AI\SW\AI Solidworks\官方文档\`（CHM 解包，权威、带说明与示例，查语义与用法）与 `C:\swapi\`（结构化 markdown，查精确签名与枚举值）。各源覆盖范围与检索入口见 [docs/sources.md](docs/sources.md)。

出厂类型库是第三套源，也是冲突时的裁决者：`FeatureFillet3` 在本机类型库里有 14 个参数，官方文档写 7 个。口径是三源互证 —— 文档、反射、CHM；冲突时以出厂类型库的反射为准。不凭记忆、不凭反射猜参数、不照抄其它项目的注释。

### 铁律 5 · 查不到就说查不到

两套源都查不到 → 写「查不到」并停下换思路，不要用相似名字蒙混。名字缺席 = 官方 API 里没有这个成员，不是「没写文档」。

### 铁律 6 · 许可红线，一次都不能越

| 许可 | 能做什么 | 义务 |
|---|---|---|
| MIT | 读、抄、改、商用 | 保留版权声明 |
| Apache-2.0 | 读、抄、改、商用 | 保留 `NOTICE`（`Slacker-LLC/solidworks-mcp` 是 `Copyright 2026 JIALE LIU`）+ 声明改动了哪些文件 |
| AGPL / GPL | 只读思想 | 不抄代码、不抄文本 |
| 无许可 / 全版权保留 | 只读思想 | 同上 |

- **单源运行**：运行时只能有一个 SolidWorks MCP —— 多个进程抢同一 COM 连接会死锁（已知事实 24），所以 MCP 选型就是运行时依赖选型：只在 MIT 那份上跑，AGPL 的 SolidPilot 只读思想。

Apache-2.0 的 NOTICE 义务跟着分发走：一旦入库，推送任何远端时都要带 `THIRD-PARTY-NOTICES.md` —— 该文件**已存在**；MIT 来源（上游与 `Eduardof0nt` / `andrewbartels1` / `vespo92`）保留各自的版权声明。完整许可判定表与来源清单见 [docs/sources.md](docs/sources.md)。

## 三、上游仓库结构（对照参考）

上游的目录树、`scripts/` 现有模块清单与新增模块的硬性要求见 [docs/upstream-layout.md](docs/upstream-layout.md)。它是对照参考与取材地图，不是我们的结构约束 —— 我们自己允许哪些顶层目录，看铁律 3。

## 四、素材库

### 4.1 两套官方离线源 + 反射（各管一头）

本机两套官方源都要查：`D:\AI\SW\AI Solidworks\官方文档\`（CHM 解包，权威、带说明与示例，查语义与用法）与 `C:\swapi\`（结构化 markdown，查精确签名与枚举值）；检索入口是 `手册\swdoc.ps1` 与 `mech-design` skill 的 `sw_know.py`。出厂类型库的反射是第三套源，也是冲突时的裁决者。各源的文件量、检索子命令与覆盖缺口见 [docs/sources.md](docs/sources.md)。

### 4.2 其它项目（`C:\swprojects\`）

四家与本项目重叠的外部 MCP 项目（克隆在 `C:\swprojects\<owner>\`，已逐份读真实 LICENSE 文件，不采信 README 徽章）：
| 克隆目录 | 项目（owner/repo） | 工具 | 许可 | 测试文件 | 自己声明跑过的环境 |
|---|---|---|---|---|---|
| `Eduardof0nt` | Eduardof0nt/Solidworks-MCP-Server | 187 | MIT | 0 个 | 未声明 |
| `andrewbartels1` | andrewbartels1/SolidworksMCP-python | 128 | MIT | 147（7 live） | 未声明（README 自述 under active construction） |
| `SolidworksMCP-TS` | vespo92/SolidworksMCP-TS | 103 | MIT | 7（0 live） | 未声明 |
| `Slacker-LLC` | Slacker-LLC/solidworks-mcp | 92 | Apache-2.0 | 2（1 live） | SW 2026 SP3.2 简体中文 |

- 工具最多的那家（187）测试文件数为 0：README 写着「Verified on SolidWorks 2024」，仓库里没有任何测试文件 —— README 说验过不等于验过。
- 四家里只有 `Slacker-LLC` 声明全工具真机跑过，而它的工具数最少（92）；它的 92 个里没有仿真 / 动画 / 拓扑 / 钣金 / 焊件 / 公差。
- `Slacker-LLC` 是 Apache-2.0：可抄，但要保留 `NOTICE`（`Copyright 2026 JIALE LIU`）并声明改动了哪些文件；推送任何远端时产生硬性义务，`THIRD-PARTY-NOTICES.md` **已存在**（153 行 / 6.5 KB，已入库）。

其余 21 个外部项目克隆的清单、逐项能补什么、许可判定表与 MIT 唯一例外，见 [docs/sources.md](docs/sources.md)。

### 4.3 来源标注制（每个移植函数都要有）

每个移植函数必须带来源头注释，并入 `capabilities.yaml` 的条目另带结构化 `provenance` 字段；格式模板、字段定义与「未实测」标注规则见 [docs/provenance-format.md](docs/provenance-format.md)。许可必须与来源表一致。

## 五、工作方法（并入五步）

1. 建全景与对差：`sw_know.py domain --list` 拿 14 个域，`swdoc.ps1` + 反射补 `cosworks` / Routing / Costing / PDM，对照上游 `capabilities.yaml` + `scripts/` + `subskills/` 建 `docs/capability-matrix.md` 与 `docs/gap-analysis.md`（从零建表，不预设缺口结论）。
2. 找来源：按优先级取素材 —— 上游相邻模块 > MIT 项目现成实现 > MIT 项目文档 / 示例 > Apache-2.0 项目实现（带 NOTICE）> 只读思想（AGPL / GPL / 无许可，绝不抄文本）> 照官方签名自建。
3. 归一：按「并入六条规则」改造，命名 / 单位 / 选择 / 验证等级 / 出处五统一。
4. 标等级与出处：`capabilities.yaml` 每条给 `level`（五级）与 `provenance{repo, license, files, upstream_verified}`。
5. 门禁与实测：`check_union_conventions.py` → `python -m compileall -q scripts subskills` → 逐 COM 调用与官方签名对齐（`docs/signature-audit.md`）→ 本机实测；缺我们自己的运行证据的条目留在 `stitched`。

产出：`docs/capability-matrix.md`、`docs/gap-analysis.md`、`docs/signature-audit.md`、`docs/union-coverage-matrix.md`、`docs/harvest-report.md`。

并入六条规则（全文 `C:\swprojects\sw-skill-fork\docs\union-conventions.md`，机器校验 `scripts/check_union_conventions.py`，已在 `release_check.py` 里硬失败）：
| # | 规则 | 校验 |
|---|---|---|
| 1 | 命名统一 `solidworks_<域>_<动作>`；headless 路线用 `cadstudio_*`，两者不混用 | 工具名正则 |
| 2 | 长度参数 `_mm` 结尾、角度 `_deg` 结尾，换算只在边界做一次（`sw_connect.mm()`） | 参数名与描述 |
| 3 | 选择用声明式 `selection`，不写裸坐标，并按 mark 分配 | 参数 schema 无裸 `x` / `y` / `z` |
| 4 | 验证等级五级 `verified` / `source_verified` / `stitched` / `indexed` / `not_implemented`；`source_verified` 不得写成 `verified` | `level` 在枚举内，`verified` 要有 `evidence` |
| 5 | 每条并入条目带 `provenance{repo(owner/repo), license, files, upstream_verified}` | `repo` 匹配 `owner/repo`，`license` 在白名单 |
| 6 | 建特征之后查 `EditRebuild3` + `GetWhatsWrong2`，不静默成功 | 建特征类工具都要调 |

## 六、已知事实（上游文档 / 注释里没有或写错的，已在本机核实，写代码直接用，不要重新推导）

| # | 事实 | 依据 |
|---|---|---|
| 1 | 切除的正确入口是 `IFeatureManager.FeatureCut4`（27 参数），不是 `FeatureExtrusion3(Flip=true)`：后者建出来是「凸台-拉伸」特征名，体积恒等于原板 | 本机实测 + 上游 `sw_part.extrude_cut` + `swdoc.ps1 -File FeatureCut4` |
| 2 | `IFeatureManager.FeatureExtrusion3` 是 23 个参数；`FeatureExtrusion2` 已废弃被 3 取代 | `C:\swapi\types\IFeatureManager\FeatureExtrusion3.md` + delancy827 README 独立佐证 |
| 3 | 「>12 参数 IDispatch 会失败」是错的（guoleizhen717 说法不可采信） | 23 / 27 参在 pywin32 迟到绑定下均正常 |
| 4 | pywin32 迟到绑定下同一成员可能是属性也可能是方法：`GetDocumentCount`、`GetMassProperties` 是属性，直接调用会 `TypeError: 'int' object is not callable`；移植代码沿上游 `get_com_member()` | 本机实测 + 上游 `sw_connect.py` |
| 5 | 质量属性用 `IModelDocExtension.GetMassProperties2(accuracy, out status, useSelected)`；下标 0-2 质心、3 体积、4 表面积、5 质量。`IModelDoc2.GetMassProperties` 是属性、返回 12 元 tuple | `C:\swapi\examples\Get_Mass_Properties_of_ActiveDoc_Example_VB.md` + CHM |
| 6 | `GetBodies2` 在 `IPartDoc` 上，不在 `IModelDoc2` 上 | 对 interop DLL 反射 |
| 7 | `ISketchManager.CreateCircle` 是 6 参（圆心 3 + 圆上点 3） | 对 interop DLL 反射 |
| 8 | `ISelectionMgr.AddSelectionListObject` 的 bool 返回值不可信，用 `GetSelectedObjectCount2(-1)` 回读 | 本机实测（12 次全 false 但计数 = 12） |
| 9 | 画草图前先 `SelectByID2` 选中基准面；基准面名随 UI 语言变（`"Front Plane"` / `"前视基准面"`）。不选面 → 特征返回 NULL 且几何零变化；沿上游 `_get_plane_name_candidates` | 本机实测 + 上游 `sw_part.py` |
| 10 | 贯穿切除用 `swEndCondThroughAll(1)` + 占位深度 0.01，不是把深度设 0 | 上游 `sw_part.extrude_cut` |
| 11 | `OpenDoc6` / `LoadFile4` 的 `[out] long` 在 SW2024/2026 的 makepy 强类型代理上会二次 `int()` → 捕获 `TypeError` 后退回 `dynamic.DumbDispatch` | 上游 `sw_connect.py` |
| 12 | 空 Dispatch 参数包 `VARIANT(VT_DISPATCH, None)` | 上游 `create_empty_dispatch_variant()` |
| 13 | 上游完全没有 SolidWorks Simulation：`cosworks` / `CWModelDoc` / `CwObjects` 在其仓库出现 0 次；它的 FEA 走 CalculiX(139 次) / Elmer(30 次) 开源求解器 | 全仓 grep |
| 14 | codestack 也没有 Simulation，且 `motion-study/` 只有 2 个文件（无实现） | 同上 |
| 15 | 标量 IDispatch → `Nothing`；Variant 数组 → `Empty`。`AddRestraint` 的 DispArray 属后者 | `swp-macro-reverse-engineering.md`（搜 `DispArray`） |
| 16 | CHM 的 `cosworks` 册只有 47 个文件、只覆盖 `ICWLoadsAndRestraintsManager` 一个接口族（34 接口页 + 13 枚举页），不等于 cosworks 全貌（DLL 里 168 接口 / 363 枚举） | `swdoc.ps1 -List` + 对 DLL 反射 |
| 17 | `C:\swapi` 不含 cosworks，只覆盖 12 个程序集；`D:\AI\SW\AI Solidworks\官方文档\` 才是全的 | `by_assembly.md` + `swdoc.ps1 -List` |
| 18 | 四家外部 MCP 项目的工具数与验证口径：Eduardof0nt/Solidworks-MCP-Server 187 / MIT / 测试文件 0 个 / 未声明环境；andrewbartels1/SolidworksMCP-python 128 / MIT / 147（7 live）/ 未声明；vespo92/SolidworksMCP-TS 103 / MIT / 7（0 live）/ 未声明；Slacker-LLC/solidworks-mcp 92 / Apache-2.0 / 2（1 live）/ SW 2026 SP3.2 简体中文。工具最多的那家测试文件为 0，README 却写「Verified on SolidWorks 2024」 | 逐份读真实 LICENSE 文件与仓库树 |
| 19 | 域覆盖矩阵（去重归一后 384 个操作，域定义见下方代码块）：本仓库只有 `高级/专项` 一域领先（3，四家全 0），其余 15 个域都不领先 —— `草图` / `钣金` / `焊件` / `模具` / `参考` 为 0，`尺寸` / `零件` / `宏` 为 1，`工程图` 3 对四家的 15–18 | `tools/build_union_map.py` 生成 `docs/union-coverage-matrix.md` |
| 20 | `高级/专项`（拓扑优化 / DFM / Costing / PDM / 路由 / DimXpert / GD&T）是唯一「四家全空、只有本仓库有」的域 | 同上 |
| 21 | 真正全网空白的只有三个域：拓扑优化（`andrewbartels1` 明确列在 "Not Yet / Simulated"）、动画导出 AVI（Motion Study 创建有人做，出片没搜到）、Costing（PDM 被 `Eduardof0nt` 的 Contributing 列为 missing） | 上网核实 + 四家仓库源码 |
| 22 | 「草图完全定义」这条纪律 `andrewbartels1`（MIT）有实现且带测试：`_check_sketch_fully_defined_impl` 多探针（`ISketch.IsFullyConstrained` SW2018+ / `ISketch.GetStatus` / `ISketch.FullyDefined`）经 `_probe_to_flag` 归一 bool/int/float/string，返回 `{sketch_name, fully_defined, state, source_api}`，并接进 `checkpoint_service` 与 `parameter_repair_service`；本仓库 grep `完全定义\|fully defined\|欠定义` 0 命中 | 其源码 `src/solidworks_mcp/adapters/solidworks/sketch.py` + 三个测试用例 |
| 23 | 并入规范与门禁的落点：`docs/union-conventions.md`（六条规则全文）、`docs/union-coverage-matrix.md`（生成物）、`tools/build_union_sources.py`、`tools/build_union_map.py`、`tools/union-sources.json`（含每家的许可与验证口径）、`scripts/check_union_conventions.py`（已接进 `release_check.py`） | 工作副本 `C:\swprojects\sw-skill-fork\` |
| 24 | 运行时只能有一个 SolidWorks MCP：多个进程抢同一 COM 连接会死锁。`Eduardof0nt/Solidworks-MCP-Server` 为此实现 Windows 命名互斥锁 `Local\SolidWorksMCPServer_SingleInstance_v1`；`Slacker-LLC/solidworks-mcp` 把「Two clients driving the same session at once will deadlock it.」写进已知限制 | 两家源码 + README |
| 25 | 上游 MCP 只引用 25 个 `scripts` 模块（含 `importlib.import_module` 的动态引用），我们后补的 58 个一个都没进，交集 = 0 ⇒「我们补的能力没被 MCP 暴露」是当前最大的结构性缺口 | `mcp-server/server.py` 静态抽取全部 `scripts.*` 记号 + 与 `git diff origin/main` 的新增模块求交 |
| 26 | 仓库构成：上游原有 389 文件 / 10.0 MB；我们新增 100 文件 / 18.2 MB；改过 13 个。`mcp-server/server.py`（104 KB，上游 45 个工具的实现）**⚠ 已不再是「一行没改」**（2026-10-01）：T-011 接线在那里**加了唯一一处**（一个 `from register_capabilities import register_capabilities` + 一次 `register_capabilities(mcp, BaseInput, ResponseFormat, _run_locked)`），**全部接线逻辑在新增的 `mcp-server/register_capabilities.py`** ⇒ 上游文件的改动保持最小、可秒级审查。接线后工具数 **45 → 65** | `git diff origin/main --stat`（113 files changed）+ `git ls-tree -r -l origin/main` + `import server` 数工具（`tests/test_server_wiring.py`）|
| 27 | 上游 `origin/main` 顶层目录 13 个；实际工作树多出 4 个：`.api-signatures` / `tools` / `output` / `.pytest_cache`（只有 `tools` 入库，另三个是未入库的工作树目录）⇒ 拿上游结构当准绳永远对不上，顶层目录以铁律 3 的白名单为准 | `git ls-tree -d --name-only origin/main` 对比工作树目录 + `git check-ignore -v` |
| 28 | **「反射里有」≠「运行期调用得到」**：`IModeler` 运行期逐个 `getattr` 实测（SW 2026 SP4.1）—— 可取 5 个（`CreateCylindricalSurface` / `CreateSphericalSurface` / `CreateConicalSurface` / `CreateToroidalSurface` / `CreateArc`）；`CreatePlanarSurface` / `CreateLine` **得 `None`**（调用报含混的 `'NoneType' object is not callable`）；`CreatePoint` / `CreateBodyFromSurf` **成员不存在**；`CreateBsplineSurface` **服务器异常 `0x80010105`**。⇒ 与本表第 11 条（makepy 代理的 `[out] long`）同类：**类型层与运行层会不一致**；`sw_surface.py` 的 14 个创建入口运行期只有 5 个可达 | 活着对象上逐个 `getattr` + 调一次看是否非 None；证据 `D:\AI\SW\probe_surface_array_shape.py` |
| 29 | `Object` 型的**点/向量**参数**五种包装全可用**：裸 `list` / 裸 `tuple` / `VARIANT(VT_ARRAY\|VT_R8)` / `VT_ARRAY\|VT_VARIANT` / 逐元素 `VARIANT`。⇒ pywin32 迟到绑定会自动把 `list`/`tuple` 转 SAFEARRAY，**不必强制调用方包 `VARIANT`**（`CreateCylindricalSurface` / `CreateSphericalSurface` 各五种全返回非 None） | 同上探针的输出 |
| 30 | **「可取」≠「调用成功」**：`getattr` 拿到绑定方法只说明**成员可达**；同一函数用不同参数仍可能返回 `None`（实测 `CreateCylindricalSurface` 在可取名单里，用 `origin=[0,0,0]` 调返回 `None`）。⇒ **判据永远是「返回非 None」，不是「在可取名单里」** | 同上探针 + `scripts/sw_surface.py` 的 `require_runtime_available` 文档串 |
| 31 | `sw_surface.py` 的 14 个曲面创建入口中，**运行期只有 5 个可达**；其余失败方式**含混**（`NoneType not callable`）。⇒ 该类模块必须区分「签名层存在」与「运行层可达」，并对不可达者给**带原因**的错误 | 同第 28 条 |
| 32 | **实体（边 / 面）没有可用的名字**：`SelectByID2("Edge1","EDGE")` 与 `SelectByID2("Face1","FACE")` 在真机上**计数均为 0**（100×60×20 mm 板，12 边 / 6 面）；`SelectByID2("","EDGE",0,0,0,…)` 也是 0（原点不在边上）。**选实体（边/面）的可行路径是 `IEntity.Select4(Append, Callout)`（按**对象**选，计数 1），或按**面上的点**定位（`SelectByID2("","FACE",x,y,z,…)`，计数 1）。**⇒ 「按名字选」**只对特征成立**（`sw_part._ensure_sketch_selected` 走的就是那一路），对实体**不成立** | 证据脚本 `D:\AI\SW\probe_entity_select_by_name.py`；落地模块 `scripts/sw_selection_spec.py`（端到端 `probe_selection_spec_e2e.py` **12/12 通过**）|
| 33 | `SelectByID2` / `Select4` 的 `Callout` 参数**必须**传 `VARIANT(VT_DISPATCH, None)`（`sw_part._empty_callout()`）；**传 `None` 得到 `'类型不匹配'`（`0x80028CA0`）**，而该错误**看不出是 Callout 的问题**。⇒ 这是已知事实 12 的一个**具体后果**，2026-10-01 又踩一次（差点据此得出「选择不可能」的错误结论）| 本机实测（同一探针的失败版 vs 修好版）|
| 34 | **`sw_sheet_metal.py` 的 6 个创建入口真机只有 2 个能跑**（2026-10-01，SW 2026 SP4.1）：✓ `create_base_flange`（真建出特征：特征树出现「钣金6 / 基体-法兰1 / 平展型式6」）· ✓ `sheet_metal_evidence`（读回 `thickness_m=0.002`、`has_base_flange=True`）；✗ `create_one_bend`（`CreateDefinition(33)` 返回 None）· ✗ `create_draft`（`CreateDefinition(3)` 返回 None）· ✗ `create_edge_flange`（设 `ReverseDirection` 报 `Property ... can not be set`）· ✗ `create_gusset`（设 `Thickness` 报同款）。**⇒ 该模块原本自述「未在本机实测」，现在是「测了，4/6 不行」**。**⚠ 真因已查明三条（2026-10-01，见事实 43）**：`create_one_bend` 的 `swFmOneBend(33)` **不在 `CreateDefinition` 接受的 35 个常量里**（已改用 `swFmSketchBend(35)`，报错从 `CreateDefinition(33) 返回 None` **前推到** `CreateFeature(35) 创建失败`）；`create_draft` 的 `swFmDraft(3)` **同样不在名单里**；其余三条现在**卡在同一层** `CreateFeature(N)`。**⚠ 2026-10-01 又查明一层**：官方 `ISMGussetFeatureData` 的 Remarks 把创建写成 **4 步**，而模块**整步跳过了第 3 步**（`ProfileDimensionScheme`）——**已补上**（含官方明写「必须」的 `UseOffset`/`UseAngleDimForProfile`），真机**属性层 8/8 读回成功**，但 `CreateFeature(118)` **仍 None** ⇒ **失败原因不在属性层**，而在步骤 2 的**预选**（夹具是平板、无折弯）。见事实 44。**⚠ 这 4 个已作为 MCP 工具暴露（T-011 接线），工具描述里已标注 `*** NOT USABLE ON THE TEST MACHINE ***`**，并有 `require_verified()` 守卫 | 证据脚本 `D:\AI\SW\probe_sheet_metal_e2e.py`；状态表 `scripts/sw_sheet_metal.py::SHEET_METAL_RUNTIME_STATUS` |
| 35 | **来源块覆盖范围不足有两种面孔，都会表现为同一句含混报错**（本会话踩 **5** 次）：① 常量/导入夹在来源块与目标 `def` 之间 ⇒ `_extend_to_code` 止于常量；② **一个来源块后面有多个代码单元** ⇒ 默认只覆盖第一个。修法：① 把常量挪到**块之前**；② 在块里加**裸的** `# 覆盖: 后续同级定义`（或 `# 覆盖: 全文件`）。**⚠ 那行加 markdown 粗体会让正则 `r"覆盖\s*[:：]\s*后续同级定义"` 的 `\s*` 匹配不到 `**`** | `scripts/check_provenance.py` 现在**直接打印这两条原因 + 修法**（2026-10-01 加，已实测会触发）|
| 36 | **同名接口分属不同族 —— 用错接口 = 对象对任何成员都没反应**：官方类型表里 Gusset 有**两个** —— `ISMGussetFeatureData`（`category: Feature Interfaces/**Sheet Metal**`，28 属性）与 `IGussetFeatureData`（`category: .../**Weldments**`，19 成员），**共有成员只有 3 个**（`AccessSelections` / `ProfileType` / `ReleaseSelectionAccess`）。`swFmSMGusset` 描述明写 "**Sheet metal** gusset" ⇒ 必须用 SM 那个。**用错时真机表现：连**读**都读不到**（`read Thickness → ✗ <unknown>.Thickness`），写报 `Property '<unknown>.X' can not be set` —— **看起来像「属性只读」，实际是「接口不对」**。⚠ **`scripts/check_member_names.py` 抓不到这一类**（它判「名字在**某个**接口里存在」，不判「在**这个**接口里存在」）| 官方类型表 `C:\swapi\types\ISMGussetFeatureData\` vs `\IGussetFeatureData\`；真机证据 `D:\AI\SW\probe_property_binding.py` |
| 37 | **查「某个东西在不在」必须查**两个仓库** —— 只查一处得出的「不存在」，是「我没找到」的另一种说法**。2026-10-01 实例：我在文档里写「`fix_bare_outparams.py` **不存在**」，实际它在**工作区根** `D:\AI\SW\fix_bare_outparams.py`（5 KB，2026-10-01 03:17），配套的 `find_bare_outparam_sites.py` 也在（4.2 KB，03:16）。**我只在代码副本 `C:\swprojects\sw-skill-fork\` 里找过。** ⚠ 工作区根有 ~600 个散落的历史 `.py` 脚本 | `Get-ChildItem` 两个根目录对比；结论「不存在」前必须先证伪 |
| 38 | **工作区根 `D:\AI\SW\` 里有一个 `mcp.py`，会遮蔽真的 `mcp` 包**：Python 把**脚本所在目录**放在 `sys.path[0]` ⇒ 任何从该目录启动的 Python 进程里 `import mcp` 拿到的是**那个脚本** ⇒ `ModuleNotFoundError: No module named 'mcp.server'; 'mcp' is not a package` ⇒ **`mcp-server/server.py` 在该 CWD 下根本 import 不了**。**⚠ 该错误信息指向不了真因**（看不出是「被本地同名文件遮蔽」）。⇒ 跑该 server 或其 import 测试时，**必须先把脚本目录从 `sys.path` 里剔除**（或换 CWD 且确认 `sys.path[0]` 不是它）。已做成可查项 `scripts/check_workspace_shadowing.py`（**不自动删**工作区脚本）| 实测撞上；证据 `D:\AI\SW\probe_wired_tools_e2e.py` 的 `sys.path` 清理段 |
| 39 | **本仓库所有 MCP 工具的入参形状是 `{"params": {...}}`**（不是扁平参数）：工具函数签名一律 `def tool(params: XxxInput) -> str` ⇒ FastMCP 生成的 schema 是 `{"properties": {"params": {...}}, "required": ["params"]}`。**上游 45 个与接线进来的 20 个在这一层**完全同形**（`cadstudio_resolve_backend` 对照过）。**⇒ 用 `Tool.run()` 直接调工具时必须传 `{"params": {...}}`**，传扁平 `{...}` 会得 `params Field required` | `tests/test_server_wiring.py` + 实测（`probe_wired_tools_e2e.py`）|
| 40 | **`IModeler.Create*Surface` 的返回值**不可靠** —— 不是「有些能有些不能」，而是**同一个调用跨次也会变****（2026-10-01，**四轮探针**）：第 13 轮 `CreateCylindricalSurface` **成功**；第 26 轮 `spherical`/`toroidal` 成、`cylindrical`/`conical` 返回 `None`；第 27 轮受控实验只 `axis=(1,0,0)` 成（**排除了顺序与单例状态**）且 `*2` 全 `None`。**官方**：该族 18 个里 **4 个标 `Obsolete`**（`CreateConicalSurface` / `CreateCylindricalSurface` / `CreatePlanarSurface` / `CreateSphericalSurface`），**各有 `*2` 后继、且 `*2` 运行期可达**（它多一个 `RefDirection`）——**但按正确 arity 调 `*2` 仍然返回 `None` ⇒ 换一代解决不了**。**⇒ 修的只能是「让失败可见」**：`sw_surface._invoke` 现在对 `None` **抛带原因的 `RuntimeError`**。⚠ 一个**存在但没人用**的守卫（`require_runtime_available` 曾如此）与没有守卫等价，**且更糟**（让人以为防住了）—— 2026-10-01 才接进 13 个公开包装器 | 证据 `D:\AI\SW\probe_surface2_correct_arity.py` / `probe_cyl_order_vs_axis.py` / `probe_cyl_none_matrix.py` / `probe_surface_generations.py`；`scripts/sw_surface.py` 的 `_invoke` / `IMODELER_RUNTIME_*` |
| 41 | **验收判据 A2 的真实缺口是「29 条里 28 条**未被分类**」，而不是「28 条缺 provenance」** —— 两者差别很大。`capabilities.yaml`（44.8 KB，**内容是 JSON、扩展名是 yaml**）29 条里只有 `mold_tools` 带 `provenance`；而 schema **没有 `source` / `origin` 字段** ⇒ **无法区分「并入来的」与「本项目自研的」**（例：`requirements_planning` 的 backend 是 `local-agent`，显然是自研，却没有地方这么说）。**🚫 正解不是给 28 条编造 provenance** —— `THIRD-PARTY-NOTICES.md` 自己写着「把未并入的东西写成已并入，是**归属造假**，比遗漏更严重」。⇒ 正解是**给每条加一个 `source` 标记**（`original` / `merged`），再由人逐条确证。**A4 已达标**（29/29 level 合法；22/22 verified 有 evidence）。⚠ 另一条：`100%` 写在 `%`-格式串里会让后面的 `%d`+中文解码错 ⇒ 必须写 `100%%` | `scripts/audit_acceptance_criteria.py`（可重跑的枚举命令）；`git ls-files --error-unmatch THIRD-PARTY-NOTICES.md`（确认它**已入库**）|**⚠ 2026-10-01 更正（查了门禁之后）**：那条「28 条未被分类」的结论**前提不全** —— A2 原文的「并入条目」有**两种读法**，答案相反：**来源条目**读法下 `tools/union-sources.json` **4/4 完整**（repo/license/declared_verified/note 四项齐全）⇒ **满足**；**能力条目**读法下 `capabilities[].provenance` **1/29** ⇒ 不满足。**而门禁（`check_union_conventions.py` L155/L189）实现的是**窄读法**：「`provenance` 的触发条件**只有** `source_verified`」——**而本仓库 `source_verified` 条目数为 0**（level 分布 verified=22 / stitched=6 / not_implemented=1）⇒ **门禁层面零要求，所以它一直绿**。**⇒ 正解不是给 29 条硬编分类，而是**消解这个措辞歧义**。**★ 另一层认识：`level: verified` 说的是「**有我们自己的运行证据**」，**不是**「代码是我们写的」⇒ **上游代码经我们真机验证后标 verified 是**正确**的**；A2 关心的「出处」由**来源级** provenance 承载，**两条线不该混**。工具 `tools/propose_capability_sources.py` 仍有用（它给出的 **21/29 有证据分类**可作人工复核的起点，且它**纠正了**我对 `sw_weldment.py`/`sw_sheet_metal.py` 的误认）
| 42 | **「成员交集为空」这个判据**抓不到「整体用错接口」那一类** —— **种负例实验证伪**（2026-10-01）：把 `create_gusset` 的 4 个成员名从 SM 那套（`GussetThickness`/`ProfileHeightDim`/…）换回**焊件**那套（`Thickness`/`ProfileDistance1`/…，即已知事实 36 的原 bug 原样）后，`check_interface_member_ownership.py` **仍然报 PASS**。**原理**：原 bug 那套名字**互相自洽**（全属 `IGussetFeatureData`）⇒ **代码并不自相矛盾**，只是**对上下文用错了接口**。⇒ 「交集为空」只能抓「混用**互斥**接口的成员」。**⚠ 另有假阳性风险**：`BendRadius`/`Path`/`Profile`/`Thickness` 这类**通用名**遍布多个接口 ⇒ 「交集非空」常是**蒙对的**。**⇒ 要抓那一类必须有 `CONST → 接口` 映射表**；**可核验**的做法是从官方 `swFeatureNameID_e` 的枚举描述里取，**不要手写**（手写错就是新的错误来源）。⚠ 该工具因此**按「诊断」定位**：退出码只反映「检查量不足」，**不冒充门禁** | `scripts/check_interface_member_ownership.py`（文档串与输出里写出了否定结果）；`C:\swapi\types\<接口>\<成员>.md`（546 个接口 / 8238 个成员，目录结构即归属表）|**★ 2026-10-01 反转**：那张映射表**已经做出来并装上了** —— `scripts/check_interface_member_ownership.py` 现在用「**成员必须在**期望的**接口上**」作判据（期望接口由 `CreateDefinition.md` 的官方括注 × 接口 `_overview.md` 的 Description **文本匹配**得到，第 30 轮：20 唯一 / 4 歧义 / 11 未映射）。**同一个负例**（把 `create_gusset` 的成员名换回焊件那套）：第 29 轮**报 PASS**、**第 38 轮精确报出**（点名调用点 L591 ⇒ 期望 `ISMGussetFeatureData`，并列出 `Thickness`/`ProfileDistance1`/`ProfileDistance2`/`ProfileAngle` 四个不在该接口上的成员）。⚠ 它仍是**诊断**（映射表有歧义/未映射的洞 ⇒ 覆盖不全的门禁会让人以为防住了）。
| 43 | **`CreateDefinition` 只接受官方列出的 **35 个**常量 —— 用它之前必须查那张名单**；`swFmOneBend(33)` / `swFmDraft(3)` 都是**合法枚举成员但不是合法类型** （⇒ 返回 `None` **是应然的**，不是 COM/权限问题）。**「一个折弯」的正确入口是 `swFmSketchBend(35)`**，接口 `ISketchedBendFeatureData` （16 个成员：`BendAngle`/`BendRadius`/`ReverseDirection`/`UseDefaultBendRadius`/`UseDefaultBendAllowance`/`SetFixedFace`/`GetFixedFace`/…；**`FixedFace`/`BendLine` 是**方法**不是属性**）。**⚠ 两套官方源在这一族**分工不同****：`C:\swapi\enums\swFeatureNameID_e.md` 的「Value」列**装的是描述、不是数值** ⇒ **数值必须去反射** `D:\AI\SW\_raw\**\enum_values_sldworks.txt`（130 个成员）。★ **可核验的 `CONST → 接口` 映射**（不手写）：`CreateDefinition.md` 的括注 × 接口 `_overview.md` 的 Description ⇒ 20 条唯一命中 / 4 歧义 / 11 未映射（`D:\AI\SW\gen_const_iface_map.py`） | `C:\swapi\types\IFeatureManager\CreateDefinition.md`（35 个常量）；`enum_values_sldworks.txt`；`gen_const_iface_map.py`；`probe_sketch_bend_entry.py` |**★ 2026-10-01 消歧完成**：4 条歧义**全部解掉** ⇒ **24 唯一命中 / 0 歧义 / 11 未映射**。三条规则**都从官方描述读出**：① **含 `group` 者是子项**（两处 `*GroupData` 的描述都写着 "feature group" / "feature's cut-extrude face group"）⇒ 排除；② 剩下的里**含 `feature` 者优先**（`ICornerReliefFeatureData` "…relief **feature data**" vs `ISMCornerReliefData` "…relief **data**"）；③ ⚠ **兜底（弱启发式）**：描述**比常量括注多出的词最少**者优先 —— `swFmLibraryFeature (library)` ⇒ `ILibraryFeatureData`（+2 词）胜过 `ILibraryFormToolFeatureData`（+4 词）。**③ 已在代码注释与提交信息里标注为弱证据。****★★ 2026-10-01 再进一步（轮 41）**：把**已逐条读官方描述确认**的 7 条写进显式的 `MANUAL_MAP` ⇒ **31 唯一（**自动 24 + 人工确证 7**）/ 0 歧义 / 4 未映射**（原 24/0/11）。**⚠ 与轮 40 那次失败的关键区别：这次是**人工表、每条在代码里注明依据**，不是启发式硬凑**（轮 40 用「名字回退」连续改 6 版都不对，已回退并记进已知事实 53）。三条设计约束：① **绝不覆盖**自动结果（只补空）；② **输出分开报**（「自动 %d + 人工确证 %d」）；③ **没有依据的不许进来**（未确证的 4 条留在 `unmapped`，按铁律 5 写「查不到」）。
| 44 | **FeatureData 接口的官方 Remarks 往往把创建写成**编号步骤** —— **必须逐步走完，跳过任何一步都会让 `CreateFeature` 返回 None****。实例（2026-10-01）：`ISMGussetFeatureData` 的 Remarks 是 4 步，第 3 步**头一句**就是「Specify `ProfileDimensionScheme`」，而 `sw_sheet_metal.create_gusset` **从未设过它**（只设了 4 个尺寸属性）⇒ **已补上**（含官方 `UseOffset.md` 明写「若未预选参照点则**必须**置 true」、`UseAngleDimForProfile.md` 明写「**valid only if ProfileDimensionScheme is set to 1**」）。**★ 但真机显示：属性层 8/8 读回成功、`CreateFeature(118)` 仍 None** ⇒ **「属性设对了」与「特征建成了」是两件事，必须分开取证** （`probe_gusset_props_readback.py` 就是为此写的）。剩余阻塞在**步骤 2 的预选**（官方要求「一个折弯的两个平面」，而夹具是平板）。⚠ 另一条：官方在 scheme=1 下给了**两种互斥的标注方案**（「两条腿」用 `ProfileHeightDim`+`UseAngleDimForProfile=false`；「d1 腿+夹角」用 `ProfileAngleDim`+`UseAngleDimForProfile=true`）⇒ **无条件置 true 而角度为 0 是自相矛盾的**，必须**按有没有角度二选一** | `C:\swapi\types\ISMGussetFeatureData\_overview.md`（Remarks 4 步）+ `ProfileDimensionScheme.md` / `UseAngleDimForProfile.md` / `UseOffset.md`；`D:\AI\SW\probe_gusset_props_readback.py` |
| 45 | **造折弯卡在 `SetFixedFace` 的 `EdgeArray` 参数上**（2026-10-01 实测）：`ISketchedBendFeatureData::SetFixedFace(X, Y, Z, EdgeArray)` 的第 4 个参数是 `Object` 型 —— 传 `None` 得到 **`类型不匹配`（`0x80028CA0`）**，**与已知事实 33（`SelectByID2` 的 `Callout` 传 `None`）是同一个错误类**。**官方**：`GetFixedFace(out X, out Y, out Z)` 的说明明写「the location is a point on the fixed face, but **in the space of the sketch** used to define the sketched-bend feature. Thus, **the z location is always 0**」⇒ **固定面的点要用**草图坐标系**给**。**四种属性组合实测全失败**（原样 / +`UseGaugeTable=False` / +`UseDefaultBendRadius=False` / +`SetFixedFace`）⇒ **缺的很可能是 `SetFixedFace`**。⚠ 另：官方 `UseGaugeTable` 明写「**must be set to false in order to set `BendRadius`**」—— 本模块无条件设 `BendRadius` 却**从不设 `UseGaugeTable`** | `C:\swapi\types\ISketchedBendFeatureData\SetFixedFace.md` / `GetFixedFace.md` / `UseGaugeTable.md`；`D:\AI\SW\probe_bend_then_gusset.py` |
| 46 | **中文界面的文档里，草图名是 `草图N` 而不是 `SketchN`** —— 2026-10-01 实测：在面上画线后，特征树里的草图叫 **`草图6`**；我的探针猜 `Sketch2` ⇒ 报「无法选择草图」，**看起来像「草图没建成」，实际是名字猜错**。证据：`SelectByID2("草图6", "SKETCH", …)` **返回 True**。**⇒ 与已知事实 9（基准面名随 UI 语言变）是同一类问题，但主体是**草图**。**⚠ 沿本仓库既有做法：用 `sw_part._ensure_sketch_selected` 的候选名表，并在**失败信息里列出实际存在的草图名**，而不是只报「无法选择」。⚠ 另：本项目**没有**递归遍历特征树的现成工具；**手写递归时 `GetFirstSubFeature` 会环回**（同名特征在子树上重现）⇒ **必须用与深度无关的 visited 键 + 深度上限** | `probe_bend_then_gusset.py` 的输出；`sw_part._ensure_sketch_selected` |
| 47 | **`ISketchedBendFeatureData` 的 `AccessSelections` / `SetFixedFace` 在 pywin32 迟到绑定下**不可调用** —— 这是**架构性限制**，不是参数没找对**（2026-10-01，**两轮 20+ 种形态**实测）：`SetFixedFace(X,Y,Z,EdgeArray)` 的**七种数组包装 × 两个重载**全部报 `类型不匹配`（位置 1 或 4）；`AccessSelections(model, None)` 报 `类型不匹配`（位置 2）、改传 `VARIANT(VT_DISPATCH, None)` 则报 **`服务器出现意外情况`（`0x80010105`）**——**与已知事实 28 的 `CreateBsplineSurface` 同一个错误码**。**⇒ 这与 `capabilities.yaml` 里**早已记录**的后端限制吻合**：「**不能调用官方标记为仅进程内非托管 C++ 的指针接口**」；反射里那对 **`IAccessSelections` / `IAccessSelections2`** 正是那种 `I` 前缀的**指针变体**。**⇒ 结论：`create_one_bend` / `create_edge_flange` / `create_gusset` 三条在 pywin32 这条后端上到不了「建成」**（除非换 `comtypes` 或进程内 C++ 后端）。⚠ **不要再用「换个参数试试」的方式继续试** —— 20+ 种已穷尽 | `D:\AI\SW\probe_setfixedface_forms.py` / `probe_setfixedface_overloads.py` / `probe_access_selections.py`；`capabilities.yaml` 的 `backend_catalog` 限制段 |
| 48 | **长文本不要内联进 Python 源码** —— 本会话在这一件事上**踩了 6 次**：文档串里嵌同类引号 / 补丁脚本插真换行 / `%`-格式串里的 `100%` / `\A` 之类坏转义 / 状态表字符串断行 / 以及 `write` 工具写的 Python 里字符串被**真实换行**截断（`SyntaxError: unterminated string literal`，**连踩两次**）。⚠ 最坑的一次：**脚本语法错 ⇒ 内容没写进去，而外面的 `git add -A && commit` 照跑**⇒ 产生「提交信息说改了文档、实际只提交了那个坏脚本」的**假提交**（2026-10-01 连出两次）。**⇒ 定则两条：① 长内容先写成**独立文件**（`.md`），再用最短脚本搬运；② 批量脚本跑完**必须核对落盘**（`grep` 一下目标文件），**不能只看脚本的 stdout**。** | `D:\AI\SW\_t011_section28.md`（正确做法）；`doc_fact47.py`（错误做法的两次失败） |
| 49 | **`sw_weldment.py` / `sw_sheet_metal.py` **是上游文件**，不是我们新增的** —— 硬证据：`git cat-file -e origin/main:scripts/sw_weldment.py` **通过**。⚠ **我此前在文档与叙述里把这两个当成「我们新增的」（多次），那是错的。**⇒ 影响：AGENTS.md 事实 34 那句「**该模块**原本自述未在本机实测」的**主语是上游**；`capabilities[sheet_metal]` / `[weldments]` 的 `source` 应为 **upstream**。**⇒ 教训：判断「某文件是不是我们的」必须跑 `git cat-file -e origin/main:<path>`，不能靠印象**（与已知事实 37 的「查两处才敢说不存在」同源，方向相反）。工具：`tools/propose_capability_sources.py`（该工具正是靠这条硬证据，**并且它纠正了我**）| `git cat-file -e origin/main:scripts/sw_<X>.py`；`D:\AI\SW\probe_*` 系列的对照 |
| 50 | **`python x.py \| Select-Object ...` 之后读 `$LASTEXITCODE` **不可靠**** —— 2026-10-01 实测：同一条命令，接管道时读到 **0**、不接管道（重定向到文件）时读到 **1**。**⇒ 正确做法二选一：① `python x.py > out.txt 2>&1` 再读 `$LASTEXITCODE`；② `$o = python x.py 2>&1; $code = $LASTEXITCODE`（**赋值，不接管道**）。**⚠ 本会话多轮用的是 ②（可靠）；只在本轮那一处用了 ① 的错误形式，**一度误以为门禁是红的**（实际 6 项全 PASS、退出码 0）。**⇒ 教训：判「门禁绿不绿」时，先确认**退出码的读法本身**是可靠的。** | `D:\AI\SW\AGENTS.md` 已知事实 7 那类「返回值不可信」在本机 shell 层的同类；证据：同一条 `check_union_conventions.py` 两种读法给出不同退出码 |
| 51 | **一个「抓不到目标类别」的检查，往往不是判据错，而是**分析范围**与代码的**组织单元**不匹配** —— 2026-10-01 在第 38 轮与第 29 轮**各踩一次同一处**：用 `WINDOW = 400` 的**行窗口**去收集 `data.X` 的用法，而 `data` 这个变量名在**多个 `_apply(data)` 嵌套函数**里复用 ⇒ 把**别的特征**的成员也算了进来（实测：base flange 那个站点把 edge flange / draft / **gusset** 的成员全吞了，**6 个假阳性**）。**⇒ 范围必须贴合代码的**组织单元**（所在函数）。**⚠ 同轮的另两处：① **形参驱动的站点只解析了第一个调用点** ⇒ 5 个站点只检查了 1 个；② 实参文本是 `int(fm_type`（**带 `int(...)` 包装**），而形参名查询直接拿它去查 ⇒ 一个都解析不到。**⇒ 教训：静态分析先问「这段代码的**组织单元**是什么」，再决定收集范围。** | `scripts/check_interface_member_ownership.py` 的 `enclosing_range` / `calls_of` / `param_index`；第 29 轮的同一处错误与第 38 轮的反转 |
| 52 | **官方接口描述里藏着**判别类型的线索**，比接口名更可靠** —— 2026-10-01 用它把 `CONST → 接口` 映射表的 **4 条歧义全部消解**（20→**24** 唯一命中、0 歧义）：① **`group` 是子项的标志** —— `ISMNormalCutGroupData` 的描述是 "…a normal cut **feature's cut-extrude face group**"、`ITabAndSlotGroupData` 是 "…a tab and slot **feature group**" ⇒ **它们不是 `CreateDefinition` 返回的那个类型**；② **`feature` 的有无是层级标志** —— `ICornerReliefFeatureData` 是 "…relief **feature data**"、`ISMCornerReliefData` 是 "…relief **data**"（**少了 feature**）⇒ 前者才是。⚠ **但有一处只能靠弱启发式**：`swFmLibraryFeature` 的两个候选**都**含 `feature`，最后按「描述比常量括注**多出的词最少**者优先」选了 `ILibraryFeatureData`（+2 词 vs +4 词）—— **已在代码里标注为弱证据**。**⇒ 教训：先看**官方 prose**，再看名字；prose 分不开的，明确标成弱证据而不是假装确定。** | `C:\swapi\types\<接口>\_overview.md` 的 `## Description` 段；`scripts/check_interface_member_ownership.py` 的 `build_map()` |
| 53 | **「调到看起来对」的识别信号：同一个启发式**连续修补 ≥3 次**还没稳定，就该停下回退** —— 2026-10-01 实例：为攻掉 `CONST → 接口` 映射表的 11 条未映射，我给检查器加「名字回退」，**连续改了 6 版**（30/4/1 ⇒ 词重叠过滤无效 ⇒ 末词过滤仍错 ⇒ 去首词变体跌到 29/0/**6** ⇒ 改词级匹配回到 24/0/11 ⇒ 改名字子串又错成 29/6/0），**每版都在同一处打补丁**，最后**回退**到 `e4794cc` 的 **24/0/11**。**⇒ 根因不是「还没调对」**：① `swFmSweepThread` 那类（"sweep thread" 是**螺纹**）**需要领域知识**，文本匹配永远得不到；② 名字匹配的**假阳性**（`swFmSolidToSheetMetal` ⇒ `ISheetMetalFeatureData`、`swFmMirrorComponent` ⇒ `IComponent2`）**压不住**。**⇒ 正解：把证据留在**文档**里（`docs/T-040-unmapped-constants-evidence.md`，11 条逐条带官方依据），**不接进工具**。**⇒ 定则：启发式需要连续 ≥3 次修补才「看起来对」时，回退 + 记证据，不要继续调。** | `docs/T-040-unmapped-constants-evidence.md`；`git log --oneline scripts/check_interface_member_ownership.py`（含回退）；已知事实 52（名字是弱信号）与 51（分析范围要贴合组织单元）|
| 54 | **来源块必须是 `def` **之前**的顶层 `#` 注释块 —— 写在 docstring 里**不算**** —— 2026-10-01 实测（轮 42）：我给 `release_check.py` 加了一个探针函数，把 `# ── 来源 ──` 块**写进函数的 docstring**（看起来更内聚）⇒ `scripts/check_provenance.py` 报「**25 行新增代码没有可追溯的出处**」，**而它报的行号是**后面** `run_release_check` 里的行**（因为插入把原来的覆盖链断开了）⇒ **错误信息指向不了真因**。**⇒ 三条：① 来源块放目标的 `def` **之前**；② docstring 里的块**不被认**；③ 覆盖多个同级定义靠 `# 覆盖: 后续同级定义`。**⚠ 与已知事实 35（覆盖范围不足的两种面孔）是**同一族但不同面** —— 35 说的是**范围**不够，本条说的是**位置**不对。★ 附：同一轮还踩了一处**判据误报** —— 用 `"[HIT]" in output` 判检查结果，而该脚本的**说明文字里**就写着「报 `[HIT]` 时值得看」⇒ **明明 `[OK]` 却报 `hits`**。**⇒ 判「输出里有没有某个标记」一律**按行首**匹配，不用 `in`。** | `scripts/release_check.py` 的 `_run_interface_ownership_probe`；`scripts/check_provenance.py`（`_extend_to_code` 的调用链）；已知事实 35 |
| 55 | **改了任何**运行时文件**之后必须重跑 `python scripts/sync_bundled_skill.py`** —— `release_check.py` 会比「仓库根的 Skill」与「桌面内嵌快照」（`apps/workbench-ui/src-tauri/resources/skill`），不一致就拦发布。**⚠ 而该快照在 `.gitignore:23` 里 ⇒ 它是**构建产物**、`git status` **看不见它** ⇒ **这条纪律不会被 git 提醒你**。**★ 2026-10-01（轮 43）实测：修掉了一个**基线失败** `test_release_check_passes_current_tree`（回归从 **6 failed / 857 passed** 变成 **5 failed / 858 passed**）—— **真因是那一步构建没跑，不是代码 bug**；跑一次 `sync_bundled_skill.py`（276 个文件）即通过，且 `git status` **仍然干净**。★ 同轮还把报错改成**可执行**的：原来只报 `桌面内嵌 Skill 与根 Skill 不一致: <bundled-skill-missing>`（**看不出该怎么办**），现在**分开报两种情况**并各给出**可直接跑的命令**；**并且验证过它是对的** —— 改完 `release_check.py` 再跑，它立刻报 `与根 Skill 不一致: scripts/release_check.py`（**检查在尽职**），而提示给的命令正是解法。 | `scripts/sync_bundled_skill.py`；`scripts/release_check.py` 的 `find_bundled_skill_drift`；`.gitignore:23` |
| 56 | **官方有时在接口自己的 `_overview.md` 里**逐字写死** `CreateDefinition` 的 Type —— 那是**官方断言**，比「拿括注去匹配描述」硬得多** —— 2026-10-01（轮 44）实例（`ISimpleFilletFeatureData2`）："To create a simple fillet feature: 1. Call [[IFeatureManager::CreateDefinition]], passing Type = [[swFeatureNameID_e]].**swFmFillet**, to create an instance of **ISimpleFilletFeatureData2**." **⇒ 全库扫出 5 条这样被点名的常量**（`swFmFillet` / `swFmFormToolInstance` / `swFmNormalCut` / `swFmRefCurve` / `swFmSolidToSheetMetal`），接成 `officially_named()` 作为**优先级最高**的来源：**官方点名（断言）> 文本匹配（对 prose 的推断）> `MANUAL_MAP`（人工确证）**，并加守卫**官方条不得被覆盖**。**⇒ 覆盖率 24/0/11（轮 39）→ 34/0/1**（35 个常量里只剩 `swFmRefSurface` 没答案）。★ **可信度交叉验证**：其中 3 条与**别的来源独立得出同一答案** ⇒ **3/3 一致**；★ 一条（`swFmFormToolInstance`）**从人工表「升级」到官方点名** —— 依据从「我的确证」变成「官方断言」。⚠ **覆盖窄**（35 条里只有 5 条），但**可靠**。 | `C:\swapi\types\<接口>\_overview.md`；`scripts/check_interface_member_ownership.py` 的 `officially_named()` |
| 57 | **一个「一直是绿的」测试，可能只是**每次跑的时候环境恰好满足** —— 不是它真的在测** —— 2026-10-01（轮 44）实例：`tests/test_tool_specs_batch4.py` 的文档串承诺「**不依赖 `mcp` 库、**不连 SolidWorks**」，但它 2 个测试的 spec `derived_args` **碰了活 COM**（`_swept_refs_and_spec` 调 `resolve_entity(model, '__current_selection__', "EDGE")` ⇒ 要求界面上**已选中一条边**）。**⇒ 干净机器上必然失败**（`RuntimeError: 没有活动文档`）；**它以前之所以绿，是因为我探测时恰好选中过边** ⇒ **纯属巧合**（`git stash` 掉我的改动后仍失败，证明与我的改动无关）。**⇒ 修法加了 `_derived_args_or_skip()`：只把「碰 COM」那一类转成**带原因 skip**（契约违约**可见**），别的异常照旧抛出。**⚠ **推论**：本仓库的回归基线**依赖 SolidWorks 的文档/选择状态** ⇒ 记基线时必须**同时记 SolidWorks 状态**，否则下轮的「多了几个失败」会被误判成代码问题。 | `tests/test_tool_specs_batch4.py` 的 `_derived_args_or_skip`；`mcp-server/tool_specs_batch4.py` 的 `_swept_refs_and_spec`；`scripts/sw_selection_spec.py` 的 `EntitySelectionError` |

```
              会话  参考  草图  尺寸  零件  曲面  钣金  焊件  模具  装配  工程图  检查  仿真  外观  宏  高级
Eduardof0nt    14    3    26    6    23   11   10    5     3    13    18    11    3    10    4    0
andrewbartels1 22    3    15    2    11    0    0    0     0     7    18     3    0     1   22    0
vespo92        10    0    16    6     3    1    1    0     0     4    15     7    1     3   21    1
Slacker-LLC     7    3    20    2    13    0    0    0     0     3    17     6    0     2    0    0
本仓库           7    0     0    1     1    2    0    0     0     6     3     2    2     4    1    3
                                                                                               ↑ 唯一独有
```

## 七、Git 规则

```
代码工作副本：C:\swprojects\sw-skill-fork\     唯一改代码的地方，已是 shallow clone
  origin : https://github.com/wzyn20051216/solidworks-automation-skill   ← 来源与对照
  MIT · 上游是来源之一，不是本仓库的历史基底
工作区仓库：  D:\AI\SW\                        git 仓库（提交 1f86c5d 起），只放产物
```

`origin` 指向上游，语义是「来源与对照」：用 `git diff origin/main --stat` 看我们相对上游的增量（当前 100 新增 / 13 改过）。自建仓库的目标远端由用户给定后再 `git remote add <name> <url>`；只有 origin 时 `git push` 会误推上游仓库。

- 三条红线（任何模式都不豁免）：删数据 / 删仓库 / 强推；对外发布；只有用户能提供的东西（凭据、业务口径）。
- 推送前置义务：并入了 Apache-2.0 来源（`Slacker-LLC/solidworks-mcp`）⇒ 推送任何远端都要带 `THIRD-PARTY-NOTICES.md`（含 `Copyright 2026 JIALE LIU` 与改动文件清单），该文件**已存在**；MIT 来源保留版权声明。这条对上游与四家一体适用。
- 分支策略：`main` 与上游保持一致便于 rebase；每个功能域一个分支（`feat/simulation`、`feat/drawing-views` …）；每个 PR 一句话写清「补了哪个官方接口族，来源是哪个项目 / 哪套文档」。

| 动作 | 是否需要用户批准 |
|---|---|
| 本地 clone / 分支 / commit / `git add` / `git remote add\|remove` | 不需要 |
| 改文件、跑 `compileall`、跑 `sw_know.py` / `swdoc.ps1` | 不需要 |
| 建自建仓库、加目标远端（`gh repo create` / 改 origin） | 要先批准 |
| `git push`（任何远端） | 要先批准 |
| 提 PR / 发布 release | 要先批准 |

## 八、智能体团队分工

角色定义、工具限制、派活维度与 `write_scopes` 登记要求见 [docs/team-roles.md](docs/team-roles.md)。

## 九、停止条件（遇到就停，不要自行拍板）

1. 两套官方源都查不到某接口，且 `sw_know suggest` 也给不出合理近似 → 先确认该接口是否存在，再写。
2. 某个缺口在 21 个项目里都找不到可移植实现，且官方文档也没有示例 → 标为「无法缝合」，写进报告的「仍然空缺」段，不要硬编。
3. 需要碰 AGPL / GPL / 无许可 / 全版权保留 的代码才能补齐 → 停下，报告「需用户提供授权或接受缺口」。
4. 需要 `git push` / 建目标远端仓库 / 提 PR → 停下，等批准。
5. 发现实际仓库结构与铁律 3 的顶层白名单不符 → 停下报告，以实际仓库为准并更新本文件。
6. 来源没有测试、我们又无法本机实测 → 标 `stitched`，不得标 `verified`。

## 十、本地资源速查

常用路径 / 脚本 / 命令的速查表见 [docs/local-resources.md](docs/local-resources.md)。

## 十一、开工第一句话模板

开工第一句话模板见 [docs/kickoff-template.md](docs/kickoff-template.md)。
