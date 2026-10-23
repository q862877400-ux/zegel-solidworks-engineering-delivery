# andrewbartels1/SolidworksMCP-python

<!-- survey: class=H; repr=feature-tree; orchestration=single; verify=run-only; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `andrewbartels1/SolidworksMCP-python` · https://github.com/andrewbartels1/SolidworksMCP-python |
| 许可 | MIT（`LICENSE:1-3` 原文 `MIT License` + `Copyright (c) 2025 ESPO Corporation`）⇒ 可借鉴，移植须保留版权行；★ 与 `vespo92` 同一版权人（同一家族，见 §3.4）|
| 元数据 | stars 84 · 最近推送 2026-10-23T17:53:04Z · 语言 Python · 仓库 18538 KB（来源：`gh api repos/andrewbartels1/SolidworksMCP-python`，2026-10-24 取）|
| 克隆 | `C:\swprojects\andrewbartels1`（HEAD `600624f`，2026-09-22 19:02:18 -0700；远端 `pushed_at` 已到 2026-10-23 ⇒ **克隆落后约一个月**，本卡一切计数以克隆快照为准）|
| 证据等级 | 读码（未跑测试：跑 pytest 会在克隆内写 `.pytest_cache`/`htmlcov`，违反「不改 C:\swprojects」纪律）|

## 1. 一句话定位

**把 `vespo92` 的 Node 版整套搬到 Python 的工程化重写**：FastMCP + 单一 STA 线程执行器 + 适配器/熔断/连接池 + mock 适配器 + 133 个工具 + 128 个测试文件，附一套「catalog 校验 + 真机 smoke」的验证分层文档——但唯一在库的真机报告写的是 `Tests: 0`。（来源：本卡 §8 证据清单）

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：MCP stdio。所有工具统一收一个 Pydantic 模型 `input_data: <XxxInput>`（如 `create_extrusion(input_data: CreateExtrusionInput)`，`src/solidworks_mcp/tools/modeling.py`），参数名/单位在模型里定义一次。

**中间表示**：仍无几何 IR，但有两层间接——`Command`/参数对象（`adapters/base.py` 的 `ExtrusionParameters`/`LoftParameters`/`SweepParameters`/`RevolveParameters`）→ 适配器方法。**特征树是唯一的状态载体**，模型靠名字/选择集续接。

**生成**：两支。① 直接 COM（pywin32 适配器）；② **VBA 文本生成**（`adapters/vba_macro_executor.py:177-178` 写 `%TEMP%/<name>_<ts>.swp` 再跑），由 11 个 `generate_vba_*` 工具（`vba_generation.py` 10 个 + `automation.py:286` 1 个）产出文本、`execute_macro`/`batch_execute_macros` 执行。

**编排**：名义上有 `execute_workflow`（`tools/automation.py:531`）与一批 `batch_*`（批量导出/批量文件操作/批量宏/批量套模板），**但 `execute_workflow` 在全仓没有任何适配器实现**（见 §5）；实际编排是「一次调用一个工具」。

**执行**：`ComExecutor`（`adapters/com_executor.py`）——单条专职 STA worker 线程，`CoInitialize()` 只在启动时调一次，所有 COM 调用作为 callable 提交、Future 等待（`:4-30` 的注释把理由讲透：FastMCP 在工作线程派发工具，缓存的 `swApp` 跨线程必炸）。方法/属性混淆由 `adapters/sw_type_info.py` 的 `flag_methods` 用 makepy 生成的包装判定（`tests/live/test_live_sw_regression.py:8-14`）。

**验证**：分两层且写成了文档（`docs/user-guide/real-tool-validation-matrix.md`）：Layer 1「全部注册工具的 catalog 校验」（工具名唯一、跨类核心名存在、写快照 JSON）；Layer 2「真机 smoke」（part/assembly/sketch 生命周期）。**逐特征几何校验没有**——`GetRebuildStatus` 只在 `get_model_info` 里读一次（`adapters/solidworks/io.py:1521-1523`），不是每个特征的门。

**交付**：`export_step`/`export_stl`/`export_iges`/`export_dwg`/`export_pdf`/`export_image` + `pack_and_go_assembly`（`tools/export.py`、`tools/file_management.py`）。

## 3. 技术方案要点（可迁移的机制）

### 3.1 工具清单与粒度：**133 个（实测），按 12 个域模块注册，无 `operation` 分派**（来源：本卡 §8 证据清单）

★ 起点数字「128 个工具 / 147 个测试文件其中 7 个 live」来自本仓 `AGENTS.md` §四 台账；**实测不符，以实测为准**：`@mcp.tool` 装饰器 133 个（逐文件：modeling 27、sketching 19、file_management 18、drawing 13、vba_generation 10、automation 8、drawing_analysis 8、export 7、macro_recording 7、template_management 6、analysis 5、docs_discovery 5 = 133，`src/solidworks_mcp/tools/*.py`），工具名去重后仍 133（`automation.py:381/423` 与 `macro_recording.py:182/228` 函数同名，但前者带显式 `name="automation_start_macro_recording"`，故注册名不撞）。测试侧同样对不上：`tests/**/*.py` 146 个（台账 147）、`test_*.py` 128 个、`tests/live/*.py` 5 个共 83 个 `def test_`（台账写 7 个 live；若把 `tests/solidworks_mcp/test_smoke_agents_live.py`——LLM 冒烟而非 SW 真机——算上则是 6 个文件名含 live）。

**三个数字互相打架（这正是「宣称 vs 事实」的标本）**：README 写 **132**（`README.md:11`）、历史清单写 **122**（`SWChecklist.md:16`）、代码实测 **133**。132→133 的差正好是最后一个提交 `feat: wire add_chamfer as an MCP tool (#110)`（`600624f`）——加了工具没同步 README。作者自己写了门禁 `src/utils/check_tool_docs_consistency.py`（AST 数工具数，全仓 "N tools" 声明逐个核对，并显式列出故意不改的 `CHANGELOG.md`/`SWChecklist.md`/`docs/planning/`），说明这套矛盾是可被机器抓住的，只是没接进 CI。

**分组**：12 个 `register_*_tools(mcp, adapter, config)` 函数在 `tools/__init__.py:25-50` 依次调用，`server.py:325-326` 再把 `len(await mcp.list_tools())` 当权威计数。粒度介于「一动词一工具」与「一参数组一工具」之间：草图有 `add_line`/`add_circle`/`add_spline`，但零件只有 `create_extrusion`/`create_revolve`/`create_loft`/`create_sweep`（没有单独的 fillet 参数族，倒有 `add_fillet`/`add_chamfer`）。

### 3.2 桥接方式与单实例互斥

**桥接**：进程内 COM（pywin32）+ 同进程 VBA 宏（写 `.swp` 到 `%TEMP%` 再 `RunMacro`）。无外部 exe、无插件、无 IPC。

**单实例互斥：没有。** 全仓 `Mutex/mutex/single_instance` **零命中**；唯一的 `asyncio.Lock` 在 `connection_pool.py:113`，保护的是池内租借，不是「一机一 MCP」。反而做了**连接池**（`ConnectionPoolAdapter`，注释写「parallel operations / load balancing」，`connection_pool.py:1-14`）——与「一个 SolidWorks 会话、一个 COM apartment」的前提相反。真机测试里用 `_pace_live_tests`（每例后清空文档 + 可选 4 s 间隔）规避累积崩溃（`tests/live/conftest.py:17-23`），这是在**绕**而不是**解**多连接问题。

**可迁移的四件机制**：

1. **`ComExecutor` 单 STA 线程**（`adapters/com_executor.py:11-22`）：注释直接点名 FastMCP 工作线程导致 `AttributeError: SldWorks.Application.<method>` 的故障形态，并给出「`_FlagAsMethod` 结果在同一对象生命期累积」的副作用说明。
2. **`flag_methods` 用 makepy 包装判方法/属性**（`adapters/sw_type_info.py`，被 `tests/live/test_live_sw_regression.py:8-14` 引为已修 bug ③）：与 `Slacker-LLC` 的 `_FlagAsMethod` 同解，但依据是类型库而非运行时猜测。
3. **验证分层写进文档**（`docs/user-guide/real-tool-validation-matrix.md`）：明确「catalog 校验」保证什么（无注册回退、名字不撞）、不保证什么，并单列「What Is Still Simulated」段（mock 适配器返回罐头、不验证 CAD 结果）。
4. **live 测试闸门与安全清理**（`tests/live/conftest.py:1-40`）：`SOLIDWORKS_MCP_RUN_REAL_INTEGRATION` 未设时 `collect_ignore_glob` **根本不收集**；`_ScratchSession` 只关「从未保存」的文档、只删自己写的文件，因此可安全跑在用户有真活的会话上。

### 3.3 覆盖域（实测按工具名归类，一工具归一类）

| 域 | 有/无 | 代表工具（清单见 `docs/user-guide/tool-catalog/*.md`，12 个分册 + `index.md`） |
|---|---|---|
| 会话 | 有 | `open_model` `close_model` `create_part` `list_open_documents` `activate_document` `save_part` `save_all` 类 |
| 参考 | 有 | `create_reference_plane` `create_axis` `create_reference_point` |
| 草图 | 有 | `create_sketch` `add_line` `add_arc` `add_spline` `sketch_offset` `sketch_mirror` `check_sketch_fully_defined` |
| 尺寸 | 有 | `add_dimension` `set_dimension` `get_dimension` `add_sketch_dimension` |
| 零件 | 有 | `create_extrusion` `create_cut_extrude` `create_revolve` `create_loft` `create_sweep` `add_fillet` `add_chamfer` `pattern_circular` `mirror_feature` `delete_feature` |
| 曲面 | **无** | —— |
| 钣金 | **无** | ——（VBA 生成器里也没有 sheet metal） |
| 焊件 | **无** | —— |
| 模具 | **无** | —— |
| 装配 | 有 | `create_assembly` `insert_component` `add_mate` `list_components` `check_interference` `pack_and_go_assembly` |
| 工程图 | 有 | `create_drawing` `create_drawing_view` `create_technical_drawing` `auto_dimension_view` `update_title_block` `update_sheet_format` + 8 个 `*_drawing_*` 分析器 |（来源：本卡 §8 证据清单）
| 检查 | 有 | `analyze_geometry` `calculate_mass_properties` `check_interference` `check_drawing_standards` `check_drawing_compliance` `validate_drawing_completeness` `compare_drawing_versions` |
| 仿真 | **无** | —— |
| 外观 | 有（弱） | 只有 `get_material_properties`、`export_image`；无外观/颜色/贴图设置 |
| 宏 | 有（强） | 11 个 `generate_vba_*`（10 个在 `vba_generation.py`、1 个在 `automation.py:286`）+ `start/stop_macro_recording`（含 `automation_` 前缀两个）+ `execute_macro` `batch_execute_macros` `analyze_macro` `optimize_macro` |
| 高级 | 有（强） | `list_configurations` `manage_design_table` `create_template`/`extract_template`/`batch_apply_template` `classify_feature_tree` `rename_feature` `undo` 与 5 个 `docs_discovery`/API 查询工具 |（来源：本卡 §8 证据清单）

**12/16 域**：多出的是**宏/VBA/模板/工程图分析**这一整条工程化支线；缺的是曲面/钣金/焊件/模具/仿真五个几何域。

### 3.4 家族关系（影响我们的引用口径）

`andrewbartels1` 与 `vespo92` 是**同一份代码的两个实现**：同样 `Copyright (c) 2025 ESPO Corporation`；`adapters/base.py:1-4` 明写「following the adapter pattern from the original TypeScript implementation」；两者都有 `SWChecklist.md`（76 工具时代的 Node 史）；`andrewbartels1` 的 `.github/workflows/integration-tests.yml` 甚至是 **Node 流程的复制件**（`npm ci`/`npm run build`/`npm run test:integration`，`:44-62`），在 Python 仓必然失败。
⇒ 我方并能力时**不能把它俩当两个独立来源**重复计权重；学机制选其一即可（倾向 `Slacker-LLC`/`andrewbartels1` 的 Python 侧）。

## 4. 运行条件与依赖

- 真机 SolidWorks（Windows 10/11）+ **Python ≥3.13**（`pyproject.toml:10`；README `:63-68` 写 Windows + python.org 的 Python 3.13+、并在 `.venv` 里跑，WSL 只适合 docs/tests/mock）。
- 依赖体积大：`uv.lock` 682 KB，含 fastmcp、pydantic-ai、sqlalchemy（agents/history_db）、loguru、typer、pytest 全家桶（`pyproject.toml` + `uv.lock`）。
- 离线可用：`USE_MOCK_SOLIDWORKS` 走 `adapters/mock_adapter.py`（120 KB 罐头）——能跑 CI，但**不验证 CAD 结果**（作者在 validation matrix 里自己写死这句）。
- 有 UI 子应用（`src/solidworks_mcp/ui/`，FastAPI + 本地 LLM + 预览 + checkpoint），非 MCP 主路径。

## 5. 失败模式与已知坑

1. **真机证据为零**：唯一在库的真机报告 `tests/reports/real_integration_report.md:3-13` 写着 `Generated: 2026-03-01` / `Tests: 0` / `Passed: 0` / `Skipped: 0`，并记录当时 `Registered tool names captured: 96`。**有 83 个 live 测试函数不等于跑过 83 个**——报告是空的。
2. **CI 的「夜跑真机」是摆设**：`integration-tests.yml:30` 声明 `runs-on: [self-hosted, windows, solidworks]`，`:44` 却执行 `npm ci`、`:62` 执行 `npm run test:integration`——本仓没有 `package.json`，第一步就失败。
3. **死工具**：`execute_workflow`（`tools/automation.py:531`）依赖 `adapter.execute_workflow`，而 `pywin32_adapter.py`/`mock_adapter.py`/`base.py` 都没有该方法 ⇒ 永远返回「Active adapter does not support execute_workflow」。它仍在 `tools/` 里被注册、被计数。
4. **三处工具数不一致**（132/122/133，§3.1）：说明书与代码已经分叉。
5. **「Verified Windows Setup」只验安装不验 CAD**：`README.md:45-58` 的「已验证」指 `Registered ... tools` / `Connected to SolidWorks` 两类日志行，与「特征建对了没」无关。
6. **连接池与单实例前提冲突**（§3.2）：多连接并行在 SolidWorks 上不是性能问题而是死锁问题。
7. **live 测试的已知脆弱点被作者记录**：headless（窗口隐藏）会让 `CreateCornerRectangle`/`InsertSketch` 间歇 `RPC_E_DISCONNECTED`，wave3 8 个里 2 个 headless 必 flake（`tests/live/conftest.py:25-31`）——省我们一次踩坑。

## 6. 对我方目标的可用处（机制层面）

**能学**：
- **`ComExecutor` + `flag_methods`**：这是「FastMCP 异步派发 × STA COM × 方法/属性混淆」三坑的一套完整解，且有 live 回归测试锁定（`test_live_sw_regression.py:1-20` 把 3 个已诊断 bug 写成测试）。我们的 `sw_connect.py`/工具层可对照它检查是否也存在跨线程引用。
- **验证分层文档**（catalog 校验 vs 真机 smoke，各自声明保证边界）：正是我仓 `capabilities.yaml` 五级 `level` 需要的「分层话术」——可以照它的措辞把「注册可见 ≠ 可用」写进我们的报告。
- **`check_tool_docs_consistency.py`**：把「N 个工具」这类声明做成 AST 门禁（连「哪些文件故意不改、为什么」都写进 docstring）——直接对应本任务硬纪律「含 N 个的行必须同行自带出处」，可作为我们 `release_check` 的一道门。
- **live 测试安全清理**（只关未保存文档、只删自写文件、可选限速）——我们真机测试要跑在用户有真活的会话上时，这是现成范式。
- **覆盖矩阵**（`docs/planning/solidworks-api-coverage.md`，47 KB，接口族↔工具名）：可作我们 `union-coverage-matrix.md` 的对照输入。
- **统一 `input_data` 信封**：133 个工具一个参数模型，便于客户端 schema 校验与文档生成。（来源：本卡 §8 证据清单）

**不能学**：
- **「工具多但验证空」**：133 工具 / 128 测试文件看起来比 `Eduardof0nt` 强，但真机报告 `Tests: 0`（§5.1）说明测试文件数不是证据；且 mock 适配器 120 KB 的罐头返回会制造「CI 全绿」的假象（作者自己承认）。我们并入时只能记 `source_verified`。（来源：本卡 §8 证据清单）
- **注册了却没人实现的工具**（`execute_workflow`）：工具表虚高一名，客户端会调用失败——我们的清单门禁应能抓「声明的能力无实现」。
- **Node 流程复制进 Python 仓的 CI**：文档/工作流与代码不同源，会产生「看起来有真机夜跑」的错觉。
- **连接池并行**：与单源运行冲突，不学。
- **Agent/UI 层的大依赖**（pydantic-ai、sqlalchemy、本地 LLM、FastAPI）：把「CAD 自动化」与「agent 编排/知识库」耦合，正是我们要避免的重心漂移。

## 7. 许可与红线

MIT（`LICENSE:1-3`，`Copyright (c) 2025 ESPO Corporation`）：可读/改/商用，义务是保留版权声明与许可全文。无 NOTICE 义务。★两个注意点：① 它与 `vespo92` 同版权人，**同一段逻辑别双重计入来源权重**；② 其 `SWChecklist.md` 里保留了旧 Node 实现的表与 QA 日志（明确标为历史文档），移植任何表都要先确认它描述的是当前 Python 实现还是 76 工具时代。

## 8. 证据清单

- `C:\swprojects\andrewbartels1\src\solidworks_mcp\tools\__init__.py:25-50`（`register_tools` + 12 个 register 调用）· `server.py:325-326`（`len(mcp.list_tools())` 为权威计数）
- 工具计数：`Get-ChildItem src\solidworks_mcp\tools -Filter *.py` 后逐文件 `@mcp.tool` 计数 ⇒ 27/19/18/13/10/8/8/7/7/6/5/5，合计 133
- `C:\swprojects\andrewbartels1\src\solidworks_mcp\adapters\com_executor.py:4-30`（STA 理由）· `adapters\connection_pool.py:1-14,113`（池 + 唯一 `asyncio.Lock`）
- `C:\swprojects\andrewbartels1\tests\live\conftest.py:1-40`（闸门/清理/headless 记录）· `tests\live\test_live_sw_regression.py:1-20`（3 个已修 bug）
- `C:\swprojects\andrewbartels1\tests\reports\real_integration_report.md:3-13`（`Tests: 0`，2026-03-01，96 个注册名）
- `C:\swprojects\andrewbartels1\.github\workflows\integration-tests.yml:30,44,62`（self-hosted 却跑 `npm`）· `ci.yml:16,34`（ubuntu + conda + `make test`）· `README.md:11`（132 tools）· `:15`（under active construction）· `:45-58`（Verified Windows Setup 的真实含义）
- `C:\swprojects\andrewbartels1\SWChecklist.md:16`（122）· `src\utils\check_tool_docs_consistency.py:1-24`（门禁自述）
- `C:\swprojects\andrewbartels1\docs\user-guide\real-tool-validation-matrix.md:1-40`（两层验证 + still simulated）
- 测试计数：`tests/**/*.py` 146 个；`test_*.py` 128 个；`tests/live/*.py` 5 个共 83 个 `def test_`
- `gh api repos/andrewbartels1/SolidworksMCP-python`（2026-10-24 取：stars/pushed_at/language/size）

## 9. 未确认事项

1. 远端 2026-09-22→2026-10-23 这一个月新增了什么（克隆落后）；133 这个数字在远端 HEAD 上是否已变——**未确认**，需 `git fetch` 后复核。
2. `flag_methods` 在所有接口族上是否都正确（makepy 包装是否覆盖未生成 makepy 的机器）——只读了注释与调用点，未验证。
3. 83 个 live 测试在真机上究竟通过率多少——**查不到**任何一次运行记录（唯一报告 `Tests: 0`）。（来源：本卡 §8 证据清单）
4. `sw_type_info` 与 `Slacker-LLC` 的 `flag_methods` 哪个更可靠（一个靠类型库、一个靠运行时 `_FlagAsMethod`）——本卡不给结论，需各自跑同一批成员对照。
