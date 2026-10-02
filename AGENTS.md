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
| `D:\AI\SW\docs\` | 本文件里 `docs/...` 相对 AGENTS.md 解析到这里（上游结构 / 素材 / 来源标注 / 团队分工 / 资源速查 / 开工模板 **6 份** + **`known-facts.md`（已知事实完整表）**）；任务产出（`union-conventions.md` 等）在代码副本的 `C:\swprojects\sw-skill-fork\docs\` | 可改 |

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

## 汇报频率

默认不汇报；只在三种情况发一条消息：一批做完、同一处卡住 ≥2 次、计划要变。
消息 ≤3 行，只写结果与影响；进度写进 ROADMAP §一 与 capabilities.yaml，不在对话里复述。

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
判据优先去开源项目里找（先去四家找现成判据，找不到再自己搓）见 [docs/evidence-first.md](docs/evidence-first.md)。

## 六、已知事实（完整表在 [`docs/known-facts.md`](docs/known-facts.md)）

**共 63 条**，全文在 [`docs/known-facts.md`](docs/known-facts.md)。
⚠ **为什么会分开**：该表已占 AGENTS.md 的 ~71%，而本文件受 **65536 字节指令预算**限制
⇒ **超预算会被截断，且截掉的是**末尾最新**的条目**（静默退化）。
⇒ **查事实请读那个文件**；本节只留**最常查的 21 条**做速查。
⚠ **新增事实**：只在下面保留「最常查的」；其余**直接追加到 `docs/known-facts.md`**，
并在本节更新条数说明。

### 速查（最常查的 21 条）

| # | 事实 | 依据 |
|---|---|---|
| 1 | 切除的正确入口是 `IFeatureManager.FeatureCut4`（27 参数），不是 `FeatureExtrusion3(Flip=true)`：后者建出来是「凸台-拉伸」特征名，体积恒等于原板 | 本机实测 + 上游 `sw_part.extrude_cut` + `swdoc.ps1 -File FeatureCut4` |
| 2 | `IFeatureManager.FeatureExtrusion3` 是 23 个参数；`FeatureExtrusion2` 已废弃被 3 取代 | `C:\swapi\types\IFeatureManager\FeatureExtrusion3.md` + delancy827 README 独立佐证 |
| 8 | `ISelectionMgr.AddSelectionListObject` 的 bool 返回值不可信，用 `GetSelectedObjectCount2(-1)` 回读 | 本机实测（12 次全 false 但计数 = 12） |
| 9 | 画草图前先 `SelectByID2` 选中基准面；基准面名随 UI 语言变（`"Front Plane"` / `"前视基准面"`）。不选面 → 特征返回 NULL 且几何零变化；沿上游 `_get_plane_name_candidates` | 本机实测 + 上游 `sw_part.py` |
| 12 | 空 Dispatch 参数包 `VARIANT(VT_DISPATCH, None)` | 上游 `create_empty_dispatch_variant()` |
| 24 | 运行时只能有一个 SolidWorks MCP：多个进程抢同一 COM 连接会死锁。`Eduardof0nt/Solidworks-MCP-Server` 为此实现 Windows 命名互斥锁 `Local\SolidWorksMCPServer_SingleInstance_v1`；`Slacker-LLC/solidworks-mcp` 把「Two clients driving the same session at once will deadlock it.」写进已知限制 | 两家源码 + README |
| 32 | **实体（边 / 面）没有可用的名字**：`SelectByID2("Edge1","EDGE")` 与 `SelectByID2("Face1","FACE")` 在真机上**计数均为 0**（100×60×20 mm 板，12 边 / 6 面）；`SelectByID2("","EDGE",0,0,0,…)` 也是 0（原点不在边上）。**选实体（边/面）的可行路径是 `IEntity.Select4(Append, Callout)`（按**对象**选，计数 1），或按**面上的点**定位（`SelectByID2("","FACE",x,y,z,…)`，计数 1）。**⇒ 「按名字选」**只对特征成立**（`sw_part._ensure_sketch_selected` 走的就是那一路），对实体**不成立** | 证据脚本 `D:\AI\SW\probe_entity_select_by_name.py`；落地模块 `scripts/sw_selection_spec.py`（端到端 `probe_selection_spec_e2e.py` **12/12 通过**）|
| 33 | `SelectByID2` / `Select4` 的 `Callout` 参数**必须**传 `VARIANT(VT_DISPATCH, None)`（`sw_part._empty_callout()`）；**传 `None` 得到 `'类型不匹配'`（`0x80028CA0`）**，而该错误**看不出是 Callout 的问题**。⇒ 这是已知事实 12 的一个**具体后果**，2026-10-01 又踩一次（差点据此得出「选择不可能」的错误结论）| 本机实测（同一探针的失败版 vs 修好版）|
| 36 | **同名接口分属不同族 —— 用错接口 = 对象对任何成员都没反应**：官方类型表里 Gusset 有**两个** —— `ISMGussetFeatureData`（`category: Feature Interfaces/**Sheet Metal**`，28 属性）与 `IGussetFeatureData`（`category: .../**Weldments**`，19 成员），**共有成员只有 3 个**（`AccessSelections` / `ProfileType` / `ReleaseSelectionAccess`）。`swFmSMGusset` 描述明写 "**Sheet metal** gusset" ⇒ 必须用 SM 那个。**用错时真机表现：连**读**都读不到**（`read Thickness → ✗ <unknown>.Thickness`），写报 `Property '<unknown>.X' can not be set` —— **看起来像「属性只读」，实际是「接口不对」**。⚠ **`scripts/check_member_names.py` 抓不到这一类**（它判「名字在**某个**接口里存在」，不判「在**这个**接口里存在」）| 官方类型表 `C:\swapi\types\ISMGussetFeatureData\` vs `\IGussetFeatureData\`；真机证据 `D:\AI\SW\probe_property_binding.py` |
| 40 | **`IModeler.Create*Surface` 的返回值**不可靠** —— 不是「有些能有些不能」，而是**同一个调用跨次也会变****（2026-10-01，**四轮探针**）：第 13 轮 `CreateCylindricalSurface` **成功**；第 26 轮 `spherical`/`toroidal` 成、`cylindrical`/`conical` 返回 `None`；第 27 轮受控实验只 `axis=(1,0,0)` 成（**排除了顺序与单例状态**）且 `*2` 全 `None`。**官方**：该族 18 个里 **4 个标 `Obsolete`**（`CreateConicalSurface` / `CreateCylindricalSurface` / `CreatePlanarSurface` / `CreateSphericalSurface`），**各有 `*2` 后继、且 `*2` 运行期可达**（它多一个 `RefDirection`）——**但按正确 arity 调 `*2` 仍然返回 `None` ⇒ 换一代解决不了**。**⇒ 修的只能是「让失败可见」**：`sw_surface._invoke` 现在对 `None` **抛带原因的 `RuntimeError`**。⚠ 一个**存在但没人用**的守卫（`require_runtime_available` 曾如此）与没有守卫等价，**且更糟**（让人以为防住了）—— 2026-10-01 才接进 13 个公开包装器 | 证据 `D:\AI\SW\probe_surface2_correct_arity.py` / `probe_cyl_order_vs_axis.py` / `probe_cyl_none_matrix.py` / `probe_surface_generations.py`；`scripts/sw_surface.py` 的 `_invoke` / `IMODELER_RUNTIME_*` |
| 43 | **`CreateDefinition` 只接受官方列出的 **35 个**常量 —— 用它之前必须查那张名单**；`swFmOneBend(33)` / `swFmDraft(3)` 都是**合法枚举成员但不是合法类型** （⇒ 返回 `None` **是应然的**，不是 COM/权限问题）。**「一个折弯」的正确入口是 `swFmSketchBend(35)`**，接口 `ISketchedBendFeatureData` （16 个成员：`BendAngle`/`BendRadius`/`ReverseDirection`/`UseDefaultBendRadius`/`UseDefaultBendAllowance`/`SetFixedFace`/`GetFixedFace`/…；**`FixedFace`/`BendLine` 是**方法**不是属性**）。**⚠ 两套官方源在这一族**分工不同****：`C:\swapi\enums\swFeatureNameID_e.md` 的「Value」列**装的是描述、不是数值** ⇒ **数值必须去反射** `D:\AI\SW\_raw\**\enum_values_sldworks.txt`（130 个成员）。★ **可核验的 `CONST → 接口` 映射**（不手写）：`CreateDefinition.md` 的括注 × 接口 `_overview.md` 的 Description ⇒ 20 条唯一命中 / 4 歧义 / 11 未映射（`D:\AI\SW\gen_const_iface_map.py`） | `C:\swapi\types\IFeatureManager\CreateDefinition.md`（35 个常量）；`enum_values_sldworks.txt`；`gen_const_iface_map.py`；`probe_sketch_bend_entry.py` |**★ 2026-10-01 消歧完成**：4 条歧义**全部解掉** ⇒ **24 唯一命中 / 0 歧义 / 11 未映射**。三条规则**都从官方描述读出**：① **含 `group` 者是子项**（两处 `*GroupData` 的描述都写着 "feature group" / "feature's cut-extrude face group"）⇒ 排除；② 剩下的里**含 `feature` 者优先**（`ICornerReliefFeatureData` "…relief **feature data**" vs `ISMCornerReliefData` "…relief **data**"）；③ ⚠ **兜底（弱启发式）**：描述**比常量括注多出的词最少**者优先 —— `swFmLibraryFeature (library)` ⇒ `ILibraryFeatureData`（+2 词）胜过 `ILibraryFormToolFeatureData`（+4 词）。**③ 已在代码注释与提交信息里标注为弱证据。****★★ 2026-10-01 再进一步（轮 41）**：把**已逐条读官方描述确认**的 7 条写进显式的 `MANUAL_MAP` ⇒ **31 唯一（**自动 24 + 人工确证 7**）/ 0 歧义 / 4 未映射**（原 24/0/11）。**⚠ 与轮 40 那次失败的关键区别：这次是**人工表、每条在代码里注明依据**，不是启发式硬凑**（轮 40 用「名字回退」连续改 6 版都不对，已回退并记进已知事实 53）。三条设计约束：① **绝不覆盖**自动结果（只补空）；② **输出分开报**（「自动 %d + 人工确证 %d」）；③ **没有依据的不许进来**（未确证的 4 条留在 `unmapped`，按铁律 5 写「查不到」）。
| 47 | **`ISketchedBendFeatureData` 的 `AccessSelections` / `SetFixedFace` 在 pywin32 迟到绑定下**不可调用** —— 这是**架构性限制**，不是参数没找对**（2026-10-01，**两轮 20+ 种形态**实测）：`SetFixedFace(X,Y,Z,EdgeArray)` 的**七种数组包装 × 两个重载**全部报 `类型不匹配`（位置 1 或 4）；`AccessSelections(model, None)` 报 `类型不匹配`（位置 2）、改传 `VARIANT(VT_DISPATCH, None)` 则报 **`服务器出现意外情况`（`0x80010105`）**——**与已知事实 28 的 `CreateBsplineSurface` 同一个错误码**。**⇒ 这与 `capabilities.yaml` 里**早已记录**的后端限制吻合**：「**不能调用官方标记为仅进程内非托管 C++ 的指针接口**」；反射里那对 **`IAccessSelections` / `IAccessSelections2`** 正是那种 `I` 前缀的**指针变体**。**⇒ 结论：`create_one_bend` / `create_edge_flange` / `create_gusset` 三条在 pywin32 这条后端上到不了「建成」**（除非换 `comtypes` 或进程内 C++ 后端）。⚠ **不要再用「换个参数试试」的方式继续试** —— 20+ 种已穷尽 | `D:\AI\SW\probe_setfixedface_forms.py` / `probe_setfixedface_overloads.py` / `probe_access_selections.py`；`capabilities.yaml` 的 `backend_catalog` 限制段 |
| 48 | **长文本不要内联进 Python 源码** —— 本会话在这一件事上**踩了 6 次**：文档串里嵌同类引号 / 补丁脚本插真换行 / `%`-格式串里的 `100%` / `\A` 之类坏转义 / 状态表字符串断行 / 以及 `write` 工具写的 Python 里字符串被**真实换行**截断（`SyntaxError: unterminated string literal`，**连踩两次**）。⚠ 最坑的一次：**脚本语法错 ⇒ 内容没写进去，而外面的 `git add -A && commit` 照跑**⇒ 产生「提交信息说改了文档、实际只提交了那个坏脚本」的**假提交**（2026-10-01 连出两次）。**⇒ 定则两条：① 长内容先写成**独立文件**（`.md`），再用最短脚本搬运；② 批量脚本跑完**必须核对落盘**（`grep` 一下目标文件），**不能只看脚本的 stdout**。** | `D:\AI\SW\_t011_section28.md`（正确做法）；`doc_fact47.py`（错误做法的两次失败） |
| 51 | **一个「抓不到目标类别」的检查，往往不是判据错，而是**分析范围**与代码的**组织单元**不匹配** —— 2026-10-01 在第 38 轮与第 29 轮**各踩一次同一处**：用 `WINDOW = 400` 的**行窗口**去收集 `data.X` 的用法，而 `data` 这个变量名在**多个 `_apply(data)` 嵌套函数**里复用 ⇒ 把**别的特征**的成员也算了进来（实测：base flange 那个站点把 edge flange / draft / **gusset** 的成员全吞了，**6 个假阳性**）。**⇒ 范围必须贴合代码的**组织单元**（所在函数）。**⚠ 同轮的另两处：① **形参驱动的站点只解析了第一个调用点** ⇒ 5 个站点只检查了 1 个；② 实参文本是 `int(fm_type`（**带 `int(...)` 包装**），而形参名查询直接拿它去查 ⇒ 一个都解析不到。**⇒ 教训：静态分析先问「这段代码的**组织单元**是什么」，再决定收集范围。** | `scripts/check_interface_member_ownership.py` 的 `enclosing_range` / `calls_of` / `param_index`；第 29 轮的同一处错误与第 38 轮的反转 |
| 53 | **「调到看起来对」的识别信号：同一个启发式**连续修补 ≥3 次**还没稳定，就该停下回退** —— 2026-10-01 实例：为攻掉 `CONST → 接口` 映射表的 11 条未映射，我给检查器加「名字回退」，**连续改了 6 版**（30/4/1 ⇒ 词重叠过滤无效 ⇒ 末词过滤仍错 ⇒ 去首词变体跌到 29/0/**6** ⇒ 改词级匹配回到 24/0/11 ⇒ 改名字子串又错成 29/6/0），**每版都在同一处打补丁**，最后**回退**到 `e4794cc` 的 **24/0/11**。**⇒ 根因不是「还没调对」**：① `swFmSweepThread` 那类（"sweep thread" 是**螺纹**）**需要领域知识**，文本匹配永远得不到；② 名字匹配的**假阳性**（`swFmSolidToSheetMetal` ⇒ `ISheetMetalFeatureData`、`swFmMirrorComponent` ⇒ `IComponent2`）**压不住**。**⇒ 正解：把证据留在**文档**里（`docs/T-040-unmapped-constants-evidence.md`，11 条逐条带官方依据），**不接进工具**。**⇒ 定则：启发式需要连续 ≥3 次修补才「看起来对」时，回退 + 记证据，不要继续调。** | `docs/T-040-unmapped-constants-evidence.md`；`git log --oneline scripts/check_interface_member_ownership.py`（含回退）；已知事实 52（名字是弱信号）与 51（分析范围要贴合组织单元）|
| 55 | **改了任何**运行时文件**之后必须重跑 `python scripts/sync_bundled_skill.py`** —— `release_check.py` 会比「仓库根的 Skill」与「桌面内嵌快照」（`apps/workbench-ui/src-tauri/resources/skill`），不一致就拦发布。**⚠ 而该快照在 `.gitignore:23` 里 ⇒ 它是**构建产物**、`git status` **看不见它** ⇒ **这条纪律不会被 git 提醒你**。**★ 2026-10-01（轮 43）实测：修掉了一个**基线失败** `test_release_check_passes_current_tree`（回归从 **6 failed / 857 passed** 变成 **5 failed / 858 passed**）—— **真因是那一步构建没跑，不是代码 bug**；跑一次 `sync_bundled_skill.py`（276 个文件）即通过，且 `git status` **仍然干净**。★ 同轮还把报错改成**可执行**的：原来只报 `桌面内嵌 Skill 与根 Skill 不一致: <bundled-skill-missing>`（**看不出该怎么办**），现在**分开报两种情况**并各给出**可直接跑的命令**；**并且验证过它是对的** —— 改完 `release_check.py` 再跑，它立刻报 `与根 Skill 不一致: scripts/release_check.py`（**检查在尽职**），而提示给的命令正是解法。 | `scripts/sync_bundled_skill.py`；`scripts/release_check.py` 的 `find_bundled_skill_drift`；`.gitignore:23` |
| 57 | **一个「一直是绿的」测试，可能只是**每次跑的时候环境恰好满足** —— 不是它真的在测** —— 2026-10-01（轮 44）实例：`tests/test_tool_specs_batch4.py` 的文档串承诺「**不依赖 `mcp` 库、**不连 SolidWorks**」，但它 2 个测试的 spec `derived_args` **碰了活 COM**（`_swept_refs_and_spec` 调 `resolve_entity(model, '__current_selection__', "EDGE")` ⇒ 要求界面上**已选中一条边**）。**⇒ 干净机器上必然失败**（`RuntimeError: 没有活动文档`）；**它以前之所以绿，是因为我探测时恰好选中过边** ⇒ **纯属巧合**（`git stash` 掉我的改动后仍失败，证明与我的改动无关）。**⇒ 修法加了 `_derived_args_or_skip()`：只把「碰 COM」那一类转成**带原因 skip**（契约违约**可见**），别的异常照旧抛出。**⚠ **推论**：本仓库的回归基线**依赖 SolidWorks 的文档/选择状态** ⇒ 记基线时必须**同时记 SolidWorks 状态**，否则下轮的「多了几个失败」会被误判成代码问题。 | `tests/test_tool_specs_batch4.py` 的 `_derived_args_or_skip`；`mcp-server/tool_specs_batch4.py` 的 `_swept_refs_and_spec`；`scripts/sw_selection_spec.py` 的 `EntitySelectionError` |
| 58 | **`subprocess.run(..., text=True)` 不给 `encoding=` 在**中文 Windows 上会炸**** —— 父进程用 `locale.getpreferredencoding()`（本机 **GBK**）去解子进程的 **UTF-8 中文**输出 ⇒ `UnicodeDecodeError: 'gbk' codec can't decode …` ⇒ **`completed.stdout` 变成 `None`** ⇒ 下游 `json.loads(None)` 抛 `TypeError`（**错误信息指向不了真因**）。**⇒ 修法：一律补 `encoding="utf-8", errors="replace"`**（与子进程实际输出一致；`errors="replace"` 保证再遇到别的编码也不至于整条测试崩掉）。★ 2026-10-01（轮 45）：本仓 **11 处**这样写，**4 个基线失败全因此**；修完全量回归 **0 failed**。⚠ **同一轮还踩了扫描的假阳性**：我按「第一个 `)`」截断调用来判断「有没有 encoding=」，**把本来就有 `encoding=` 的多行调用误判了，报了 23 处**，真值只有 11 处⇒ **判「某个调用带没带某参数」必须按**括号配对**切分整段调用，不能按第一个 `)` 截。** | `tests/test_cad_studio_cli.py` / `tests/test_dfm_review.py` / `scripts/fea_analysis.py` 等 6 个文件；Python 标准库 `subprocess` 文档（`text`/`encoding`）|
| 59 | **`Path("D:")` 是「带盘符的**相对**路径」，不是盘根** —— `Path("D:") / "AutoCAD 2024" / "acad.exe"` 得到 **`'D:AutoCAD 2024\\acad.exe'`（缺反斜杠）**，而 `Path("D:/") / …` 才得到 `'D:\\AutoCAD 2024\\acad.exe'`。**⇒ 2026-10-01（轮 45）在 `scripts/cad_installation.py` 的 `_common_candidates` 里发现这个真实功能 bug**：`root = Path(drive)`（`drive` 是 `"D:"` / `"E:"`）⇒ **D:/E: 盘上的 AutoCAD / SolidWorks 一直发现不了**（不影响 C:，因为 C: 走的是 `ProgramFiles` 环境变量拼的路径）。**⇒ 修法 `Path(drive + "/")`；修完全量回归 0 failed。**★ **这个 bug 是测试**尽职抓到的** —— `test_discover_installation_supports_injected_filesystem` 注入的 `exists` **只认精确字符串** `d:\\autocad 2024\\acad.exe`，于是把「路径拼错」暴露成了断言失败。**⇒ 教训：注入式的精确匹配测试能抓到「路径拼错」这类功能 bug；「在不在」类测试（模糊匹配）抓不到。** | `scripts/cad_installation.py` 的 `_common_candidates`；`tests/test_cad_reliability.py`；Python 标准库 `pathlib` 文档（`Path("c:")` 与 `Path("c:/")` 的区别）|
| 61 | **批量改文件的脚本必须**先证明它只做加法** —— `git diff --stat` 出现 `deletions` 就要停下查** —— 2026-10-01（轮 46）**严重事故**：我用一个「括号配对 + 就地插入」的脚本同时改两个文件，结果 `apps/desktop/cad_workbench/queue_worker.py` 的 `git diff --stat` 是 **`5 insertions(+), 232 deletions(-)`** —— **`process_queue` 连同 232 行消失**；`tests/test_cad_studio_cli.py` 末尾 5 行断言被删且丢了末尾换行。**⇒ 立刻 `git checkout --` 恢复两文件，改用 `edit` 工具逐处改**（差异回到正常的 `4 ++++` / `4 ++--`）。**⇒ 三条定则：① 批量脚本跑完**先看 `git diff --stat`**，有 `deletions` 就当成自己的 bug 查；② 能用 `edit` 工具逐处改就**不要**写批量替换脚本（尤其在有来源块的仓库里）；③ 改完**回读**被改文件（事实 48 定则②）。**⚠ 同一次事故里**事实 60 又重演**：我的脚本第二次改坏了来源块的**散文** —— **因为我在**门禁里**写了剥注释/字符串的函数，却**没在修复脚本里用**。****⇒ 定则④：写了一个好用的工具函数，就要在**所有**同类场合用它，别只用在门禁里。** | `git log --oneline -p` 里轮 46 的恢复；`scripts/check_env_pitfalls.py` 的 `strip_comments_and_strings()`（门禁里用了、修复脚本里没用）|
| 62 | **一个门禁「写了」不等于它「有效」—— 负例测试是唯一的证明** —— 2026-10-01（轮 46）：我为「`Path("<盘符>:")` 当盘根」（事实 59）写的门禁**第一版只认字面量** `Path("D:")`，而**真 bug 的形态是 `root = Path(drive)`**（`drive` 是 `for drive in ("D:", "E:")` 的循环变量）⇒ **负例测试当场失败，证明门禁抓不到它真正要抓的东西**（「一个存在但没人用的守卫与没有守卫等价」）。**⇒ 补**轻量数据流**（先找被绑定成 `"X:"` 的变量名，再找 `Path(<那个变量>)`）后，用**修复前的原文**验证：`git show <修复前>:scripts/cad_installation.py` ⇒ **命中 1 处**，修复后 **0 处** ⇒ **这才叫「门禁能抓到那个 bug」。**⚠ 中途还试过「要求 `/` 紧邻 `Path(drive)`」—— **也抓不到**（中间隔了十几行才 `root / "AutoCAD 2024"`）⇒ 最终判据改为「`Path("D:")` **本身**就该报」（盘根只有 `"D:/"` 一种正解，报它无害）。★ **可复用的手法：用 `git show <commit>^:<path>` 取**修复前**的原文当负例输入 —— 比手写一个「像 bug 的样本」硬得多。** | `scripts/check_env_pitfalls.py` 的 `find_drive_only_root`；`tests/test_env_pitfalls_gate.py`；`git show 7ffa842^:scripts/cad_installation.py` |


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
