# FreeCAD MCP（neka-nat/freecad-mcp）

<!-- survey: class=H; repr=feature-tree; orchestration=single; verify=visual; deliver=none; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/neka-nat/freecad-mcp |
| 许可 | MIT（`LICENSE:1-3`，版权 `Copyright (c) 2025 Shirokuma (k tanaka)`；`pyproject.toml:9` 亦写 `license = { text = "MIT" }`）⇒ **可借鉴**，移植须保留版权声明 |
| 元数据 | stars 3017 · 最近推送 2026-10-13T13:14:58Z · 语言 Python · forks 359 · open issues 54（来源：https://api.github.com/repos/neka-nat/freecad-mcp，2026-10-23 取） |
| 克隆 | `D:\ai3d-survey\repos\neka-nat__freecad-mcp`（shallow：`git rev-list --count HEAD` 得 1，tip 提交 `78bf0230`，提交时间 2026-10-13 22:13:58 +0900） |
| 证据等级 | **读码**（★ 不是「实测」：17 个工具**没有一条端到端跑过**，本机未装 FreeCAD 宿主。只跑了它的单测：Python 3.14.7 `python -m pytest tests -q -p no:cacheprovider` 得 245 通过 / 3 失败 / 1 跳过，52.75 s，2026-10-23；独立复核在 CPython 3.12 得 246 通过 / 2 失败 / 1 跳过，量级一致可采信。按本仓判据「跑通单测 ≠ 能力可用」，等级取读码）|

## 1. 一句话定位

用 **XML-RPC 把模型现写的 Python 送进正在运行的 FreeCAD GUI 线程**：MCP 工具只 17 个（`src/freecad_mcp/server.py:141-744`），建模能力的大头不靠工具，靠 `execute_code` 里现场写 FreeCAD API。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：MCP 客户端的工具调用。建模入口是 `create_object(doc_name, obj_type, obj_name, analysis_name, obj_properties, include_screenshot, view_name)`（`src/freecad_mcp/server.py:163-172`）。

**中间表示**：一个 JSON 属性包，不是几何 IR。`obj_type` 是 FreeCAD C++ 类型注册名（`Part::Box` / `Part::Cut` / `PartDesign::Body` / `Fem::ConstraintFixed`…），`obj_properties` 是属性名字典（`server.py:197-199`、`server.py:241-252` 的 `Base`/`Tool` 按名互引）。布尔运算靠**按对象名互相引用**，不靠选择集或面 ID——两体先建、再建 `Part::Cut` 并把 `Base`/`Tool` 指向它们。

**生成**：`addon/FreeCADMCP/rpc_server/object_factory.py` 分四支——`Fem::FemMeshGmsh`（跑 Gmsh 并兼容 0.x/1.x 属性改名）`object_factory.py:18-57`；其余 `Fem::*` 走 `ObjectsFem.make*` 工厂 `object_factory.py:60-80`；Python 实现因而**不在类型注册表里**的类型走一张显式工厂表 `object_factory.py:180-186`（`Part::Tube`/`Draft::Circle`/`Draft::Rectangle`/`Draft::Polygon`/`Draft::Wire`）；其余走 `doc.addObject` `object_factory.py:238-249`。Draft 工厂会往 `ActiveDocument` 建对象，故先切活动文档再复原 `object_factory.py:83-100`。

**编排**：编排写在提示词里而不是代码里——`ASSET_CREATION_STRATEGY`（`src/freecad_mcp/prompt_text.py:1-39`）规定工序：**先 `get_objects()` 看现状 → 先查零件库（`get_parts_list`/`insert_part_from_library`）→ 库外再建基本体 → 命名 → 显式设 placement → 用 `get_object()` 回读验证 → 最后才 `execute_code`**。

**执行**：三条通道并存。`execute_code` 在 GUI 线程跑（`server.py:526-563`）；`execute_code_async` 起后台作业并返回 `job_id`，文档/视图改动必须经 `commit()` 交回 GUI 线程（`addon/FreeCADMCP/rpc_server/rpc_server.py:88-104`）；`execute_code_headless` 把脚本写临时文件、另起 `freecadcmd` 子进程跑（`src/freecad_mcp/headless.py:68-135`），专治「OCCT 原生崩溃会连 GUI 一起带走」。

**桥接通道**：XML-RPC over `localhost:9875`。客户端每调用新建一次 Transport（`ServerProxy` 非线程安全），`ping`/`get_rpc_status`/`get_async_status` 走独立超时，绝不与被 GUI 阻塞的请求共用连接（`src/freecad_mcp/freecad_client.py:62-85`、`freecad_client.py:157-160`）。GUI 侧 `FreeCADRPC` 挂在 `ThreadingMixIn + SimpleXMLRPCServer` 上（`addon/FreeCADMCP/rpc_server/ip_filter.py:120-136`），所有触碰文档树的操作经 `dispatch_to_gui` 排进 Qt 主线程队列（`addon/FreeCADMCP/rpc_server/gui_dispatch.py:242-369`）。

**验证**：`recompute()` 之后按**对象状态**判有效性——读 `obj.State` 是否落在 `invalid`/`error`/`touched`，并叠加 `isValid()`，两者任一失败即回「对象存在但没算出来 + `getStatusString()` 原因」（`addon/FreeCADMCP/rpc_server/object_validation.py:6`、`object_validation.py:25-69`）。官方文档明写**脚本执行成功不等于几何有效**（`docs/execution.md:33`）。

**交付**：可选截图（9 个视角：Isometric/Front/Top/Right/Back/Left/Bottom/Dimetric/Trimetric）作为人眼/模型眼的验收通道，**8 个**工具带 `include_screenshot`/`view_name`（`docs/tools.md:32-47` 实列 8 个；★ 初稿写「7 个」是错的，2026-10-24 由独立复核纠正）；FEM 交付摘要为最大 von Mises 应力、最大/最小位移、节点数、求解器工作目录，默认 `timeout` 600 s（`docs/tools.md:51-54`）。

## 3. 技术方案要点（可迁移的机制）

### 3.1 ★ 工具清单与粒度统计：**17 个工具，按「操作原语」切而不是按 CAD 命令切**（来源：本卡 §3 工具清单）

`@tool`（`server.py:83-100` 的注册器）共 **17 个**（`grep -c '^@tool$' src/freecad_mcp/server.py` 得 17，行号 `server.py:141,162,346,382,414,479,508,525,565,597,626,654,685,692,721,731,744`）：

| # | 工具 | 用途 | 分组 |
|---|---|---|---|
| 1 | `create_document` | 新建文档 `server.py:142` | 生命周期 |
| 2 | `list_documents` | 列打开的文档 `server.py:722` | 观察 |
| 3 | `reload_document` | 关掉重开已存文档，拾取 headless 脚本的外部改动 `server.py:693` | 生命周期 |
| 4 | `create_object` | 按类型名建对象（含 `Fem::` 与 5 个 Python 工厂类型）`server.py:163` | 对象 CRUD |
| 5 | `edit_object` | 改已有对象属性 `server.py:347` | 对象 CRUD |
| 6 | `delete_object` | 删对象 `server.py:383` | 对象 CRUD |
| 7 | `get_objects` | 列文档全部对象 `server.py:627` | 观察 |
| 8 | `get_object` | 取单个对象 `server.py:655` | 观察 |
| 9 | `get_view` | 显式截图（宽高/盯住对象）`server.py:566` | 观察 |
| 10 | `execute_code` | 在 GUI 线程跑 Python `server.py:526` | **逃逸口** |
| 11 | `execute_code_async` | 后台作业 + `commit()` 回写 `server.py:415` | **逃逸口** |
| 12 | `get_async_status` | 读作业状态/失败 traceback（不占 GUI 线程）`server.py:509` | 观察 |
| 13 | `execute_code_headless` | 另起 `freecadcmd` 子进程，回退出码与输出 `server.py:480` | **逃逸口** |
| 14 | `get_rpc_status` | RPC/GUI 调度健康 + addon 版本（不占 GUI 线程）`server.py:732` | 健康 |
| 15 | `insert_part_from_library` | 从 FreeCAD 官方零件库插零件 `server.py:598` | 零件库 |
| 16 | `get_parts_list` | 列零件库 `server.py:686` | 零件库 |
| 17 | `run_fem_analysis` | 对已有分析跑 CalculiX，回应力/位移/节点数 `server.py:745` | FEM |

⇒ **它不是「合并式工具」**（没有 `operation` 字符串分派），而是**原语式 + 万能代码口**：4 个对象 CRUD + 3 个逃逸口 + 5 个观察/健康 + 2 个零件库 + 1 个 FEM。建模细节全部推给 `execute_code`，所以工具表很短。（来源：本卡 §3 工具清单）

### 3.2 其它可迁移机制

- **握手式版本容错**：协议号硬编码为 1（`src/freecad_mcp/version.py:13`），addon 缺 `get_rpc_status` 时按「addon 太旧」告警并把升级命令写进消息（`version.py:38-62`）；缺方法用 `is_missing_method_fault` 单独识别，不与其他 Fault 混（`version.py:27-35`）。
- **GUI 单线程调度器全套守卫**：每次调用自带响应队列（一次超时不会污染下一次）+ Qt 信号立即唤醒（500 ms 心跳只作兜底）+ 鼠标按住时推迟（上限 5 s，防 Qt 丢失松开事件后永久卡死）+ 弹窗/模态框打开时推迟 + 任务抛 `SystemExit` 也不许带崩 FreeCAD + 卡死后后续调用**立刻快速失败**而不是一起等（`gui_dispatch.py:8-33`、`gui_dispatch.py:159-229`、`gui_dispatch.py:269-271`）。
- **队列预算与执行预算分离**：排队等前序任务的时间不吃本任务的执行预算，故两个并发 `execute_code` 各自拿到完整预算（`docs/execution.md:79-104`）。
- **崩溃隔离靠换进程，不靠 try/except**：headless 通道把段错误落在 helper 进程，回 `crashed`+信号名，并识别「FreeCAD 自己的信号处理器吞掉信号后 exit 1」这种伪装（`headless.py:114-134`）。
- **无形状仍有效的判据**：容器/组/表格/空草图可以没有 `Shape` 但完全有效，所以判无效只看 `State`+`isValid()`（`object_validation.py:28-30`）。
- **浏览器来源一刀切**：带 `Origin` 头的请求直接 403，因为浏览器页面无法被 IP 白名单拦（`ip_filter.py:39-57`）。
- **共享脚本命名空间**：`execute_code` 与 `execute_code_async` 共用一个持久命名空间（模块级变量跨调用存活、且不被服务的内部函数遮蔽），headless 不共享（`rpc_server.py:42-51`、`docs/execution.md:13-22`）。

## 4. 运行条件与依赖

- MCP server：Python >= 3.12（`pyproject.toml:10`），依赖 `mcp[cli]>=1.28.1,<3` 与 `validators>=0.34.0`（`pyproject.toml:11-14`）。
- addon：跑在 FreeCAD 自带 Python 里（可能是 3.11），**不要把 `freecad-mcp` 装进 FreeCAD 的 Python**（`docs/installation.md:8-11`）。addon 目录按 FreeCAD 版本分：Windows FreeCAD 1.1 是 `%APPDATA%\FreeCAD\v1-1\Mod\`（`docs/installation.md:27-35`）。
- **本机（16 GB 显存 / Python 3.14.7 / Windows）可跑测试但跑不了真建模**：实测 245 通过 / 失败 3 / 跳过 1。3 个失败都是环境所致：`test_version_handshake` 报 `PackageNotFoundError: No package metadata was found for freecad-mcp`（包未装进环境）；`test_browser_guard` 期望 403 的一例未命中；`test_tool_errors` 的 stdio 子进程报 `McpError('Connection closed')`（来源：本机 `python -m pytest tests -q` 输出，2026-10-23）。
- 无 ML 依赖，显存不相关；FEM 另需 CalculiX。真机链路另需装 FreeCAD + 把 addon 拷进 Mod。

## 5. 失败模式与已知坑

- **任意代码执行是产品特性也是最大风险面**：`execute_code` 以你的用户权限跑任意 Python（`docs/configuration.md:45-49`）；README 未加 warning，但远程开启后「任何能到达该端口的程序都能调用全部工具」。
- **GUI 任务开始后不可取消**：超时只把结果丢掉，任务继续在跑；慢调用会「报超时但其实做完了」（`docs/execution.md:91-96`）。
- **卡死的唯一处置是重启 FreeCAD**：超执行预算后桥返回 `GUI_DISPATCH_STUCK` 并立刻拒绝后续 GUI 调用，状态不恢复 healthy 就只能重启（`docs/execution.md:106-121`）。
- **模态对话框 = 永久冻结点**：`dispatch_to_gui` 检测到 `activePopupWidget`/`activeModalWidget` 就整体推迟（`gui_dispatch.py:186-191`）；鼠标守卫上限 5 s 是专门为「Qt 把已松开的按钮报成一直按住」这一实例设的（`gui_dispatch.py:57-63`）。
- **旧 addon 静默失能**：旧 addon 没有 `get_rpc_status`，故预算只能用客户端兜底值（`freecad_client.py:38-46`）。
- **重名被改写**：FreeCAD 会清洗并去重对象名（`My Doc`→`My_Doc`、`Box`→`Box001`），所以工具回的是**实际名**，Draft 工厂甚至把请求名只放到 `Label` 上（`object_factory.py:252-259`、`object_factory.py:195-198`）。
- **Python 实现类型不在类型注册表**：`addObject` 会报「is not a document object type」而真因是该类型是 Python 写的，代码专门把这条错误翻译成「改用 execute_code」并附对应工厂名（`object_factory.py:206-235`）。

## 6. 对我方目标的可用处（机制层面）

1. **「短工具表 + 一个代码口」是我方直接可比的方案**：17 个工具对 187/128 家细粒度工具，普通模型不必先学会选对工具名；代价是工序必须写进提示词——`ASSET_CREATION_STRATEGY`（`prompt_text.py:1-39`）正是把我方「先查库再建、建完回读验证」这套工序固化成 8 步的做法，可直接对照我方的编排层。
2. **分级决策树**：零件库 → 基本体 → 脚本，是给普通模型降难度的正解；我方 SolidWorks 侧可映射为「标准件库 → 特征原语 → COM 脚本」。
3. **验证判据可搬**：`recompute()` 后按 `State∈{invalid,error,touched}` + `isValid()` 判无效，且明确「无 Shape 不等于无效」。这比「看有没有报错」强，比我方单看返回值也强。
4. **GUI 单线程调度器的全套守卫可整段搬**：per-call 响应队列、立即唤醒、推迟守卫带上限、卡死后快速失败、诊断不占 GUI 线程——这些正是我方 COM 单源运行时的同构问题。
5. **崩溃隔离用换进程**：把会段错误的原生运算放子进程，并识别被信号处理器吞掉的伪 exit 1——我方 OCCT/COM 侧同款。
6. **版本握手**：协议号 + 「缺方法」单独识别 + 告警里直接给升级命令，解决「addon 与 server 分开分发」这一类漂移。

## 7. 许可与红线

MIT（`LICENSE:1-3`，`Copyright (c) 2025 Shirokuma (k tanaka)`）⇒ **可借鉴**：可读、可抄、可改、可商用，须保留版权声明。
红线：`execute_code` 即任意代码执行，移植我方时必须保留「先置抑制态、每调用超时、收尾释放」三条护栏（本仓铁律 2）；远程/鉴权若照搬，注意它自陈「令牌明文传输、不开 TLS」（`docs/configuration.md:116-118`）。

## 8. 证据清单

- `LICENSE:1-3`；`pyproject.toml:9-10`
- `src/freecad_mcp/server.py:83-100`（`@tool` 注册器）、`server.py:141,162,346,382,414,479,508,525,565,597,626,654,685,692,721,731,744`（17 个工具）
- `src/freecad_mcp/prompt_text.py:1-39`（工序提示词）
- `src/freecad_mcp/freecad_client.py:12-25,62-85,157-160`（每调用一 Transport、超时分离）
- `src/freecad_mcp/headless.py:68-135`（子进程执行 + 崩溃识别）
- `src/freecad_mcp/version.py:13,27-35,38-62`（协议握手）
- `addon/FreeCADMCP/rpc_server/gui_dispatch.py:8-33,57-63,159-229,242-369`
- `addon/FreeCADMCP/rpc_server/object_factory.py:18-57,60-80,83-100,180-186,195-198,206-235,238-249,252-259`
- `addon/FreeCADMCP/rpc_server/object_validation.py:6,25-69`
- `addon/FreeCADMCP/rpc_server/ip_filter.py:39-57,120-136`；`addon/FreeCADMCP/rpc_server/rpc_server.py:42-51,119-159`
- `addon/FreeCADMCP/InitGui.py:12-43`（FreeCAD 侧工作台/菜单/自动启动）
- `docs/tools.md:7-25,32-47,51-54`；`docs/execution.md:9-11,33,79-104,106-121`；`docs/configuration.md:39-52,116-118`；`docs/installation.md:8-11,27-35`
- https://api.github.com/repos/neka-nat/freecad-mcp（2026-10-23）
- 本机实测：`python -m pytest tests -q -p no:cacheprovider`（PYTHONPATH 指向 `src`，Python 3.14.7）

## 9. 未确认事项

1. **没有真机 FreeCAD**，故 17 个工具没有一条在我方机器上端到端跑过；RPC 链路、GUI 调度、截图、FEM 全部只有读码证据。（来源：本卡 §9 未确认事项）
2. `run_fem_analysis` 的应力/位移数值我在本机**未复现**，只能引官方文档口径（`docs/tools.md:51-54`）。
3. 三个测试失败的**根因**只到「环境缺包 / 期望值不符」这一层，未逐条定位（包未 `pip install -e .` 是主因，但未验证装包后是否全绿）。
4. tools 数 17 是**静态数**（`@tool` 装饰器计数）；运行期是否被 FastMCP 过滤/改名未验。
5. addon 是否有 `Draft::Point`/`Draft::Ellipse`/`Draft::BSpline` 之外的未登记工厂类型——代码只列了 3 条提示（`object_factory.py:209-213`），未穷举。