# S3-2 · subskill 函数能力盘点（第 2 段）

**被扫文件**：`D:\AI\SW\subskills\solidworks-engineering-drawing\scripts\drawing_workflow.py`（全文件 **2746 行**）

## 一、边界声明（★ 以实际读到的 `def` 行号为准）

| 项 | 值 |
|---|---|
| 本段起 | **第 941 行** `def create_standard_views` —— 任务给的「约 916」之后**第一条** `def`（916 之前最近的一条是第 806 行 `create_adaptive_standard_views`，归上一段） |
| 本段止 | **第 1707 行** `def inspect_drawing_structure` —— 任务给的「约 1830」之前**最后一条** `def`（其后第 1883 行 `auto_insert_center_marks` 归下一段） |
| 本段 `def` 条数 | **27**（文件内 83 条匹配中的 27 条；本段内**无嵌套 `def`** —— 全文件只有 3 处缩进 `def`，在 348 / 548 / 694 行，均在本段外） |
| 本段跨越的行区间 | 941 – 1880（`inspect_drawing_structure` 的函数体结束于 1880 行） |

## 二、判定口径

★ 「能挂」的**唯一**判据 = **形参里有没有 `ToolSpec.Param` 表达不了的东西**。`Param` 的字段只有 `name / kind / default / description / required`（`mcp-server/tool_registry.py:217-236`），宿主对象只走 `ToolSpec.inject` 一个通道（`tool_registry.py:303-318`）。

| 判定 | 含义 |
|---|---|
| **能** | 全部形参是标量（str/float/int/bool）或标量容器（list/dict，本仓 `Param("bom_rows", list, …)` / `Param("properties", dict, …)` 已有先例）+ 宿主对象走 `inject`；返回值可 JSON 化 |
| **需包装** | 形参能声明，但**返回值是 COM 对象 / SafeArray**（要证据化就得 `extra_op` 或再加一层），或**调用前有必须先做的选择/选中动作**（要 `pre_call`），或官方实参里有本函数硬编码掉的 SafeArray 位 |
| **不能** | **形参本身**是 COM 对象 —— `Param` 没有「任意 COM 对象入参」这种通道，`inject` 也只给宿主对象 |

★ 返回值依据已逐条核对官方签名（`C:\swapi\types\`），未凭印象：见文末「核对到的官方返回类型」。

## 三、主表（本段 27 条）

| # | 函数名 | 定义行号 | 一句话用途 | 建/读 | 能否挂成 MCP 工具 | 若不能 / 需包装，卡在哪 |
|---|---|---|---|---|---|---|
| 1 | `create_standard_views` | 941 | 调 `IDrawingDoc.Create3rdAngleViews2(part_path)` 建第三角标准三视图 | 建 | **能** | 形参只有 `part_path`(str) + inject 的 `drawing_model`；官方返回 `bool`。⚠ **与 #2 功能重叠**（本条无 `projection`、无状态字典），挂工具时二者应只留一条 |
| 2 | `create_standard_views_with_projection` | 952 | 按 `projection` 选 `CreateFirstAngleViews2`/`Create3rdAngleViews2` 建原生三视图，返回 `status/error_code` 字典 | 建 | **能** | 形参全标量，返回 dict 可直接 JSON 化。⚠ 成员不存在时返回 `blocked` + `manual_review_required`（不是抛错） |
| 3 | `add_view` | 978 | 用 `CreateDrawViewFromModelView3` 按标准视图名建单个视图，可再设 `ScaleRatio` | 建 | **需包装** | 形参全标量可声明，但**官方返回 `View` COM 对象** ⇒ 返回值要证据化。官方 Remarks 另要求 `ViewName` **必须含星号**（`*Front`）、`ModelName` 须为带 `.sldprt`/`.sldasm` 的完整路径，**函数体两样都不校验** |
| 4 | `add_section_view` | 998 | 在「当前选中的剖切线」处调 `CreateSectionViewAt5` 建剖视图 | 建 | **需包装** | ① 官方 Remarks 原文：「Before calling this method, **select the section line** or lines to use as a section line.」⇒ 必须 `pre_call` 钩子先选中；② 官方第 6 参 `ExcludedComponents` 是 `System.object`（组件数组），**本函数硬编码传 `None`** 且形参里没有它 ⇒ SafeArray 位 `Param` 表达不了；③ 官方返回 Section view COM 对象 |
| 5 | `add_detail_view` | 1022 | 用 `CreateDetailViewAt4`（补齐官方 12 参）建局部放大视图 | 建 | **需包装** | 12 个实参全是标量（能声明），但官方返回 `System.object`（视图对象）⇒ 返回值需证据化。⚠ 函数自带来源块已写明「静态签名比对后修正，**未在本机实测**」 |
| 6 | `insert_dimensions` | 1079 | 激活一个视图后调 `InsertModelAnnotations4`（回退 `3`）插入模型尺寸，返回注释数组或 `False` | 建 | **需包装** | ① 官方返回 **IAnnotation 数组（SafeArray）**，不能直接当工具返回值，要转计数/名单；② 形参 `view` 是 COM 对象；③ ★ **形参 `view` 是死参数** —— 1079–1149 行内该标识符**只出现在 def 行与 docstring**，函数体从未引用（实测逐行匹配确认） |
| 7 | `_note_text` | 1151 | 读 `INote.GetText`，动态 COM 取不到时按 DISPID 2 兜底 | 读 | **不能** | 首参 `note` 是 COM 对象，`Param` 表达不了、`inject` 也不给任意对象 |
| 8 | `_note_annotation` | 1166 | 取 `INote` 对应的 `IAnnotation`，取不到时按 DISPID 85 兜底 | 读 | **不能** | 同上（COM 对象入参）。另：私有名 ⇒ `scripts/sw_drawing.py` 桥接**不导出**它（桥接只导出不以 `_` 开头的名字，`sw_drawing.py:27`），只能走 `extra_op` |
| 9 | `_set_annotation_position` | 1183 | 写 `IAnnotation.SetPosition2`，取不到时按 DISPID 91 兜底 | **写** | **不能** | 首参 `annotation` 是 COM 对象。★ 本段**唯一直接改文档坐标**的 helper（`add_note` 的内部步骤） |
| 10 | `_annotation_position` | 1201 | 回读 `IAnnotation.GetPosition` 的图纸坐标，取不到返回 `None` | 读 | **不能** | 首参 `annotation` 是 COM 对象 |
| 11 | `_note_box` | 1214 | 读 `INote.GetExtent`（DISPID 22）作为图纸空间范围，取不到退回 `_annotation_box` | 读 | **不能** | 两个形参 `note` / `annotation` **都是** COM 对象 |
| 12 | `_note_evidence` | 1228 | 组合 `_note_text` + `_annotation_position` + `_note_box` 产出注释证据 dict | 读 | **不能** | `note` 是 COM 对象（返回 dict 本身没问题，卡在入参） |
| 13 | `add_note` | 1238 | 插文字注释 → `SetPosition2` 定位 → 回读文字与坐标做验证，返回状态字典 | 建 | **能** | 形参 `x,y`(float) + `text`(str) 全标量，返回 dict 可 JSON 化。⚠ `x/y` 语义是**米**（图纸坐标），挂工具须按规则 2 在 `derived_args` 里换算为 `_mm` 对外 |
| 14 | `insert_bom_table` | 1326 | 走 `model.Extension.InsertBomTable4`（补齐官方 9 参）插 BOM 表 | 建 | **需包装** | 形参全标量可声明，但官方返回 **BOM table annotation（`System.object`）** ⇒ 返回值需证据化。⚠ 官方 `X`/`Y` 签名为 `System.int` 且**文档未注明单位**（本仓注释已按铁律 5 记「查不到」）⇒ 挂工具时单位标定悬空 |
| 15 | `set_sheet_format` | 1400 | 取当前页并 `ISheet.SetTemplateName` 换图框 | **写** | **能** | 形参 `format_path`(str) + inject 的 `drawing_model`，返回 `bool`。⚠ 改的是**当前活动页**，工具须声明 `idempotent=False` |
| 16 | `add_sheet` | 1411 | 调 `NewSheet4`（16 参）新建一张图纸页 | 建 | **能** | 16 个实参全是标量（`paper_size` int / `first_angle` bool / `template_path` str），官方返回 `System.bool` ⇒ 声明即可 |
| 17 | `add_a3_sheet` | 1426 | 先选本机 A3 图框（段 1 第 406 行 `select_drawing_template`）再建横向 A3 页，返回状态字典 | 建 | **能** | `template_candidates` 实为**路径字符串列表**（下游 `for raw_path in candidates` + `Path(raw_path)`，见 415–417 行）⇒ `Param(kind=list)` 可声明。⚠ 它把候选路径当用户入参，工具侧要决定收 list 还是收「本机扫描目录」 |
| 18 | `setup_current_sheet_as_a3` | 1453 | 用 `IDrawingDoc.SetupSheet6`（19 参）把**当前页**设为横向 A3，返回状态字典 | **写** | **能** | 19 个实参全是标量与字面量，返回 dict。⚠ `projection` 非法时是 `raise ValueError`（与 #17 的返回式失败不一致） |
| 19 | `get_all_views` | 1521 | 列当前页所有视图的 `name` / `type` / `ScaleRatio` | 读 | **能** | 只有宿主对象形参，返回 list-of-dict 可 JSON 化（`ScaleRatio` 是 COM 元组，json 会序列化成数组） |
| 20 | `_paper_size_from_template` | 1536 | 用正则从模板文件名猜标准图幅，猜不到返回 `None` | 读（**纯字符串，不碰 COM**） | **能** | 形参 `template_path`(str) 单标量，返回 `str|None` ⇒ **本段最容易挂的一个**。⚠ 但它是私有名 ⇒ 桥接不导出，要么工具层 `extra_op` 重写同样逻辑，要么先加公开包装（那是改文件，本任务不做） |
| 21 | `_table_cell_text` | 1556 | 按 `DisplayedText2→DisplayedText→Text2→Text` 顺序读表格单元格文字 | 读 | **不能** | 首参 `table`（`ITableAnnotation`）是 COM 对象 |
| 22 | `_table_evidence` | 1570 | 回读表格类型 / 行列数 / 全部单元格 / BOM 配置 / 边界 | 读 | **不能** | `table` 是 COM 对象（第 2 参 `sheet_name` 是 str，无问题）。产出已被 #27 吸收 ⇒ 单独暴露价值低 |
| 23 | `_annotation_text_parts` | 1605 | 用 `GetTextCount` + `GetTextAtIndex` 逐段读专业标注的可见文字 | 读 | **不能** | `annotation_owner` 是 COM 对象 |
| 24 | `_professional_annotation_record` | 1621 | 把「标注 owner + 种类 + 所属视图记录」拼成一条证据 dict | 读 | **不能** | `owner` 是 COM 对象（第 3 参 `view_record` 是 dict，本身可声明） |
| 25 | `_view_center_marks` | 1633 | 遍历视图中心标记链（`GetFirstCenterMark2`→`GetNext`，旧版回退 `GetCenterMarks`） | 读 | **不能** | `view` 是 COM 对象；且返回的是 **COM 对象列表**（不可 JSON 化）⇒ 即便包一层也必须先转成记录 |
| 26 | `_collect_view_professional_annotations` | 1653 | 按视图收集中心标记 / 中心线 / 基准标签 / 几何公差框 / 表面粗糙度 / 焊接符号 | 读 | **不能** | `view` 是 COM 对象。★ 它是 #27 的内核之一 ⇒ 不单独暴露，走 #27 |
| 27 | `inspect_drawing_structure` | 1707 | 遍历全部图纸页，读视图 / 尺寸 / 注释 / 表格 / 专业标注，产出结构审计报告（docstring 明写「不修改文档」） | 读 | **能（已挂）** | 形参 `paper_size_hint`(str) + `title_block_box`(dict，键 `left/bottom/right/top`) 都可声明。★ 证据：已接入 `mcp__solidworks__solidworks_inspect_drawing`（`mcp-server/server.py:104` 的 `drawing_inspect_structure` 映射，`:2228` 调用，**只传 `paper_size_hint`**）；另一处传 `title_block_box` 的调用点在 `generate_drawing_from_spec`（2254 行，**段 3**）。⚠ 现成工具走的是「按 `drawing_path` 自己开件 + 出预览 + 落盘 JSON」路线，**对当前已打开的图纸没有轻量读数** |

## 四、汇总

| 判定 | 条数 | 函数 |
|---|---|---|
| **能** | **10** | `create_standard_views` · `create_standard_views_with_projection` · `add_note` · `set_sheet_format` · `add_sheet` · `add_a3_sheet` · `setup_current_sheet_as_a3` · `get_all_views` · `_paper_size_from_template` · `inspect_drawing_structure` |
| **需包装** | **5** | `add_view` · `add_section_view` · `add_detail_view` · `insert_dimensions` · `insert_bom_table` |
| **不能** | **12** | `_note_text` · `_note_annotation` · `_set_annotation_position` · `_annotation_position` · `_note_box` · `_note_evidence` · `_table_cell_text` · `_table_evidence` · `_annotation_text_parts` · `_professional_annotation_record` · `_view_center_marks` · `_collect_view_professional_annotations` |

★ **12 条「不能」里有 11 条是下划线私有名** —— 它们在 `scripts/sw_drawing.py` 桥接下**根本取不到**（桥接只导出不以 `_` 开头的名字），所以「不能」有两层：**形参是 COM 对象** + **名字私有不导出**。这 11 条里有 8 条是纯读证据 helper，已被 #27 `inspect_drawing_structure` 吸收 ⇒ **不建议逐条暴露**，暴露点应当是 #27（以及 `auto_insert_center_marks`，1883 行，段 3）。

## 五、本段值得单独上报的三条事实

1. **`insert_dimensions` 的 `view` 形参是死参数**（1079 行定义，docstring 第 1084 行写「None 则标注所有视图」）—— 1079–1149 行内标识符 `view` **只出现在 def 行与 docstring**，函数体一次都没用到它。docstring 承诺的行为（指定视图 vs 全部视图）在实现里不存在。
2. **本段 5 条「需包装」全部卡在返回值，不是形参** —— `add_view` / `add_section_view` / `add_detail_view` / `insert_bom_table` 返回 COM 对象，`insert_dimensions` 返回 **SafeArray**。这类缺口用 `extra_op` 或再加一层证据回读就能解，不需要动形参。`add_section_view` 另有**官方硬前置**（必须先选中剖切线）+ **一个被硬编码掉的 SafeArray 形参位**（`ExcludedComponents`）。
3. **`create_standard_views`（941）与 `create_standard_views_with_projection`（952）是同一件事的两条实现** —— 前者无投影法参数、无状态字典，后者有。挂工具时两条同时暴露会造成能力重复。

## 六、核对到的官方返回类型（本段的判断依据，未凭印象）

| 官方成员 | 官方文档 | 文件 |
|---|---|---|
| `IDrawingDoc.Create3rdAngleViews2` | `System.bool` / 「True if successful, false if not」 | `C:\swapi\types\IDrawingDoc\Create3rdAngleViews2.md` |
| `IDrawingDoc.CreateDrawViewFromModelView3` | 返回 `View`（新建物体的指针）；Remarks：`ViewName` 必须含星号 | `C:\swapi\types\IDrawingDoc\CreateDrawViewFromModelView3.md` |
| `IDrawingDoc.CreateSectionViewAt5` | 返回 Section view；Remarks：调用前必须先选中剖切线；`ExcludedComponents` 为 `System.object` 组件数组 | `C:\swapi\types\IDrawingDoc\CreateSectionViewAt5.md` |
| `IDrawingDoc.CreateDetailViewAt4` | 返回 `System.object`（12 参） | `C:\swapi\types\IDrawingDoc\CreateDetailViewAt4.md` |
| `IDrawingDoc.NewSheet4` | 返回 `System.bool`（16 参） | `C:\swapi\types\IDrawingDoc\NewSheet4.md` |
| `IModelDocExtension.InsertBomTable4` | 返回「BOM table annotation」，签名 `System.object`（9 参） | `C:\swapi\types\IModelDocExtension\InsertBomTable4.md` |
| `ToolSpec.Param` / `ToolSpec.inject` / `pre_call` / `derived_args` / `extra_op` | 本仓声明模型 | `mcp-server/tool_registry.py:217-318` |

★ **查不到、故未下断言的项**：`add_section_view` / `add_detail_view` 的 `x`、`y` 参数**单位**，官方参数说明未写、本文件 docstring 也未写 ⇒ 挂工具前需要单独查证（对比：`add_view` 的 `LocX/LocY` 官方明确写 "in meters"）。

★ 本次**只读**：未修改任何已有文件，未启动 SolidWorks，未运行 pytest。
