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
| A2 | 每个并入条目带 `provenance`（`owner/repo` 全名 + 许可 + 文件 + 来源验证状态） | grep 抽查 10 条，100% 命中 |
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

Apache-2.0 的 NOTICE 义务跟着分发走：一旦入库，推送任何远端时都要带 `THIRD-PARTY-NOTICES.md` —— 该文件尚未创建；MIT 来源（上游与 `Eduardof0nt` / `andrewbartels1` / `vespo92`）保留各自的版权声明。完整许可判定表与来源清单见 [docs/sources.md](docs/sources.md)。

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
- `Slacker-LLC` 是 Apache-2.0：可抄，但要保留 `NOTICE`（`Copyright 2026 JIALE LIU`）并声明改动了哪些文件；推送任何远端时产生硬性义务，`THIRD-PARTY-NOTICES.md` 尚未创建。

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
| 34 | **`sw_sheet_metal.py` 的 6 个创建入口真机只有 2 个能跑**（2026-10-01，SW 2026 SP4.1）：✓ `create_base_flange`（真建出特征：特征树出现「钣金6 / 基体-法兰1 / 平展型式6」）· ✓ `sheet_metal_evidence`（读回 `thickness_m=0.002`、`has_base_flange=True`）；✗ `create_one_bend`（`CreateDefinition(33)` 返回 None）· ✗ `create_draft`（`CreateDefinition(3)` 返回 None）· ✗ `create_edge_flange`（设 `ReverseDirection` 报 `Property ... can not be set`）· ✗ `create_gusset`（设 `Thickness` 报同款）。**⇒ 该模块原本自述「未在本机实测」，现在是「测了，4/6 不行」**；真因**尚未查明**（是 `swFm` 取值错？FeatureData 属性名错？缺 `AccessSelections`？）。**⚠ 这 4 个已作为 MCP 工具暴露（T-011 接线），工具描述里已标注 `*** NOT USABLE ON THE TEST MACHINE ***`**，并有 `require_verified()` 守卫 | 证据脚本 `D:\AI\SW\probe_sheet_metal_e2e.py`；状态表 `scripts/sw_sheet_metal.py::SHEET_METAL_RUNTIME_STATUS` |
| 35 | **来源块覆盖范围不足有两种面孔，都会表现为同一句含混报错**（本会话踩 **5** 次）：① 常量/导入夹在来源块与目标 `def` 之间 ⇒ `_extend_to_code` 止于常量；② **一个来源块后面有多个代码单元** ⇒ 默认只覆盖第一个。修法：① 把常量挪到**块之前**；② 在块里加**裸的** `# 覆盖: 后续同级定义`（或 `# 覆盖: 全文件`）。**⚠ 那行加 markdown 粗体会让正则 `r"覆盖\s*[:：]\s*后续同级定义"` 的 `\s*` 匹配不到 `**`** | `scripts/check_provenance.py` 现在**直接打印这两条原因 + 修法**（2026-10-01 加，已实测会触发）|
| 37 | **查「某个东西在不在」必须查**两个仓库** —— 只查一处得出的「不存在」，是「我没找到」的另一种说法**。2026-10-01 实例：我在文档里写「`fix_bare_outparams.py` **不存在**」，实际它在**工作区根** `D:\AI\SW\fix_bare_outparams.py`（5 KB，2026-10-01 03:17），配套的 `find_bare_outparam_sites.py` 也在（4.2 KB，03:16）。**我只在代码副本 `C:\swprojects\sw-skill-fork\` 里找过。** ⚠ 工作区根有 ~600 个散落的历史 `.py` 脚本 | `Get-ChildItem` 两个根目录对比；结论「不存在」前必须先证伪 |
| 38 | **工作区根 `D:\AI\SW\` 里有一个 `mcp.py`，会遮蔽真的 `mcp` 包**：Python 把**脚本所在目录**放在 `sys.path[0]` ⇒ 任何从该目录启动的 Python 进程里 `import mcp` 拿到的是**那个脚本** ⇒ `ModuleNotFoundError: No module named 'mcp.server'; 'mcp' is not a package` ⇒ **`mcp-server/server.py` 在该 CWD 下根本 import 不了**。**⚠ 该错误信息指向不了真因**（看不出是「被本地同名文件遮蔽」）。⇒ 跑该 server 或其 import 测试时，**必须先把脚本目录从 `sys.path` 里剔除**（或换 CWD 且确认 `sys.path[0]` 不是它）。已做成可查项 `scripts/check_workspace_shadowing.py`（**不自动删**工作区脚本）| 实测撞上；证据 `D:\AI\SW\probe_wired_tools_e2e.py` 的 `sys.path` 清理段 |
| 39 | **本仓库所有 MCP 工具的入参形状是 `{"params": {...}}`**（不是扁平参数）：工具函数签名一律 `def tool(params: XxxInput) -> str` ⇒ FastMCP 生成的 schema 是 `{"properties": {"params": {...}}, "required": ["params"]}`。**上游 45 个与接线进来的 20 个在这一层**完全同形**（`cadstudio_resolve_backend` 对照过）。**⇒ 用 `Tool.run()` 直接调工具时必须传 `{"params": {...}}`**，传扁平 `{...}` 会得 `params Field required` | `tests/test_server_wiring.py` + 实测（`probe_wired_tools_e2e.py`）|
| 36 | **同名接口分属不同族 —— 用错接口 = 对象对任何成员都没反应**：官方类型表里 Gusset 有**两个** —— `ISMGussetFeatureData`（`category: Feature Interfaces/**Sheet Metal**`，28 属性）与 `IGussetFeatureData`（`category: .../**Weldments**`，19 成员），**共有成员只有 3 个**（`AccessSelections` / `ProfileType` / `ReleaseSelectionAccess`）。`swFmSMGusset` 描述明写 "**Sheet metal** gusset" ⇒ 必须用 SM 那个。**用错时真机表现：连**读**都读不到**（`read Thickness → ✗ <unknown>.Thickness`），写报 `Property '<unknown>.X' can not be set` —— **看起来像「属性只读」，实际是「接口不对」**。⚠ **`scripts/check_member_names.py` 抓不到这一类**（它判「名字在**某个**接口里存在」，不判「在**这个**接口里存在」）| 官方类型表 `C:\swapi\types\ISMGussetFeatureData\` vs `\IGussetFeatureData\`；真机证据 `D:\AI\SW\probe_property_binding.py` |

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
- 推送前置义务：并入了 Apache-2.0 来源（`Slacker-LLC/solidworks-mcp`）⇒ 推送任何远端都要带 `THIRD-PARTY-NOTICES.md`（含 `Copyright 2026 JIALE LIU` 与改动文件清单），该文件尚未创建；MIT 来源保留版权声明。这条对上游与四家一体适用。
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
