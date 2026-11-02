# kumar1441/forge_ai

<!-- survey: class=H; repr=feature-tree; orchestration=loop; verify=geometry-gate; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `kumar1441/forge_ai` · https://github.com/kumar1441/forge_ai |
| 许可 | **MIT**（`LICENSE:1-3` = `MIT License` / `Copyright (c) 2026 Ravi`）⇒ 可读可抄可商用，保留版权声明 |
| 元数据 | stars 6 · forks 1 · 语言 C#（561 个 `.cs`）· 仓库 21068 KB · 建档 2026-08-05 · 最近推送 2026-09-02（来源：`gh api repos/kumar1441/forge_ai`，2026-11-02 取）|
| 克隆 | `D:\swagent-2026Q4\repos\kumar1441__forge_ai`（`--depth 1`）|
| 证据等级 | **读码**（**仓内没有任何测试工程**：`*.csproj` 只有 `solidworks/Forge.SolidWorks.csproj` 与 `inventor/Forge.Inventor.csproj` 两个，`xunit|nunit|MSTest` 命中 0；C# 需本机 SolidWorks 互操作程序集，**未编译未跑**；建模能力结论止步 `source`）|

## 1. 一句话定位

**把「独立复算」写成教义并真的为每条命令写了第二套测量实现的一家**：`GroundTruth` 有 237 个按命令拆分的独立测量文件，明写「与执行管线不共享任何代码」，每条命令回一个 `Verified` 布尔，验不过就 fail-closed 报错。（`solidworks/Harness/GroundTruth.cs`）

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：SolidWorks add-in（`net48` C#，`WebView2` 面板 `solidworks/panel.html` 44 KB）。用户在面板里说一句话，主进程按 `docs/ARCHITECTURE.md`「Intent pipeline」分五段：**parse**（请求 → 结构化动作 + 目标）→ **resolve**（动作 → 处理器；可选 LLM / 无 LLM 的正则本地路 / 本地路）→ **confirm-or-ask**（有歧义就问，不猜）→ **execute** → **verify**（用与执行无关的独立检查复测）。

**中间表示**：**一张处理器规格表**（不是几何 IR）。`solidworks/ForgePanel.Pipeline.cs:58-70` 的 `HSpec { Name, Actions[], AssemblyOnly, Destructive, Preview, Execute }`；实测 `new HSpec` 计数 **270** 条（`(Select-String -Path 'solidworks\ForgePanel*.cs' -Pattern 'new HSpec' -AllMatches).Count` ⇒ 270）。特征/装配几何本身仍由 SolidWorks 特征树承载。

**生成**：不生成代码；两种解析路径——LLM（BYOK，`shared/Forge.Providers/` 有 Anthropic 与 OpenAI 兼容两个客户端，密钥 DPAPI 加密、当前用户范围）与**无 LLM 的确定性本地解析**（`README.md`「Works with zero LLM」：相当一部分命令走本地正则，免费离线）。

**编排**：单轮 loop（parse→resolve→ask→execute→verify）。**没有多轮规划**，没有 `build_part` 式的整件计划口。

**执行**：单个 `solidworks/` 工程内直接调 COM 互操作（`ISwAdapter` 只出现在注释与文档里，**代码里没有这个接口**，见 §5 #1）。

**验证**：**本批最强的一档**（见 §3.2）。

**交付**：`export_stl` / `export_file` / `FlatDxf` / 工程图族（`add_drawing_view`/`insert_bom`/`update_revision_table`），`deliver` 覆盖 STEP/STL/DXF/工程图。

## 3. 技术方案要点（可迁移的机制）

### 3.1 工具面与粒度：**270 条命令规格**（实测计数，与 README 的 283 有差）（`solidworks/ForgePanel.Pipeline.cs`）

计数命令与结果：`(Select-String -Path 'solidworks\ForgePanel*.cs' -Pattern 'new HSpec' -AllMatches).Count` ⇒ **270**；`Name = ` 出现 276 次（含少量非 HSpec 的赋值）。`README.md` 自述「283 tools」、`docs/ARCHITECTURE.md` 自述「~260 handlers」——**三者不一致**，本卡以实测 270 为准。
粒度 = **一动词一规格**（`mate`/`explode`/`isolate`/`mirror`/`scale`/`set_dimension`/`add_hole`/`add_counterbore`/`insert_bom`/`update_revision_table`…），**没有万能代码口、没有整件计划口**。按域看它比 A 线其他家更「装配 + 图样」重：`AutoMate`（螺栓全自动配合，75 KB）、`RedWave`（31 KB，红波浪=过定义配合诊断）、`ConvertStepToParametric`（43 KB，STEP 转参数化）。（`solidworks/ForgePanel.Pipeline.cs` 的 `HSpec.Actions`）

### 3.2 独立复算（GroundTruth）：本卡的核心价值

**教义原文**（`docs/ARCHITECTURE.md`「GroundTruth doctrine」）：「Every mutation Forge makes is independently re-measured before it is reported as done: the verification never reuses the code path that performed the edit, and the expected result is derived by a separate `GroundTruth.*` pass from the raw model state — never from Forge's own claims.」而 `solidworks/Harness/GroundTruth.cs:9-18` 的类注释把动机讲得更狠：「Deliberately shares NOTHING with the AutoMate pipeline's geometry interpretation or its self-reported verdicts — it re-reads post-rebuild geometry from the SolidWorks API with its own code so the harness cannot inherit **the self-certification blind spots we killed all day**.」

**规模**：`solidworks/Harness/GroundTruth.cs` 94875 字节，另有 **237 个** `GroundTruth.<命令>.cs` 分文件（`(Get-ChildItem solidworks\Harness -File -Filter 'GroundTruth.*.cs').Count` ⇒ 237）——即**每条命令一份独立测量实现**，例如 `GroundTruth.MeasureBoltCircle.cs` 18954 字节、`GroundTruth.DescribeGeometry.cs` 9761 字节、`GroundTruth.FilletChamfer.cs` 9254 字节。

**判据形状**：每条命令回 `HOutcome`（`ForgePanel.Pipeline.cs:27-38`），字段 `Verified` 的注释就是口径——「fail closed: only true when the handler CONFIRMED the result (geometry / read-back / clean rebuild)」，另有 `AskedConfirm`/`Question`（歧义就提问）与 `Card`（面板卡片）。全仓 `HOutcome` 出现 **596 次**（同文件命令：`(Select-String -Path 'solidworks\*.cs' -Pattern 'HOutcome' -AllMatches).Count`），`FailClosed|fail-closed|FAIL CLOSED` 出现 **258 次**。

**⇒ 可迁移的两条**：① **验证代码与执行代码物理分离**（不同文件、不同作者意图、禁止复用）；② **每条命令自带一个 `Verified` 布尔 + 人类可读的失败理由**，且失败要 fail-closed（不改模型或回滚）。

### 3.3 无头回归台：**请求文件投递 + 双跑幂等检查**

`solidworks/Harness/Harness.cs`（205998 字节）是一个**运行在 add-in 内的测试台**（注释：「Everything here runs INSIDE the add-in (the only place COM works on this 3DEXPERIENCE build)」），由外部编排脚本 `run-harness.ps1` 往约定路径丢一个请求 JSON（`{assemblyPath, handlerIntent, resultPath, screenshotPath}`），面板里一个轮询定时器认领后：**打开装配 → 跑处理器 → 用 GroundTruth 独立测量 → 把同一处理器再跑一遍查幂等 → 截图 → 写结果 JSON → 不保存关闭**。

配套还有一条很实的运维知识：`CleanOrphanLocks` 清 `~$` 锁文件，注释写明「崩溃会留下 6 字节锁文件，下次打开时 SolidWorks 以为文件被别处打开 ⇒ 冻结或只读」，并给了危害量级（「会在一小时内杀死 24/7 测试循环」）。

⇒ **可迁移的是这个形状**：当 COM 只能在被调进程内跑时，用「文件投递 + 进程内轮询」当控制通道，并把「**双跑幂等**」作为判据的一部分。我方若有长跑回归需求，这是现成范式。

### 3.4 依赖「第二套实现」的代价：它与真实代码的落差

`docs/ARCHITECTURE.md` 描述六模块（`Forge.Core` / `Forge.Providers` / `Forge.Handlers` / `Forge.Sw` / `Forge.Telemetry` / `Forge.Ui`）与「one class per handler, `IForgeHandler`」，但**代码里不存在**：`IForgeHandler` 命中 0，`solidworks/` 是单工程（一个 420 KB 的 `ForgePanel.Pipeline.cs` + 一堆按命令命名的 20–40 KB 文件），`shared/` 只有 `Forge.Cad` / `Forge.Providers` 两个库。⇒ **文档描述的是目标架构，不是现状**。这条必须写进结论：**它的「分层」目前是意图，不是事实**。

### 3.5 领域坑手册（本轮质量最高的单份文档之一）

`docs/SOLIDWORKS-GOTCHAS.md`（18235 字节）按「能用的读 / 死掉的读 / 静默无效的写 / 返回码与枚举 / 偏好与会话 / 几何读取雷区 / 配合最佳实践 / 自然语言解析坑」分章，每条给「症状 + 根因 + 修法」，且标注是在 **3DEXPERIENCE SOLIDWORKS Design R2026x** 上真机踩的。本卡挑出对我方直接有用的 12 条（原文均有行号可查）：

1. **`swAddMateError_NoError = 1`，不是 0**：判 `== 0` 会丢掉所有好配合；`code=5` 是过定义但**配合已创建**（要捕获对象再删）。
2. **`swSuppressionChangeOk = 2`**（0=组件坏、1=状态坏、3=失败）。
3. **`swDimensionDrivenState_e` 是反的**：`Unknown=0, Driven=1, Driving=2`。
4. **`FeatureFillet3` 不带 `swFeatureFilletUniformRadius` 就返回 NULL**；且**给长方体 12 条边全倒角会在 8 个角上失败**（真实单圆角限制，只能倒子集）。（`docs/SOLIDWORKS-GOTCHAS.md`）
5. **`SketchTrim` 成功也返回 False**：只能按几何判（非构造段长度确实下降）。
6. **`IEquationMgr.Add/Add2/Add3` 全是死的**（返回 -1，任何插入位置/字符串格式/配置范围）——读能用，写不能。
7. **`FullyDefineSketch` 返回 `swAutodimStatusSuccess(0)` 但草图永远停在 `swUnderConstrained(2)`**。
8. **`Component2.GetBox` 返回 NULL**（用 `Transform2` 的平移槽 `[9,10,11]`）；**`IComponent2.IsSuppressed()` 对轻化组件返回 TRUE**（唯一诚实判据是 `GetSuppression2() == swComponentSuppressed(0)`）。
9. **`FeatureFillet3`/`FeatureChamfer` 返回 `int` 不是 `IFeature`**（SW2025+），`.Name` 会炸。
10. **`ToolsCheckInterference2` 是 Sub**，晚绑定下 out 参数永远 None ⇒ 永远「无干涉」。
11. **特征类型名不是猜的**：切拉伸报 `"ICE"` 不是 `"Cut"`；特征树遍历还会列出 11 个空容器文件夹（`CommentsFolder`/`EqnFolder`/…），必须跳过所有 `*Folder`；**特征文件夹是扁平「起止标签」区间**（`Name|FtrFolder` … `Name___EndTag___|FtrFolder`），`GetFirstSubFeature()` 返回空。（`docs/SOLIDWORKS-GOTCHAS.md`）
12. **`GetTessTriangles` 会返回离实体几十米的伪顶点**，且 `GetClosestPointOn` 在**面所属零件的局部坐标系**里（装配里要先 `Transform2.Inverse()`）。

★ 这份清单与我方 `docs/known-facts.md`/`dead-ends.md` 的对应度极高，**是最值得交叉验证的一份外部台账**（见 §9 的分歧点）。

### 3.6 四件套：它解了哪几件

- **持久引用**：无拓扑 ID；有 `SelectFace`/`SelectEdge` 族工具与 `GetSelectedEntities`（读 GUI 当前选择），选择靠用户/几何谓词，**未见跨调用的引用句柄**。
- **回读验证**：**解了，且是本批最强**（§3.2）。
- **事务式建模**：**部分**——教义写「rolls back or leaves the model untouched」，代码侧只有 `HOutcome.Error` 与 `AutoMate` 的**按紧固件原子回滚**（`docs/SOLIDWORKS-GOTCHAS.md`「Mating best practices」段：「Per-fastener ATOMIC rollback … Roll back per fastener, never the whole run」）；没有全局的特征树快照回滚（对比 `sw-hjbaard-solidworks-mcp.md` §3.3）。
- **单源 COM 互斥**：单 add-in 进程一档；且**它把这一点变成了架构约束**——Harness 之所以必须跑在 add-in 内，正是因为「COM 只在那里面能用」。

## 4. 运行条件与依赖

- Windows + SolidWorks 2022+ + .NET Framework 4.8 + VS2022（或 Build Tools）；`dotnet build solidworks/Forge.SolidWorks.csproj -c Release -p:Platform=x64`，然后 `regasm /codebase`（管理员）注册。
- 需要本机 SolidWorks 互操作程序集（`solidworks/Forge.SolidWorks.csproj` 的 `HintPath` 需指向 `…\SOLIDWORKS Corp\SOLIDWORKS\api\redist\`）。
- LLM 可选：BYOK（Anthropic / OpenAI 兼容 / Ollama），密钥 DPAPI 加密、当前用户范围；**无密钥也能用本地解析路径**。
- 遥测默认关闭、可选开启（`solidworks/Telemetry.cs`、`ForgeData.cs`，README「Data & privacy」段）。
- 测试：**无**（见字段表）；回归靠 §3.3 的 Harness，但**驱动脚本 `run-harness.ps1` 不在仓内**。

## 5. 失败模式与已知坑

1. **文档 ≠ 现状**：`docs/ARCHITECTURE.md` 的六模块与 `IForgeHandler` 在代码里不存在（`IForgeHandler` 命中 0）；照文档读代码会找不到落点。
2. **仓内没有测试工程**：`README.md`/`CONTRIBUTING.md` 说「one new command is one spec row + one handler + one test」、「~260 handlers … one test」，但 `*.csproj` 只有 2 个、`xunit|nunit|MSTest` 命中 0 ⇒ **测试承诺没有兑现进仓**。
3. **`run-harness.ps1` 缺失**：Harness 的注释点名它，仓内 `*.ps1` 只有 installer/register/unregister 三个 ⇒ 回归台**跑不起来**（缺驱动）。
4. **单文件 420 KB**：`solidworks/ForgePanel.Pipeline.cs` 420896 字节，270 条 HSpec 全在里面；`Name = ` 计数与 `new HSpec` 计数不一致（276 vs 270）说明同一文件里还有别的赋值——**可维护性差，且这类文件几乎不可能被 review 完整**。
5. **`Verified` 的语义边界**：「clean rebuild」也是通过条件之一，意味着**未重建成功的命令会被判未验证**——这是好事，但也意味着 Verified 不等于「几何对」，只是「按该命令自己的判据过」。
6. **能力口径混乱**：README「283 tools」/ ARCHITECTURE「~260 handlers」/ 实测 270 条 HSpec 三处不一致。（`README.md`、`docs/ARCHITECTURE.md` 与实测对比）
7. **前置条件重**：`regasm /codebase` 需要管理员、需 VS2022、需互操作 DLL 路径正确——一次装不成就卡住整条链。

## 6. 对我方目标的可用处（能学 / 不能学）

**Q2 逐条答**：
| 问题 | 它解到什么程度 | 依据 |
|---|---|---|
| 持久引用 | **没解**：无跨调用引用句柄；靠 `SelectFace`/`SelectEdge` 与 `GetSelectedEntities` | `solidworks\Harness\GroundTruth.SelectFace.cs`、`GetSelectedEntities.cs` |
| 回读验证 | **解了，本批最强**：237 个独立测量文件 + 每命令 `Verified` + fail-closed | `docs/ARCHITECTURE.md`「GroundTruth doctrine」、`solidworks\Harness\GroundTruth.cs:9-18` |
| 事务式建模 | **部分**：教义写回滚/不动模型；代码见按紧固件原子回滚，无全局快照回滚 | `docs/SOLIDWORKS-GOTCHAS.md`「Mating best practices」 |
| 单源 COM 互斥 | **解了进程内一档**，并把「COM 只能在被调进程内」升格为架构约束 | `solidworks\Harness\Harness.cs:15-21` |

**Q3 答**：**不是 MCP 服务端、不是 CLI、不是库——是 SolidWorks add-in 应用（自带面板与 intent 管线）**；工具面 **270 条命令规格**（`solidworks/ForgePanel*.cs` 的 `new HSpec`）；粒度 = **一动词一规格 + 歧义即提问**（`AskedConfirm`），无万能代码口、无整件计划口。

**能学（按性价比排序）**：
1. **「验证代码与执行代码物理分离」+ 每命令一个 `Verified` 布尔**：这是我方 `verify` 从 `run-only`/`run-only+numeric` 升级的最短路径，且**判据归属明确**（服务端算，不是模型算）。
2. **`docs/SOLIDWORKS-GOTCHAS.md` 的 12 条**（§3.5）：性价比极高，可直接与我方 `known-facts` 交叉验证并补负例测试——尤其 #1（`NoError=1`）、#5（`SketchTrim` 假 False）、#6（方程写死）、#8（`GetBox` NULL / 轻化≠抑制）、#10（Sub 的 out 参数）、#11（`ICE` 类型名与 `*Folder` 空壳）。
3. **`Harness` 的「文件投递 + 进程内轮询 + 双跑幂等 + 截图 + 不保存关闭」**：长跑回归的现成范式，尤其「双跑查幂等」这一判据我方目前没有。
4. **`~$` 锁文件的运维知识**：崩溃残留会伪装成「文件被占用」并冻结下次打开——便宜且高杀伤。
5. **`HOutcome` 的字段设计**（`Verified`/`AskedConfirm`/`Question`/`Card`）：把「成功」「需要确认」「有歧义要问」三态放进同一个返回结构，比抛异常或返回字符串更可判。
6. **无 LLM 的确定性本地解析路径**：同一命令两条路（LLM / 正则），可离线、可测；对我方「先验收后能力」的思路是支撑。

**不能学**：
- **单文件 420 KB 的管线**：这是「一动词一规格」的反面代价，不可维护也不可 review。（`solidworks/ForgePanel.Pipeline.cs`）
- **文档先行于实现**（ARCHITECTURE 描述不存在的模块）：我方 `docs/` 与 `scripts/` 的漂移已有门禁，这里正好是一个反面样本。
- **不要照抄它的「Verified」定义**：它的 `Verified` 是「按该命令自己的判据过」，**不等于几何正确**；我方若引入同名概念，必须把判据写进字段文档（否则又是一个 `stitched` 写成 `verified` 的陷阱）。
- **把测试承诺写在 README 而仓内没有测试**。

## 7. 许可与红线

**MIT**（`LICENSE:1-3`，`Copyright (c) 2026 Ravi`）。可移植，义务：保留版权声明。★ 移植 `GroundTruth` 的「独立复算」形状、`Harness` 的文件投递+双跑幂等、以及把 `SOLIDWORKS-GOTCHAS.md` 的事实并入 `known-facts.md` 时：来源头写 `kumar1441/forge_ai（MIT，LICENSE:3）` + 改动说明；**事实本身不受版权保护，但那份文档的措辞受**——并入时须自己重写句子，不得整段搬文本。

## 8. 证据清单

- `docs/ARCHITECTURE.md`（六模块表、「Intent pipeline」五段、「Handler catalog」~260 handlers、**「GroundTruth doctrine」全段**）
- `docs/SOLIDWORKS-GOTCHAS.md:1-274`（全文；本卡引用的 12 条分布在「Return codes & enums」「Writes that silently no-op」「Model & geometry reading landmines」「Mating best practices」「Natural-language parsing pitfalls」各章）
- `solidworks/ForgePanel.Pipeline.cs:27-38`（`HOutcome` 定义，`Verified` 的 fail-closed 注释）· `:58-70`（`HSpec` 定义）· `:60`（`mate` 规格样例：`Verified = mr.RebuildClean && mr.Proud == 0`）
- `solidworks/Harness/GroundTruth.cs:9-31`（「shares NOTHING with the pipeline」的教义与动机 + `MeasureByKey` 分支表）
- `solidworks/Harness/Harness.cs:15-21`（进程内测试台；请求 JSON 四字段；「open → run → ground truth → second run → screenshot → result → close without saving」）· `:29-66`（`CleanOrphanLocks` 与 `~$` 锁文件的危害）
- `solidworks/AutoMate.cs`（75046 字节，螺栓全自动配合）· `solidworks/RedWave.cs`（30961 字节，过定义配合诊断）· `solidworks/ConvertStepToParametric.cs`（43545 字节）
- `shared/Forge.Providers/`（`AnthropicClient.cs`、`OpenAiCompatibleClient.cs`、`KeyStore.cs` 3028 字节 = DPAPI 存储）· `shared/Forge.Cad/ICadAdapter.cs`（816 字节）
- `solidworks/Forge.SolidWorks.csproj`（5010 字节，`HintPath` 指向互操作程序集）
- 实测计数：`new HSpec` ⇒ 270；`GroundTruth.*.cs` ⇒ 237；`HOutcome` ⇒ 596；`FailClosed|fail-closed|FAIL CLOSED` ⇒ 258；`*.csproj` ⇒ 2；`IForgeHandler` ⇒ 0；`xunit|nunit|MSTest` ⇒ 0；`run-harness.ps1` 不在 `*.ps1` 列表内
- 元数据：`gh api repos/kumar1441/forge_ai`（2026-11-02 取：stars 6 / MIT / pushed 2026-09-02）

## 9. 未确认事项

1. **未编译未运行**：`dotnet build` 需要本机互操作程序集路径正确，本卡**未尝试**；270 条命令与 237 个 GroundTruth 文件的真实通过率**未知**。（`solidworks/ForgePanel.Pipeline.cs`、`solidworks/Harness/`）
2. **`Verified` 在各命令上的实际判据**：我只读了 `mate` 一条与 `GroundTruth` 的总纲，**237 个文件里的具体判据未逐条核**（`solidworks/Harness/GroundTruth.cs` + 237 个分文件）（其中「是否真的与执行代码不共享任何函数」也未逐文件验证，只有作者声明）。
3. **`run-harness.ps1` 是否在别处发布**（release 资产/issue 附件）：仓内没有，**未查**。
4. **README「283 tools」与实测 270 条的差**：是有 13 条未进 `HSpec`（例如走 WebView2 侧的前端动作），还是文档过期，**未确认**（`README.md` 与实测计数）。
5. **与 `docs/SOLIDWORKS-GOTCHAS.md` 的事实冲突点**：例如它说 `FullyDefineSketch` 完全无效、`IEquationMgr.Add` 全死——这两条与「其他家在真机上用通了」并不必然矛盾（版本/方式不同），但**需我方在 SW2026 上逐条复验**，本卡不下结论。
6. **`AutoMate` 的「按紧固件原子回滚」实现位置**：文档有口径，**代码里未定位到对应函数**，未确认。
7. **遥测上传的实际字段**：只读 README 的白名单描述与 `Telemetry.cs` 文件名，**未核代码是否与声明一致**。
