# arthurle3210/SwpilotCLI

<!-- survey: class=B; repr=code; orchestration=loop; verify=visual; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `arthurle3210/SwpilotCLI` · https://github.com/arthurle3210/SwpilotCLI |
| 许可 | **不是开源许可**（`LICENSE` 全文为自定义条款：个人与**组织内部**免费；**不得**提供给客户/第三方/公众、不得作为对外服务、不得再分发/再许可；商业用途须书面授权。GitHub 判 `NOASSERTION`）⇒ **只读思想，不抄代码、不抄文本** |
| 元数据 | stars 35 · forks 9 · 语言 C#（46 个 `.cs`）· 仓库 1726 KB · 建档 2026-04-30 · 最近推送 2026-10-20（来源：`gh api repos/arthurle3210/SwpilotCLI`，2026-11-02 取）|
| 克隆 | `D:\swagent-2026Q4\repos\arthurle3210__SwpilotCLI`（`--depth 1`）|
| 证据等级 | **读码**（仓内**零测试**：`(Get-ChildItem -Recurse -File -Include *test*).Count` ⇒ 0；`dotnet` 项目需要本机 SolidWorks 互操作 DLL 才能编译，**未跑**；建模能力结论止步 `source`）|

## 1. 一句话定位

**路线最不一样的一家：它不发 MCP 工具，而是把 Claude Code / Codex CLI 直接嵌进 SolidWorks 的 Task Pane，让 agent 自己写 C# 小工具（`swpilotcli-*`）编译运行；干完活把「值得复用」的那些提升进工具库，用 `SKILL.md` + 生成的 `TOOLS.md` 当索引**——即「agent 自建工具库」那条路。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：SolidWorks 里的 **Task Pane**（WebView2 + 内嵌 PowerShell 终端，`Install/swpilotcli-install/src/TaskPaneControl.cs` 48 KB、`PSTerminalControl.cs` 33 KB）。用户在里面跑自己的 Claude Code / Codex / 任何能跑命令行的模型 CLI；add-in 只负责开一个终端和一颗「眼睛」。指令文件是仓根的 `AGENTS.md`（5006 字节，Claude 的 `CLAUDE.md` 同内容）。

**中间表示**：**没有 IR，中间表示就是 C# 源码本身**。工具是一个目录一动词：`sup_tools/swpilotcli-<verb>/scripts/<Xxx>/Program.cs` + 该目录的 `SKILL.md`（YAML frontmatter：`name` / `description`）+ `API_REFERENCE.md` + `README.md`。索引 `TOOLS.md`（19 KB）由 `scripts/sync-tools.ps1` 扫 `main_tools`/`sup_tools` 的 `SKILL.md` frontmatter 生成（脚本头「Scans main_tools/ and sup_tools/ directories and generates TOOLS.md」）。

**生成**：**agent 写代码**，这是它的核心。工作流写死成四步（`README.md`「Deep Dive: SwpilotCLI Tool Training Workflow」）：先查 `TOOLS.md` → 没有匹配工具就在 `SolidWorksConsole` 建草稿项目 → 开发并验证 → 值得复用就提升进 `sup_tools` → 跑 `sync-tools.ps1` 重生成 `TOOLS.md`。⇒ **工具库是长出来的，不是设计出来的**。

**编排**：agent 自己的 loop（Claude Code / Codex 原生），加 `AGENTS.md` 的硬规矩：涉及「看/确认/排错」先跑 `swpilotcli-eye-screenshot` 再用 `Read` 看图（`AGENTS.md`「Vision / Visual Verification」段，明写「Never say "I cannot see"」）；工程图/手绘草图先走 `swpilotcli-read-drawing` 协议再分析。

**执行**：两种粒度——① 已提升的工具：`dotnet run --project ./sup_tools/swpilotcli-feature-extrude-boss/scripts/ExtrudeBoss/ExtrudeBoss.csproj -- <depth_mm>`（`sup_tools/swpilotcli-feature-extrude-boss/SKILL.md` 的 Usage 段，**位置参数**）；② 没有现成工具时：写新 C# 项目再跑。

**验证**：**视觉为主 + 领域断言为辅**。视觉是「截图 → `Read` 看 → 自己判断」；领域断言体现在工具名与 `inspect-*` 族上：`check-dangling-dims`（悬空尺寸）、`diagnose-ic-rigidity`（瞬心法刚性诊断）、`inspect-drawing` / `read-drawing`、`inspect-sketch-setup`。⇒ **没有统一的几何回读层**，验证靠 agent 看图 + 事后诊断工具。

**交付**：`export-part-to-xt`、`export-assembly-parts-to-xt`、`batch-xt-to-step`、`save-drawing-as` / `save-drawing-as-copy`。

## 3. 技术方案要点（可迁移的机制）

### 3.1 工具面与粒度：**36 个工具目录，一动词一个可执行程序**（实测计数）（`TOOLS.md` 与目录树一致）

计数命令与结果：`(Get-ChildItem main_tools -Directory).Count` ⇒ 2，`(Get-ChildItem sup_tools -Directory).Count` ⇒ 34，合计 **36**；其中 **34 个 `sup_tools` 目录全部带 `SKILL.md`**（`(Get-ChildItem sup_tools -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') }).Count` ⇒ 34）。

粒度 = **一动词一 CLI 程序 + 位置参数**。它不是「工具」而是「命令行程序」，这带来三个后果：① 每次调用都要 `dotnet run`（启动开销）；② 参数是**位置参数**（`-- 10` 表示 10 mm），没有名字、没有 JSON schema，全靠 `SKILL.md` 文字说明；③ 工具的存在与顺序完全由 agent 自己读 `TOOLS.md` 决定——**没有机器可校验的工具契约**。

### 3.2 「工具库会长」是我方最该评估的一条

`README.md` 的流程图与 `scripts/sync-tools.ps1` 一起构成一个**自扩展工具库**：agent 一次性写出的代码被沉淀为可复用工具，下次同类任务直接命中。它明写了不用这个流程的后果：「若不提升到 `sup_tools`，下次会重写同一份代码」。

⇒ 这条对我方的价值是**判断题**，不是抄不抄：它能解决「同一类活反复写代码」，但代价是 ① 工具质量参差（没有统一验证层）；② 索引是生成的 Markdown，**没有 schema**，模型只能靠读描述；③ 工具数量会无界增长且无退役机制。**我方 439 个工具的治理压力，在这里以另一种形式重现**。（`capabilities.yaml` 的 439 条为基线）

### 3.3 工具名里的领域知识：这是它真正的差异化

34 个工具里有一整族**机构学**工具：`plot-ic-points`、`plot-ic-bisectors-at-68`、`sweep-ic-by-dimension`、`diagnose-ic-rigidity`（IC = 瞬心 instantaneous center），还有 `move-rollback-bar`（回滚棒）、`delete-orphan-sketches`、`check-dangling-dims`、`ActionGroup-replace-notes`。⇒ 它不是「通用 CAD 自动化」，而是**某个工程师自己的作业流程被固化成工具**；`swpilotcli-ActionGroup-*` 的命名规则（`README.md`「Naming Rules」：`ActionGroup` = 多函数组成的自定义工作流）说明它区分「原子动词」与「作业流程」。

### 3.4 模型调用面：MCP 只用来查 API，不用来建模

`Install.md` 配置的 MCP 只有一条：`swapi-pilot` → `https://swapi-pilot.com/mcp`（`README.md`「What the Installation Configures」），而且作者自述那个 MCP 是「用来查 SolidWorks API」的（`README.md`「Interface Overview」：「it uses `swapi-pilot-solidworks-mcp` to query the SolidWorks API」）。⇒ **真正的建模动作走本地 shell + 自写 C#**，MCP 只承担「API 知识检索」。这是与 A 线其他各家最根本的分歧：**模型不通过工具契约碰几何，而是通过代码**。

### 3.5 持久引用 / 事务 / 互斥：三件都没解

- **持久引用**：无任何拓扑 ID 或选择器抽象；选择逻辑写在每个 `Program.cs` 里（如 `sketch-draw` 的 `SketchDrawer.cs` 15 KB）。⇒ 每次工具重写都可能换一种选法，**一致性靠人**。
- **事务式建模**：无回滚；只有 `undo-one-step` 与 `move-rollback-bar` 两个**手工**工具。
- **单源 COM 互斥**：add-in 与 CLI 子进程**各自连 COM**（每个 `Program.cs` 自己 `GetActiveObject`/`Activator`），**天生多连接**。这与「单源运行」纪律正面对撞——但它的形态是「同一台机上很多短命进程轮流连」，实践中风险取决于是否真的并发。

## 4. 运行条件与依赖

- Windows + SolidWorks；**.NET 8 SDK + .NET Framework Developer Pack**（`README.md`「What the Installation Configures」）。
- 需要**付费的 Claude Code Pro 或 Codex Pro**（作者明说这是它受众小的原因）。
- 安装建议关掉沙箱（`README.md` 安装段第 2 条「I recommend turning off sandbox mode」）⇒ **安全边界被主动撤掉**。
- 无测试工程；验证靠人跑 + 看截图。

## 5. 失败模式与已知坑

1. **无测试、无契约**：36 个工具目录、零测试文件（计数见字段表）⇒ 任何 C# 改动的回归全靠人。（同 `scripts/sync-tools.ps1` 的扫法）
2. **位置参数**：工具一旦加了参数就破坏所有既有调用方的肌肉记忆，且模型只能从 `SKILL.md` 文本推断参数顺序。
3. **`dotnet run` 每次调用都编译检查**：交互延迟高（未实测，属【推断】）。
4. **沙箱被建议关闭**：agent 在 SolidWorks 进程旁边的无约束 shell 里跑任意代码，风险面 = 整台机器。
5. **多进程各自连 COM**：与「单源」纪律冲突，并发时可能撞死锁（我方已知事实 24 的情形）。
6. **视觉验证是「看图说话」**：`eye-screenshot` 截整个屏幕由模型判断，**没有数值判据**，也没有「这一步应该让体积变成多少」的对照。
7. **工具库无退役机制**：`README.md` 只说「不是每个草稿都要提升」，没说什么时候删。

## 6. 对我方目标的可用处（能学 / 不能学）

**Q2 逐条答**：
| 问题 | 它解到什么程度 | 依据 |
|---|---|---|
| 持久引用 | **没解**：无抽象，选择逻辑散在各 `Program.cs` | `sup_tools/swpilotcli-sketch-draw/scripts/SketchDraw/SketchDrawer.cs` |
| 回读验证 | **没解**：靠截图 + agent 判断，无数值回读层 | `AGENTS.md`「Vision / Visual Verification」段 |
| 事务式建模 | **没解**：只有 `undo-one-step` / `move-rollback-bar` 手工工具 | `TOOLS.md` 工具清单 |
| 单源 COM 互斥 | **反着做**：每个 CLI 子进程各自连 COM | `Install/swpilotcli-install/src/*.cs` 与各 `Program.cs` |

**Q3 答**：**CLI + 脚本路线（不是 MCP 服务端、不是库）**；工具面 **36 个可执行工具目录**（`main_tools` 2 + `sup_tools` 34）；粒度 = **一动词一个 CLI 程序**（位置参数），另加一层 `ActionGroup-*` 作业流程工具。（`TOOLS.md`）

**能学**：
1. **「工具作为自描述目录」的组织法**：一个动词 = 一个目录 = `SKILL.md`（frontmatter 给机器读）+ `API_REFERENCE.md` + `README.md` + 源码，索引由脚本生成。这是把「工具文档」与「工具实现」绑在一起的最小做法，**比我方「439 个工具 + 一份清单」更难漂移**。
2. **`AGENTS.md` 里的「先看再答」硬规矩**（涉及确认/排错必须先截图再 `Read`）：把「不要凭空断言」写成 agent 的操作顺序，而不是写在报告里。
3. **`TOOLS.md` 由脚本从 `SKILL.md` frontmatter 生成**：索引永不手改，天然防漂移（`scripts/sync-tools.ps1`）。
4. **领域作业流程固化成工具**（瞬心法、回滚棒、悬空尺寸、孤儿草图）：这是「工程判据进工具」的样本，与我方 `E1–E7` 的方向一致——**判据可以是一个工具，而不是一段文档**。
5. **`inspect-*` / `diagnose-*` 与 `feature-*` 分族**：读类与写类在命名上就分开，便于人对账。

**不能学**：
- **许可**：自定义条款禁止再分发与商业使用 ⇒ **一行代码、一段文本都不抄**。
- **无测试 + 无契约 + 关沙箱**：三条都是我方红线的反面。
- **多进程各自连 COM**：与单源纪律正面冲突。
- **位置参数**：没有 schema 的工具面，模型只能靠猜。
- **把「agent 自己写工具」当默认路径**：它解决了「重复写代码」，但把「工具质量」外包给了模型，且没有验证层兜底。

## 7. 许可与红线

**自定义专有条款**（`LICENSE` 全文）：个人与组织内部免费；**明确禁止**「provided to clients, third parties, or the public」「used as part of any external service」「Repackage, resell, sublicense, or redistribute」；商业/对外使用须书面授权。GitHub 判 `NOASSERTION`。
⇒ **红线：只读思想**。不复制 C# 代码、不复制 `SKILL.md`/`AGENTS.md` 文本、不复制 `TOOLS.md` 结构文本；§3/§6 里的一切只能作为**做法层面的启发**，落地时必须自己重写，且不得声称来源于此项目的代码。

## 8. 证据清单

- `LICENSE:1-40`（自定义条款全文：个人/内部免费、禁止再分发与对外服务、商业须授权）
- `README.md`「The SwpilotCLI workflow」（三步：自动建工具 → 提升进 `sup_tools` → 复用）·「Installation Demo」与「What the Installation Configures」（.NET 8、Framework Pack、`swapi-pilot` MCP = `https://swapi-pilot.com/mcp`）·「Interface Overview」（MCP 只用于查 API）·「Tool Creation Example」·「Vision System」·「Naming Rules」·「Deep Dive: Tool Training Workflow」（流程图 + 目录角色表）
- `AGENTS.md`（5006 字节；默认目标是**当前活动文档**、`swApp.GetActiveDoc()`、视觉优先顺序、工程图先走 `read-drawing` 协议）
- `TOOLS.md`（19 KB；`main_tools` / `sup_tools` 两段；每个工具给 Path / Skill Definition / API Reference）
- `scripts/sync-tools.ps1:1-25`（扫目录、读 `SKILL.md` YAML frontmatter、生成 `TOOLS.md`）
- `sup_tools/swpilotcli-feature-extrude-boss/SKILL.md`（frontmatter `name`/`description`；Usage = `dotnet run --project … -- <depth_mm>`；「How it works」三步：读位置参数 → `FeatureExtrusion3` → `EditRebuild3` + `GraphicsRedraw2`）
- `sup_tools/swpilotcli-extrude-boss`…（同目录族：`sketch-draw` 的 `SketchDrawer.cs` 15728 字节是最大的单个工具实现）
- `Install/swpilotcli-install/src/TaskPaneControl.cs`（48385 字节，Task Pane 宿主）· `PSTerminalControl.cs`（33616 字节，内嵌 PowerShell 终端）· `SwpilotTaskPane.cs`、`SwAddIn.cs`（add-in 生命周期）
- 实测计数：`(Get-ChildItem main_tools -Directory).Count` ⇒ 2；`(Get-ChildItem sup_tools -Directory).Count` ⇒ 34；`(Get-ChildItem sup_tools -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') }).Count` ⇒ 34；`(Get-ChildItem -Recurse -File -Include *test*).Count` ⇒ 0
- 元数据：`gh api repos/arthurle3210/SwpilotCLI`（2026-11-02 取：stars 35 / `NOASSERTION` / pushed 2026-10-20）

## 9. 未确认事项

1. **未编译、未运行**：`dotnet` 构建需要本机 SolidWorks 互操作 DLL，本卡**未尝试**；36 个工具的真实可用性**未知**。（`TOOLS.md` 列出的目录）
2. **`swapi-pilot` MCP 是闭源服务**（`https://swapi-pilot.com/mcp`，作者另有 `arthurle3210/swapi-pilot-solidworks-mcp` 仓库）⇒ 它的 API 知识面能力**未核**（不在本线范围）。
3. **`ActionGroup-*` 的实际数量与组合方式**：只有 `replace-notes` 一个实例，**是否真按文档所说的「多函数组合」实现，未确认**。
4. **位置参数之外是否有 JSON 输入通道**：只读了 `SKILL.md` 一例，**未逐工具确认**。
5. **多进程连 COM 的实际并发度**：`dotnet run` 是短命进程，**是否真的会与 add-in 抢锁，未验证**。
6. **`README.md` 的三个 demo 视频内容**：未观看（YouTube 链接），**未确认**其能力展示与代码一致。
