# 扫描 S3-3 · subskill 函数能力盘点（第 3 段）

**扫描对象**：`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`
**文件实测行数**：2746 行
**扫描性质**：★ **只读静态扫描** —— 未运行 SolidWorks、未跑 pytest、未修改任何既有文件

---

## 一、我的段落边界（以实际读到的 `def` 行号为准）

| 项 | 值 |
|---|---|
| 派工的名义边界 | 约第 1831–2746 行 |
| 名义起点 1831 落在谁身上 | 第 **1707** 行 `inspect_drawing_structure` 的**函数体内部**（该函数跨 1707–1881 行）⇒ 起点不落在任何 `def` 上 |
| 紧随 1831 之后的**第一个** `def` | 第 **1883** 行 `auto_insert_center_marks` |
| 本段之前最后一个 `def` | 第 **1707** 行 `inspect_drawing_structure`（属 S3-2） |
| ★ 本段实际覆盖 | **第 1883 – 2746 行**（以 `def` 行为界；文件末尾即 2746 行，末个 `def` 在 2743） |
| ★ 本段 `def` 数量 | **32**（**全部是顶层 `def`，本段内无嵌套 `def`**） |
| 段内模块级常量（非 `def`，不计） | `SUPPORTED_SECTION_PROPERTIES`@2616、`MODEL_VIEW_MANAGER_UI_MEMBERS`@2692 |

> 本段 32 个 `def` 的行号（按序）：
> 1883, 1996, 2042, 2094, 2169, 2306, 2351, 2358, 2370, 2377, 2384, 2390, 2418, 2425, 2432, 2439, 2446, 2453, 2460, 2468, 2489, 2496, 2503, 2533, 2540, 2648, 2656, 2710, 2718, 2729, 2737, 2743。
> 边界缺口：**1707–1881 行（`inspect_drawing_structure` 的后半段）属于 S3-2**，本段不重复计。

---

## 二、判定「能否挂成 MCP 工具」的依据（全部逐行核过源码，不是印象）

| 依据 | 源码位置 | 含义 |
|---|---|---|
| `Param` 只有 5 个字段：`name / kind / default / description / required` | `mcp-server/tool_registry.py:217-236` | 形参类型只能是**能被 MCP 客户端 JSON 序列化的类型**（实践 `str`/`float`/`int`/`bool`/`list`/`dict`）。**COM 对象不在其中** |
| `p.kind` 直接进 Pydantic 注解 | `tool_registry.py:228-229`、`:462-465` | 同上 |
| **注入解析器是一张固定表** `RESOLVERS`，当前键只有 6 个 | `mcp-server/register_capabilities.py:112-137` | 可用注入名 = `model` / `sw_app` / `study` / `asm_model` / `manager` / **`drawing_model`** |
| ★★ **`drawing_model` 已是已注册注入名** | `register_capabilities.py:136`（`"drawing_model": resolve_model`） | ⇒ 本段所有首参叫 `drawing_model` 的函数**可直挂**（`inject="drawing_model"`）。**这一条修正了 S3-1 第 31 行的说法**（那里写「注入名得改成约定名 `model`」）—— 事实是该行**早已存在** |
| 注入是**单值**：`inject: str = ""`；注入键字面等于 `inject`（`register()` 不往下传 `inject_as`） | `tool_registry.py:308`、`:507`、`:559`；`register_capabilities.py:127-128` | ⇒ **一个工具只能注入一个宿主对象**，形参里要第二个 COM 宿主对象就走不通 |
| 返回值**必须能 JSON 化**：`_result()` 对 JSON 走 `json.dumps(payload)`；对 markdown 走 `payload.get('status','result')` | `mcp-server/server.py:1001-1014`；异常被 `:1041` 吞成 `_tool_error` | ⇒ 返回 **COM 对象** ⇒ `TypeError: not JSON serializable` ⇒ **工具报 error**；返回 `bool`/`str`/`int` ⇒ **markdown 格式必炸**（`'bool' object has no attribute 'get'`），JSON 格式侥幸能过 |
| 规则 3 门禁：裸坐标名 `{"x","y","z","point","coordinate"}` + 结构判据 `_looks_like_coord_component` | `tool_registry.py:93`、`:96`、`:379-383` | ⇒ 形参名命中即 **GateError**，声明都过不了 |
| 规则 2 长度门禁：`("radius","diameter","depth","thickness","distance","width","height","length","offset","spacing","pitch")` 必须以 `_mm` 结尾（`bool` 除外） | `tool_registry.py:147-150`、`:410-420` | ⇒ 命中即 GateError，除非改名或进 `_LEN_SUFFIX_EXEMPT` |
| 规则 2 角度门禁：`("angle","degrees","draft")` 必须以 `_deg` 结尾 | `tool_registry.py:158`、`:423-431` | ★ **本段 32 个函数没有任何形参命中**（已逐名核对） |
| `param_alias` 改的是**对外名 → 目标形参名** | `tool_registry.py:271-277`、`:494-498` | ⇒ ★ **能绕开命名门禁**：声明 `Param("x_mm", float)` + `param_alias={"x_mm":"x"}`，门禁查的是对外名 `x_mm`（不命中黑名单），调用时传 `x=` |
| `omitted_params` 可显式声明「故意不暴露」某形参 | `tool_registry.py:291`、`:299-300` | ⇒ 形参对象可被有意省略（且必须显式，省略与漏抄可区分） |
| 挂载路径：父目录名 `solidworks-engineering-drawing` **带连字符**（非合法标识符），`module=` 走 `__import__("scripts.%s" % module)` | `tool_registry.py:524`；`register_capabilities.py:129-130` | ⇒ **不能** `module="solidworks-engineering-drawing.scripts.drawing_workflow"`；须走 `scripts/sw_drawing.py`（按路径 `spec_from_file_location` 加载后逐个导出公开名）|
| 当前注册面 | `grep drawing_workflow mcp-server/*.py` → 2 处命中，**均为注释引用**（`tool_specs_batch19.py:7` 指向第 1707 行 `inspect_drawing_structure`，`register_capabilities.py:125` 是来源说明） | ⇒ ★ **本段 32 个函数目前一个都没有挂成 MCP 工具** |

**一句话判据**：形参若是「COM 对象 / SafeArray / 回调用法」且**不是** `RESOLVERS` 里已有的注入名 ⇒ `Param` 表达不了 ⇒ **不能**；形参能挂但**返回值不是 dict**（COM 对象 / 标量）或**形参名过不了规则 2/3 门禁** ⇒ **需包装**；其余 ⇒ **能挂**。

---

## 三、第 3 段逐个 `def` 盘点（32 条）

| # | 函数名 | 行号 | 一句话用途 | 建 / 读 | 能否挂成 MCP 工具 | 若不能，卡在哪 |
|---|---|---|---|---|---|---|
| 1 | `auto_insert_center_marks` | 1883 | 按需求列表给每个标准视图自动插中心标记，并以「中心标记实体数」前后对比作成功判据 | **建**（`AutoInsertCenterMarks2`）+ 读（`_view_center_marks` 回读） | **能** | — |
| 2 | `export_sheet_to_pdf` | 1996 | 把工程图导出为 PDF（可指定图纸页） | **建**（写文件） | **需包装** | ① 形参 `sw_app` 是**第二个宿主对象**，而 `inject` 是单值 `str`（`tool_registry.py:308`、`:507`）⇒ 只能走 `omitted_params=["sw_app"]`（函数内会自己 `GetActiveObject`）；② **返回 `bool` 不是 dict** ⇒ markdown 响应格式必炸（`server.py:1005` 调 `payload.get`） |
| 3 | `setup_current_sheet` | 2042 | 按图幅 + 投影法 + GB/T 模板配置当前图纸页（`SetupSheet6`，17 参）并回读配置证据 | **建** + 读 | **能** | — |
| 4 | `validate_generic_drawing_generation` | 2094 | 纯 Python 前置校验：列出通用生成器无法可靠执行的 DrawingSpec 字段 | 读（纯计算，**零 COM**） | **能** | — |
| 5 | `generate_drawing_from_spec` | 2169 | 按已校验 DrawingSpec 串起「图幅 → 布局 → 三视图 → 中心标记 → 尺寸 → BOM → 备注 → 结构复核」全流程 | **建** | **能** | — |
| 6 | `insert_table_annotation` | 2306 | 在图纸坐标插入表注解；给了 `template` 走 7 参 `InsertTableAnnotation2`，否则走 5 参 `InsertTableAnnotation` | **建** | **需包装** | ① 形参 `x`/`y` 命中 `_BARE_COORD_NAMES`（`tool_registry.py:93`、`:379`）⇒ **GateError**，须经 `param_alias` 改成 `_mm` 名并做单位换算（图纸坐标是**米**）；② **返回 COM 对象**（表注解）⇒ json 序列化必失败；③ `table_type` 的枚举**两套官方源都查不到**（本文件 2300-2302 行自己写明）⇒ 该形参只能透传，`Param.description` 须如实标注 |
| 7 | `read_table_text` | 2351 | 读表内一格文本 | 读 | **不能** | 形参 `table` 是 **COM 对象**（`ITableAnnotation`），且 `RESOLVERS` 无对应注入名 |
| 8 | `get_table_shape` | 2358 | 回读表的行列数、锚定状态与锚点类型 | 读 | **不能** | 同 #7 |
| 9 | `set_table_row_hidden` | 2370 | 显隐表某一行 | **建** | **不能** | 同 #7 |
| 10 | `set_table_column_hidden` | 2377 | 显隐表某一列 | **建** | **不能** | 同 #7 |
| 11 | `delete_table_row` | 2384 | 删除表某一行 | **建** | **不能** | 同 #7 |
| 12 | `delete_table_column` | 2390 | 删除表某一列 | **建** | **不能** | 同 #7 |
| 13 | `get_general_table` | 2418 | 取通用表的底层表对象（`GeneralTable` 属性） | 读 | **不能** | 形参 `table` 是 COM 对象；且**返回 COM 对象** |
| 14 | `get_hole_table` | 2425 | 取孔表的底层表对象（`HoleTable` 属性） | 读 | **不能** | 同 #13 |
| 15 | `get_bend_table` | 2432 | 取折弯表的底层表对象（`BendTable` 属性） | 读 | **不能** | 同 #13 |
| 16 | `get_weldment_cutlist_table` | 2439 | 取焊接下料表的底层表对象（`WeldmentCutListFeature` 属性） | 读 | **不能** | 同 #13 |
| 17 | `get_revision_table_feature` | 2446 | 取修订表的底层表对象（`RevisionTableFeature` 属性） | 读 | **不能** | 同 #13 |
| 18 | `get_table_custom_property_column` | 2453 | 读表的自定义属性列名（5 个表族共有成员） | 读 | **不能** | 形参 `table` 是 COM 对象 |
| 19 | `set_table_custom_property_column` | 2460 | 设表的自定义属性列名 | **建** | **不能** | 同 #18 |
| 20 | `sort_table` | 2468 | 表排序（孔表/通用表/焊接下料表/修订表族共有 `Sort(Int32, Boolean)`） | **建** | **不能** | 形参 `table` 是 COM 对象；另 `option` 的枚举口径**本文件未给**（2468-2470 只写「共有 Sort」）⇒ 挂工具时须先查到枚举值表，否则只能原样透传 |
| 21 | `add_revision` | 2489 | 给修订表新增一个修订号，返回官方给出的行号 | **建** | **不能** | 形参 `revision_table` 是 COM 对象；且**返回 `int` 不是 dict** ⇒ markdown 格式必炸 |
| 22 | `delete_revision` | 2496 | 按行号删除修订号 | **建** | **不能** | 同 #21（返回 `bool`） |
| 23 | `get_current_revision` | 2503 | 读当前修订号 | 读 | **不能** | 形参 `revision_table` 是 COM 对象；返回 `str` 同 #21 的格式问题 |
| 24 | `get_section_view_data` | 2533 | 取剖视图的定义对象 `ISectionViewData` | 读 | **不能** | 形参 `section_view` 是 COM 对象；且**返回 COM 对象** |
| 25 | `set_section_style` | 2540 | 逐项设置剖视显示样式（14 个可选 keyword-only 属性，只设显式给值的） | **建** | **不能** | 形参 `section_data` 是 COM 对象（`ISectionViewData`）。⚠ 附带：`first_offset`/`second_offset`/`third_offset` 三个形参名含 `offset` ⇒ 即使解决了 COM 形参，**仍会被规则 2 长度门禁拦**（`tool_registry.py:149`、`:410-420`）；`first_color`/`second_color`/`third_color` 是颜色索引不是长度，本文件未自述其单位 |
| 26 | `activate_annotation_view` | 2648 | 激活注释视图（可选同时重定向） | **建** | **不能** | 形参 `annotation_view` 是 COM 对象（`IAnnotationView`） |
| 27 | `get_annotation_view_evidence` | 2656 | 回读注释视图状态（显示与否、注释数、2D/展开/未分配标记、水平夹角） | 读 | **不能** | 形参 `annotation_view` 是 COM 对象。★ 它的**返回形状已是证据 dict**（天然 JSON 友好）⇒ 只差一个「从图纸里定位并取回注释视图」的入口 |
| 28 | `get_model_view_manager` | 2710 | 取 `IModelViewManager`（是属性，不是方法） | 读 | **需包装** | 首参 `model` 可注入；但**返回 COM 对象** ⇒ 须包一层「取到后回读某个标量/布尔证据」的包装，否则 json 序列化失败 |
| 29 | `create_section_view_data` | 2718 | 创建剖视定义对象 `ISectionViewData`（0 参） | **建** | **需包装** | 同 #28：**返回 COM 对象** |
| 30 | `create_feature_manager_section_view` | 2729 | 用 FeatureManager 路径创建剖视 | **建** | **不能** | 首参 `model` 可注入，但**第二形参 `section_data` 是 COM 对象**，而 `inject` 是单值 ⇒ 表达不了 |
| 31 | `get_feature_manager_section_data` | 2737 | 按名字取剖视定义对象 | 读 | **需包装** | 形参都能挂（`model` + `name`），但**返回 COM 对象** ⇒ 同 #28 |
| 32 | `remove_feature_manager_section_view` | 2743 | 删除当前剖视（0 参） | **建** | **需包装** | 形参层面无障碍（首参 `model` 可注入、其余无参）；**返回 `bool` 不是 dict** ⇒ markdown 响应格式必炸（`server.py:1005`），须包成 `{"status":..., "removed":...}` |

---

## 四、本段小结（可核对的事实）

| 分类 | 个数 | 函数名（行号） |
|---|---|---|
| **能挂**（形参可注入或全是标量、返回值是 dict、命名过得了规则 2/3 门禁） | **4** | `auto_insert_center_marks`@1883、`setup_current_sheet`@2042、`validate_generic_drawing_generation`@2094、`generate_drawing_from_spec`@2169 |
| **需包装**（形参可挂，但返回值不是 dict / 有门禁命名冲突 / 双宿主注入） | **6** | `export_sheet_to_pdf`@1996、`insert_table_annotation`@2306、`get_model_view_manager`@2710、`create_section_view_data`@2718、`get_feature_manager_section_data`@2737、`remove_feature_manager_section_view`@2743 |
| **不能** · 形参含 COM 对象且不在 `RESOLVERS` 里 | **22** | `read_table_text`@2351、`get_table_shape`@2358、`set_table_row_hidden`@2370、`set_table_column_hidden`@2377、`delete_table_row`@2384、`delete_table_column`@2390、`get_general_table`@2418、`get_hole_table`@2425、`get_bend_table`@2432、`get_weldment_cutlist_table`@2439、`get_revision_table_feature`@2446、`get_table_custom_property_column`@2453、`set_table_custom_property_column`@2460、`sort_table`@2468、`add_revision`@2489、`delete_revision`@2496、`get_current_revision`@2503、`get_section_view_data`@2533、`set_section_style`@2540、`activate_annotation_view`@2648、`get_annotation_view_evidence`@2656、`create_feature_manager_section_view`@2729 |
| **合计** | **32** | 4 + 6 + 22 = 32 ✓ |

- **建 / 读分布**：**建** 18 个、**读** 14 个，合计 32。
  - 建：`auto_insert_center_marks`、`export_sheet_to_pdf`、`setup_current_sheet`、`generate_drawing_from_spec`、`insert_table_annotation`、`set_table_row_hidden`、`set_table_column_hidden`、`delete_table_row`、`delete_table_column`、`set_table_custom_property_column`、`sort_table`、`add_revision`、`delete_revision`、`set_section_style`、`activate_annotation_view`、`create_section_view_data`、`create_feature_manager_section_view`、`remove_feature_manager_section_view`
  - 读：`validate_generic_drawing_generation`、`read_table_text`、`get_table_shape`、`get_general_table`、`get_hole_table`、`get_bend_table`、`get_weldment_cutlist_table`、`get_revision_table_feature`、`get_table_custom_property_column`、`get_current_revision`、`get_section_view_data`、`get_annotation_view_evidence`、`get_model_view_manager`、`get_feature_manager_section_data`
- **22 个「不能」的共性**：全部形参是**已从图纸上取回、但无法跨工具调用传递的 COM 对象**（表注解 12 个 / 修订表 3 个 / 剖视相关 4 个 / 注释视图 2 个 / `IModelViewManager` 侧 1 个）。
  ⇒ **要挂这一族，先决条件不是写 `ToolSpec`，而是先有一个「按声明式选择器从活动图纸定位并取回该对象」的解析器**（往 `register_capabilities.py:112-137` 的 `RESOLVERS` 加键）。
  ★ **其中 4 个的形参是可从纯字符串推出来的**（表注解、修订表），值得优先：`insert_table_annotation` 已能建表 ⇒ 只需配「按图纸页 + 位置取回刚建的表」这一步，就能把 #7–#20、#21–#23 全部解锁。
  ★ **`get_annotation_view_evidence`@2656 与 `get_section_view_data`@2533 的返回形状本来就可 JSON 化** ⇒ 解锁后**不必**再包证据层。
- **`SUPPORTED_SECTION_PROPERTIES`@2616 / `MODEL_VIEW_MANAGER_UI_MEMBERS`@2692 是模块级常量、不是 `def`**，按派工口径不计入 32 条；两者分别是「`set_section_style` 支持的属性名白名单（33 项，超出该函数实际设置的 14 项）」与「`IModelViewManager` 42 成员中本项目**刻意不封装**的 36 项名单」。

---

## 五、本段未查到 / 不做的判断

- **`sort_table` 的 `option` 枚举值**：本文件 2468-2470 只写「共有 `Sort(Int32, Boolean)`」，未给 `Int32` 的取值表 ⇒ **查不到**，不下断言。
- **`insert_table_annotation` 的 `table_type` 枚举**：本文件 2300-2302 行自己写明「其枚举在两套官方源里都查不到（`sw_know` 检索无对应枚举定义）」⇒ **查不到**，只透传。
- **`Text` / `DisplayedText` 的下标是 0 基还是 1 基**：本文件 2346-2347 行写明两套官方源都未说明 ⇒ **查不到**，函数按原样透传。
- **修订号字符串的格式（GB/T 的 A/B/C 还是 1/2/3）**：本文件 2484-2485 行写明两套官方源都未说明 ⇒ **查不到**。
- **各函数在真机上的实测状态**：**未查**（本次只读静态扫描，不跑 SolidWorks、不跑 pytest）⇒ ★ 本文件不对任何函数写「已验证 / 已跑通」。
- **`Param.kind` 填 `list` / `dict` 时本仓库门禁是否放行**：与 S3-1 同一处，**未查到**显式规则；本文件只按「能被 MCP 客户端 JSON 序列化」这一层判断，**未断言** Pydantic 侧一定通过。
- **「22 个不能」是否已被 `scripts/sw_drawing.py` 的转发导出解决**：**未查** —— 已确认该文件只做「按路径加载 + 导出公开名」（`scripts/sw_drawing.py:17-28`），**没有**任何把 COM 对象跨工具调用传递的机制。

---

## 六、给 Lead 的两条跨段提示

1. ★ **`drawing_model` 已是可用注入名**（`register_capabilities.py:136`，键存在且复用 `resolve_model`）⇒ **S3-1 第 31 行 / #6 / #24 的「注入名得改成约定名 `model`」这一条已被仓库自身解决**；S3-1 的 #6 / #24 因此可以从「需包装」上调。
2. ★ **`Param.kind` 的字段注释只写了「`str`/`float`/`int`/`bool`」**（`tool_registry.py:222`），而本段有 3 个函数的形参天然是 `list` / `dict`（`template_candidates`、`sheet_names`、`spec`、`requirements`）⇒ **要挂这 4 个函数，得先确认门禁对 `list`/`dict` 的口径**（S3-1 已提出同一处未查，本段仍未查到）。
