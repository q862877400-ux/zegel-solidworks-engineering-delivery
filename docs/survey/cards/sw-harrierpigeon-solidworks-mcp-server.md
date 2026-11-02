# HarrierPigeon/Solidworks-MCP-Server

<!-- survey: class=H; repr=feature-tree; orchestration=single; verify=run-only; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `HarrierPigeon/Solidworks-MCP-Server` · https://github.com/HarrierPigeon/Solidworks-MCP-Server |
| 许可 | **MIT**（`LICENSE:1-3` = `MIT License` / `Copyright (c) 2026 Joseph Robertson`；`pyproject.toml` 同）⇒ 可读可抄可商用，保留版权声明 |
| 元数据 | stars 32 · forks 5 · 语言 Python · 仓库 450 KB · 建档 2026-07-29 · **最近推送 2026-08-14**（来源：`gh api repos/HarrierPigeon/Solidworks-MCP-Server`，2026-11-02 取）⇒ 三个月内无更新 |
| 克隆 | `D:\swagent-2026Q4\repos\HarrierPigeon__Solidworks-MCP-Server`（`--depth 1`）|
| 证据等级 | **读码**（`test.py` 全部用例都要活的 SolidWorks，无 mock，故未跑；SolidWorks 未跑，建模能力结论止步 `source`）|

## 1. 一句话定位

**工具数量第二多（95 个）却把「读回」做得最像给人看的一家**：每个特征、草图、实体都发一个 `feat:`/`sketch:`/`comp:` 稳定 ID 并按文档分域记账，面可以「用一句话找」（朝向 + 创建特征 + 曲面类型 + 面积序），还能把面编号**画在截图上**让模型照着点。（`server.py` + `solidworks/*.py`）

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：MCP stdio（低层 `mcp.server.Server` + 手写 `list_tools`/`call_tool`，`server.py:101-176`）。工具定义由 15 个工具模块各自 `get_tool_definitions()` 产出，`server.py:91-94` 拼成 `name -> module` 路由表。

**中间表示**：**一张按文档分域的对象登记表**（`solidworks/state_tracker.py:13-20` 定义 ID 格式：`feat:<特征名>` / `sketch:<草图名>` / `entity:<草图>/<类型>_<序号>` / `ref:<参考几何>` / `comp:<组件名>` / `mate:<配合名>`）。它不是拓扑 ID：`register_feature` 直接 `f"feat:{sw_name}"`（`state_tracker.py:402-415`），改名时用 `_rebase_entity_ids` 重挂（`state_tracker.py:272`）——**本质是「SolidWorks 名字 → 语义 ID」的簿记层**，让模型说的和 SolidWorks 里的对得上，并给裸名用法打弃用警告（`solidworks/com_utils.py:90-101`）。

**生成**：不生成代码。但它**会启动 SolidWorks**：`GetActiveObject` 失败后 `win32com.client.Dispatch("SldWorks.Application")`（`solidworks/connection.py:24-35`）——本轮六家里唯一会自己拉起进程的一家。

**编排**：一个 `solidworks_batch` 工具，一次最多 25 个子调用、顺序执行、`stopOnError` 默认真；明写「批内后续调用**不能**引用前面的返回值，需要返回值就切开」（`server.py:106-143`、`:197-225`）。⇒ 这是「少工具 + 批量口」的折中档：不是万能代码口，只是把「互不依赖的调用」打包省往返。

**执行**：进程内晚绑定 pywin32，**没有专用 COM 线程**（`server.py:243` 只在主线程 `CoInitialize`），**没有 `CommandInProgress`**（全仓 0 处引用，计数命令 `(Select-String -Path 'solidworks\*.py' -Pattern 'CommandInProgress' -AllMatches).Count`）。

**验证**：点状。共享件 `com_utils.verify_rebuild`（`solidworks/com_utils.py:11-47`）在改动后 `ForceRebuild3` 并逐个特征读 `GetErrorCode2`；注释交代了它为什么存在——「尺寸改动弄坏下游特征时，以前无条件回 ✓，`ForceRebuild3` 的返回和特征树的错误标记从没被读过」。特征级另有「按特征树前后差确认建成」的检查（`solidworks/applied_features.py:506-522` 抽壳）。**没有**体积/质量的期望值断言，也**没有**失败回滚。

**交付**：`save_document` 按扩展名分流导出 STEP/IGS/X_T/SAT/STL（`README.md` 工具表「Documents & assemblies」段），另有 `capture_views` 出标准视图 PNG。

## 3. 技术方案要点（可迁移的机制）

### 3.1 工具面与粒度：**95 个，一动词一工具 + 一个批量口**（实测计数）（`server.py`）

计数命令与结果：`(Select-String -Path 'solidworks\*.py' -Pattern 'name="solidworks_' -AllMatches).Count` ⇒ **94**，加 `server.py:106-143` 手写的 `solidworks_batch` ⇒ **95**。逐模块分布（同一条命令按文件分组）：`sketching.py` 21、`modeling.py` 11、`assembly.py` 9、`document_manager.py` 8、`applied_features.py` 7、`configurations.py` 7、`geometry_query.py` 7、`cut_features.py` 4、`features.py` 4、`feature_tree.py` 4、`reference_geometry.py` 4、`patterns.py` 3、`state_query.py` 3、`hole_features.py` 2。⇒ 一动词一工具为主，**外加一个「批量互不依赖调用」的口**（25 条上限）；无 `operation` 枚举、无任意代码执行。

### 3.2 持久引用：**不解，但给了「描述式选择器 + 带编号的截图」这个组合**

`find_face` 按**谓词**找面：朝向（`TOP`/`BOTTOM`/`ANGLED`/`ANY`）、创建它的特征、曲面类型、面积序（最大/最小），命中的面按面积降序排，返回 `samplePoint` 供后续选择用（`solidworks/geometry_query.py:221-301`）。选不中时回一句「放宽条件或先 `get_faces`」而不是抛错。

更巧的是 `_label_faces`（`geometry_query.py:370-394`）：把面编号**投影到截图上**，于是 `look_at_model` 返回的图与 `get_faces` 的编号是同一套——模型可以「看图标号 → 用坐标选面」。⇒ 这是把「视觉」和「选择」缝在一起的具体做法，**比我方截图只用于人看更进一步**。

代价：两者的锚点都是**坐标**。改几何后坐标变，谓词可能命中另一张面；代码里没有「这个选择器是否仍然唯一」的检查（对比 soheil-mp 的 `expect:4` 约定，见 `sw-soheil-mp-solidworks-mcp.md` §3.2）。

### 3.3 单源 COM 互斥：**没解，而且也没把前提写下来**

无专用线程、无 `CommandInProgress`、无跨进程互斥。它反而**主动 `Dispatch` 拉起** SolidWorks（`connection.py:34`），在多 MCP 并存时是最容易踩「两个进程抢同一个 COM 连接」的一种形态。⇒ 这是本卡最该反着学的一条。

### 3.4 一条可直接进我方「已知事实」的绑定坑：**别用 `callable()` 判 COM 返回值**

`solidworks/com_utils.py:104-117`：晚绑定下若把「可能是属性、可能是 0 参方法」的成员结果用 `callable()` 判断，会把 **COM 对象本身**也判成可调用（`CDispatch` 有自己的默认分发方法），一调就报 `Member not found`。正确判据是 `isinstance(val, types.MethodType)`。★ 这条与 hjbaard 的 `value()` 写法**互相矛盾**（后者用「可调用就调一次」，见 `sw-hjbaard-solidworks-mcp.md` §3.6），两条都跑在真机上、结论相反 ⇒ 说明这个判断必须按「返回值到底是 bound method 还是 COM 对象」分开做，不能一把抓。

另一条实测读数：`IFeature.GetErrorCode2` 的形参是 **BYREF BOOL 的 VARIANT**，传裸 `bool`/`int` 报 Type mismatch（`com_utils.py:27-38`，注释标注探针日期 2026-07-11）。

### 3.5 稳定 ID 的「改名重挂」

`rename_feature` 之后 `rename_object` 把旧 ID 换成新 ID，并递归把 `entity:<草图>/…` 前缀整体 rebase（`state_tracker.py:272-338`）。⇒ 我方若做「给对象起语义名」这一层，改名时必须同步改引用，否则下一次调用会指到不存在的名字。这是簿记层的必要条件，不是可选项。

## 4. 运行条件与依赖

- Windows + SolidWorks 2022+（README 称「tested on SolidWorks 2025」）；MCP 客户端 Claude Desktop / Codex / ChatGPT 桌面端。
- Python ≥3.10（README「Manual install」）；依赖见 `requirements.txt`（`mcp`、`pywin32`）。
- 一键安装脚本 `scripts/install.ps1`（装 uv、下载 release、注册客户端）。
- 测试：`python test.py`（**全部用例需要活的 SolidWorks**；README 明说「There is no mock of the COM layer」），另有 `tests/agent_capability_tests.md` 的 46 条端到端提示词。⇒ **本机不可跑**，故本卡只给【读码】。

## 5. 失败模式与已知坑

自述（`README.md`「Known limitations」）+ 实读：
1. **工程图（2D drafting）没实现**。
2. **`hole_wizard` 会触发阻塞对话框**，官方兜底建议是「让模型改用草图圆 + 拉伸切除」。
3. **设计树文件夹是平的，且成员只能在创建时决定**（SolidWorks 拒绝 `MoveToFolder` 把特征移进已有文件夹）。
4. **`recognize_features` 只恢复部分特征树**，且需要 Professional/Premium。
5. **WIDTH 配合没实现**；组件定位只能靠配合（晚绑定下无法直接设变换）。
6. **无 PDM / 3DEXPERIENCE 感知**。
7. **会自己 `Dispatch` 拉起 SolidWorks**（`connection.py:34`）⇒ 与「单源运行」纪律冲突的形态。
8. **批内不能链式取返回值**（`server.py:110-118`）——模型必须自己知道「这一批里别依赖上一步的结果」，这是把编排责任推给模型的典型代价。

## 6. 对我方目标的可用处（能学 / 不能学）

**Q2 逐条答**：
| 问题 | 它解到什么程度 | 依据 |
|---|---|---|
| 持久引用 | **不解，绕行**：描述式谓词找面 + 坐标选择；改名时 ID 重挂，但没有「选择器仍唯一」的校验 | `solidworks/geometry_query.py:221-301`、`state_tracker.py:272` |
| 回读验证 | **点状**：`verify_rebuild` 读 `GetErrorCode2`；无期望值、无回滚 | `solidworks/com_utils.py:11-47` |
| 事务式建模 | **无** | 全仓无回滚路径 |
| 单源 COM 互斥 | **无**，且会主动拉起第二个实例 | `solidworks/connection.py:24-35` |

**Q3 答**：**MCP 服务端**；工具面 **95 个**（`solidworks/*.py` 的 94 个 `name="solidworks_*"` + `server.py` 的 `solidworks_batch`）；粒度 = 一动词一工具，**外加一个 25 条上限的批量口**（不是万能代码口，是往返压缩）。

**能学**：
1. **`_label_faces`：把面编号画到截图上**，让 `get_faces` 的索引与视觉一一对应。这是「视觉反馈」与「精确选择」之间的最短桥，我方截图能力可直接加这一层。
2. **`com_prop` 的 `isinstance(val, types.MethodType)` 判据 + 「不要用 `callable()`」的理由**——直接可进 `known-facts.md`，并用来校验我方现有绑定代码。
3. **`GetErrorCode2` 要 BYREF BOOL VARIANT**：一条具体签名事实，配一个负例测试。
4. **`verify_rebuild` 的存在理由**（「以前无条件回 ✓，重建返回和错误标记从没被读过」）：这是把「假成功」变成「可读失败」的最小改动，成本极低。
5. **`find_face` 的谓词设计**（朝向 + 特征 + 曲面类型 + 面积序）与「选不中就给放宽建议」的报错形状。
6. **`exit_active_sketch` 的回读真实草图名**（`com_utils.py:50-87`）：隐式退出草图后不读回真名，会让后续实体 ID 全部错位——一条具体的一致性陷阱。

**不能学**：
- **「无专用线程 + 无 `CommandInProgress` + 主动 `Dispatch`」**：与我方单源纪律正面冲突。
- **把编排责任推给模型**（批内不能链式）：错一步就整批语义可疑，且模型很难自己发现。
- **只能靠配合定位组件**（无变换设置）：装配调试成本高。
- **「most complete MCP server」这类自评**：工具数 95 但工程图缺失、无回滚、无互斥，「最完整」是数量口径不是能力口径。

## 7. 许可与红线

**MIT**（`LICENSE:1-3`，`Copyright (c) 2026 Joseph Robertson`）。可移植，义务：保留版权声明。★ 移植 `_label_faces`/`find_face`/`com_prop`/`verify_rebuild` 的形状时，来源头写 `HarrierPigeon/Solidworks-MCP-Server（MIT，LICENSE:3）` + 改动说明。

## 8. 证据清单

- `server.py:16-33`（15 个工具模块导入）· `:91-94`（`name -> module` 路由表）· `:101-143`（手写 `list_tools`，`solidworks_batch` 定义）· `:146-181`（`call_tool`；`IMAGE_FILE:` 约定把 PNG 转成 `ImageContent`）· `:183-195`（`_route_tool`）· `:197-225`（批执行，无结果链式）· `:241-244`（`run()` 主线程 `CoInitialize`）
- `solidworks/state_tracker.py:1-20`（ID 格式与按文档分域的理由）· `:34-44`（标题归一化）· `:272`（`_rebase_entity_ids`）· `:338`（`rename_object`）· `:402-415`（`register_feature` 生成 `feat:<sw_name>`）· `:417-440`（`remove_feature` 级联删草图/实体记录）
- `solidworks/geometry_query.py:221-301`（`find_face` 描述式选择 + 返回 `samplePoint`）· `:370-394`（`_label_faces` 把编号投影到截图）· `:822`（`get_faces`）· `:874`（`get_edges`）
- `solidworks/com_utils.py:11-47`（`verify_rebuild`：`ForceRebuild3` + 逐特征 `GetErrorCode2`，含 BYREF VARIANT 与探针日期）· `:50-87`（`exit_active_sketch` 回读真实草图名）· `:90-101`（`resolve_tracked_name` 对裸名打弃用警告）· `:104-117`（`com_prop`：不要用 `callable()` 判 COM 返回值）
- `solidworks/connection.py:24-35`（`GetActiveObject` → 失败 `Dispatch` 拉起 + `Visible=True`）· `:80-110`（模板发现/新建装配）
- `README.md`「The tools」（工具表）、「Known limitations」（工程图缺、`hole_wizard` 阻塞框、文件夹平铺、`recognize_features` 部分恢复、无 WIDTH 配合、无 PDM）、「Development」（`test.py` 无 COM mock、46 条提示词）
- `tests/agent_capability_tests.md`（46 条端到端提示词，只读未跑）
- 元数据：`gh api repos/HarrierPigeon/Solidworks-MCP-Server`（2026-11-02 取：stars 32 / pushed 2026-08-14 / MIT）

## 9. 未确认事项

1. **95 个工具里有多少在真机上被跑过**：`test.py` 有 45 个 `def test_`（计数命令 `(Select-String -Path 'test.py' -Pattern '^\s*def test_').Count`），远少于 95，**哪些工具有测试、哪些没有，未逐条映射**。
2. **`find_face` 在多面同法向时的唯一性**：代码按面积排序返回全部命中，**是否会出现「选了错的面但形状对」**，未验。
3. **`_label_faces` 的编号与 `get_faces` 索引是否严格同序**：只读代码未见显式断言，**未确认**。
4. **`solidworks_batch` 在部分失败后的状态**：`stopOnError=true` 时前面成功的子调用**不回滚**，对特征树的净效果未验。
5. **三个月无推送（2026-08-14 起）是否意味着停更**：无法从仓库判定，**未确认**。
6. **`Dispatch` 拉起路径在已有实例时的行为**：未读全 `connection.py` 的重连逻辑，**未确认**是否会拿到第二个进程。
