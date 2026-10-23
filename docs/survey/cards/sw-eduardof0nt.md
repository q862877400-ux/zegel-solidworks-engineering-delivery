# Eduardof0nt/Solidworks-MCP-Server

<!-- survey: class=H; repr=feature-tree; orchestration=single; verify=run-only; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `Eduardof0nt/Solidworks-MCP-Server` · https://github.com/Eduardof0nt/Solidworks-MCP-Server |
| 许可 | MIT（`LICENSE:1-3` 原文 `MIT License` + `Copyright (c) 2026 Eduardo Font Cruz`）⇒ 可借鉴，移植须保留版权行 |
| 元数据 | stars 10 · 最近推送 2026-05-22T06:38:42Z · 语言 Python（来源：`gh api repos/Eduardof0nt/Solidworks-MCP-Server`，2026-10-24 取）|
| 克隆 | `C:\swprojects\Eduardof0nt`（HEAD `ba40520`，2026-05-22 00:38:36 -0600；与远端 `pushed_at` 同日 ⇒ 快照不落后）|
| 证据等级 | 读码（未跑任何东西：克隆内 0 个测试文件可跑，且纪律不许改动克隆）|（来源：本卡 §8 证据清单）

## 1. 一句话定位

**用两个巨文件把 SolidWorks COM 的 187 个动词挨个包成 MCP 工具**：`server.py`（161 KB，187 个 `@mcp.tool`）＋`sw_client.py`（124 KB，198 个方法的单一 `SolidWorksClient`），没有抽象层、没有测试，README 声称「已在 SolidWorks 2024 验证」。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：MCP stdio 工具调用，参数由每个工具各自的 Pydantic 模型校验（`server.py:76` 起 `FastMCP`，逐工具 `@mcp.tool(name="sw_...")`）。

**中间表示**：无几何 IR。参数即 COM 调用的实参，直接落到 `SolidWorksClient` 的同名方法（187 个工具 1:1 对应 198 个客户端方法中的绝大多数，`sw_client.py:200` 起）。唯一的中间态是**选择集**：多数特征工具先 `SelectByID2(feature/plane, ...)` 选上对象再建特征（`sw_client.py:860`、`926-938`）。

**生成**：不生成代码，只调 API。极少数入口是逃逸口——`sw_run_vba_code` 直接执行用户给的 VBA 文本、`sw_run_macro` 跑 `.swp`（`README.md:259-266` 一节）。

**编排**：无。一次工具调用 = 一次 COM 动作序列，没有工作流/批处理/模板层（无 `operation` 分派器，见 §3）。

**执行**：**单线程 STA 线程池**——`ThreadPoolExecutor(max_workers=1, initializer=pythoncom.CoInitialize)`（`server.py:85-88`），所有 COM 调用提交到这一条线程，避免跨线程 `IDispatch`。连接走 `GetActiveObject("SldWorks.Application")` → `Dispatch` 兜底拉起（`sw_client.py:239`、`253`）。

**验证**：**几乎没有**。工具把 COM 返回值直接回给客户端；量测类工具（质量/包围盒/测量）确实读回数字，但没有一处把数字与几何断言比较后拒收。`check_geometry` 更是在 `CheckDocument` 抛异常时把结果置 0（`sw_client.py:1224-1236`），于是「检查失败」被渲染成 `status: "OK"`。

**交付**：`sw_export_step` / `sw_export_stl` / `sw_export_file` / `sw_export_drawing_pdf` / `sw_export_drawing_dwg` 直接 `SaveAs`（`sw_client.py:387`、`473` 的 `SaveAs` + `VARIANT(VT_DISPATCH,None)`）。无回读校验。

## 3. 技术方案要点（可迁移的机制）

### 3.1 工具清单与粒度：**187 个（实测），一动词一工具，无合并式 `operation` 分派**（来源：本卡 §8 证据清单）

★ 起点数字「187 个工具 / 测试文件 0 个」来自本仓 `AGENTS.md` §四 台账；**实测复核一致**：`Select-String -Pattern '@mcp\.tool' server.py` 得 187（其中 88 个是裸 `@mcp.tool(`、99 个带显式 `name=`），去重后仍 187 个工具名；测试文件 **0**（克隆内仅 7 个文件：`server.py`/`sw_client.py`/`README.md`/`LICENSE`/`requirements.txt`/`.gitignore`/`.gitattributes`）。

**分组只在 README 里**：16 个基础小节（Connection / Files & Documents / Selection / Sketch / Features (Part) / Reference Geometry / Surface Modeling / Assembly / Drawing / Dimensions & Parameters / Analysis / Properties & Configurations / Equations / Visualization / Macros & Automation / Sheet Metal — Basic，`README.md:120-275`）＋「Extended Toolset (**additional 99 tools**)」17 个小节（`README.md:276-446`）；99 是 README 自称，其余 88 个由 187−99 推得。**代码里没有分组**：187 个装饰器在同一文件顺序排布。

**粒度**：极细且扁平——`sw_sketch_line`/`sw_sketch_circle`/`sw_sketch_rectangle` 各是一个工具，`sw_add_centerline`/`sw_add_balloon`/`sw_add_revision_table` 这类单条注解也各占一个工具。代价：模型要自己记住 187 个名字与参数，没有「先查再建」的元工具。（来源：本卡 §8 证据清单）

### 3.2 桥接方式与单实例互斥

**桥接**：进程内 COM（win32com 迟到绑定 + DISPID 直接 `Invoke`），无外部 exe、无插件、无文件 IPC。三个可迁移的小机制：

1. **DISPID 强制方法调用**：`_invoke(obj, dispid, *args)` 用 `obj._oleobj_.Invoke(dispid, 0, 1 /*DISPATCH_METHOD*/, 1, *args)` 绕开 win32com 把 SW 2024 的 dual 成员当属性取（`sw_client.py:26-38`；常量表 `sw_client.py:20-26`，如 `NewDocument=111`、`OpenDoc6=167`、`SelectByID2=68`）。`_resolve_dispid` 再按名在运行时查 DISPID（`sw_client.py:40-46`）。
2. **`_get()` 双形态自适应**：属性可能返回数值也可能返回可调用对象，`_get` 判 `isinstance(val,(str,int,float,bool,bytes,None))` 就直接用、`callable` 就调一次（`sw_client.py:48-60`）。
3. **失败阶梯**：`get_bounding_box` 依次试 `Extension.GetDocumentBoundingBox(0)` → `doc.GetModelBoundingBox()` → `body.GetBodyBox()`（`sw_client.py:1175-1200`）；`get_mass_properties` 依次试 `CreateMassProperty2` → `CreateMassProperty` 并处理「是属性不是方法」（`sw_client.py:1120-1160`）。

**单实例互斥：有锁，但已被降级为「软警告」**——这条必须改口径。`server.py:33-69` 建命名互斥 `Local\SolidWorksMCPServer_SingleInstance_v1`，但 HEAD 提交正是 `Relax single-instance mutex from hard exit to soft warning`（2026-05-22）：`ERROR_ALREADY_EXISTS` 时**默认只往 stderr 写一行警告然后继续**，只有 `SW_MCP_SINGLE=1` 才 `sys.exit(1)`（`server.py:56-68`）。文件头注释还辩称「两个实例同时跑是安全的，SolidWorks 会用 STA 消息队列串行化」（`server.py:36-42`）——这与本仓已知事实 24（多进程抢同一 COM 会死锁）相反。**结论：当前代码不提供单实例保护，`AGENTS.md` §四里「为此实现命名互斥锁」这句只对 2026-05-22 之前成立，引用时必须注明版本。**

### 3.3 覆盖域（实测按工具名归类，一工具归一类，列代表工具）

| 域 | 有/无 | 代表工具 |
|---|---|---|
| 会话 | 有 | `sw_connect` `sw_get_status` `sw_open_document` `sw_save_all` `sw_close_all` `sw_save_as_copy` |
| 参考 | 有 | `sw_create_reference_plane` `sw_create_reference_axis` `sw_create_reference_point` |
| 草图 | 有 | `sw_create_sketch` `sw_sketch_line` `sw_sketch_trim` `sw_sketch_text` `sw_start_3d_sketch` `sw_split_line` |
| 尺寸 | 有 | `sw_add_sketch_dimension` `sw_get_dimension` `sw_set_dimension` `sw_link_dimension_to_equation` |
| 零件 | 有 | `sw_extrude` `sw_revolve` `sw_fillet` `sw_shell` `sw_loft` `sw_sweep` `sw_hole_wizard` `sw_rib` `sw_dome` `sw_wrap` `sw_intersect` `sw_boundary_boss` |
| 曲面 | 有 | `sw_planar_surface` `sw_trim_surface` `sw_extend_surface` `sw_knit_surfaces` `sw_thicken_surface` `sw_delete_face` `sw_filled_surface` |
| 钣金 | 有 | `sw_base_flange` `sw_edge_flange` `sw_sketched_bend` `sw_jog` `sw_hem` `sw_unfold` `sw_fold` `sw_flatten_sheet_metal` `sw_export_flat_pattern` |
| 焊件 | 有 | `sw_insert_weldment` `sw_add_structural_member` `sw_add_gusset` `sw_add_end_cap` `sw_trim_weldment` |
| 模具 | 有 | `sw_parting_line` `sw_shut_off_surface` `sw_tooling_split` |
| 装配 | 有 | `sw_insert_component` `sw_add_mate` `sw_check_interference` `sw_explode_assembly` `sw_pattern_component_linear` |
| 工程图 | 有 | `sw_add_drawing_view` `sw_add_section_view` `sw_add_bom_table` `sw_add_geometric_tolerance` `sw_add_datum_feature` `sw_export_drawing_pdf` |
| 检查 | 有 | `sw_check_geometry` `sw_measure_distance` `sw_get_mass_properties` `sw_get_bounding_box` `sw_analyze_draft` |
| 仿真 | 有 | `sw_create_simulation_study` `sw_run_simulation` `sw_create_motion_study`（注释自带「requires Simulation add-in」，`sw_client.py:2364-2395`） |
| 外观 | 有 | `sw_set_appearance_color` `sw_set_material` `sw_capture_screenshot` `sw_set_view_orientation` `sw_set_background` `sw_take_photoview_screenshot` |
| 宏 | 有 | `sw_run_macro` `sw_run_vba_code` `sw_start_macro_recording` `sw_stop_macro_recording` |
| 高级 | 有 | `sw_add_configuration` `sw_create_design_table` `sw_get_custom_properties` `sw_list_sensors` `sw_activate_display_state` `sw_list_global_variables` |

**16/16 域全有**——这是四家里**广度最全**的一家（旧台账写它「高级=0」，与本卡实读不符：它确有配置/设计表/自定义属性/传感器/显示状态，见上表末行）。

## 4. 运行条件与依赖

- **必须真机 SolidWorks**（COM，Windows only）；README 写 2018+、按 2024 开发（`README.md:34-35`）。
- Python 3.10+（`README.md:37`；徽章 `Python 3.10+`）。
- 依赖仅三条：`mcp>=1.0.0`、`pydantic>=2.0.0`、`pywin32>=306`（`requirements.txt:1-3`）。**无测试依赖**——这也是它 0 测试的一个旁证。
- 仿真/PhotoView 需对应 add-in 装好并加载（`README.md:641-642`）。

## 5. 失败模式与已知坑

**自述限制**（`README.md:635-645`）：Windows only；stdio 单客户端；长操作阻塞 COM 线程；部分操作要求 SolidWorks UI 可交互（文件对话框/报错框）；两个工具依赖 add-in。

**代码层面的坑（本卡实读，比 README 严重）**：

1. **失败即成功（fail-open）**：`check_geometry` 捕 `CheckDocument` 异常后 `result = 0` ⇒ `status: "OK"`（`sw_client.py:1228-1236`）。检查的意义被这一行抵消。
2. **「分析」只开 UI 不读结果**：`analyze_draft` 调 `ShowDraftAnalysis(...)` 后直接 `return {"analysis_active": True}`（`sw_client.py:1238-1241`），没有任何拔模角数据回读——模型会以为做过了。
3. **回退阶梯无出处**：三路 bbox 里哪一路成功、为什么退，返回值里没有字段可查（`sw_client.py:1175-1200`），出问题时无法定位。
4. **187 个工具的 docstring/参数说明与 SW 版本强绑定但无版本判据**：README 让贡献者「在你真跑过的版本上标 SW 版本」（`README.md:628-630`），说明作者自己也知道覆盖面是按版本漂移的。
5. **文档与代码已经分叉**：README 说「单实例」，代码是软警告（§3.2）；`AGENTS.md` 台账也沿用了旧的硬互斥说法。
6. **零测试结构性地放大以上所有问题**：没有一条自动化断言能发现「检查失败报 OK」。

## 6. 对我方目标的可用处（机制层面）

我方目标：让普通模型在 SolidWorks 里建出能用、规范、可验证的参数化模型。

**能学（机制）**：
- **187 个动词名就是一张官方 API 覆盖清单**：可直接当「本仓还缺哪些域/哪些动词」的对照表（对照我们 `docs/union-coverage-matrix.md` 的空格），比读 API 索引快。
- **DISPID 强制方法调用 + `_get` 双形态**：这两条正是我们「属性/方法混淆」类坑的现成解法，且实现只有 ~30 行，可搬进我们的 COM 层（我们已有等价事实，但缺少这样集中的一处 helper）。（来源：本卡 §8 证据清单）
- **多路失败阶梯**（bbox 三路、mass property 两代）：与我们「官方签名三源互证」互补——签名先定，运行时再留降级路径；但**必须把「用了哪一路」写进返回值**（它没写，我们补上）。
- **187 个工具全带 MCP `annotations`**（`readOnlyHint`/`destructiveHint`，`server.py` 的 `@mcp.tool(name=..., annotations={...})`）：给客户端做授权/确认策略用，成本极低，值得照做。
- **单 STA 线程池**：最小实现（一个 worker + `CoInitialize` initializer），可作我们 executor 的兜底方案。

**不能学**：
- **「工具多但零测试」**：187 工具 / 0 测试文件（本卡实测）＋ README 一句 `Verified on SolidWorks 2024`（`README.md:14`，**【宣称】**，全仓无任何测试、报告、截图或日志支撑）。广度不能替代验证；我们并入时每条只能记 `source_verified`，绝不可提级。
- **fail-open 验证**：把异常吞成 0 再报 OK，是「看起来验过」的最坏形态——比不验证更危险，因为它会让模型继续下一步。
- **God object**：161 KB + 124 KB 两文件、198 方法的单类，命名/单位/选择/出处四件事没有一处统一层（对比 `Slacker-LLC` 的 mm/deg 边界契约）。我们不该按它的形状长。（来源：本卡 §8 证据清单）
- **把互斥降级为警告**（§3.2）：与我方「单源运行」判据直接冲突。
- **仿真/渲染类工具只「建 study / 开对话框」**：这种工具进了清单会让覆盖矩阵虚高。

## 7. 许可与红线

MIT（`LICENSE:1-3`，`Copyright (c) 2026 Eduardo Font Cruz`）：读/改/商用皆可，**唯一义务是保留版权声明与许可全文**。无 NOTICE 义务、无 copyleft。移植任一函数须在来源头写 `repo/LICENSE/文件:行`，并在 `capabilities.yaml` 的 `provenance` 标 `license: MIT`。红线：不得把它的「已验证」措辞连带抄进我们的证据字段（我们只认自己的运行证据）。

## 8. 证据清单

- `C:\swprojects\Eduardof0nt\server.py:20-26`（DISPID 常量）· `:29-38`（`_invoke`）· `:40-46`（`_resolve_dispid`）· `:48-60`（`_get`）
- `C:\swprojects\Eduardof0nt\server.py:33-69`（命名互斥；`:56-68` 软警告分支）· `:72`（模块级获取）· `:85-88`（单线程 STA 池）
- `C:\swprojects\Eduardof0nt\sw_client.py:200`（`class SolidWorksClient`）· `:239/253`（GetActiveObject/Dispatch）· `:860`（SelectByID2）· `:1019`（check_interference）· `:1120`（mass properties）· `:1175-1200`（bbox 三路）· `:1224-1236`（check_geometry fail-open）· `:1238-1241`（analyze_draft）· `:2364-2395`（Simulation）
- `C:\swprojects\Eduardof0nt\README.md:10`（187 tools）· `:14`（Verified on SolidWorks 2024，**宣称**）· `:120-275`（基础小节）· `:276`（additional 99 tools）· `:544-566`（架构自述）· `:635-645`（限制）
- `C:\swprojects\Eduardof0nt\requirements.txt:1-3`
- `gh api repos/Eduardof0nt/Solidworks-MCP-Server`（2026-10-24 取：stars/pushed_at/language）
- 计数命令：`Select-String -Pattern '@mcp\.tool' server.py | Measure-Object` = 187；`Get-ChildItem -Recurse -File` = 7 个文件、0 个 `test_*`

## 9. 未确认事项

1. README 的 `Verified on SolidWorks 2024` 究竟指哪一次会话、验了哪些工具——**查不到**任何记录（无 CI、无报告、无 issue 引用）。
2. 187 个工具里有多少在真机上「建成了特征」而非「调用没报错」——无证据，无法判定；本卡不敢给任何百分比。（来源：本卡 §8 证据清单）
3. 软互斥下真有两个进程同时驱动时的实际行为（是否死锁、几秒死锁）——本卡未实测，只按已知事实 24 记为风险。
4. `sw_run_vba_code` 在 SW 2024+ 需要的 `.swp` OLE 容器形态是否被它正确处理——未读透实现，未确认。
