# faust-machines/fusion360-mcp-server

<!-- survey: class=H; repr=feature-tree; orchestration=single; verify=numeric; deliver=STEP; evidence=实测 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/faust-machines/fusion360-mcp-server （PyPI 包 `fusion360-mcp-server`，`README.md:52`） |
| 许可 | MIT（读克隆内 `LICENSE:1-3` 原文首行「MIT License」+ 版权行「Copyright (c) 2025 Faust Network, Inc.」；`pyproject.toml:7-8` 写 `license = "MIT"`）→ **可借鉴**（保留该版权行）；无 NOTICE 义务 |
| 元数据 | stars 131 · 最近推送 2026-10-06T04:52:43Z · 语言 Python（来源：`gh api repos/faust-machines/fusion360-mcp-server`，取数日 2026-10-24）；同源读数 open issues 8 · forks 28 |
| 克隆 | D:\ai3d-survey\repos\faust-machines__fusion360-mcp-server （HEAD `19b9f1e`，末次提交 2026-10-06T04:52:43Z，工作树干净；本次未改任何文件） |
| 证据等级 | **实测**（本机跑仓库自带单测套件：`PYTHONUTF8=1` 下 **367 passed / 15.69 s**；默认 GBK 环境下 **17 failed / 350 passed**，17 条全为同一个 `UnicodeDecodeError`——见 §5、§8。通道行为本身仍未实测，见 §9；来源：本卡 §4 的实测命令与输出）

## 1. 一句话定位

一个 MCP(stdin/stdout) 服务端 + 一份常驻 Fusion 360 的伴生插件：把「AI 客户端 → stdio MCP → TCP 套接字 → 插件内工作队列 → Fusion 主线程」串成一条单命令通道，暴露 93 个建模/查询/装配/钣金/曲面/CAM 工具，每条改模型的命令自动回带质量与包围盒增量（`README.md:11-20`、`README.md:126`、`addon/server/command_handler.py:270-273`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

1. **输入**：MCP 工具调用 `(工具名, 参数 dict)`。工具清单即唯一协议面，由 `src/fusion360_mcp/tools.py` 的静态表给出，`@app.list_tools()` 直接返回该表（`src/fusion360_mcp/server.py:187-189`、`src/fusion360_mcp/tools.py:2482-2495`）。
2. **中间表示**：线上只传一行 JSON `{"type": <工具名>, "params": {...}}`——**工具名同时就是插件侧的派发键**，没有第二套命令语言（`src/fusion360_mcp/connection.py:147-155`、`addon/server/command_handler.py:117-229`）。模型侧的"状态"是 Fusion 自己的设计树（草图/特征时间线/用户参数），读回走 `get_scene_info`/`get_object_info`/`get_parameters`（`addon/server/command_handler.py:120-123`）。
3. **生成**：没有代码生成路线。模型只能挑工具给参数；唯一的自由生成口是 `execute_code`，在 Fusion 进程里以全权限执行（`addon/server/command_handler.py:3528-3564`）。
4. **编排**：单进程 stdio，一次一条命令；服务端不排队、不循环、不做多智能体（`src/fusion360_mcp/server.py:469-475`）。工具按副作用分三档下发 `readOnlyHint`/`destructiveHint`/`idempotentHint`，供客户端决定是否自动放行（`src/fusion360_mcp/tools.py:2426-2479`）。
5. **执行——这条通道逐段**（本卡重点；与我方 SolidWorks COM/STA 约束同构）：
   - **段 A｜工具分派（客户端进程内）**：`call_tool` 用工具名查定义表 → `_send(mode, name, arguments)`；`mock` 模式在此分叉去 `mock_command`，真机模式取单例连接（`src/fusion360_mcp/server.py:191-221`、`src/fusion360_mcp/server.py:34-46`）。
   - **段 B｜客户端连接器**：`send_command()` 组一行 JSON、`sendall`、`settimeout(45.0)`、读回（`src/fusion360_mcp/connection.py:147-161`）。超时参数写死：命令 45 s、ping 5 s、重试 2 次、间隔 1 s（`src/fusion360_mcp/connection.py:36-41`）；45 s 是刻意大于插件侧 30 s 桥超时，好让结构化 `TIMEOUT` 先到（`src/fusion360_mcp/connection.py:36-38`）。帧格式是换行分隔 JSON，且带"无换行时整包试解析"的兜底（`src/fusion360_mcp/connection.py:201-219`）。
   - **段 C｜宿主插件监听**：插件 `run()` 里按 `CommandHandler → EventBridge → Fusion360MCPServer` 顺序装配，`FUSION_MCP_HOST/PORT` 覆盖绑定（`addon/Fusion360MCP.py:44-50`）。监听器每条客户端连接起一个**守护线程**（`addon/server/socket_server.py:149-156`），该线程只做收包与组帧，然后在 `_dispatch` 里把命令交给桥（`addon/server/socket_server.py:168-192`、`addon/server/socket_server.py:220-226`）。accept 循环外层还能自愈重绑（最多 10 次、每次隔 2 s）（`addon/server/socket_server.py:111-143`、`addon/server/socket_server.py:22-23`）。
   - **段 D｜跨线程交接（核心）**：`EventBridge.submit()` 把命令包成 `WorkItem`（带 `threading.Event` 完成信号与 `cancelled` 标记）压入 `queue.Queue`，然后 `fireCustomEvent` 捅一下主线程（`addon/server/event_bridge.py:25-38`、`addon/server/event_bridge.py:92-99`）。CustomEvent 在装配时注册到 `adsk.core.Application`，其 handler 的 `notify()` **运行在 Fusion 主线程**，只做一件事——`drain_queue()`（`addon/server/event_bridge.py:41-49`、`addon/server/event_bridge.py:67-69`）。另有一个 200 ms 的备份定时器，队列非空就再捅一次，防止"守护线程里 `fireCustomEvent` 不可靠"（`addon/server/event_bridge.py:22`、`addon/server/event_bridge.py:163-171`）；`ping` 走快路径，根本不进 API（`addon/server/event_bridge.py:86-89`）。
   - **段 E｜主线程执行**：`drain_queue()` 在主线程逐个取件，调 `CommandHandler.execute_command(command)`，异常被就地捕成字符串写回 item，最后 `item.done.set()` 唤醒段 D 里阻塞等待的套接字线程（`addon/server/event_bridge.py:130-157`）。派发表是惰性建一次并缓存在类属性上，未知命令返回 `UNKNOWN_COMMAND` 而不是抛（`addon/server/command_handler.py:117-118`、`addon/server/command_handler.py:234-242`）；业务异常统一转成 `{ok: False, error_kind, error_message, hints, traceback}` 数据包——**错误不抛过线程边界**（`addon/server/command_handler.py:247-264`）。
   - **段 F｜回程**：主线程结果 → 段 D 的 item → 段 C 的 `_send` 一 JSON 一行 → 段 B 的 `_recv_json` → 段 A 的 `_format_result` 渲染成 text（含 deltas 缩进块）或 image 块；`ok: False` 则置 `isError=True`（`addon/server/socket_server.py:228-234`、`src/fusion360_mcp/server.py:96-155`）。
   - **取消语义（防重复执行）**：客户端放弃后，段 D 把 item 标 `cancelled`，`drain_queue` 跳过它，于是"超时命令不会迟到执行"（`addon/server/event_bridge.py:101-111`、`addon/server/event_bridge.py:139-141`）；插件停止时把队列里剩下的 item 全部置错并唤醒（`addon/server/event_bridge.py:202-222`）。
   - **改状态命令永不自动重试**：连接层只对只读命令重试，改状态命令超时后直接报错并提示先查设计状态（`src/fusion360_mcp/connection.py:136-141`、`src/fusion360_mcp/connection.py:157-179`）。
6. **验证**：改模型的命令自动做前后快照——体数、整体包围盒、总质量（含 occurrence），差分后挂在返回的 `deltas` 上（`addon/server/command_handler.py:244-245`、`addon/server/command_handler.py:270-273`、`addon/server/command_handler.py:3620-3687`）；服务端再把 deltas 渲染成人类/模型都易读的几行（`src/fusion360_mcp/server.py:74-93`）。另有显式验证工具：`check_interference`、`measure_distance/angle`、`get_physical_properties`、`compare_meshes`（与参考网格的 min/max/mean/RMS 偏差）、`render_view`（把视图存 PNG 再以 base64 塞成 image 内容块）（`src/fusion360_mcp/tools.py:1651-1775`、`addon/server/command_handler.py:3693-3778`）。
7. **交付**：`export_step`/`export_stl`/`export_f3d` 加一个按 `format` 或扩展名分流的 `export`（`src/fusion360_mcp/tools.py:576-706`、`addon/server/command_handler.py:160-167`）；另有 `export_view_sheet` 出四视图 PNG 供目检（`addon/server/command_handler.py:1669`）。

## 3. 技术方案要点（可迁移的机制）

- **「快路径 + 慢路径」双通道**：`ping` 在主线程之外就能答，所以"插件活着但主线程被模态框卡住"与"插件没起"能被区分开（`addon/server/event_bridge.py:86-89`、`src/fusion360_mcp/connection.py:103-113`）。
- **执行权只给主线程**：所有 `adsk` 调用都在 CustomEvent 回调里发生，套接字线程永不直接碰 API（`addon/server/event_bridge.py:41-49`、`addon/server/socket_server.py:1-10`）。
- **备份心跳**：主事件通道之外再挂 200 ms 定时器，容错"跨线程发事件不可靠"（`addon/server/event_bridge.py:163-171`）。
- **超时即取消而非补执行**：`cancelled` 标记让"客户端已判失败"的命令不再迟到生效（`addon/server/event_bridge.py:101-111`、`addon/server/event_bridge.py:139-141`）。
- **改状态不重试**：把"重试一次可能做两遍"的代价显式写进错误文案（`src/fusion360_mcp/connection.py:165-179`）。
- **自动差分反馈**：每个改状态命令都免费获得质量/包围盒/体数增量；作者把这个当"不用渲染就能判效果"的替代（`addon/server/command_handler.py:270-273`、`AGENTS.md:202-204`）。
- **错误分类表 + 修复提示**：12 条正则 → `error_kind` + hints 清单，客户端拿到的不是散文而是可分支的标签（`addon/server/hints.py:16-128`、`addon/server/hints.py:131-144`；标签全集见 `AGENTS.md:200`）。
- **两份镜像表 + 漂移门禁**：插件装进 AddIns 后无法 import 包内模块，故 `hints._RULES` 与"改状态命令集"各存两份；CI 用 AST 静态比对两份是否逐字相等，并断言"工具名集合 == 派发键集合"（`tests/test_addon_sync.py:1-13`、`tests/test_addon_sync.py:60-88`、`tests/test_addon_sync.py:118-137`）。
- **API 用法的静态回归**：对"曾因 `except: pass` 而假成功"的三处（`delete_all`/`check_interference`/`draft_faces`）写出 AST 级断言——必须走 `TimelineObject.entity`、必须用 Design 级干涉 API、`createInput` 必须三参且角度用 `setSingleAngle`（`tests/test_addon_api_usage.py:1-9`、`tests/test_addon_api_usage.py:48-72`、`tests/test_addon_api_usage.py:92-114`、`tests/test_addon_api_usage.py:115-162`）。
- **单位走"带单位字符串"**：裸实数按 Fusion 内部单位（长度 cm、角度弧度）解释，所以要进 mm 时必须传带单位表达式；该判定被抽成不依赖 `adsk` 的纯函数以便单测（`addon/server/parameter_units.py:1-42`、`README.md:310`）。
- **热重载走同一条队列**：`reload_handler` 在主线程重新 import 兄弟模块并按依赖顺序换掉 handler 实例（`addon/server/event_bridge.py:143-150`、`addon/server/event_bridge.py:177-196`）。
- **mock 模式与真机同形**：`--mode mock` 由同一份工具表驱动，且对改状态命令自动补 `deltas`，于是"错误信封/deltas 形状"可以脱机验证（`src/fusion360_mcp/server.py:34-46`、`src/fusion360_mcp/mock.py:77-108`、`scripts/smoke_envelope.py:1-53`）。
- **★ 工具清单与粒度统计**：总数 **93**（`src/fusion360_mcp/tools.py` 中 8 空格缩进的 `"name"` 与 `"title"` 各 93 处；`README.md:126` 同数）。
  - 分组形态 1（源码注释分段，**28 段**合计 93 条，段名即分组）：`scene/query`3 · `sketch`4 · `features`6 · `new commands`6 · `code execution`1 · `additional geometry`7 · `assembly`3 · `export`4 · `import`1 · `parameters`4 · `sketch constraints`2 · `sketch dimensions`1 · `construction geometry`3 · `splines`1 · `sketch curve operations`3 · `advanced features`6 · `direct primitives`5 · `assembly (extended)`2 · `inspection/analysis`6 · `appearance/material`2 · `project geometry`1 · `timeline control`2 · `surface operations`5 · `sheet metal`4 · `CAM/manufacturing`7 · `health`1 · `design type safety`2 · `perception`1（分段注释散见 `src/fusion360_mcp/tools.py:11-2373`）。
  - 分组形态 2（协议层真下发的风险分级）：`readOnlyHint` 16 个、`destructiveHint` 2 个、`idempotentHint` 21 个，其余默认为可写非幂等（`src/fusion360_mcp/tools.py:2430-2479`）。
  - 粒度取向：单次调用只做**一个**操作（不改状态的多步被明令禁止），`create_box` 是"无历史"直建体、`create_box_parametric` 才是"草图+尺寸+拉伸"的历史特征——同一结果给出两种粒度（`README.md:311`、`AGENTS.md:217-219`、`src/fusion360_mcp/tools.py:1444-1523`）。

## 4. 运行条件与依赖

- 语言：Python `>=3.10`（`pyproject.toml:6`），运行时依赖只有 `anyio>=4.5`、`click>=8.1`、`mcp>=1.0,<2`；开发组 `pytest`、`ruff`（`pyproject.toml:10-14`、`pyproject.toml:44-48`）。
- 宿主侧不是 Python 包装器：插件要用 Fusion 自带的 `adsk.core/fusion/cam`（`addon/server/command_handler.py:19-21`），因此**必须有 Fusion 360 本体**；安装方式是整目录拷进 Fusion 的 AddIns，再从 Shift+S → Add-Ins 里 Run（`README.md:39-48`）。
- 本机（Windows / Python 3.14.7 / RTX 4080S 16GB）：`python --version` = 3.14.7、`uv 0.12.5` 均在（本机实测）；但检查 `%LOCALAPPDATA%\Autodesk\webdeploy`、`%APPDATA%\Autodesk\Autodesk Fusion 360`、`C:\Program Files\Autodesk` 三处**均不存在**（本机实测 `Test-Path`），即**没装 Fusion 360** ⇒ 本机只能跑 mock 模式与服务端单测，通道真机行为无法复现。GPU 无要求（依赖表无加速器包，`pyproject.toml:10-14`）。
- **本机测试可跑（实测）**：用 `uv run --no-project --with "mcp>=1.0,<2" --with anyio --with click --with pytest python -m pytest tests -q -p no:cacheprovider`（`PYTHONPATH=src`、`PYTHONDONTWRITEBYTECODE=1`，uv 解析到的解释器是 CPython **3.12.14**）——`PYTHONUTF8=1` 时 **367 passed / 15.69 s**，默认（GBK）环境 **17 failed / 350 passed**；宿主 Fusion 未装，所以 `adsk` 相关只被 AST 检查覆盖，真机调用没跑（`.github/workflows/ci.yml:15-18` 的 CI 同样不启动 Fusion）。
- 跨机/容器：套接字可绑 `0.0.0.0` 走局域网，但**无任何认证**，作者自己写了"只在可信局域网"（`README.md:114`、`addon/Fusion360MCP.py:8-11`）；容器场景要过一段 `netsh portproxy` + 防火墙放行，因为插件绑在 `127.0.0.1`（`devcontainer/README.md:5-24`）。

## 5. 失败模式与已知坑

- **30 s 主线程预算会吃掉长操作**：CAM 刀路、复杂圆角超时后客户端只能拿到 `TIMEOUT`，作者给的解法是"拆小步"而不是调大超时（`addon/server/event_bridge.py:82`、`src/fusion360_mcp/connection.py:172-178`、`addon/server/hints.py:109-116`）。
- **批量是明令禁止的**：一次工具调用一个操作；`execute_code` 里也不要用循环——Fusion API 非线程安全且复杂脚本会把插件搞崩（`README.md:311`、`AGENTS.md:217-219`）。
- **`execute_code` 没有沙箱**：命名空间里直接给了 `adsk`/`app`/`ui`/`design`/`component`，无过滤、无白名单，等于把宿主全权限交给模型（`addon/server/command_handler.py:3532-3564`）。
- **静默失败曾是主 bug 族**：三个工具的失败被 `except: pass` 吞掉，工具报成功却什么都没做；修复后补的是 AST 门禁而不是返回值断言（`tests/test_addon_api_usage.py:6-8`、`tests/test_addon_api_usage.py:66-71`）。
- **审核靠人眼的文档有漂移**：README 与 AGENTS.md 都自称 93 个工具，但 AGENTS.md 的表只列了 85 条（`AGENTS.md:5`、`AGENTS.md:21-164`）；README 用 17 个小标题覆盖 93 行（`README.md:130-289`）。代码侧由 `test_tools_match_addon_dispatch` 兜住，文档侧没有门禁（`tests/test_addon_sync.py:118-137`）。
- **中文 Windows 上 17/367 条测试必挂（我方可直接复现的坑）**：这些测试读 UTF-8 源码时调用 `Path.read_text()` 却没传 `encoding=`，于是用了 locale 默认的 GBK，在 `pathlib.py:1028` 抛 `UnicodeDecodeError: 'gbk' codec can't decode byte 0x94 in position 9464`；分布是 `test_addon_api_usage` 9 条、`test_hole_geometry` 4 条、`test_addon_sync` 2 条、`test_parameter_units` 2 条（本机实测；`PYTHONUTF8=1` 后 367 全绿）。与我方已知事实 58 同一族问题——**门禁/测试"写了"但被环境静默打死**。二次独立复现（本次会话另用临时副本 + CPython 3.12.14 + `uv run --python 3.12 --frozen pytest -q`）得到同一分布：**17 failed / 350 passed / 17.34 s**；字节级根因已定位——该文件是 UTF-8，非 ASCII 字符集只有 U+2014（em dash）、U+2192（→）、U+2500（─）三种，GBK 在第 9464 字节处撞上 U+2014 的 UTF-8 三字节编码 E2 80 94 的末字节 0x94，全文 141067 字节（实测 `python -c` 读字节与码点统计）。
- **"测试数"是自述且已过期**：README 写 363 个测试（`README.md:304`），本机实跑收集到 **367** 个用例（`tests/*.py` 里只有 245 个 `def test_`，差额来自参数化）——文档数字落后于代码。
- **CI 不覆盖宿主**：CI 只有 ubuntu-latest + Python 3.12，跑 `ruff` 与 `pytest`，从不启动 Fusion（`.github/workflows/ci.yml:13-30`）⇒ 插件里所有 `adsk` 调用只能靠 AST 静态断言与 mock 兜（`tests/test_addon_sync.py:32-57`）。
- **`render_view` 是重负载**：单次返回约 200 KB–2 MB base64，作者要求只在逻辑检查点用（`AGENTS.md:204`）；代码侧只做了尺寸夹取 16–4096（`addon/server/command_handler.py:3716-3717`）。
- **设计类型会被悄悄改掉**：`execute_code` 前后比对 `designType`，变了就附加 `design_type_warning` 提示用 `set_design_type` 救回（`addon/server/command_handler.py:3529-3530`、`addon/server/command_handler.py:3569-3592`）。
- 遗留问题密度：open issues 8 个（来源：`gh api repos/faust-machines/fusion360-mcp-server`，只取计数，未逐条读）。

## 6. 对我方目标的可用处（机制层面）

- **与我方 STA 约束同构的那一段**：段 D+E 就是"任何 CAD API 调用必须回到主线程"的完整实现——工作队列 + 跨线程完成信号 + 主线程事件回调 + 备份心跳（`addon/server/event_bridge.py:52-171`）。我方 SolidWorks COM 的线程亲和性与之同族，这条链把"谁在等、等到什么时候、放弃后怎么办"三件事都写了。
- **超时后的语义**是这条链最值得注意的部分：放弃 = 打 `cancelled`，被跳过的命令不补执行（`addon/server/event_bridge.py:101-111`）；写命令不重试（`src/fusion360_mcp/connection.py:136-141`）。这正对"COM 调用超时后线程不可强杀、重试可能做两遍"的处境。
- **两侧超时要错开**：客户端 45 s > 宿主 30 s，才拿得到结构化超时而不是裸连接错误（`src/fusion360_mcp/connection.py:36-38`）。
- **免费差分**：改状态命令自动回带质量/包围盒/体数（`addon/server/command_handler.py:3620-3687`）——对"普通模型是否真把模型改了"是一道不需要视觉的判据。
- **错误分类表**（12 条正则 → 标签 + 修复提示，`addon/server/hints.py:16-128`）与我方"失败分类即改法"同路，且标签是稳定枚举，模型可分支。
- **两份镜像 + AST 漂移门禁**（`tests/test_addon_sync.py:60-88`、`tests/test_addon_sync.py:118-137`）可搬到"工具清单 ↔ 派发表"这类必然重复的地方；它证明的是"工具名集合相等"，不是"行为相同"。
- **静态 API 用法断言**（`tests/test_addon_api_usage.py`）是"把验证责任转移到静态比对"的现成样板：连"`createInput` 必须三参、角度必须 `setSingleAngle`"这种签名级事实都能锁住（`tests/test_addon_api_usage.py:125-146`）。
- **单位陷阱显式化**：裸实数 = 内部单位，带单位字符串才换单位（`addon/server/parameter_units.py:1-42`）——与我方 mm/cm 口径混乱属同一类问题。
- **风险分级标注**（read-only / destructive / idempotent）可直接映射到我方工具清单，供宿主决定自动放行（`src/fusion360_mcp/tools.py:2426-2479`）。

## 7. 许可与红线

- MIT：可读、可抄、可改、可商用；义务仅"保留版权声明与许可声明"。本仓版权行为「Copyright (c) 2025 Faust Network, Inc.」（`LICENSE:1-3`）。
- 架构来源被作者点名：套接字桥架构出自 BlenderMCP；另列 6 个 Fusion MCP 项目为思想来源（`README.md:317-327`）——这些上游各有自己的许可，不能只看本仓 LICENSE。
- 红线：本次对克隆**只读**——未改任何文件（跑完 `git status --porcelain` 为空）、未安装宿主 Fusion、未启动插件；唯一执行过的是仓库自带单测，且用 `uv run --no-project` 的临时环境 + `PYTHONDONTWRITEBYTECODE=1` + `-p no:cacheprovider`，没在克隆里留 `.venv`/`__pycache__`/`.pytest_cache`。`execute_code` 的全权限执行路径属设计事实，我方不引入这条口子时不要把它的错误处理假设当既有保障。

## 8. 证据清单

```
D:\ai3d-survey\repos\faust-machines__fusion360-mcp-server\README.md:11-20,39-48,52,114,126,128,130-289,291-298,304,310-315,317-327
...\AGENTS.md:5,10-17,21-164,166-204,215-224
...\LICENSE:1-3 · pyproject.toml:6,7-8,10-14,21-22,44-48 · .github\workflows\ci.yml:13-30
...\src\fusion360_mcp\server.py:34-46,74-93,96-155,180-221,225-246,325-340,344-400,469-475
...\src\fusion360_mcp\connection.py:36-41,67-80,103-121,127-199,201-219,226-261
...\src\fusion360_mcp\tools.py:10,11-2423,2426-2479,2482-2501
...\src\fusion360_mcp\hints.py · mock.py:19,77-108 · __init__.py · __main__.py
...\addon\Fusion360MCP.py:8-11,29-81 · addon\server\__init__.py:1-30
...\addon\server\socket_server.py:1-10,22-23,26-37,43-52,82-97,111-162,168-234
...\addon\server\event_bridge.py:21-22,25-49,52-76,82-124,130-157,163-171,177-196,202-222
...\addon\server\command_handler.py:19-21,31-36,42,61-113,115-275,281-333,3528-3592,3620-3687,3693-3778
...\addon\server\hints.py:16-128,131-144 · parameter_units.py:1-42 · hole_geometry.py
...\tests\test_addon_sync.py:1-13,32-57,60-88,118-137 · tests\test_addon_api_usage.py:1-9,48-72,92-114,115-162
...\scripts\smoke_envelope.py:1-53 · devcontainer\README.md:5-24
```
- 计数实测（在克隆内跑 `pwsh`）：`tools.py` 中 `"name":`（8 空格缩进）93 处、`"title":` 93 处、分段注释 28 段；`_READ_ONLY` 16 / `_DESTRUCTIVE` 2 / `_IDEMPOTENT` 21；`tests/*.py` 中 `def test_` 245 处；`command_handler.py` 共 3819 行；`tools.py` 共 2501 行。
- 元数据来源：`gh api repos/faust-machines/fusion360-mcp-server`（取数 2026-10-24，返回 stars 131 / pushed 2026-10-06T04:52:43Z / language Python / license MIT / open_issues 8 / forks 28）。
- 实测记录（本机 2026-10-24，克隆内，未污染工作树）：`PYTHONUTF8=1 PYTHONPATH=src uv run --no-project --with "mcp>=1.0,<2" --with anyio --with click --with pytest python -m pytest tests -q -p no:cacheprovider` → `367 passed in 15.69s`；去掉 `PYTHONUTF8=1` 后 → `17 failed, 350 passed in 15.59s`，17 条 `UnicodeDecodeError` 全部来自 `pathlib.py:1028`（`read_text()` 未指定 encoding）。解释器：CPython 3.12.14（uv 管理）。

- 二次独立复现（本次会话，另一条路径：整树复制到临时目录后 `uv run --python 3.12 --frozen pytest -q`）→ 默认 GBK 环境 `17 failed, 350 passed in 17.34s`（与上一条的 367 总数一致，仅耗时不同）。同批另跑 `python -c`（读 `addon/server/command_handler.py` 字节与码点）得：非 ASCII 字符集只有 U+2014/U+2192/U+2500 三种、文件 141067 字节、GBK 失败点在第 9464 字节。

## 9. 未确认事项

- **通道没跑过真机**：本机没有 Fusion 360（`%LOCALAPPDATA%\Autodesk\webdeploy`、`%APPDATA%\Autodesk\Autodesk Fusion 360`、`C:\Program Files\Autodesk` 三处 `Test-Path` 全 False），插件依赖的 `adsk.*` 无法加载 ⇒ §2 的段 A–F、§3 的取消/超时语义、§5 的 30 s 预算行为，全部是**读码**结论；本卡的 `实测` 只覆盖仓库自带单测（367 passed，含 AST 级门禁与 mock 模式），不覆盖与 Fusion 的任何交互。
- README 的 363 个测试与实测 367 不一致：差额来自参数化展开，具体是哪些用例被参数化、README 数字对应哪个提交 **未核**（`README.md:304`）。
- 17 条 GBK 失败我**没有改代码去修**（只读纪律），故"加 `encoding='utf-8'` 后是否全绿"这一点只能由 `PYTHONUTF8=1` 间接证明（它等价于改用 UTF-8 默认编码），未逐文件打补丁验证。（来源：本卡 §5 已知坑）
- 8 个 open issue 只取了计数，未读内容，故 §5 的"已知坑"可能不全（来源：`gh api repos/faust-machines/fusion360-mcp-server`）。
- Fusion 版本敏感性未核：README 说在 Fusion 2705.1.15 (macOS arm64) 上测过，并给 4 个工具打了 **(2026+)** 标记——`auto_constrain`/`create_ucs`/`compare_meshes`/`set_color`（`README.md:156,226,244,250`，口径见 `README.md:128`、`README.md:315`）；这些 API 在旧构建上的实际失败形态未读代码验证。
- 段 D 的"备份定时器必要性"只有作者注释（"`fireCustomEvent` from a daemon thread is unreliable"，`addon/server/event_bridge.py:5-6`），没有对应的回归测试或复现记录。
- `devcontainer/fusion-mcp-bridge.ps1`（6.8 KB，要 Administrator 权限改 `netsh portproxy` 与防火墙）未执行、未逐行读；该路径与本机环境无关。
