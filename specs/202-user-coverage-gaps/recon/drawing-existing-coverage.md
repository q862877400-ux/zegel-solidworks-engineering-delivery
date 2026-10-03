# 工程图 13 项功能 · 本仓现有实现查证

**查证范围**：`subskills/solidworks-engineering-drawing/scripts/` 与 `scripts/`
（★ 已按要求排除 `scripts/sw_api_*.py` —— 那是生成的反射索引，不算实现；
`scripts/sw_drawing_view.py` 里的 `VIEW_MEMBER_ARITY`（第 105 行起）同理是**生成的实参个数登记表**，本表不把它当实现，只在备注里点名）
**MCP 工具查证范围**：`mcp-server/`（`tool_specs_batch*.py` 的 `module=`/`function=`，与 `server.py` 的 `@mcp.tool` 声明）
**查证方式**：逐个 `grep` + 读函数体，只抄**真的被调用**的官方成员（注释里提到的、登记表里列出的都不算）
**本仓工程图实现只有一个文件**：`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`（2741 行 / 51 个公开函数）；`scripts/sw_drawing.py` 只是把它整包 re-export 的桥接文件（29 行）。

| 功能 | 本仓实现（文件:行号 + 函数名） | 它调的官方成员 | 是否已挂 MCP 工具 | 备注 |
|---|---|---|---|---|
| 1. 投影视图 | `drawing_workflow.py:804 create_adaptive_standard_views`；`:939 create_standard_views`；`:950 create_standard_views_with_projection`；`:976 add_view` | `CreateDrawViewFromModelView3`（:811、:988）、`CreateFirstAngleViews2`（:826 经候选元组、:956 经 `getattr`，调用点 :965）、`Create3rdAngleViews2`（:826、:947）、`ScaleRatio`（:601、:992）、`SetViewPosition`（:605）、`UseParentScale` / `PositionLocked`（:598、:600） | **是** —— `solidworks_generate_drawing`（`server.py:2094`） | 生成链 `generate_drawing_from_spec:2199` 只调 `create_adaptive_standard_views`；`add_view` / `create_standard_views` / `create_standard_views_with_projection` 三个入口**未挂工具** |
| 2. 剖面视图 | `drawing_workflow.py:996 add_section_view`；`:2528 get_section_view_data`；`:2535 set_section_style`；`:2705 get_model_view_manager`；`:2713 create_section_view_data`；`:2724 create_feature_manager_section_view`；`:2732 get_feature_manager_section_data`；`:2738 remove_feature_manager_section_view` | `CreateSectionViewAt5`（:998）、`GetDefinition`（:2532）、`GetModelViewManager`（:2707）、`CreateSectionViewData`（:2721）、`CreateSectionView`（:2729）、`GetSectionViewData`（:2735）、`RemoveSectionView`（:2741）、`ShowSectionCap` / `ZonalSection` / `TransparentSection` / `TransparencyValue` / `GraphicsOnlySection` / `KeepCapColor` / `SectionedZones` / `FirstColor` / `SecondColor` / `ThirdColor` / `FirstOffset` / `SecondOffset` / `ThirdOffset`（:2562–:2599） | **未挂工具** | `generate_drawing_from_spec` 的 9 个调用点里没有它们；`server.py` 的 `exports`（第 100–107 行）也没导出 |
| 3. 局部视图 | `drawing_workflow.py:1020 add_detail_view` | `CreateDetailViewAt4`（:1061，12 参） | **未挂工具** | 同上。枚举 `DET_VIEW_STYLES` / `DET_CIRCLE_SHOW_TYPES` 在同文件 :53 / :71 |
| 4. 断裂视图 | 无 | 无 | **未挂工具** | 全仓（除 `sw_api_sldworks.py` 反射索引）无任何调用点。`scripts/sw_drawing_view.py:273` `'InsertBreak3': 6` 与 `:280` `'IsBroken': 0` 都只是 `VIEW_MEMBER_ARITY` 登记表条目 |
| 5. 辅助视图 | 无 | 无 | **未挂工具** | 全仓无任何调用点。`scripts/sw_drawing_view_types.py:46` `SW_DRAWING_AUXILIARY_VIEW = 5` 只是**枚举常量**（该文件 63 行全是常量） |
| 6. 图纸格式/模板 | `drawing_workflow.py:404 select_drawing_template`；`:1398 set_sheet_format`；`:1409 add_sheet`；`:1424 add_a3_sheet`；`:1451 setup_current_sheet_as_a3`；`:2037 setup_current_sheet` | `GetCurrentSheet`（:1405、:1461、:2048）、`SetTemplateName`（:1406）、`NewSheet4`（:1419）、`SetupSheet6`（:1478、:2055）、`GetName`（:1462、:2049） | **是** —— `solidworks_generate_drawing`（`server.py:2094`） | `generate_drawing_from_spec:2181` 只调 `setup_current_sheet`；`set_sheet_format` / `add_sheet` / `add_a3_sheet` / `setup_current_sheet_as_a3` **未挂工具**。`select_drawing_template`（:404）**不调任何 COM**，纯文件系统打分 |
| 7. 表面粗糙度 | 无（创建） | 无（创建） | **未挂工具** | 全仓无 `InsertSurfaceFinishSymbol{,2,3}` 的调用点。**只读回读**有：`drawing_workflow.py:1651 _collect_view_professional_annotations` → `GetSFSymbols`（:1692）、`GetSymbolType` / `GetSymbol` / `GetDirectionOfLay`（:1695–1697），经 `inspect_drawing_structure:1748` 收集 |
| 8. 基准符号 | 无（创建） | 无（创建） | **未挂工具** | 全仓无 `InsertDatumTag{,2}` 的调用点。**只读回读**有：`drawing_workflow.py:1671` `GetDatumTags` + :1673 `GetLabel`，经 `inspect_drawing_structure:1748` 收集。★ `scripts/sw_gtol.py` 是几何公差（GTOL），不是基准符号 |
| 9. 注释/文字 | `drawing_workflow.py:1236 add_note`；`:2301 insert_table_annotation` | `InsertNote`（:1253）、`ForceRebuild3`（:1265）、`InsertTableAnnotation2`（:2317）、`InsertTableAnnotation`（:2322） | **是** —— `solidworks_generate_drawing`（`server.py:2094`） | `generate_drawing_from_spec:2233` 调 `add_note`。★ `insert_table_annotation` **未挂工具** |
| 10. 气泡序号 | 无 | 无 | **未挂工具** | 全仓无 `AutoBalloon{,2,3,4,5}` / `InsertBOMBalloon{,2}` / `CreateAutoBalloonOptions` 的调用点（仅 `sw_api_sldworks.py` 反射索引命中） |
| 11. 孔表 | `drawing_workflow.py:2301 insert_table_annotation`（通用表注解创建）+ `:2420 get_hole_table`（只读）+ `:2463 sort_table` | `InsertTableAnnotation`（:2322）、`InsertTableAnnotation2`（:2317）、`HoleTable`（:2424）、`Sort`（:2468） | **未挂工具** | ★ **没有孔表专用创建入口**：全仓**无 `IView.InsertHoleTable{,2,3}` 的调用点**（`scripts/sw_drawing_view.py:275` `'InsertHoleTable3': 9` 只是登记表）。来源块 :2295-2297 自述「`InsertTableAnnotation` 的 `Int32 Type` 枚举在两套官方源里都查不到 ⇒ 只做透传、不设默认类型」 |
| 12. 修订表 | `drawing_workflow.py:2301 insert_table_annotation`（通用表注解创建）+ `:2441 get_revision_table_feature` + `:2484 add_revision` + `:2491 delete_revision` + `:2498 get_current_revision` + `:2463 sort_table` | `InsertTableAnnotation`（:2322）、`InsertTableAnnotation2`（:2317）、`RevisionTableFeature`（:2445）、`AddRevision`（:2488）、`DeleteRevision`（:2494）、`CurrentRevision`（:2501）、`Sort`（:2468） | **未挂工具** | ★ **无 `ISheet.InsertRevisionTable{,2}` 的调用点**。已有的只是「拿到已存在的修订表对象后的增删改查」，建表要走第 11 行那个通用入口 |
| 13. 中心符号线 | `drawing_workflow.py:1878 auto_insert_center_marks`；回读侧 `:1631 _view_center_marks`（私有）与 `:1651 _collect_view_professional_annotations` | `AutoInsertCenterMarks2`（:1929，10 参）、`GetFirstCenterMark2`（:1633）、`GetFirstCenterMark`（:1635）、`GetCenterMarks`（:1648）、`GetNext`（:1644）、`GetCenterLines`（:1669）、`ActivateView`（:1925）、`ForceRebuild3` / `GraphicsRedraw2`（:1943、:1944） | **是** —— `solidworks_generate_drawing`（`server.py:2094`） | `generate_drawing_from_spec:2203` 调 `auto_insert_center_marks`。★ 建的是**中心标记**（`AutoInsertCenterMarks2`）；图纸**中心线**只有读（`GetCenterLines`），无创建 |

**已实现 8/13 · 已挂工具 4/13**

---

### 统计口径（为免误读，逐条写明）

- **「已实现」= 8**：第 1、2、3、6、9、13 项（6 项）+ 第 11、12 项（2 项）。
  - 6 项是**完整创建实现**：`CreateDrawViewFromModelView3` / `CreateSectionViewAt5` / `CreateDetailViewAt4` / `SetupSheet6`+`NewSheet4`+`SetTemplateName` / `InsertNote` / `AutoInsertCenterMarks2`。
  - 2 项（**孔表、修订表**）只有**通用表注解创建（`InsertTableAnnotation{,2}`，Type 枚举查不到）+ 读取 / 排序 / 修订行增删改**，**没有各自的专用创建入口**（`InsertHoleTable3`、`InsertRevisionTable2` 全仓无调用点）。按「有个对应函数」算已实现，按「能专门建出这种表」算未实现 —— 两种口径都给，不替读者选。
  - **创建侧无实现**的 5 项：第 4（断裂视图）、5（辅助视图）、7（表面粗糙度）、8（基准符号）、10（气泡序号）。其中 7、8 有只读回读（`GetSFSymbols` / `GetDatumTags`），4、5、10 连回读都没有。
- **「已挂工具」= 4**：第 1、6、9、13 项，全部经同一个工具 **`solidworks_generate_drawing`**（`mcp-server/server.py:2094`）。
  - `solidworks_review_drawing`（`server.py:2171`）与 `solidworks_inspect_drawing`（`server.py:2211`）只走 `inspect_drawing_structure`（只读），**不创建任何这 13 项里的东西**。
  - 第 2、3 项的实现存在但**没有任何工具声明指向它们** —— `server.py` 的 `exports` 字典（第 100–107 行）只导出了 `drawing_generate_from_spec` / `drawing_export_sheet_to_pdf` / `drawing_inspect_structure` 三个 drawing_workflow 函数；`mcp-server/tool_specs_batch*.py` 里没有一条 `module=` 指向 `sw_drawing` 或 `drawing_workflow`。

### 本次查证顺带确认的「排除项」（都不是实现，别当已有能力）

| 位置 | 是什么 | 为什么不算 |
|---|---|---|
| `scripts/sw_api_sldworks.py` | SolidWorks 类型库反射索引 | 生成物，按要求排除；本表 4、5、7、8、10 的所有命中**只在这里** |
| `scripts/sw_drawing_view.py:105` `VIEW_MEMBER_ARITY` | `IView` 成员「实参个数」自动登记表 | 只列名字与元数，**从不调用**；`AutoInsertCenterMarks2`(:110) / `InsertBreak3`(:273) / `InsertHoleTable3`(:275) / `IsBroken`(:280) 都只是它的条目 |
| `scripts/sw_drawing_view_types.py` | `swDrawingViewTypes_e` 枚举常量单一真源（63 行） | 纯常量，无函数 |
| `scripts/sw_drawing_query.py` | 图纸页/视图只读查询 | 18 个函数全是读；且其 3 个已挂工具（`tool_specs_batch19/36/42/44`）与这 13 项的**创建**无关 |
| `scripts/sw_gtol.py` | 几何公差（GTOL）符号 | 是 GD&T 公差框，不是基准符号（Datum Feature Symbol） |
| `tools/prove_drawing_batch.py` | 真机验证探针脚本 | 在 `tools/`，**不在本次查证的两个目录内**；它确实写了 `CreateAuxiliaryViewAt2` / `InsertSurfaceFinishSymbol3` / `AutoBalloon5` / `InsertHoleTable3` / `InsertRevisionTable2` 的调用，但那是**探针**，不是仓库交付实现 |
| `specs/202-user-coverage-gaps/recon/check_drawing_signatures.py` | 签名 arity 静态核对表 | 同上，只对照不调用 |