# hjbaard/SolidWorks-MCP

<!-- survey: class=H; repr=feature-tree; orchestration=single; verify=numeric; deliver=STEP; evidence=实测 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `hjbaard/SolidWorks-MCP` · https://github.com/hjbaard/SolidWorks-MCP |
| 许可 | **MIT**（`LICENSE:1-3` = `MIT License` / `Copyright (c) 2026 Henk Jan Baard`；`pyproject.toml` `license = { text = "MIT" }`）⇒ 可读可抄可商用，保留版权声明即可 |
| 元数据 | stars 20 · forks 3 · 语言 Python · 仓库 1822 KB · 建档 2026-06-25 · 最近推送 2026-10-29（来源：`gh api repos/hjbaard/SolidWorks-MCP`，2026-11-02 取）|
| 克隆 | `D:\swagent-2026Q4\repos\hjbaard__SolidWorks-MCP`（`--depth 1`，HEAD `a7fd83c`，提交时间 2026-10-29 15:14:59 +0100）|
| 证据等级 | **实测**（限离线单测：`python -m pytest -m "not solidworks"` ⇒ 388 passed / 2 failed / 334 deselected；**SolidWorks 未跑**，建模能力结论止步 `source`）+ 读码 |

## 1. 一句话定位

**目前把「每一步都回读几何」写进产品契约最彻底的一家 Python MCP 服务端**：87 个工具（`src/solidworks_mcp/server.py`）、每个建模调用都返回实测体积／质量／包围盒，配一个专用 STA COM 线程、一个「失败即回滚到调用前特征树」的守卫，以及 25 KB 给 agent 读的建模指南。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：MCP stdio（`FastMCP`）。连接的客户端先收到一段短指令（会话约定 + 坑），完整版是资源 `solidworks://guide`（`src/solidworks_mcp/server.py:20-54`，正文 `src/solidworks_mcp/guide.md` 约 25 KB）。

**中间表示**：**没有几何 IR**。三个替代物：① 单位契约——MCP 边界一律 mm/度，进 `units.py` 一次性换成米/弧度（`src/solidworks_mcp/units.py:1-20`）；② 参数化标识——每个特征拿到稳定名，尺寸按角色取名（`width@Sketch1` / `D1@BlockExtrude`），改尺寸走 `set_dimension`（`server.py:26` 的指令段）；③ 选择器——面不按拓扑 ID 存，按「方向 + 点」现算（见 §3.2）。

**生成**：不生成代码、不生成宏、不跑任意脚本（`server.py:41-42` 明写 "There is no run arbitrary code tool"）。

**编排**：无编排层。一次调用一个工具，`_call()` 把可调用对象投到 COM 线程（`server.py:87-105`）。

**执行**：三层防御——① 早绑定强制（`src/solidworks_mcp/binding.py:1-15` 说明为什么：`GetActiveObject` 返回的 dispatch 其 `GetTypeInfo()` 失败，纯晚绑定下 `IModelDoc2.FirstFeature` 报 `DISP_E_MEMBERNOTFOUND`，于是从安装的 typelib 生成 makepy wrapper 再 `wrap()` 回强类型接口，走 `InvokeTypes(dispid,…)` 绕过名字解析）；② 专用 STA 线程（`src/solidworks_mcp/com_worker.py:1-23`，`ComWorker._run` 在该线程 `CoInitialize`，全部 COM 排队串行）；③ 超时语义（`com_worker.py:37` `DEFAULT_CALL_TIMEOUT_S = 120.0`，超时抛出「大概是模态框挡住了」的可读错误，**且明确说明 COM 调用无法强制中止，只解除等待**，`com_worker.py:20-22`）。

**验证**：三层——① 每个建模调用返回实测质量属性（`session.py:5022` `get_mass_properties`，强制 `UseSystemUnits = True` 且失败即报错，`session.py:5032-5034`）；② 失败回滚（`session.py:3928-3950` `run_guarded`：进入前拍「特征名集合」快照，异常时按名删掉新增特征再 `ForceRebuild3`，`session.py:4039-4049`）；③ 判据在**测试**里而**不在工具里**——集成测试拿手算体积对拍（README 自述 724 tests，`tests/` 实测 511 个 `def test_`）。

**交付**：`export` 到 STEP/STL/IGES/Parasolid/3MF（`server.py` 的 `export` 工具），`make_drawing` 出 PDF/`.slddrw`（第一角投影）。

## 3. 技术方案要点（可迁移的机制）

### 3.1 工具面与粒度：**87 个，一动词一工具，零 `operation` 分派**（实测计数，`src/solidworks_mcp/server.py`）

计数命令与结果：`(Select-String -Path 'src\solidworks_mcp\server.py' -Pattern '@(mcp|server)\.tool' -AllMatches).Count` ⇒ **87**，与 README 自述「87 tools in total」一致（README「It verifies, not just generates」段）。粒度是「一动词一工具」，且**把「同一动词的不同几何入口」也拆开**：`add_extruded_profile` / `add_extruded_profile_on_plane` / `add_extruded_profile_on_face` / `add_extruded_spline` 是四个工具，理由是选择面这件事本身要参数化（`src/solidworks_mcp/server.py` 工具表）。无 `operation` 枚举、无万能代码口。

### 3.2 持久引用：**不解，改走「语义选择器」**（这是本卡最该抄的一条）

它的答案不是存拓扑 ID，而是**每次调用现算**：面的选择器是方向 + 可选 `:outer`/`:inner`，或「一个落在面上的 3D 点」（`session.py:595-623`）。语义是「朝向 `+z` 的最外侧面」而不是「面 #17」，所以几何变了、面重建了，同一个选择器仍然指着「该方向的那个面」。选不中时报错并**列出该方向上所有面所在的标高**（`session.py:616-619`），让 agent 能自己改点——这是把选择失败变成可纠正信号，而不是静默选错。

代价写在同一处：当一个方向上有多张面（被槽切开顶面、抽壳后的内腔面），必须靠 `:outer`/`:inner` 或点来消歧（`server.py:25` 的指令段）。⇒ **这是绕行不是解决**：它把「持久引用」换成了「可复算的选择谓词」，前提是 agent 每次都能说出谓词。

### 3.3 事务式建模：有，而且粒度选得对

`run_guarded`（`session.py:3928-3950`）包住**每一次工具调用**：快照是「当前文档标题 + 特征名集合」，回滚是「删掉集合里没有的特征，从新到旧」。三个设计细节值得抄：
- **只回滚特征树，不假装回滚一切**：函数换文档就不回滚（`_roll_back` 先比标题，`session.py:4035`），并在错误里如实说「没清干净的是哪些」（`session.py:3943-3944`）。
- **`CommandInProgress` 继承而不是强设**：`_command_in_progress` 只在状态确实要变时才写，返回旧值由 `finally` 还原（`session.py:4013-4026`），注释记录实测读数「置位后 COM 调用快 100 倍（读 144 条边 0.01 s，原 1.5 s；verified）」，且「它按计数生效，每写一次 True 要配一次 False」。
- **静音 UI 治崩溃**：`_quiet_ui` 在操作期间停视图/特征树/草图重绘，注释给出实测「SP4.0 上 7 次跑崩 6 次，改后 15 次调用 0 崩」（`session.py:3970-3986`）。

### 3.4 回读验证：给了「原始量」，没给「期望值」

每个建模工具返回 `volume_mm3`/`mass_kg`/`bounding_box_mm`，并在连接指令里要求 **agent 自己做手算对拍**（`server.py:33`：「Every modelling call returns volume, mass and bounding box: check them against your own hand calculation after each step」）。⇒ 它把「判据」外包给模型，工具只负责**如实测量**。这与我方 `verify` 从 `run-only` 升级的方向一致，但**力度弱于** forge_ai 的独立复算（见 `sw-kumar1441-forge-ai.md` §3.2）与 Millwright 的分类断言（见 `sw-raylanlin-millwright.md` §3.3）。

两个「官方接口骗人」的实测读数（`session.py:5046-5053`）：`IPartDoc.GetPartBox` 对曲面**跑松**（放样到 10 的零件报 10.004）；`IAssemblyDoc.GetBox` 把旋转过的零件按外包盒算（Ø20 圆盘转 45° 报 28.3 宽）——所以它自己按实体极点算紧包围盒。

### 3.5 单源 COM 互斥：进程内一档，且把前提写死

一个进程、一个 `ComWorker` 线程、一个队列（`com_worker.py:40-99`）。**没有跨进程互斥**，但把后果写进了注释与错误信息：超时提示「大概是模态框」、`shutdown()` 显式拒绝新任务（`com_worker.py:73-74`）。⇒ 与我方「运行时只能有一个 SolidWorks MCP」同一档位。

### 3.6 早绑定 vs 晚绑定：**与本轮另外两家结论相反，两家都对**

它说「本 build 上早绑定是强制项」（`binding.py:1-15`）；Millwright 说「别为此切早绑定，会撞接口墙」（`docs/COM-PITFALLS.md` #1-#2）。两者撞的是**同一个**故障（`IModelDoc2` 上找不到 `GetBodies2`/`FirstFeature`），解法相反：一家把 raw dispatch 包回生成的强类型接口类、另一家留在纯 IDispatch + `_FlagAsMethod`。⇒ 说明这里没有唯一正解，只有「按接口墙的位置选边」；**可迁移的是这个判据**，不是任一家实现。

## 4. 运行条件与依赖

- Windows + **正在运行的** SolidWorks（`GetActiveObject` 附着，不启动；`binding.py:85-95`）。
- Python ≥3.11；依赖只有两条：`pywin32>=306; sys_platform == 'win32'` 与 **`mcp>=1.26,<2`**（`pyproject.toml` 依赖段注释写明理由：mcp 2.x 改名 `FastMCP`，导入即炸）。
- 需要 **Y-up 零件模板**；Z-up 零件会被明确拒绝（README「Requirements and compatibility」）。
- 自检入口 `uvx solidworks-mcp --selftest`（`src/solidworks_mcp/selftest.py`）。
- 我本机实测（2026-11-02，Python 3.14.7）：`PYTHONPATH=src python -m pytest -m "not solidworks" -q -p no:cacheprovider` ⇒ **388 passed, 2 failed, 334 deselected in 124.72 s**。两条失败都在 `tests/test_server_portability.py`，根因是它 spawn 子进程假装非 Windows 时按 GBK 解码 stdout 抛 `UnicodeDecodeError`，reader 线程死掉后子进程 60 s 超时——**是本机代码页问题，不是产品逻辑失败**。

## 5. 失败模式与已知坑

自述 + 实读：
1. **`mcp` 2.0 会打断导入**：`pyproject.toml` 把上界压在 `<2` 并写明原因。
2. **首次调用慢 / `EnsureModule` 报错**：makepy 生成 `gen_py` 缓存；缓存坏了要删（README Troubleshooting）。
3. **只测过 SOLIDWORKS 2026（3DEXPERIENCE R2026x）**，README 自己说 2020–2025「should work, but that is untested」。
4. **模态框仍会冻结调用**：120 s 超时只解除等待，不解除线程（`com_worker.py:20-22`）。
5. **`AUTO` 文档切换不回滚**：换过文档的调用失败后不清理（`session.py:3933`）。
6. **语言本地化**：标准面/特征名走本地化名，同时用 `D1@<name>` 这类语言无关寻址规避（README 与 `server.py:26`）。
7. **「724 tests」与实测 511 个 `def test_` 的差**（`tests/test_features.py` 等 30 个文件的 `def test_` 计数）：差在参数化用例展开，**未逐个核对**（见 §9）。
8. **`pytest` 离线层在本机要 2 分 4 秒**（实测：`python -m pytest -m "not solidworks"`），其中 334 个用例因 `solidworks` marker 被 deselect——**离线层覆盖的是纯函数**（单位、选择器解析、多边形清洗、装配位姿数学），COM 行为一律不测。

## 6. 对我方目标的可用处（能学 / 不能学）

**Q2 逐条答**：
| 问题 | 它解到什么程度 | 依据 |
|---|---|---|
| 持久引用（几何变更后选择失效） | **不解，绕行**：无拓扑 ID，选择器是「方向 + 点」现算，选不中报出可选标高 | `session.py:595-623` |
| 回读验证 | **解一半**：工具如实返回体积/质量/包围盒 + 回滚；但「对不对」要 agent 手算，工具不自带期望值 | `session.py:5022`、`server.py:33` |
| 事务式建模 | **解了**：每次工具调用一个特征树快照 + 失败按名回滚；换文档不回滚且如实说明 | `session.py:3928-4049` |
| 单源 COM 互斥 | **解了进程内那一档**：单 STA 线程 + 队列；无跨进程互斥 | `com_worker.py:40-99` |

**Q3 答**：**MCP 服务端**；工具面 **87 个**（`src/solidworks_mcp/server.py`，命令见 §3.1）；粒度 = 一动词一工具，**并且把「几何入口」也当独立工具拆**（同一 extrude 四种入口四个工具），无 `operation` 分派、无万能代码口。

**能学（按性价比排序）**：
1. **`run_guarded` 的「特征名集合」快照回滚**——比「事务日志」便宜得多，天然支持「调用失败 = 零件没变」，且能如实报出「没清干净的特征名」（`src/solidworks_mcp/session.py`）。我方 439 个工具里凡改特征树的都该包这一层。
2. **`CommandInProgress` 的「继承而非强设 + 计数语义」**——直接补我方护栏的一条已知坑，且它给了实测读数（144 条边 0.01 s vs 1.5 s，`src/solidworks_mcp/session.py:4017`）。
3. **`_quiet_ui` 的崩溃抑制**（停重绘 → 操作 → 恢复），带崩溃计数证据，与我方弹窗护栏是同一类「把不确定性变成可观测」的思路。
4. **「语义选择器 + 选不中时报出候选标高」**——把选择失败变成 agent 可纠正的输入，而不是静默选错面。我方选择器的报错信息可以照这个形状写。
5. **两个包围盒陷阱**（`GetPartBox` 曲面跑松、装配 `GetBox` 按外包盒算旋转件）——便宜、高杀伤，各配一个负例测试。
6. **早绑定强制 + `wrap()` 幂等 + 返回 None 直通**（`binding.py:65-74`）：`wrap()` 对 `None` 原样返回，让调用方能用 `if not ...` 接住 SolidWorks「失败不抛异常」的返回值。
7. **依赖上界写理由**（`mcp<2`）：与我方「依赖声明里写清为什么」一致，是现成范本。

**不能学**：
- **把判据外包给模型**：它靠「agent 每次手算」当验证。我方若照抄，等于把 `verify` 又降回 `run-only`——**只能取它的「如实测量」，不能取它的「判据位置」**。
- **`export` 白名单式的宽容**：它允许把 3MF/PNG 与 STEP 放在同一个工具里，我方 `deliver` 分类要更严（这是它做得松的地方）。
- **无 IR**：它没有中间表示，几何全靠特征树 + 选择器现算，**结构上无法做「先编译后执行」**（对比 `sw-qdaia-auto-solidworks.md` 的 IR 路线）。

## 7. 许可与红线

**MIT**（`LICENSE:1-3`，`Copyright (c) 2026 Henk Jan Baard`）。可移植，义务只有一条：**保留版权声明**。★ 具体到本项目：凡移植 `run_guarded`/`_command_in_progress`/`_quiet_ui`/`binding.wrap` 的形状，来源头写 `hjbaard/SolidWorks-MCP（MIT，LICENSE:3）` + 说明改动了什么；无需 NOTICE、无 copyleft 传染。

## 8. 证据清单

- `src/solidworks_mcp/server.py`（87 个 `@mcp.tool()`，计数命令见 §3.1）· `:20-45`（会话指令：约定 / 小步验证 / 坑）· `:50-54`（`solidworks://guide` 资源）· `:87-105`（`_call` 错误规整为 `{ok:false,error}`）
- `src/solidworks_mcp/com_worker.py:1-23`（为什么要专用 STA 线程、不能注册事件 sink）· `:37`（`DEFAULT_CALL_TIMEOUT_S = 120.0`）· `:79-94`（超时错误文案）· `:73-74`（关停后拒绝新任务）
- `src/solidworks_mcp/binding.py:1-15`（早绑定强制的原因）· `:26-27`（typelib GUID）· `:48-62`（`EnsureModule` 失败 = 修安装）· `:65-74`（`wrap` 幂等、`None` 直通）· `:85-95`（`GetActiveObject` 附着 + `Visible=True`）
- `src/solidworks_mcp/session.py:595-623`（按法向选面 / 按点选面 / 选不中报标高）· `:633-651`（方向表与 `#5` 索引）· `:3928-3950`（`run_guarded`）· `:4013-4026`（`CommandInProgress` 继承与实测加速）· `:4034-4049`（回滚实现）· `:3970-3986`（静音 UI 与崩溃读数）· `:5022-5044`（质量属性 + 强制 SI）· `:5046-5060`（包围盒陷阱）· `:4392`（`_failing_features`）· `:3501`（`_under_defined_sketches`）
- `tests/conftest.py:1-63`（两层测试；`part` fixture 在收尾强制断言「没有欠定义草图」——**把「全约束」做成每个用例的通用水位线**）
- `tests/test_server_portability.py`（本机 2 例失败的位置）
- `pyproject.toml`（`requires-python = ">=3.11"`；依赖 `pywin32>=306; sys_platform=='win32'`、`mcp>=1.26,<2` 及压上界的理由；`[tool.pytest.ini_options] markers`）
- 实测：`PYTHONPATH=src python -m pytest -m "not solidworks" -q -p no:cacheprovider` ⇒ `388 passed, 2 failed, 334 deselected in 124.72s`（2026-11-02，Python 3.14.7）
- 元数据：`gh api repos/hjbaard/SolidWorks-MCP`（2026-11-02 取 stars/pushed_at/license）

## 9. 未确认事项

1. **README 的「724 tests」与仓内 511 个 `def test_` 对不上**（`README.md` 与 `tests/` 实测计数）——差值是参数化展开还是历史遗留，**未确认**（未逐文件核对 parametrize 数量）。
2. **「每个特征都对拍手算」的覆盖面**：`tests/test_features.py` 59 KB 里逐特征的判据我只读结构未逐条核，**未确认**哪些特征是「体积对拍」、哪些只是「建出来了」。
3. **SW 2020–2025 是否真能跑**：README 自称 untested，`constants.py` 的枚举值是从 2026 typelib 读出的，**未确认**跨版本可用性。
4. **`--selftest` 的输出**：需要真机，**未跑**。
5. **`run_guarded` 在「工具内部换过文档又换回来」时**：标题相同会被判为同一文档，是否可能误删，**未确认**（代码只比标题）。
6. **`AddDimension` 类的模态框**：它靠「静音 UI + 超时」应对，未看到像 soheil-mp 那样主动应答对话框的实现——**未确认**是否有 Win32 层处理（本卡未见 `win32gui` 引用）。
