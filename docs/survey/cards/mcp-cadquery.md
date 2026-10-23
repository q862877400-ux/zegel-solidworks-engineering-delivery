# mcp-cadquery

<!-- survey: class=B; repr=code; orchestration=loop; verify=run-only; deliver=STEP; evidence=实测 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/bertvanbrakel/mcp-cadquery （无独立主页——API 里 `description` 与 `homepage` 都没给；来源：https://api.github.com/repos/bertvanbrakel/mcp-cadquery ） |
| 许可 | **无 LICENSE**（克隆内按 `*LICEN*` 递归实测零命中；`gh api` 的 `license` 字段为 null）→ **只读思想**。`pyproject.toml:16` 的 classifier 自称 `License :: OSI Approved :: MIT License`，但同一行行尾写着 `# Choose appropriate license`，仓库内既无版权行也无许可正文 ⇒ 不构成授权 |
| 元数据 | stars 19 · 最近推送 2025-04-07T12:15:23Z · 语言 Python（来源：https://api.github.com/repos/bertvanbrakel/mcp-cadquery ，取数日 2026-10-24） |
| 克隆 | D:\ai3d-survey\repos\bertvanbrakel__mcp-cadquery （HEAD `eae44ca`，末次提交 2025-04-07 22:15 +1000，工作树干净） |
| 证据等级 | 读码 |

## 1. 一句话定位

把 CadQuery 包成 MCP 工具面的**执行后端**：模型交一整段 CadQuery Python 源码，它在「每个 workspace 一个 venv」的子进程里跑，几何落成 BREP 按 `result_id` 登记，之后凭同一个 id 再去导出 STEP/STL/SVG 或读体积/包围盒（`README.md:22-36`、`handlers.py:714-724`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

1. **输入**：一次工具调用 = `workspace_path` + 整段 `script`，可选 `parameters`/`parameter_sets`（`models.py:5-25`）。传输层是自家行式 JSON，不是 JSON-RPC（见 §5）。
2. **中间表示**：**用户手写的 CadQuery 源码**是唯一真源；服务端只留执行产物——每个 shape 落一份 BREP 并记住路径（`script_runner.py:150-168`），结果按 `result_id` 进内存表（`handlers.py:115`、`state.py:19-21`）。
3. **生成**：`cqgi.parse(script)` + `model.build()`，**不做任何参数注入**（`script_runner.py:104-108`）。模型的重写动作发生在客户端，服务端只负责「这一版能不能编译出实体」。
4. **编排**：同一入口两种形态——FastAPI/SSE（`GET /mcp` 建流、`POST /mcp/execute` 收工具请求，`web_server.py:76`、`web_server.py:114`）与 stdio 逐行读（`stdio_server.py:37-50`）；工具面 10 条，权威声明是 `handlers.py:714-724` 的字典，schema 由 Pydantic 模型反推（`mcp_api.py:24-43`）。
5. **执行**：先 `prepare_workspace_env()` 自举 `.venv` 并 `uv pip install cadquery`（`env_setup.py:88-137`），再用该 venv 的 python 起子进程跑 `script_runner.py`，stdin 灌 JSON、stdout 收 JSON、cwd 设为 workspace（`handlers.py:89-113`）。
6. **验证**：**只有构建层成败**——`build_result.success` 与 `exception_str`（`script_runner.py:111-120`）。几何读数（包围盒/体积/面积/质心/面边点计数）是另一支工具按需返回（`core.py:124-190`、`core.py:197-281`），既无自动判据也无自动重试。
7. **交付**：`export_shape` 先 `cq.importers.importBrep(intermediate_path)`，再把形状交给 `exporters.export(...)`，格式由调用方给（`handlers.py:180-200`、`core.py:86-100`）；另有 SVG 预览（`handlers.py:299`、`core.py:102-122`）和零件库缩略图（`handlers.py:391`）。

## 3. 技术方案要点（可迁移的机制）

- **执行与导出解耦**：执行时就把几何写盘并登记，导出/量测/渲染都只凭 `result_id` 取（`script_runner.py:145-168`、`handlers.py:173-190`）——一次构建可以派生多种交付物。
- **每 workspace 一个隔离环境，依赖按 mtime 增量**：`requirements.txt` 的 mtime 变了才重装（`env_setup.py:108-137`）。
- **一次调用多参数组 fan-out**：外层循环逐组起独立子进程，各组成败分别汇总、互不污染（`handlers.py:76-139`）。
- **库即索引**：扫目录里的 `.py`，以文件 mtime 作缓存键（`handlers.py:364-369`）；元数据只用 `ast.get_docstring` 读模块 docstring 里的 `Key: Value` 行（`handlers.py:394-396`、`core.py:16-51`）。
- **目录约定即元数据规范**：零件脚本顶层 docstring 写 Name/Description/Tags/Author，`show_object()` 交结果（`README.md:225-226`）。
- **检索是字段加权打分**（id +5、tags +5、part +3、description +2、filename +1），不是向量检索（`handlers.py:559-572`）。
- **子进程边界只画了一半**：脚本执行有隔离（`handlers.py:89-104`），但库扫描反而在主进程里直接跑（`handlers.py:375-377`）。
- **写盘有路径约束，但只在一处**：`save_workspace_module` 禁分隔符 + 前缀比对（`handlers.py:467-480`）；`export_shape` 对绝对/相对路径直接放行（`handlers.py:198-200`）。
- **环境自举写进启动脚本**：首次运行自动建 venv 装依赖（`README.md:24-28`），把「能跑起来」从文档义务变成代码动作。

## 4. 运行条件与依赖

- Python `>=3.10`（`pyproject.toml:13`）；依赖钉在 `cadquery==2.5.2` + `fastapi`/`uvicorn`/`sse-starlette`/`typer`（`pyproject.toml:20-28`、`requirements.txt`）。
- 必须有 `uv`：缺失时直接抛错并给安装链接（`env_setup.py:77-80`）；它自建 venv 时写死 `PYTHON_VERSION = "3.11"`（`env_setup.py:10`）——这是**在 3.14 机器上仍能跑**的关键：venv 不跟宿主解释器版本走。
- 本机（Windows / Python 3.14.7 / RTX 4080S 16GB）判断：**原则上能跑，但有两处要绕**——① 官方启动脚本是 `server_sse.sh`/`server_stdio.sh`（`README.md:5-10`），Windows 上得直接 `python server.py --mode stdio|sse`（`server.py:13-14`、`cli.py:29-34`）；② `cadquery==2.5.2` 有没有 cp314 的 Windows wheel **未确认**，而 `uv venv -p 3.11` 那条路不依赖宿主版本。GPU 无要求：依赖表里没有任何加速器包（`pyproject.toml:20-28`）。

## 5. 失败模式与已知坑

- **`install_workspace_package` 必然失败**：调用处写 `success, output = _run_command_helper(...)`（`handlers.py:522`），而该函数返回的是 `subprocess.CompletedProcess`（`env_setup.py:15`、`env_setup.py:37`），解包即 `TypeError`；且它默认 `check=True`，失败会抛 `CalledProcessError` 而不是返回 `False`（`env_setup.py:27-33`）。
- **参数扫描是空转**：`script_runner.py:90-92` 明写「跳过参数替换（由调用方处理）」，`parameters` 只被读来打日志（`script_runner.py:61`、`script_runner.py:74`）；`core.py:65` 的 `_substitute_parameters` 只被测试调用（`tests/test_core_helpers.py:11`）⇒ 传 N 组参数得到 N 份同一结果。
- **协议不是 MCP**：stdio 分支只认 `{"tool_name","request_id"}`（`stdio_server.py:46-47`）；HTTP 侧是 `GET /mcp`（SSE 推）与 `POST /mcp/execute`（`web_server.py:76`、`web_server.py:114`）；全仓无 `jsonrpc`/`initialize`/`tools/list`。而 `README.md:84-135` 给的是标准 `mcpServers` 配置块。
- **库扫描在主进程内执行**：注释自己写着「如果真需要隔离才该走 subprocess」（`handlers.py:375-377`）⇒ 一个死循环或爆内存的零件脚本会带走整个服务。
- **默认库目录不存在**：默认值 `part_library`（`state.py:32`），克隆内实测无此目录；README 举例的 `my_cq_workspace/`、`sample_house_workspace/` 又被 `.gitignore` 末行的 `*_workspace/` 排除 ⇒ 开箱扫描是空表。
- **版本钉不住**：`requirements.txt` 写 `cadquery==2.5.2`，而 `env_setup.py:104` 装的是**未钉版本**的 `cadquery`。
- **测试的真实覆盖面有限**：`tests/` 下 11 个文件（`tests/` 实测计数），只有 1 个真 import cadquery 的用例，几何断言只到「文件非空 / 含 `<svg`」（`tests/test_cadquery_core.py:48-56`），其余是 mock 单测 ⇒ 不能据它推断「几何对不对」。

## 6. 对我方目标的可用处（机制层面）

- **「执行 → 落盘中间件 → 按 id 再交付」** 正是 SolidWorks 侧该有的形态：一次 build 把零件/装配存成文件并登记，之后导出 STEP、读质量特性、出图都凭同一个 id，而不是每件事都重跑一遍建模（`handlers.py:173-190`）。
- **每 workspace 一个隔离环境 + 依赖 mtime 增量** 是「项目级依赖」的现成模板（`env_setup.py:53-140`），可搬到我们的多项目/多 SW 版本场景。
- **库即索引（目录 + docstring + mtime 缓存）** 是零件库的最小可用形态（`handlers.py:364-396`）；但元数据要换成显式 schema——docstring 解析只认单行，还为多词键 "Part Name" 单开了特例（`core.py:47-50`）。
- **反例：没有几何门禁**。返回 `success: true` 只意味着脚本没抛异常（`script_runner.py:111-120`），这正撞上我们那条「入口修好 ≠ 效果验证」。
- **反例：路径约束两套口径**（`handlers.py:467-480` 有守卫 vs `handlers.py:198-200` 无守卫）⇒ 我方工具面必须把 confinement 收到一处，不能靠每个 handler 自觉。
- 多参数组 fan-out 的形态可直接用于「参数扫描 / 一次出多规格」，但必须先修掉空转（§5）。

## 7. 许可与红线

- **无 LICENSE**：只读思想，不抄代码、不抄文本（含 `README.llm.md`/`context.llm.md`/`code_review.llm.md` 这类 LLM 语境文档）。
- `pyproject.toml:16` 的 MIT classifier 不是授权文件，作者自己在行尾留了 `# Choose appropriate license`——按「无许可 / 全版权保留」处理。
- 本次对克隆只读，未改任何文件。

## 8. 证据清单

```
D:\ai3d-survey\repos\bertvanbrakel__mcp-cadquery\README.md:5-10,22-36,84-135,152-165,225-226
...\pyproject.toml:13,16,20-28 · requirements.txt · .gitignore（末行 *_workspace/）
...\src\mcp_cadquery_server\handlers.py:16,76-139,89-113,173-200,221-302,304-450,467-480,494-536,539-578,714-724
...\src\mcp_cadquery_server\script_runner.py:61,74,90-92,104-108,111-120,145-168
...\src\mcp_cadquery_server\env_setup.py:10,15,27-33,37,53-140,77-80,88-137,104,108-137
...\src\mcp_cadquery_server\core.py:16-51,47-50,65,86-100,102-122,124-190,197-281
...\src\mcp_cadquery_server\state.py:19-21,32 · models.py:5-25 · cli.py:29-34 · mcp_api.py:24-43
...\src\mcp_cadquery_server\web_server.py:76,114 · stdio_server.py:37-50
...\server.py:13-14 · tests\test_cadquery_core.py:29-58 · tests\test_core_helpers.py:11
```
- 元数据来源：https://api.github.com/repos/bertvanbrakel/mcp-cadquery （取数 2026-10-24）。
- 计数实测（在克隆内跑 `Get-ChildItem`）：`tests/` 11 个 `test_*.py`；`src/mcp_cadquery_server/` 11 个模块；工具字典 10 条（`handlers.py:714-724`）。

## 9. 未确认事项

- 未安装、未运行（本机 Python 3.14.7，未建 venv）；本卡行为结论全部来自读码，等级 `读码`。
- `cadquery==2.5.2` 是否有 cp314 的 Windows wheel **未确认**（未去 PyPI 核 wheel 文件名）。
- 机读 tag 取严格口径：`verify=run-only` 指服务端只回传构建成败与异常栈（`script_runner.py:111-120`），几何读数虽有（`core.py:124-190`）但无自动判据；`orchestration=loop` 指回环由调用方闭合——服务端本身单次调用、不重试。
- 与标准 MCP 客户端的互通性**未实测**（§5 说协议目测不符）；`README.md:84-135` 的 RooCode 配置块能否真握手未验。
- `frontend/`（React 前端）未读；`code_review.llm.md`、`research_log.llm.md`、`context.llm.md` 只取了个别段落。
- 5 个 Pydantic 入参模型（`models.py`）与 handler 实际取值是否一一对应，只抽查了 `execute`/`export`/`save_module` 三条。
