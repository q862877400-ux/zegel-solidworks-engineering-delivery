# qdaia/Auto-SolidWorks

<!-- survey: class=D; repr=dsl; orchestration=loop; verify=geometry-gate; deliver=drawing; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `qdaia/Auto-SolidWorks` · https://github.com/qdaia/Auto-SolidWorks |
| 许可 | **MIT**（`LICENSE:1-3` = `MIT License` / `Copyright (c) 2026 Auto SolidWorks contributors`）；但**内含第三方**：`plugins/auto-solidworks/surface/CurvesWB/` 整包 vendored **LGPL-2.1-or-later**（其中 TiGL 派生的 Gordon/BSpline 算法是 Apache-2.0），`THIRD_PARTY_NOTICES.md` 已逐项声明并保留原许可文本 ⇒ 我方若取材，**只能取 MIT 部分的机制，不得取 CurvesWB 的代码** |
| 元数据 | stars 7 · forks 0 · 语言 C#（277 个 `.cs`）+ Python（160 个 `.py`）+ 90 个 `.md` · 仓库 11492 KB · 建档 2026-09-06 · 最近推送 2026-10-25（来源：`gh api repos/qdaia/Auto-SolidWorks`，2026-11-02 取）|
| 克隆 | `D:\swagent-2026Q4\repos\qdaia__Auto-SolidWorks`（`--depth 1`）|
| 证据等级 | **读码**（C# 需本机 SolidWorks 互操作程序集、`dotnet` 构建；`tests/` 是 20 个 Python 脚本且多数要真机；**未跑**。SolidWorks 未跑，建模能力结论止步 `source`）|（`tests/cases.py` 等 20 个脚本；`src/AutoSolidWorks.ModelingMcp/Program.cs`）

## 1. 一句话定位

**本批唯一带「建模中间表示（IR）」并且把「执行」推到独立 Windows 进程的一家**：入口是工程图/尺寸 → 识别 → 尺寸绑定 → 编译成 IR → 执行 → 回读验收；口径上明写「持久引用、执行租约、回执区分完成/失败/未知」，也明写「本次发布没有重跑原生建模验收」——**文档诚实度最高的一份**。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：Codex 插件（`plugins/auto-solidworks/.codex-plugin`）+ `skills/auto-solidworks`（含 `references/capability-manifest.json`）+ MCP 工具面。原始输入是**工程图/PDF/显式尺寸**（`README.en.md`：「Provide an engineering image, PDF or explicit dimensions」）。

**中间表示**：**真的有 IR**——`src/CadModeling.Ir/` 22 个文件，包括 `DesignIntent.cs`、`NativeFeatures.cs`、`SketchEditing.cs`、`DimensionExpressions.cs`、`DrawingDimensionTrace.cs`、`DrawingGeometryAnchors.cs`、`DrawingShapeDecomposition.cs`、`ShapeVerification.cs`、`VerificationAndRecovery.cs`、`PerformanceTrace.cs`。`docs/architecture.en.md` 的分层表把它写成「Modeling IR：represent operation dependencies, units, configurations, geometry references, outputs and acceptance requirements」⇒ **依赖、单位、配置、几何引用、输出、验收要求全部进 IR**，这是本批唯一做到的一档。

**生成**：四段固定流水（`README.en.md`）：「**recognition → dimension binding → compile → model**」，末尾产出原生文件。工具名与四段对得上：`cad_read_drawing` → `cad_find_source_geometry`/`cad_find_source_circles`/`cad_parse_source_callout`/`cad_prepare_binding_workspace`/`cad_add_binding_crops` → `cad_bind_source_dimensions`/`cad_bind_source_geometry`/`cad_assemble_source_bindings`/`cad_compile_binding_review` → `cad_create_model_plan`/`cad_build_model` → `cad_inspect_model`/`cad_verify_*`/`cad_review_model_delivery`。

**编排**：有状态机而不是单轮——`cad_execution_status`、`cad_pause_execution`、`cad_read_result`，以及 `docs/architecture.en.md` 的「Build identity binds production-source, capability-manifest and runtime hashes」。

**执行**：**独立进程**。分层表写「SolidWorks executor：Call local SolidWorks from **a separate Windows process**, creating native features and saving/reopening/readback」⇒ 它把「执行」与「推理/MCP」进程隔开，并用**执行租约**限制并发（「A native execution lease limits concurrent access」）——这是本批唯一显式处理「单源互斥」的一种形态。

**验证**：**回读 + 回执**。「receipts distinguish completion, failure and **unknown** outcomes」（`docs/architecture.en.md`）——★ 承认「未知」这一档，是本轮所有项目里唯一明确区分「不知道成没成」的。另有 `cad_verify_hole_group` / `cad_verify_edge_treatment` / `cad_verify_revolved_family` 三个族级验收工具、`ShapeVerification.cs`、以及「local/whole-model geometry checks」与「repair receipts」（`README.en.md`「Existing models」行）。

**交付**：`cad_export_drawing`（SLDDRW / PDF 第一角投影，含尺寸导入、布局与分页）、零件 SLDPRT/STEP/STL、装配 SLDASM（`README.en.md` 工作流表）。

## 3. 技术方案要点（可迁移的机制）

### 3.1 工具面与粒度：**32 个唯一工具名（43 个注册点）**，是「阶段工具」不是「几何动词」（`src/AutoSolidWorks.ModelingMcp/Program.cs`）

计数命令与结果：`(Select-String -Path 'src\AutoSolidWorks.ModelingMcp\*.cs' -Pattern 'McpServerTool\(Name="([^"]+)"' -AllMatches).Matches` ⇒ **43 个注册点、32 个唯一名字**（重复来自 `Program.cs` 里按 `profile == "full"` 追加注册 `AdvancedModelingTools`——同一工具出现两次）。名字全部 `cad_*`，且**按流水阶段命名**（`read_*` / `find_*` / `bind_*` / `compile_*` / `create_model_plan` / `build_*` / `verify_*` / `review_*` / `export_*`）。

⇒ 粒度是**第三档**：既不是「一动词一工具」（Millwright/hjbaard/soheil-mp 那一档），也不是「一个万能口」（infei12306），而是**「一阶段一工具 + IR 承载细节」**。这是唯一能在不改工具面的前提下扩展几何能力的结构——因为细节进 IR 不进工具签名。

### 3.2 持久引用 / 事务 / 互斥：**三件都有明确的架构位**

`docs/architecture.en.md` 末段一句话把三件事全点了：「A native execution **lease** limits concurrent access; **receipts** distinguish completion, failure and unknown outcomes. **Checkpoints and persistent references** determine whether a recovery prefix remains valid.」

- **持久引用**：IR 里的 `geometry references` + 恢复时要判「引用是否仍然有效」（recovery prefix validity）⇒ 它不只存引用，还**判引用失效**。
- **事务式建模**：checkpoint + receipt（完成/失败/**未知**）⇒ 三态而不是二态。
- **单源互斥**：`lease`（跨进程租约）。

★ **注意**：以上是 **架构文档的声明**，本卡未在代码里逐条定位到实现（见 §9）。相比之下 hjbaard 的回滚（`sw-hjbaard-solidworks-mcp.md` §3.3）与 soheil-mp 的 `expect` 断言（`sw-soheil-mp-solidworks-mcp.md` §3.1）是**代码级可核**的。⇒ 本卡把 qdaia 的这三条标为**待核**，价值在于「它认为该这么设计」，不在于「它已经这么做了」。

### 3.3 「回执三态」：把我方最怕的一类失败显式化

它的口径是 completion / failure / **unknown**。我方最贵的坑之一正是「工具报成功但几何没变」（Millwright 与 forge_ai 都记录了同类）。⇒ **引入 `unknown` 这一档**（而不是硬塞进成功或失败）是低成本高收益的改法：回读拿不到、重建状态不明、弹窗未清时，如实报「未知」，而不是猜。

### 3.4 工程图作为一等输入：本批唯一的「图纸 → 参数化」

`README.en.md` 的工作流表把输入写成「engineering image, PDF or explicit dimensions」，并把「recognition → dimension binding」独立成两个阶段，还配了 `cad_add_binding_crops`（绑定裁图）、`cad_review_drawing_coverage`（图纸覆盖度复核）、`cad_compare_source_projection`（源投影比对）、`DrawingOmission.cs`/`DrawingCalloutReview.cs`/`DrawingDimensionTrace.cs`（IR 侧的遗漏/标注/尺寸溯源）。⇒ 这是「图纸驱动」而不是「对话驱动」，与我方 E4/E5（图样合规）方向最近的一家。

### 3.5 诚实度：三处主动降级声明

1. `README.en.md` 发布说明：「Release validation and native CAD acceptance are recorded separately; **native modeling is not rerun for this release**.」⇒ **明说本次没重跑原生建模验收**。
2. `docs/architecture.en.md` 的「Build identity binds production-source, capability-manifest and runtime hashes」⇒ 用哈希绑定「代码版本 ↔ 能力清单 ↔ 运行时」，防「清单说有、代码没有」。
3. `THIRD_PARTY_NOTICES.md` 逐项列 vendored 许可并声明「This does not relicense those files under the project's MIT license.」

⇒ 这三条分别对应我方 A7（不把 stitched 写成 verified）、五统一对账、许可红线——**是现成的「怎么写才不算吹」的样本**。

## 4. 运行条件与依赖

- Windows x64 + SolidWorks（本地）+ .NET（`Directory.Build.props` 固定）+ Python 3（`tests/` 与部分脚本）。
- 安装：`install.ps1`；下载页 `docs/download.en.md`；发布 `v1025`（版本号即日期 `1025` = 2026-10-25，与 `README.en.md` 的「Version 1025 · 2026-10-25」一致）。
- Codex 插件形态：`plugins/auto-solidworks/.codex-plugin` + `skills/auto-solidworks`（含 `references/capability-manifest.json`、`references/progressive-native-evidence/`）。
- 第三方运行时：本地 FreeCAD/OpenCascade **不打包**（`THIRD_PARTY_NOTICES.md`：只打包 CurvesWB 源码，FreeCAD/OCCT 需另行安装）。
- 测试：`tests/` 20 个 Python 文件（`cases.py` 24979 字节、`focused_three.py` 13516、`local_geometry.py` 13421、`contract_cases.py` 2748 等），多数要真机；**未跑**。

## 5. 失败模式与已知坑

1. **文档-实现落差风险最高的一家**：`docs/architecture.en.md` 声明了 lease / receipts / persistent references / checkpoints，**我在代码里只定位到 `ArtifactFreshness.cs`（13037 字节）、`VerificationAndRecovery.cs`（8467）等候选文件，未逐条确认落地**（§9）。
2. **C# + 独立执行进程 + 插件 skills + IR 四件套**⇒ 安装与调试面最宽：任何一环（互操作程序集、进程启动、MCP 注册、skill 加载）出问题都表现为「模型不像」。
3. **第三方 vendored 代码**：`plugins/…/surface/CurvesWB/` 是 LGPL-2.1-or-later 整包，**改它会引入 copyleft 义务**；取材时必须绕开。
4. **本次发布未重跑原生建模验收**（README 自述）⇒ 能力声明与最新代码状态**可能不同步**。
5. **`profile == "full"` 才注册 `AdvancedModelingTools`**（`Program.cs`）：默认 profile 下部分能力不可见，工具面随配置变化——对账时容易误判「没有这个工具」。
6. **中文为主**：主 README 是中文，英文版是 `README.en.md`；`docs/` 52 个文件里大量 `.zh-CN.md`。术语对照需小心（如「原生」= native）。
7. **规模**：749 个文件（非 bin/obj）、11.5 MB，是本批第二大的仓库（仅次于 forge_ai）；**没有测试工程**（`.csproj` 是功能工程，测试是 Python 脚本）。

## 6. 对我方目标的可用处（能学 / 不能学）

**Q2 逐条答**：
| 问题 | 它解到什么程度 | 依据 |
|---|---|---|
| 持久引用 | **声称有**（IR 的 geometry references + recovery 时判引用是否仍有效），**代码未逐条核** ⇒ 待核 | `docs/architecture.en.md` 末段 |
| 回读验证 | **有族级验收工具**（`cad_verify_hole_group`/`cad_verify_edge_treatment`/`cad_verify_revolved_family`）+ 回执三态；代码未核 | `src/AutoSolidWorks.ModelingMcp/AdvancedModelingTools.cs`、`docs/architecture.en.md` |
| 事务式建模 | **声称有**（checkpoints + receipts + recovery prefix）；代码未逐条核 ⇒ 待核 | 同上 |
| 单源 COM 互斥 | **声称有**（native execution lease，跨进程）；代码未核 ⇒ 待核 | 同上 |

**Q3 答**：**混合形态**——Codex 插件（skills）+ **MCP 服务端**（C#，32 个唯一工具名）+ 独立执行的 SolidWorks 进程。粒度 = **一阶段一工具 + IR 承载细节**（第三档，见 §3.1）。（`src/AutoSolidWorks.ModelingMcp/CompactModelingTools.cs`）

**能学（按性价比排序）**：
1. **「回执三态」（完成/失败/未知）**：把我方最怕的「不知道成没成」显式化，成本极低。
2. **「持久引用 + 恢复前缀有效性」这个提法**：引用不只是「保存下来」，还要在恢复时**判它是否还有效**——这是比我方现有思路更完整的一步。
3. **IR 的字段清单**（`CadModeling.Ir` 的 22 个文件）：依赖、单位、配置、几何引用、输出、**验收要求**都在 IR 里，「验收要求」进 IR 这一点尤其值得抄（需求与验收同源）。
4. **「阶段工具」而不是「几何动词工具」**：`cad_read_* → cad_bind_* → cad_compile_* → cad_build_* → cad_verify_* → cad_review_*`。若我方要从 439 个动词工具收敛，这是唯一现存的替代范式。（`src/AutoSolidWorks.ModelingMcp/Program.cs`）
5. **build identity 哈希绑定**（代码 ↔ 能力清单 ↔ 运行时）：对我方「清单说有、代码没有」的漂移是机械判据。
6. **工程图侧的三件**：`cad_review_drawing_coverage`（覆盖度）、`cad_compare_source_projection`（源投影比对）、`DrawingOmission`（遗漏记录）——图纸驱动路线的现成工具名与职责划分。
7. **发布说明的写法**（「本次没重跑原生建模验收」）：诚实降级的模板。

**不能学**：
- **把架构文档当已实现**：本卡的三条 Q2 结论都只能标「声称」，不能标「解了」。
- **vendored LGPL 整包**：取材必须绕开 `plugins/…/surface/CurvesWB/`。
- **profile 切换导致工具面变化**：对账困难。
- **规模失控**：749 个文件、无 C# 测试工程。（`src/AutoSolidWorks.ModelingMcp/Program.cs` 与实测文件计数）

## 7. 许可与红线

**MIT**（`LICENSE:1-3`）+ **内嵌 LGPL-2.1-or-later**（CurvesWB 整包）与 **Apache-2.0**（TiGL 派生算法）——`THIRD_PARTY_NOTICES.md` 已声明且保留原文本。
⇒ 红线三条：① 只取 **MIT 部分**的机制；② **不得**复制 `plugins/auto-solidworks/surface/CurvesWB/` 下任何文件（LGPL 传染）；③ 若移植 MIT 部分，来源头写 `qdaia/Auto-SolidWorks（MIT，LICENSE:3）` + 改动说明。★ 另注意 `plugins/auto-solidworks/surface/` 是**运行期才用**的 FreeCAD 侧代码，与 SolidWorks 执行链无关，不要因为「在同一个仓里」就一并处理。

## 8. 证据清单

- `README.en.md`（「Version 1025 · 2026-10-25」；四段流水「recognition → dimension binding → compile → model」；工作流表：参数化零件 / 曲面与空间曲线 / 设计参数 / 既有模型 / 装配 / 图纸 / 执行管理；★「native modeling is not rerun for this release」）
- `docs/architecture.en.md:1-17`（五层职责表；★末段「native execution lease」「receipts distinguish completion, failure and unknown outcomes」「Checkpoints and persistent references determine whether a recovery prefix remains valid」；「Build identity binds production-source, capability-manifest and runtime hashes」）
- `src/CadModeling.Ir/`（22 个文件：`DesignIntent.cs` 3940、`NativeFeatures.cs` 8061、`DimensionExpressions.cs` 1056、`DrawingDimensionTrace.cs` 1991、`DrawingGeometryAnchors.cs` 2406、`DrawingShapeDecomposition.cs` 4092、`DrawingOmission.cs` 6119、`ShapeVerification.cs` 1443、`VerificationAndRecovery.cs` 8467、`SketchEditing.cs` 1841、`PerformanceTrace.cs` 5037、`SourceInterpretation.cs` 980 …）
- `src/AutoSolidWorks.ModelingMcp/Program.cs:41-48`（`AddMcpServer().WithStdioServerTransport().WithTools<CompactModelingTools>(…)`，并按 `profile == "full"` 追加 `AdvancedModelingTools`）· `AdvancedModelingTools.cs:8-32`（三个 `cad_verify_*`，`ReadOnly=true, UseStructuredContent=true`）· `CompactModelingTools.cs:15-29`（`cad_parse_source_callout`/`cad_store_model_input`/`cad_execution_status`）
- `src/CadModeling.Core/ArtifactFreshness.cs`（13037 字节，与「build identity / 新鲜度」相关的候选实现）· `src/CadModeling.Core/AdvancedFeatureValidation.cs`（12615）· `src/CadModeling.Executor.SolidWorks/`（执行器工程）· `src/CadModeling.Drawing.Ingestion/`、`src/CadModeling.Drawing.Contracts/`
- `THIRD_PARTY_NOTICES.md:1-5`（CurvesWB commit `e47b47927f59c87b93a1820c9f6ad4b4dc187076`，LGPL-2.1-or-later + TiGL Apache-2.0；「This does not relicense those files under the project's MIT license」）
- `plugins/auto-solidworks/.codex-plugin`、`plugins/auto-solidworks/skills/auto-solidworks/references/capability-manifest.json`、`…/references/progressive-native-evidence/`
- `tests/`（20 个文件：`cases.py` 24979、`focused_three.py` 13516、`local_geometry.py` 13421、`contract_cases.py` 2748、`assembly_cases.py` 4110、`optimization_*.py` 6 个）
- 实测计数：`McpServerTool(Name="…")` ⇒ 43 个注册点 / **32 个唯一名字**（`Program.cs` 的 full profile 重复注册）
- 元数据：`gh api repos/qdaia/Auto-SolidWorks`（2026-11-02 取：stars 7 / MIT / created 2026-09-06 / pushed 2026-10-25）

## 9. 未确认事项

1. **★ 三条「声称」未落代码级核实**：native execution **lease**（跨进程互斥）、**receipts 三态**、**persistent references + recovery prefix 有效性**。我只在 `docs/architecture.en.md` 读到声明，在 `CadModeling.Core` 里看到 `ArtifactFreshness.cs`/`VerificationAndRecovery.cs` 等候选，**未逐函数确认**。⇒ 本卡一律标「声称」。
2. **未构建未运行**：C# 需互操作程序集与 .NET 配置，`tests/` 需真机，**全部未跑**。
3. **32 个唯一工具的语义边界**：只按名字与文件归属推断职责，**未逐个读实现**；`cad_build_model` 与 `cad_build_assembly` 的差别、`cad_compile_binding_review` 与 `cad_review_model_delivery` 的分工**未确认**。（`src/AutoSolidWorks.ModelingMcp/CompactModelingTools.cs`）
4. **IR 的 schema 是否机器可校验**：`ModelingIrJson.Options` 出现在注册代码里，但**是否有 JSON Schema 文件与校验器未确认**。
5. **`profile` 有哪几档**：只见到 `full` 一种分支，**默认档与其它档未确认**。
6. **「1025」版本与 git 标签的对应**：`gh api` 的 `pushed_at` 是 2026-10-25，**是否即 `v1025` 未核 release 记录**。
7. **FreeCAD/OCCT 侧的 Gordon 面工具**：`GordonSurfaceTools.cs`（6704 字节）依赖本地 FreeCAD，**是否影响主链未确认**。
