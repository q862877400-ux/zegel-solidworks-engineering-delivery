# Slacker-LLC/solidworks-mcp

<!-- survey: class=H; repr=feature-tree; orchestration=single; verify=numeric; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `Slacker-LLC/solidworks-mcp` · https://github.com/Slacker-LLC/solidworks-mcp（★`pyproject.toml` 的 `Homepage` 仍写旧账号 `limuzi013/solidworks-mcp`；`gh api` 两个 slug 返回同 stars/同 `pushed_at`/同创建时间，判定为重命名/重定向，以克隆目录 `Slacker-LLC` 为准）|
| 许可 | **Apache-2.0**（`LICENSE` 为 Apache-2.0 标准全文、正文无版权行；版权行在 `NOTICE:2` = `Copyright 2026 JIALE LIU`；`pyproject.toml:9-10` `license = "Apache-2.0"` + `license-files = ["LICENSE", "NOTICE"]`）⇒ **可借鉴，但必须保留 NOTICE 并声明改动过的文件** |
| 元数据 | stars 22 · 最近推送 2026-10-13T21:39:29Z · 语言 Python · 仓库 384 KB（来源：`gh api repos/Slacker-LLC/solidworks-mcp`，2026-10-24 取）|
| 克隆 | `C:\swprojects\Slacker-LLC`（HEAD `6019ce0`，2026-08-16 19:46:55 +0800；远端 `pushed_at` 已到 2026-10-13 ⇒ **克隆落后约两个月**，计数以快照为准）|
| 证据等级 | 读码（未跑：`tests/live_p0_regression.py` 要真机，离线 24 例若跑会在克隆内留 `__pycache__`，违反「不改 C:\swprojects」纪律）|

## 1. 一句话定位

**四家里工程纪律最好、广度最窄的一家**：92 个工具、7 个模块（`sw_core` 统管单位/选择/特征树，其余按域分文件），**mm/deg 边界契约 + 单进程 `asyncio.Lock` 串行化 + 每特征 rebuild 后读 `GetWhatsWrong`**；README 用 3000 字记下真正花时间的 COM 坑，并声称全部工具在 SW 2026 SP3.2 简体中文上跑过。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：MCP stdio。工具声明是「装饰器 + 显式 JSON Schema」：`@tool("name", "描述", {properties...}, required=[...])` 把 `Tool` 推进 `TOOLS`、把处理函数推进 `HANDLERS`（`solidworks_mcp/sw_core.py:182-206`）。⇒ 加工具不用改 dispatch 表（`server.py:76-95` 只是查表）。

**中间表示**：**单位契约**是它的核心抽象——MCP 边界一律毫米/度（参数名 `*_mm`/`*_deg`），进入 `sw_core` 后**一次性**转成 COM 的米/弧度（`server.py:17-21` 的 docstring 明写「conversion happens once, in sw_core」）。几何状态仍靠特征树 + 选择集，无 IR。

**生成**：不生成代码/宏。**不启动 SolidWorks、不注册 add-in、不跑任意代码**（`server.py:15-18` 明列为设计边界）。

**编排**：无。一次调用一个处理函数，`server.py:82` 进 `COM_LOCK` 后同步执行。

**执行**：进程内 COM（pywin32 迟到绑定）。核心是三个防御函数：`flag_methods(obj, *names)` 对每个「带参数调用」的成员先 `_FlagAsMethod`（逐个 flag，不靠 `_FlagAsMethod(*names)` 的批量语义，`sw_core.py:303-325`）；`value(obj, member)` 取出后若是可调用对象就调用一次再返回（`sw_core.py:259-300`）；选择走 `select_by_id`/`select_at_point`/`select_object` 三条（`sw_core.py:639-691`）。

**验证**：**数值/结构双判据**。每个特征工具建完 `rebuild` 并读 `ModelDocExtension.GetWhatsWrong`，失败就把问题清单回给调用方（`sw_feature.py` 全体；`rebuild_document` 亦然 `sw_file.py` 尾部）；`check_errors` 直接暴露该接口。`sketch_trim` 用「草图段数是否变化」判成功（因为 `SketchTrim` 成功返 `False`），`add_relation` 用**关系数**判成功，失败时回报「这个选择本来能接受哪些关系」。

**交付**：`export_document` → `SaveAs`，白名单扩展名 `{.step,.stp,.iges,.igs,.stl,.x_t,.x_b,.png,.jpg,.bmp,.3mf}`（`sw_core.py:142`）。

## 3. 技术方案要点（可迁移的机制）

### 3.1 工具清单与粒度：**92 个（实测，与台账一致），按域分 7 个模块，无 `operation` 分派**（来源：本卡 §8 证据清单）

★ 起点数字「92 个工具 / 2 个测试 1 live」来自本仓 `AGENTS.md` §四 台账；**实测一致**：`@tool(` 装饰器 92 个，逐模块 `sw_sketch.py` 28、`sw_drawing.py` 18、`sw_feature.py` 17、`sw_inspect.py` 11、`sw_file.py` 10、`sw_assembly.py` 5、`sw_refgeom.py` 3 = 92（`solidworks_mcp/sw_*.py`）。另有 2 个演示工具（`demo_create_basketball`/`demo_upgrade_basketball`）**只在 `SW_MCP_DEMO_TOOLS` 为真时注册**（`sw_demo.py:300-330`），默认不计入。

**粒度**：草图最细（28 个：`draw_line`/`draw_3point_arc`/`sketch_trim`/`sketch_fillet`/`add_relation`/`get_sketch_status` 各一个），特征层一动词一工具（`boss_extrude`/`cut_extrude`/`revolve`/`fillet`/`chamfer`/`shell`/`draft`/`rib`/`simple_hole`/`sweep`/`loft` + 4 个阵列/镜像 + 删除/改名/压制）。**没有合并式 `operation` 参数**——与四家其余三家一致，四家都没走「一个万能工具 + operation 枚举」的路。（来源：本卡 §8 证据清单）

### 3.2 桥接方式与单实例互斥

**桥接**：进程内 COM（pywin32），**附着到用户已开的会话**，不拉起 SolidWorks、不装 add-in、不做文件 IPC（`server.py:15-18`）。

**单实例互斥：有，且是进程内唯一正确的那一档**——`COM_LOCK = asyncio.Lock()`，注释写明「一个 SOLIDWORKS 会话、一个 COM apartment：串行化工具调用，免得慢 rebuild 与下一次调用的选择交错」（`server.py:66-68`，`:82` `async with COM_LOCK`）。**它没有跨进程互斥**，但 README 把后果写进已知限制：「One SOLIDWORKS session, one COM apartment: tool calls are serialised. **Two clients driving the same session at once will deadlock it**」（`README.md:248-251`）。⇒ 与本仓已知事实 24 完全一致，是四家里**唯一把这条写进文档**的一家。

**可迁移的八件机制**（这是本卡价值主体）：

1. **`_FlagAsMethod` + `value()` 组合**（`sw_core.py:259-325`）：README 把故障讲得很具体——`IBody2.GetFaces` 被 pywin32 解析成「无参调用后的 bound method」，被当成「只有一个面」的结果；而 `ModelDocExtension.AddDimension` 这样调用**直接让 SolidWorks 崩溃**（`README.md:206-215`）。解法不是猜，而是对每个「带参调用」的成员显式 flag、对零参成员用 `value()` 兜住可调用对象。
2. **模态框治理**：`AddDimension2` 在「Input dimension value」开启时（默认开）会弹 Modify 框，**模态框阻塞打开它的 COM 调用，进而冻结整个 server**；尺寸工具临时关掉该偏好、事后恢复（`README.md:216-220`）。⇒ 与本仓 `sw_guard` 弹窗护栏同源问题，可交叉验证。
3. **返回值不可信**（`README.md:222-228`）：`SketchTrim` 成功返 `False`；`Create*` 草图 API 返回的数组真值不可靠；`SketchAddConstraints` 收到不认识的关系串会**静默忽略**。⇒ 判成功要换成「可观测的副作用」（段数、关系数、`GetWhatsWrong`）。
4. **多参考特征吃 mark 不吃选择顺序**：`InsertRefPlane` 从 **mark 0/1/2** 取第一/二/三参考；全用 mark 0 会**静默什么都不建**（`README.md:237-241`，`create_plane` 因此给每个参考单独 mark）。⇒ 直接印证本仓已知事实 32 的 mark 语义。
5. **两个单位陷阱**（`README.md:243-246`）：`IPartDoc.GetPartBox(False)` 返回**文档单位**而非米（当米用会大 1000 倍，要传 `True`）；`swSketchLINE` 的枚举值是 **0**，用 `or` 串类型会把每条线判成 unknown。
6. **`through_all_both` 要翻译成双向特征**：直接传 `swEndCondThroughAllBoth` 在 SW 2026 上**只切一侧**，得翻成两个方向都 `through_all`（`README.md:272-274`）。
7. **工程图视图的两条硬约束**：同一个父视图只能成功投影**第一个** `insert_projected_view`；detail view 的 scale 是**绝对于图纸**（不是相对父视图），1:4 图纸上写 2:1 会溢出（`README.md:262-268`）。
8. **选择三件套**：`select_by_id(name,type,mark)` / `select_at_point("",type,x,y,z,mark)` / `select_object(obj,mark)`（`sw_core.py:639-691`），并统一用 `nothing()`/`pythoncom.Nothing` 传 Callout——与「实体没有名字、只能按对象或按点选」的现实对上。

### 3.3 覆盖域（实测按模块归类；92 个工具）（来源：本卡 §8 证据清单）

| 域 | 有/无 | 代表工具 |
|---|---|---|
| 会话 | 有 | `solidworks_status` `get_active_document_info` `create_new_document` `open_document` `save_document` `save_active_document` `rebuild_document` |
| 参考 | 有 | `list_reference_planes` `create_plane` `create_axis` |
| 草图 | 有（28，最强） | `create_sketch` `draw_line` `draw_slot` `sketch_trim` `sketch_offset` `convert_entities` `add_relation` `add_dimension` `get_sketch_status` |
| 尺寸 | 有 | `add_dimension` `set_dimension` `list_dimensions`（+ `get_sketch_status` 报完全定义状态） |
| 零件 | 有 | `boss_extrude` `cut_extrude` `revolve` `loft` `sweep` `fillet` `chamfer` `shell` `draft` `rib` `simple_hole` `linear_pattern` `circular_pattern` `mirror_feature` |
| 曲面 | **无** | —— |
| 钣金 | **无** | —— |
| 焊件 | **无** | —— |
| 模具 | **无** | —— |
| 装配 | 有（5） | `list_components` `insert_component` `add_mate` `list_mates` `set_component_fixed` |
| 工程图 | 有（18，次强） | `create_drawing` `insert_standard_views` `insert_projected_view` `insert_section_view` `insert_detail_view` `auto_dimension_view` `insert_center_marks` `add_note` |
| 检查 | 有 | `check_errors` `measure` `get_mass_properties` `get_bounding_box` `list_faces` `list_edges` `list_vertices` + 每特征 `GetWhatsWrong` |
| 仿真 | **无** | —— |
| 外观 | 有（弱） | `set_appearance` `set_material` `set_view` `capture_screenshot` |
| 宏 | **无** | ——（设计上就不跑任意代码，`server.py:15-18`） |
| 高级 | **无** | 无配置/自定义属性/方程/设计表/模板类工具（仅内部 `discover_template` 找默认模板，`sw_core.py`） |

**10/16 域**：**草图/特征/工程图/检查**是它的强项；曲面/钣金/焊件/模具/仿真/宏**全缺**，配置与自定义属性也没有。

## 4. 运行条件与依赖

- 真机 SolidWorks（Windows）+ **Python ≥3.10**（`pyproject.toml:11`）。
- 依赖只有三条：`mcp>=1.29,<2`（**刻意压在上 2.0 以下**——注释写明 2.0 移除了它用的低层 `Server.list_tools()`/`call_tool()` 装饰器 API）、`pywin32>=306`、`pillow>=10`（`pyproject.toml:26-31`）。四家里依赖最轻。
- 入口：`solidworks-mcp = solidworks_mcp.server:run`（`pyproject.toml` `[project.scripts]`）；`server.json` 另给 MCP 注册清单。
- 测试：离线 `python -m unittest discover -s tests`（24 例）；真机 `tests/live_p0_regression.py`（要 SW 已开）。

## 5. 失败模式与已知坑

**自述限制**（`README.md:248-280`，质量很高，逐条都有机制解释）：单会话串行、两客户端会死锁；`list_faces`/`list_edges` 的快照索引**一改几何就失效**（要重列、不许缓存）；别人开的模态框仍会阻塞；`rib` 挑轮廓（`InsertRib` 返回 void，不满足条件就静默不建，工具会报「哪个方向成功了」）；同一父视图只能投影一次；detail scale 绝对；标准面/视图名**本地化**（用 `front`/`top`/`right`，不许硬编码英文 UI 名）；`circular_pattern` 不能阵列建了独立实体的特征；`save_document` 不能覆盖当前已打开的文件。

**本卡实读发现的缺口**：

1. **真机证据是「宣称」而非「事实」**：`README.md:293-298` 写「Every tool has been exercised against SOLIDWORKS 2026 SP3.2 on a Simplified Chinese install」，并列出 4 类数值核对（旋转环/扫掠杆/放样锥体积、5° 拔模楔形、rib 三角、`through_all_both` 全圆柱）——但仓内**没有逐工具记录/报告/日志**，只有 1 个 live 脚本的 3 个用例。⇒ 【宣称】，只能记 `source_verified`。
2. **live 测试只有 3 例**（`tests/live_p0_regression.py:63/95/107`）：`through_all_both` 用体积差判（`math.isclose(removed, π·10²·10, rel_tol=0, abs_tol=0.05)`，`:87-90`）、`equal_circles` 判半径相等、`trim` 判改对了段。判据质量高，但覆盖面窄。
3. **离线测试只测纯 Python 三块**（`tests/test_sw_core.py:16-21` 自述：method-flagging 控制流、单位换算、装配变换数学，24 例 7 个类）；**COM 行为一律不测**（作者自己说「matters here cannot be mocked faithfully」）。
4. **演示代码与产品代码同注册器**：`sw_demo.py`（12 KB，篮球）虽然默认关闭，但仍与服务同包、同 `tool()` 注册路径。
5. **依赖附着在已有会话**：不能无人值守从零拉起 SolidWorks（这是它的设计选择，但对「headless 批处理」场景是限制）。
6. **克隆落后**：HEAD 2026-08-16，远端 2026-10-13 ⇒ README 的 SW 2026 SP3.2 说法与当前远端是否一致，未确认。

## 6. 对我方目标的可用处（机制层面）

**能学（机制）**：
- **mm/deg 边界契约 + 只在 `sw_core` 转一次**：与我们「单位统一」判据直接对口，是把单位约定**落成命名与单一转换点**的现成范式，比写在文档里强。
- **`flag_methods`/`value()` 双件套**：对治「PROPGET with arguments」这条最贵的坑，且给了两个具体故障形态（一个面 vs 全部面、`AddDimension` 崩溃）供我们写负例测试。
- **「用可观测副作用判成功」**：段数变化/关系数/`GetWhatsWrong`——这是我们 `verify` 从 `run-only` 升到 `numeric` 的最短路径。
- **mark 语义（`InsertRefPlane` 0/1/2）与 `through_all_both` 翻译**：两条可直接进我们 `dead-ends.md`/`known-facts.md` 的事实，且与已知事实 32 互相印证。
- **两个单位陷阱**（`GetPartBox(False)`、`swSketchLINE=0`）：便宜且高杀伤，值得各写一个测试。
- **单进程 `asyncio.Lock` + 文档明写「两客户端会死锁」**：这是「单源运行」最省事的实现档位（不搞跨进程互斥，但把前提讲死）。
- **live 测试数值判据写法**（体积闭式值 + 0.05 mm³ 容差）：我们几何门的直接样板。
- **策略性压 `mcp` 版本上限**（`<2` 因为 2.0 删了低层装饰器 API）：依赖声明里写清「为什么压」的范例。

**不能学**：
- **广度**：92 个 / 10 域，缺曲面/钣金/焊件/模具/仿真/宏/配置——对我们只有机制价值，没有广度价值。（来源：本卡 §8 证据清单）
- **「每个工具都跑过」的宣称**：无逐工具记录，**这是本卡唯一必须打【宣称】的地方**，不能当事实并入。
- **测试规模**：2 个测试文件（1 离线 24 例 + 1 live 3 例）不足以支撑 92 个工具；数值判据再好也是点状覆盖。（来源：本卡 §8 证据清单）
- **把演示（篮球）放在产品注册器里**：即便默认关闭也不该进产品包。
- **只能附着已有会话**：无人值守从零起不来。

## 7. 许可与红线

**Apache-2.0**（`LICENSE` 全文 + `NOTICE:1-2`）。★义务三件，缺一不可：① **保留 `NOTICE`**（内容 `solidworks-mcp` / `Copyright 2026 JIALE LIU`）；② **声明改动过的文件**（Apache-2.0 §4(b)：修改过的文件必须带显著变更声明）；③ 保留 `LICENSE` 全文与任何归属声明。⇒ 我们一旦移植它的 `flag_methods`/`value`/单位契约，必须在来源头写 `Slacker-LLC/solidworks-mcp（Apache-2.0，NOTICE:2）` + 改动说明，并在 `THIRD-PARTY-NOTICES.md` 里保留该 NOTICE；推送任何远端都带这份文件（本仓已有）。★别名注意：`pyproject` Homepage 指向 `limuzi013/solidworks-mcp`，引用出处时以 `Slacker-LLC` 为准并注明旧 slug。

## 8. 证据清单

- `C:\swprojects\Slacker-LLC\solidworks_mcp\server.py:15-21`（设计边界 + 单位契约）· `:66-68`（`COM_LOCK`）· `:76-95`（查表派发）· `:82`（`async with COM_LOCK`）
- `C:\swprojects\Slacker-LLC\solidworks_mcp\sw_core.py:142`（导出白名单）· `:182-206`（`TOOLS`/`HANDLERS`/`tool()`）· `:259-300`（`value()`）· `:303-325`（`flag_methods`）· `:639-691`（三个选择函数）
- `C:\swprojects\Slacker-LLC\solidworks_mcp\sw_file.py`（`export_document` 用 `EXPORT_EXTENSIONS`；`rebuild_document` 读 `GetWhatsWrong`）
- `C:\swprojects\Slacker-LLC\README.md:200-247`（四条「花时间」的坑）· `:248-280`（已知限制，含两客户端死锁 `:250-251`）· `:288-298`（Testing + 「Every tool has been exercised…SP3.2」**宣称**）
- `C:\swprojects\Slacker-LLC\tests\live_p0_regression.py:63-120`（三例与 `math.isclose` 体积判据）· `tests\test_sw_core.py:16-21`（离线只测三块，24 例）· `solidworks_mcp\sw_demo.py`（`DEMO_ENABLED` 门控的 2 个演示工具）
- `C:\swprojects\Slacker-LLC\pyproject.toml:9-11,26-31`（Apache-2.0 + NOTICE + 三条依赖与版本上限理由）· `NOTICE:1-2`（`Copyright 2026 JIALE LIU`） · 工具计数：`solidworks_mcp/sw_*.py` 逐文件 `^\s*@tool\(` ⇒ 28/18/17/11/10/5/3 = 92（`sw_demo.py` 的 2 个在 `DEMO_ENABLED` 分支内）
- `gh api repos/Slacker-LLC/solidworks-mcp` 与 `gh api repos/limuzi013/solidworks-mcp`（2026-10-24 取：同 stars/同 `pushed_at`/同 `created_at`）

## 9. 未确认事项

1. `README.md:293` 的「Every tool has been exercised…」是否有仓外记录（issue/PR/博客）——**查不到**，本卡按【宣称】处理。
2. 92 个工具里数值判据覆盖了哪几个（README 只点了 4 类）——无映射表，**未确认**。（来源：本卡 §8 证据清单）
3. 远端 2026-08-16→2026-10-13 的增量（克隆落后）是否改了工具数/坑记录——**未确认**，需 `git fetch` 后复核。
4. `flag_methods` 与 `andrewbartels1` 的 `sw_type_info`（makepy 路）谁更可靠——两者思路不同（运行时 flag vs 类型库），本卡不下结论，需同一批成员对照实测。
5. `COM_LOCK` 只在单事件循环内有效；同机第二个 MCP 进程仍会抢 COM——README 已承认会死锁，但**未说明**它是否提供任何跨进程保护（实测代码里没有）。
