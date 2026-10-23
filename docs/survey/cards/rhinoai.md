# RhinoAI（McNeel 官方 Rhino MCP）

<!-- survey: class=H; repr=code; orchestration=loop; verify=visual; deliver=none; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/mcneel/RhinoAI · 文档 https://mcneel.github.io/RhinoAI/docs/ |
| 许可 | MIT（`LICENSE:1-3`，`Copyright (c) 2026 Robert McNeel & Associates`）⇒ **可借鉴**，移植须保留版权声明；仓根只有这一个代码许可文件（`git ls-files` 里 LICENSE 仅 1 个，另有 `CODE_OF_CONDUCT.md`/`PRIVACY.md`，无第二个许可文本）|
| 元数据 | stars 377 · forks 59 · open issues 17 · 最近推送 2026-10-23T13:06:10Z · 语言 C# · 默认分支 `rhino-9.x`（来源：`gh api repos/mcneel/RhinoAI`，2026-10-24 取）|
| 克隆 | `D:\ai3d-survey\repos\mcneel__RhinoAI`（shallow：`git rev-list --count HEAD` 得 1，tip `2685f315`，提交时间 2026-10-23 14:42:48 +0200；体积 19.1 MB，来源：`Get-ChildItem -Recurse -File | Measure-Object Length -Sum` 实测 2026-10-24）|
| 证据等级 | **读码**（非「实测」：本机无 Rhino；`dotnet` 只有 runtime 没有 SDK——`dotnet --version` 报 `The application '--version' does not exist`，实测 2026-10-24。构建另需 Rhino 侧 props：`rhino/plugin/RhinoAI.csproj:3`）|

## 1. 一句话定位

**一个 MCP 端点 + 一个多 Rhino 实例路由器**：AI 客户端连的是一张固定工具表（本文数到 42 个工具，来源见 §3.1），每次调用被路由到某个真实 Rhino 会话；**建模本身不靠结构化工具，靠模型现场写 Python/C# 脚本**（`run_python`/`run_csharp` 在 `rhino/plugin/Tools/RunPythonTool.cs:8`、`RunCSharpTool.cs:11`），结构化工具只覆盖「读状态 / 选择 / 相机 / 文档 / Grasshopper 图」。

A–J 里归 `H`（GUI/API 代理）：它代理的不是 CAD 内核 API 的抽象层，而是**一个正在运行的 Rhino 进程**；`repr=code` 是因为中间表示就是脚本源码串。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：MCP `tools/call`（JSON-RPC 2.0 over `HttpListener`，方法表见 `rhino/plugin/Server/McpEndpoint.ai.cs:103-116`）。工具不是手写注册表，而是**反射扫描程序集**：凡打了 `[McpServerToolType]` 的类里、标了 `[McpServerTool("name", …)]` 的方法都成工具，重名即抛（`rhino/plugin/Server/ToolRegistry.ai.cs:22-63`）。

**中间表示**：两层。① 结构化参数（`SchemaBuilder` 从方法签名生成 inputSchema，`ToolRegistry.ai.cs:33-36`）；② **脚本源码串**——`run_python` 收一个 `script` 参数，脚本编辑器注入 `__rhino_doc__` 作为文档句柄，描述里明写「不要信任 `scriptcontext.doc` 与 `rhinoscriptsyntax`」（`RunPythonTool.cs:9-10`）；C# 侧额外自动注入 usings（`RunCSharpTool.cs:17-25`）。

**生成**：模型自己写代码或调 `run_command` 跑 Rhino 原生命令（`rhino/plugin/Tools/RunCommandTool.cs:8`）。插件不生成几何，只提供**执行与回读**。

**编排**：循环不在插件里，在**外部 agent CLI 里**——`ClaudeHarness.StreamLoopAsync` 用 `StartClaude` 起子进程，再把一行行 turn 流回面板（`rhino/sdk/Harnesses/ClaudeHarness.cs:42,53,228`）；Codex 侧同构（`rhino/sdk/Harnesses/CodexHarness.cs`）。插件只负责「把 Rhino 的工具暴露给这个子进程」并「把 turn 渲染出来」，没有自己的轮数上限常量（见 §9）。

**执行**：`ScriptProjectRunner.RunScript(doc, Lang.Python3, script)`（`RunPythonTool.cs:13`）在 Rhino 主线程执行；带 `[BackgroundThread]` 的工具不 marshal 到 UI 线程（`ToolRegistry.ai.cs:40`）。多实例由 router 管：每个 Rhino「slot」一个 OS 进程 + 自己的私有端口，从 10500 起递增，端口用「先绑 0 让 OS 分配再释放」取空闲号（`rhino/plugin/RhinoAIHost.ai.cs:116,122-152`；`rhino/router/RhinoManager.ai.cs:27-28`），slot 状态落 SQLite 以便并发 router 不抢端口（`RhinoManager.ai.cs:13-18`、`SlotStore.ai.cs`）。

**验证**：两条。① **结构化快照**：`get_context` 一次往返给出「选择集 + 活动视口相机 + 文档对象/图层计数 + 每个 GH 版本的组件/连线计数」，且**每段独立 try/catch**，坏一段只进 `Warnings` 不毁整份快照（`rhino/plugin/Tools/GetContextTool.ai.cs:12-14,39-62,103-114`）。② **视觉**：`get_viewport_image` 抓视口成图（`rhino/plugin/Tools/GetViewportImageTool.cs:15`），由模型看图判断。GH 侧另有一层真诊断，见 §3.2。

**交付**：无专用导出工具。落地只有 `save_doc`（存 .3dm，`rhino/plugin/Tools/SaveDocTool.cs:12`）；要 STEP/STL 得靠 `run_command` 跑 Rhino 的 `Export` 命令或 `run_python` 调 RhinoCommon，属**逃逸口**而非产品路径（故 `deliver=none`）。

## 3. 技术方案要点（可迁移的机制）

### 3.1 工具清单与粒度：**42 个工具 = 18 个通用 + 12 个 GH1 + 12 个 GH2**（来源：本卡 §8 证据清单）

按 `[McpServerTool(` 属性逐条数（`Select-String -Path rhino/plugin/Tools/**/*.cs -Pattern 'McpServerTool\('`，2026-10-24）：

| 组 | 数量 | 成员（属性所在文件） |
|---|---|---|
| 通用（18） | 18 | `ask_user`（`AskUserTool.ai.cs:8`，另带 `[BackgroundThread]` 与 `[InPanelOnly]`，`:9-10`）、`close_doc`、`manage_plugin_commands`、`get_commands`、`get_context`、`get_selection`、`get_viewport_image`、`list_objects`、`open_doc`、`run_command`、`run_csharp`、`run_python`、`save_doc`、`set_camera`、`set_layer_material`、`set_selection`、`zoom_to_layer`、`zoom_to_object`（后 17 个各是 `rhino/plugin/Tools/` 下同名 `*Tool.cs` 里 `[McpServerTool(` 那一行，逐条见 §8）|
| GH1（12） | 12 | `g1_apply_graph`、`g1_clear_canvas`、`g1_connect`、`g1_connect_many`、`g1_delete_component`、`g1_describe_component`、`g1_get_canvas_graph`、`g1_place_component`、`g1_place_slider`、`g1_search_components`、`g1_solve_graph`、`g1_start`（`rhino/plugin/Tools/GH1/*.cs:11-35`）|
| GH2（12） | 12 | `g2_apply_graph`、`g2_clear_canvas`、`g2_connect`、`g2_connect_many`、`g2_delete_component`、`g2_describe_component`、`g2_get_canvas_graph`、`g2_place_component`、`g2_place_slider`、`g2_search_components`、`g2_solve_canvas`、`g2_start`（`rhino/plugin/Tools/GH2/*.cs:11-34`；与 GH1 逐项对应，唯一改名的是求解者：GH1 叫 `g1_solve_graph`、GH2 叫 `g2_solve_canvas`；`g2_*` 受 `#if R9` 约束，`GetContextTool.ai.cs:50-52`）|

粒度判据是**工具四元属性**，不是功能域：每个工具声明 `(readOnly, destructive)` 两枚布尔，直接映射成 MCP 的 `readOnlyHint`/`destructiveHint` 注解（`ToolRegistry.ai.cs:46-52`；`McpEndpoint.ai.cs:161-166`）。写操作几乎全标 `destructive=true`（`run_python`/`run_csharp`/`run_command`/`save_doc`/`open_doc`/`close_doc`），读操作标 `readOnly=true`——**这是给客户端做权限提示的元数据，不是服务端拦截**。

### 3.2 其它可迁移机制

- **失败回传是四段式，不是一句错误串**：`IToolResult` 固定带 `Code`（枚举）、`Error`（枚举的人话）、`Message`（具体发生了什么，例："Layer not found: Walls"）、`Guidance`（**下一步该干什么**）（`rhino/plugin/Tools/ToolResult.cs:3-22`）。`Code` 共 23 个值：7 个通用 + 8 个 Rhino + 8 个 GH（`ToolResult.cs:129-153`）。
- **「工具跑了但失败」与「工具没跑」严格分开**：前者回 `CallToolResult{IsError:true}`（协议里的数据），后者回 JSON-RPC error（`McpEndpoint.ai.cs:262-280` 的注释把这条口径写死了）。这条区分让 agent 能分辨「重试」和「改参数」。
- **GH 图求解回传结构化诊断**：`g2_solve_canvas` 返回 `{Solved, Phase, Errors, Warnings, Diagnostics[]}`，每条诊断是 `{Id, Name, Nickname, Level (Remark|Warning|Error|Fault), Message}`，`Solved` 只在无 Error/Fault 时为真（`rhino/plugin/Tools/GH2/GH2_SolveTool.cs:13-30`）；`g2_apply_graph` 内部**单步失败不中止其余步骤**，逐步报状态并在末尾自动 solve（`GH2_ApplyGraphTool.cs:34,101`）。插件把这条写成编排指令塞进系统提示（`rhino/plugin/Agents/AgentPrompts.cs:27-42`）：读图 → 改图 → 解 → **读回诊断** → 改坏的那个组件 → 再解，直到干净。
- **双端点做权限分层**：`/`（外部）与 `/agent`（面板内）各一个 dispatcher，`InPanelOnly` 工具（`ask_user`）只在后者的 `tools/list` 里出现；外部即使硬调也拿到一段「该工具只对面板可用」的**正常结果**而非传输错误，好让外部 agent 能自行恢复（`McpEndpoint.ai.cs:141-170,235-250`；`ToolRegistry.ai.cs:75-79`）。
- **接地（grounding）只许拉、不许推**：默认不注入任何文档/选择状态，agent 必须先 `get_context` 再动作；提示词里明写「永不断言当前选中了什么、开了哪个文档」（`AgentPrompts.cs:17-25`）。
- **`.ai.cs` 后缀当溯源**：AI 起草的 C# 文件一律改名 `*.ai.cs`，一条 `git ls-files '*.ai.cs'` 就能列出所有机器起草、需要重点 review 的文件；后缀不随人类编辑而消失（`AGENTS.md:3-13`）。
- **slot 生命周期**：router 起/管/拆 Rhino 实例，卡在 `Launching` 超过 90 秒即视为陈旧、探活 1 秒预算、`ActiveSlotId` 只活在内存里（`RhinoManager.ai.cs:29-38,42-48`）。

## 4. 运行条件与依赖

- 目标框架：Windows 上 `net8.0;net48`，非 Windows 只有 `net8.0`（`rhino/plugin/RhinoAI.csproj:18-19`）；默认 `RhinoTarget=R9`（`RhinoAI.csproj:6`）。
- 宿主：Rhino 8 或 Rhino 9；**GH2 工具要 Rhino 9 WIP/BETA**（`docs/content/docs/troubleshooting.md:46,50`）。产品形态是 `.rhp` 插件（`RhinoAI.csproj:24` 的 `TargetExt`）。
- 构建依赖 Rhino 的 msbuild props（`RhinoAI.csproj:3` 的 `RhinoProjectPropertySheet`），即**必须有 Rhino SDK 的源码树**；仓内 `rhino.slnx` 含 plugin/router/sdk/acp/panel 多个工程。
- **本机（Windows / Py3.14.7 / RTX 4080S 16GB）跑不了**：① 无 Rhino 进程（`C:\Program Files` 下无 Rhino 目录，实测 2026-10-24）；② `dotnet` 只有运行时无 SDK（`dotnet --version` 失败）；③ 构建还要 Rhino 侧 props/sdk。显存与它无关——全仓无本地模型，LLM 由外部 CLI 或用户配置的 provider 提供。

## 5. 失败模式与已知坑

- **文档与代码的工具名不一致**：`docs/content/docs/troubleshooting.md:50` 写 Grasshopper 2 工具前缀是 `gh2_`，代码实际注册的是 `g2_*`（`GH2_StartTool.cs:11`）。照文档去拼工具名会全部落空。
- **随包 Claude Code 插件的 agent 定义引用了不存在的工具**：`cc-plugin/agents/rhino-modeler.md:4` 与 `rhino-inspector.md` 都带 `mcp__rhino__probe_intersection`，该名在全部 `.cs` 里 **0 命中**（`Select-String -Pattern probe_intersection` 实测）；GH 类 agent 写的是 `solve_canvas`/`start_gh2`/`connect_many` 等无前缀名，而实际名是 `g2_solve_canvas`/`g2_start`/`g1_connect_many`（`cc-plugin/agents/grasshopper-scripter.md:4` vs §3.1 清单）。8 个 agent 定义文件全有这个漂移。
- **多窗口误靶是官方承认的坑**：`troubleshooting.md:30-34` 明写「助手说改完了但你没看到」的三个原因——**改错了另一个 Rhino 窗口**、几何在原点远处、图层被隐藏。slot 路由的粘性策略（先用本会话上次的 slot，再退到用户最早开的那个）是缓解手段（`RhinoManager.ai.cs:56-62`）。
- **平台门槛是硬的**：`troubleshooting.md:57-60` 列「.NET Framework 不支持、Intel Mac 不支持、Rhino 版本要最新」。
- **`run_python`/`run_csharp`/`run_command` 是任意代码执行**，且描述里只交代「别信任 `rhinoscriptsyntax`」，**没有任何沙箱或确认环节**（`RunPythonTool.cs:9-13`）。安全边界完全落在客户端的 `destructive` 提示上。
- **`ask_user` 的语义是「问完就结束回合」**：工具不返回答案，用户回复作为下一条消息回来（`AgentPrompts.cs:9-13`）；把它当同步问答会卡住。
- **42 个工具里 24 个是 Grasshopper 专用**（§3.1），不做 GH 的用户实际可用面只有 18 个；且 12 个 `g2_*` 在没有 Rhino 9 时是死工具（`GetContextTool.ai.cs:50-52` 的 `#if R9`）。

## 6. 对我方目标的可用处（机制层面，含边界）

1. **失败回传的四个字段**（Code / Error / Message / **Guidance**）是普通模型最缺的东西：模型知道「下一步该改什么」比知道「错在哪个类型」更能收敛。SolidWorks 侧的工具集可直接照这个结构设计返回体。
2. **23 个错误码按宿主分层**（通用 / Rhino / GH）比一大坨自由文本错误串更适合做静态判据——错误码可以被 grep、被测试断言。（来源：本卡 §8 证据清单）
3. **「工具跑了但失败」≠「工具没跑」** 这条协议级区分，正好对上我方「特征建出来是 NULL 但调用返回成功」的老坑（本仓已知事实 1 的同类）；它给出的是**协议层**的解法：失败必须是数据，不是异常。
4. **GH2 的「求解→读回逐组件诊断→改坏的那一个→再解」闭环**，与 slvsx-cli 卡（`docs/survey/cards/slvsx-cli.md`）里「求解器只回一个状态码、DoF 根本没传出来」形成对照：同样是 solver 型反馈，RhinoAI 做到了 per-component 定位。
5. **`readOnly`/`destructive` 注解 + 双端点 `InPanelOnly`** 是「同一批工具、两种信任级」的最小实现，可对应我方「读操作随时跑、写操作要人批」的分层。
6. **边界一**：它没有几何数值验证——`get_context` 只给计数（对象数/图层数/组件数/连线条数，`GetContextTool.ai.cs:29,116-130`），不校验尺寸、体积、水密；判「建对了没有」全靠模型看图。
7. **边界二**：多实例路由（一 Rhino 一进程一端口）在 SolidWorks COM 上是**反向**的——同进程多实例会抢同一个 COM 连接（本仓已知事实 24），这套 slot 机制不能照搬，只能借它的**生命周期与陈旧探测**思路。
8. **边界三**：许可 MIT 可抄，但它是 C#/.NET + Rhino SDK，落到我方 Python/COM 栈只能借结构、不能借代码。

## 7. 许可与红线

- MIT（`LICENSE:1-3`，`Copyright (c) 2026 Robert McNeel & Associates`）⇒ 可读、可抄、可改、可商用，须保留版权声明。
- 红线：`run_python`/`run_csharp`/`run_command` 是**以用户权限执行任意代码**的能力，且官方描述只提醒 API 用法、没有沙箱（`RunPythonTool.cs:9-13`）。任何形态的移植都要保留我方三条护栏（先置抑制态、每调用超时、收尾释放）。
- 克隆仓库只读，未改动任何文件。

## 8. 证据清单

- `LICENSE:1-3`；`AGENTS.md:3-13`
- `rhino/plugin/Server/ToolRegistry.ai.cs:22-63,33-36,40,46-52,75-79`
- `rhino/plugin/Server/McpEndpoint.ai.cs:103-116,141-170,161-166,235-250,262-280`
- `rhino/plugin/Tools/ToolResult.cs:3-22,91-125,129-153`
- `rhino/plugin/Tools/RunPythonTool.cs:8-13`；`RunCSharpTool.cs:11-25`；`RunCommandTool.cs:8`；`SaveDocTool.cs:12`
- `rhino/plugin/Tools/GetContextTool.ai.cs:12-14,39-62,50-52,103-114,116-130`
- `rhino/plugin/Tools/GetViewportImageTool.cs:15`；`AskUserTool.ai.cs:8`
- `rhino/plugin/Tools/GH2/GH2_SolveTool.cs:13-30`；`GH2/GH2_ApplyGraphTool.cs:34,101`；`GH1/*.cs:11-35`；`GH2/*.cs:11-34`
- `rhino/plugin/Agents/AgentPrompts.cs:9-13,17-25,27-42`
- `rhino/plugin/RhinoAIHost.ai.cs:116,122-152`；`rhino/router/RhinoManager.ai.cs:13-18,27-38,42-48,56-62`；`rhino/router/SlotStore.ai.cs`
- `rhino/sdk/Harnesses/ClaudeHarness.cs:42,53,228`；`rhino/sdk/Harnesses/CodexHarness.cs`
- `rhino/plugin/RhinoAI.csproj:3,6,18-19,24`
- `docs/content/docs/troubleshooting.md:30-34,46,50,57-60`
- `cc-plugin/agents/rhino-modeler.md:4`；`cc-plugin/agents/rhino-inspector.md:4`；`cc-plugin/agents/grasshopper-scripter.md:4`；`cc-plugin/.mcp.json:1-6`
- https://github.com/mcneel/RhinoAI（`gh api repos/mcneel/RhinoAI`，2026-10-24）

## 9. 未确认事项

1. 42 个工具是**静态计数**（`[McpServerTool(` 属性），运行期会被 `AISettings.DisabledTools` 过滤（`McpEndpoint.ai.cs:143-145,152`），实际 `tools/list` 返回几个未验。
2. 面板内 agent 的**轮数上限**没找到常量（`rhino/plugin/Agents/*.cs` 无 `MaxTurns` 类常量；`Select-String -Pattern MaxTurns|MaxIterations` 0 命中），推断上限在外部 agent CLI 里，未验证。
3. 未跑过任何工具，也未构建：`dotnet` 无 SDK、无 Rhino，读码结论只到「代码这么写」这一层。
4. GH2 的 12 个工具在 Rhino 8 上的真实行为（编译期被 `#if R9` 排除）未验。（来源：本卡 §8 证据清单）
5. `acp/`（Agent Client Protocol）与 `panel/`、`connector/` 三块的职责边界只按目录名理解，未逐文件读。
