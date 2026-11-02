# soheil-mp/solidworks-mcp

<!-- survey: class=H; repr=feature-tree; orchestration=single; verify=numeric; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `soheil-mp/solidworks-mcp` · https://github.com/soheil-mp/solidworks-mcp |
| 许可 | **MIT**（`LICENSE:1-3` = `MIT License` / `Copyright (c) 2026 Soheil and the solidworks-mcp contributors`）⇒ 可读可抄可商用，保留版权声明 |
| 元数据 | stars 10 · forks 4 · 语言 C#（203 个 `.cs`）· 仓库 3187 KB · 建档 **2026-10-23** · 最近推送 **2026-10-31**（来源：`gh api repos/soheil-mp/solidworks-mcp`，2026-11-02 取）⇒ 本批最新的一家 |
| 克隆 | `D:\swagent-2026Q4\repos\soheil-mp__solidworks-mcp`（`--depth 1`；首轮 HTTPS 握手失败，重试 1 次成功）|
| 证据等级 | **读码**（契约测试自述「need the build (SOLIDWORKS installed) but not a running SOLIDWORKS」，即需本机互操作程序集；**未编译未跑**。SolidWorks 未跑，建模能力结论止步 `source`）|

## 1. 一句话定位

**工具面最宽（161 个）且对「选错东西」这件事防得最死的一家**：几何引用是一个联合类型（`id` / 声明式查询 `where` + **必需的命中数 `expect`** / 最近点 `at` / 名字），命中数不符就抛 `EntityAmbiguous` 并列出候选；配合编译期绑死的强类型互操作（晚绑定在构建期被禁止）、单一 STA 调度器、命名化的对话框自动应答规则。（`README.md` 与 `src/SolidWorksMcp.Server/Tools/FeatureTools.cs` 实测计数）

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：MCP stdio（`ModelContextProtocol` 官方 C# SDK，`[McpServerToolType, Toolset("sketch")]` 分工具集）。连接时下发 `Instructions.cs`（3446 字节）的规约；另有 `sw_help` 工具展开 `Hosting/Guide.cs`（21480 字节）的详解。

**中间表示**：三层。① **单位契约**：mm / 度 / kg（`README.md`「Conventions」），且明确 SOLIDWORKS 是 **Y-up，top 平面是 XZ**；② **几何引用 `EntityRef`**（`src/SolidWorksMcp.Core/Model/EntityRef.cs`，见 §3.1）；③ **特征树本身**（无几何 IR）。

**生成**：不生成代码。它**不提供任意代码执行口**（161 个工具全是显式动词）。（`src/SolidWorksMcp.Server/Tools/FeatureTools.cs` 等 25 个工具类）

**编排**：无编排层；一次调用一个工具，全部 COM 走 `Com/StaDispatcher.cs`（16631 字节，单 STA 线程 + 时限）。

**执行**：**C# + 官方互操作程序集**，强类型直接调用——`README.md`「Typed calls」段明写「Late binding is forbidden at build time, so a wrong member or argument count is a compile error」。⇒ 它用编译期检查替代了 Python 侧那一整套 `_FlagAsMethod`/`flag_methods`（对比 `sw-hjbaard-solidworks-mcp.md` §3.6 与 `sw-raylanlin-millwright.md` §5 #1/#2）。

**验证**：**Tier-A / Tier-B 两级 + 回滚**（`src/SolidWorksMcp.Core/Verify/FeatureVerifier.cs`，见 §3.2）。`README.md`「No fake success」段：「Every change is verified: feature identity, rebuild errors, volume and geometry changes, and file headers. A failed feature is **rolled back** and the error says so.」

**交付**：导出族覆盖 STEP/IGES/STL/Parasolid/PDF/DXF（`ExportService.cs` 55859 字节），另有工程图族（`DrawingService.cs` 113129 字节 + `DrawingService.Tables.cs`）。

## 3. 技术方案要点（可迁移的机制）

### 3.1 几何引用：**四选一 + 命中数断言**（本卡最该抄的一条，直接答「持久引用」）

`EntityRef` 的优先级写在类注释里（`src/SolidWorksMcp.Core/Model/EntityRef.cs:5-10`）：`id`（来自列表或特征结果）> `where`（查询）> `at`（最近点，mm）> `name`（平面/轴/草图/特征/实体/组件/草图段）。字段：

| 字段 | 作用 |
|---|---|
| `id` | 列表或结果里给的稳定 id（`F3`/`E12`——**注意它仍是「本次列举的序号」**，见 §5 #3）|
| `where` | 声明式过滤，17 个字段：`type`/`surface`/`curve`/`normal`/`parallelTo`/`radiusMm`/`radiusTolMm`/`lengthMm`/`near`/`withinMm`/`extreme`/`feature`/`body`/`ofFace`/`loop`/`component`/`angleTolDeg`（`EntityFilter`，字段表见 `EntityRef.cs` 后半）|
| `expect` | **用 `where` 时必需的命中数**；`EntityResolver.cs:179-186` 在数量不符时抛 `EntityAmbiguous`，消息里带「matched N, expected M」和最多 10 个候选（id + 坐标），Hint 教你「放宽 filter 或改用 id」|
| `at` + `tolMm` / `strict` | 最近点匹配；`strict` 拒绝「超出容差仍退到最近的那个」|

`where` 用 `StrictJson`（`UnmappedMemberHandling.Disallow`）解析 ⇒ **拼错字段名会直接报错**，不会静默忽略（`EntityRef.cs` 的 `WhereFilter`）。

⇒ **这是对「几何变更后选择失效」最诚实的答案**：不存拓扑 ID，而是「**每次重新用谓词查 + 断言应该查到几个**」。几何一变、谓词命中的数量跟着变，于是**立刻以「ambiguous/not found」失败并列出候选**，而不是安静地选错面去倒角。`README.md` 的建模循环示例就是这个形状：`feature_fillet {radiusMm:5, edges:[{where:{curve:"line",parallelTo:"y"}, expect:4}]}`。

### 3.2 验证：Tier-A 结构判据 + Tier-B 意图判据 + 回滚

`FeatureVerifier.cs:8-31` 定义 `VolumeRule { Increase, Decrease, Change, Any }` 与 `FeatureSpec(string Tool, string[] Types, VolumeRule Volume, bool RequireFaces)`；类注释说明新特征用**特征 id 集合差**识别，因此「void API、多节点特征、回滚过的特征树」都能处理；副作用之后任何失败都会**删掉该调用创建的东西**（调用前已存在的被吸收草图保留）并在错误里说明。

与 Millwright 的分类断言（`sw-raylanlin-millwright.md` §3.2）同一思路，但**判据落在「具体工具 → 期望特征类型 + 体积方向」的声明式记录**上，并且有 `FeatureOutcome(…, Checks)` 把通过的检查项写进结果。⇒ 「验证结论可读」这一点比只回一个布尔更有用。

### 3.3 对话框：**命名化的自动应答规则 + 阻塞即返回**

`Win32/DialogRules.cs` 把已知弹窗写成规则（标题正则 + 可选必含文本 + 应答按钮 + 说明 + 是否错误）：VBA 运行期错误（按 `End`）、`Modify` 尺寸框（按 ok）、Simulation 保存提示（Yes/No 两版）、「Make Dimension Driven?」（按 cancel，于是 `sketch_dimension_add` 报拒绝）、FeatureWorks「是否识别特征」（按 decline）。类注释写明规则**只对声明了它的操作生效**（`DialogRules.cs:3`）。

配套 `Win32/Dialogs.cs`（5452 字节）+ `Win32/DialogWatchdog.cs`（3336 字节），以及 `README.md`「No hangs」段的口径：**「A modal dialog makes the call return `DIALOG_BLOCKING` within seconds, and `dialog_list` / `dialog_respond` work while SOLIDWORKS is blocked」**。

⇒ 与我方 `sw_guard`/`sw_dialog_watch` 同问题；**它的增量是「把每个已知弹窗写成一个具名规则 + 只在该操作上启用」**（避免「一刀切自动点掉」），以及**把「被阻塞」变成一个可被 agent 读取的错误码**而不是超时。

### 3.4 工具目录本身有预算门禁

`src/SolidWorksMcp.Server/Hosting/CatalogCheck.cs`（7453 字节）+ `tests/…/ContractTests.cs` 的 `Tool_catalog_follows_the_conventions` 断言三件事：工具数 ≥20、**每个工具的平均字节数不超过 `CatalogCheck.AverageToolBudget`**、以及 `EntityRef` schema 被压缩且只在一处解释。⇒ **161 个工具不是白送的**：它用测试守住 `tools/list` 的 token 成本。这条对「我方 439 个工具怎么控制上下文成本」是直接可用的判据。

### 3.5 错误形状：`CODE: message Hint: what to do`

`README.md`「Built for agents」段 + `src/SolidWorksMcp.Server/Hosting/ToolErrorFilter.cs`（7995 字节）。与 hjbaard 的 `{ok:false,error}`、Millwright 的 `{ok,data|error}` 相比，多了一个**机器可读的 CODE**（如 `EntityAmbiguous` / `EntityNotFound` / `DIALOG_BLOCKING` / `NOT_SUPPORTED`），让 agent 能按码分支。⇒ 我方工具的报错目前偏「给人读」，这是一条升级方向。

## 4. 运行条件与依赖

- Windows + **SOLIDWORKS 2025 SP1.2**（`README.md`「Live test status」明写测试环境；其它版本 untested）；.NET（`global.json`/`Directory.Build.props` 固定 SDK）。
- 需要本机 SOLIDWORKS 互操作程序集（`SolidWorks.Interop.sldworks.dll` 等）；构建即强类型校验。
- 运行形态：本地 MCP stdio；`SWMCP_EXPERIMENTAL=1` 打开实验能力（如真实螺纹孔）。
- 测试两层：**425 个 live 测试**（要真机，`README.md` 自述全过）+ 契约测试（需构建但不需运行 SolidWorks）。本机**未跑**（缺互操作程序集）。

## 5. 失败模式与已知坑

自述（`README.md`「Known issues」）+ 实读：
1. **长会话把 SolidWorks 拖慢**：一个会话里几百份文档之后，开/关文档要 20 秒到几分钟，必须重启（它自己的数字）。（`README.md`「Known issues」）
2. **工程图标注在长会话里会静默停止生效**（`drw_center_marks` / `drw_dimensions_auto`），原因未知；提示文本会这么说。
3. **出现过一次挂死**：某个工程图测试再也不返回（SolidWorks 仍响应、无弹窗），杀进程后重跑通过。
4. **STEP AP242 可能按 AP203 导出**（取决于许可），此时导出**拒绝并报 `NOT_SUPPORTED`**，而不是把文件谎称 AP242 —— 这是「宁可失败也不假成功」的一个正面例子。
5. **螺纹孔默认只做底孔**，除非 `SWMCP_EXPERIMENTAL=1`。
6. **明确不做的**：螺钉配合（SW2025 通过 API 设螺距会被忽略，`asm_mate_add` 直接拒绝）、钣金折弯（jogs）、运动研究（结果无法可靠回读）、PhotoView 渲染（SW2025 已移除）、柔性特征；**齿轮配合的速比回读是反的**，工具接受并如实报告。
7. **id 是「本次列举的序号」**：`id` 的说明是「Id from a listing or result」（`EntityRef.cs:` 的 `Id` 字段注释），**改几何后重新列举会换号** ⇒ 所以它才要求 `where`+`expect` 优先。这一点若被误用（长期缓存 id）就是「静默选错」的来源。
8. **本卡无法验证的规模**：161 个工具里有多少 live 覆盖，只能看它的分域表（`README.md`「Live test status」逐域列了数量），**我没有逐个映射工具↔测试**。

## 6. 对我方目标的可用处（能学 / 不能学）

**Q2 逐条答**：
| 问题 | 它解到什么程度 | 依据 |
|---|---|---|
| 持久引用 | **解到本批最好的一档**：不存 id，改「谓词查询 + 命中数断言」；不符就 `EntityAmbiguous` 并给候选 | `src/SolidWorksMcp.Core/Model/EntityRef.cs`、`src/SolidWorksMcp.Core/Geometry/EntityResolver.cs:179-186` |
| 回读验证 | **解了**：Tier-A 特征集合差 + 体积方向 + 回滚；错误码机器可读 | `src/SolidWorksMcp.Core/Verify/FeatureVerifier.cs:8-31` |
| 事务式建模 | **解了单步回滚**：失败删掉本次调用创建的特征（保留调用前已有的被吸收草图） | 同上，类注释 |
| 单源 COM 互斥 | **解了进程内一档**：全部 COM 走 `StaDispatcher` 单线程 + 时限 | `src/SolidWorksMcp.Core/Com/StaDispatcher.cs` |

**Q3 答**：**MCP 服务端**（C#/.NET，官方 MCP SDK）；工具面 **161 个**（`(Select-String -Path 'src\SolidWorksMcp.Server\Tools\*.cs' -Pattern '\[McpServerTool\(' -AllMatches).Count` ⇒ 161）；粒度 = **一动词一工具**（按域分 25 个工具类），**无 `operation` 分派、无万能代码口**。

**能学（按性价比排序）**：
1. **`EntityRef` 的四形态 + `where`/`expect`**：直接回答我方「几何变更后选择失效」。落地要点是 **`expect` 必填**（不填就等于允许 ambiguous）与**报错带候选**。
2. **错误码 + Hint**（`EntityAmbiguous` / `DIALOG_BLOCKING` / `NOT_SUPPORTED`）：把「失败」变成可分支的信号。
3. **对话框规则具名化 + 只对声明它的操作启用**：比我方「全局扫弹窗」更安全，二者可以叠加（全局兜底 + 局部具名）。
4. **工具目录预算门禁**（`CatalogCheck.AverageToolBudget` + 平均字节断言）：我方 439 个工具正需要这条。（`src/SolidWorksMcp.Server/Hosting/CatalogCheck.cs`）
5. **Tier-A 体积方向表 + 失败回滚**：与 Millwright 的分类断言互为印证，两边独立得到同一结论，可信度高。
6. **「宁可 `NOT_SUPPORTED` 也不谎称」**（AP242 例）：与我方 A7（不把 stitched 写成 verified）同一条纪律的现成样本。
7. **强类型互操作 = 编译期签名校验**：如果哪天我方要换语言，这是最有力的论据（对比 Python 侧三种绕法：`_FlagAsMethod` / 早绑定包装 / 纯晚绑定）。

**不能学**：
- **`id` 的语义含混**：它既是「列表序号」又被当稳定引用用；若长期缓存就会静默选错——**我方若引入 id，必须写清「只在同一快照内有效」**。
- **161 个工具的宽度**：它靠 C# 强类型撑住了，Python 侧照抄会立刻爆。（`src/SolidWorksMcp.Server/Tools/FeatureTools.cs` + `README.md`）
- **只有单步回滚**：多步计划失败仍留半成品（与我方「事务式建模」目标还有距离）。
- **live 测试依赖单一 SP 版本**（2025 SP1.2）：跨版本行为未知。

## 7. 许可与红线

**MIT**（`LICENSE:1-3`，`Copyright (c) 2026 Soheil and the solidworks-mcp contributors`）。可移植，义务：保留版权声明。★ 移植 `EntityRef`/`EntityFilter` 的**字段设计**与 `where`/`expect` 语义、`FeatureVerifier` 的体积方向表、`DialogRules` 的规则形状时，来源头写 `soheil-mp/solidworks-mcp（MIT，LICENSE:3）` + 改动说明。

## 8. 证据清单

- `src/SolidWorksMcp.Core/Model/EntityRef.cs`（`EntityRef` 四形态 + 优先级注释；`where` 用 `StrictJson` 拒绝未知字段；`Expect` 字段说明「Exact number of matches required with 'where'」；`EntityFilter` 17 个字段）
- `src/SolidWorksMcp.Core/Geometry/EntityResolver.cs:179-186`（命中数不符抛 `EntityAmbiguous`，消息带 matched/expected + 至多 10 个候选 + Hint）
- `src/SolidWorksMcp.Core/Verify/FeatureVerifier.cs:8-31`（`VolumeRule` 四值、`FeatureSpec`、`FeatureOutcome`、特征 id 集合差识别新特征、失败删除本次创建物、`VolEps = 1e-13` m³）
- `src/SolidWorksMcp.Core/Win32/DialogRules.cs:1-40`（具名规则：VBA 运行期错误按 End、`Modify` 按 ok、Simulation 保存 Yes/No、`Make Dimension Driven` 按 cancel、FeatureWorks 按 decline；注释「只对声明它的操作生效」）· `Win32/Dialogs.cs`（5452 字节）· `Win32/DialogWatchdog.cs`（3336 字节）
- `src/SolidWorksMcp.Core/Com/StaDispatcher.cs`（16631 字节，单 STA 调度）· `Com/ComArgs.cs`（5147 字节）· `Com/OperationContext.cs`（2507 字节）
- `src/SolidWorksMcp.Server/Hosting/CatalogCheck.cs`（7453 字节，目录约定 + 平均工具字节预算）· `Hosting/Guide.cs`（21480 字节，`sw_help` 正文）· `Hosting/Instructions.cs`（3446 字节）· `Hosting/ToolErrorFilter.cs`（7995 字节）
- `src/SolidWorksMcp.Server/Tools/*.cs`（25 个工具类，`[McpServerToolType, Toolset("…")]`；`SketchTools.cs` 里 `sketch_start`/`sketch_add`/`sketch_import` 的 `[Description]` 写法）
- `tests/SolidWorksMcp.LiveTests/ContractTests.cs:1-30`（「Contract tests that need the build (SOLIDWORKS installed) but not a running SOLIDWORKS」；工具目录预算断言）
- `README.md`「Why another SolidWorks MCP server?」（自述前作「about 115 of 187 tools were broken or silently wrong」）·「Typed calls」「No fake success」「Selection that works」「No hangs」「Safe by default」「Built for agents」·「Live test status」（2025 SP1.2、425 live tests、逐域数量表）·「Known issues」·「Conventions」（mm/deg/kg、Y-up、`{id}/{at}/{name}/{where,expect}`）
- 实测计数：`[McpServerTool(` ⇒ 161（分域：`sketch_edit` 14、`drawing` 16、`properties` 15、`body` 13、`assembly` 12、`feature_mgmt` 12、`part_feature` 11 …，逐文件计数见该命令的输出）；`[Fact|Theory` ⇒ 492
- 元数据：`gh api repos/soheil-mp/solidworks-mcp`（2026-11-02 取：stars 10 / MIT / created 2026-10-23 / pushed 2026-10-31）

## 9. 未确认事项

1. **未编译未跑**：缺本机互操作程序集与 .NET 配置，`161` 个工具与 `FeatureVerifier` 的真机行为**全部未验证**；自述的「425 live tests 全过」属【宣称】。
2. **`expect` 是否对所有工具都强制**：`EntityResolver` 只在给了 `where` 时才检查；**不给 `where` 只用 `at` 时是否有兜底断言，未逐路径确认**。
3. **`id` 的生成与失效规则**：是否每次列举重排、是否在重建后仍指向同一个面，**未读到实现**（只看到它建议优先用 `where`）。
4. **`DIALOG_BLOCKING` 的返回时机与恢复**：`dialog_list`/`dialog_respond` 能在 SolidWorks 阻塞时工作的原理（是另起线程发 Win32 消息？）**未读代码确认**。
5. **`AverageToolBudget` 的具体数值**：只读到测试里有这个常量与断言，**数值未取**。
6. **`wt`/`st` 之外的工具集分层**（`Toolset("sketch")` 等标签是否用于按需加载工具）：只见标签，**未确认是否支持分组启用**。
7. **与 SW2026 的兼容性**：只在 2025 SP1.2 上测过，我方环境不同，**未验证**。
