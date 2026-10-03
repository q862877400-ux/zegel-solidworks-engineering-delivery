# 扫描 S3-1 · subskill 函数能力盘点（第 1 段）

**扫描对象**：`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`
**文件实测行数**：2746 行（`Get-Content .Count`）
**文件实测 `def` 数**：83（含私有与嵌套，`grep '^\s*def\s+\w+'`）

---

## 一、我的段落边界（以实际读到的 `def` 行号为准）

| 项 | 值 |
|---|---|
| 三等分名义边界 | 2746 / 3 = 915.33 ⇒ 第 1 段名义 1–915 行 |
| 落在名义边界内的**最后一个** `def` | 第 **806** 行 `create_adaptive_standard_views` |
| 紧随其后的**第一个** `def` | 第 **941** 行 `create_standard_views` |
| ★ 本段实际覆盖 | **第 1 – 940 行**（以 `def` 行为界，止于下一个 `def` 之前） |
| 第 2 段起点 | 第 941 行 |
| ★ 本段 `def` 数量 | **24**（21 个顶层 + 3 个嵌套） |

> 本段 24 个 `def` 的行号：102, 113, 122, 148, 154, 166, 275, 286, 313, **348**(嵌套), 406, 453, **548**(嵌套), 590, 596, 631, 650, 661, 678, **694**(嵌套), 738, 755, 790, 806。

---

## 二、判定「能否挂成 MCP 工具」的依据（已核对注册器源码）

依据来自 `mcp-server/tool_registry.py` 实读，不是印象：

| 依据 | 源码位置 | 含义 |
|---|---|---|
| `Param.kind` 直接进 Pydantic 注解 | `tool_registry.py:228-232`（`kind: type`）、`:463-465`（`fields[p.name] = (p.kind, Field(...))`） | 入参类型只能是**可被 MCP 客户端 JSON 序列化的类型**（实践中 `str` / `float` / `int` / `bool`） |
| `inject` 只能注一个宿主对象，且注入关键字名必须等于目标函数真实形参名 | `tool_registry.py:268-269`、`:499-507` | 形参名 `drawing_model` 若要靠注入，注入名得**改**成约定名 `model`，或走 `extra_op` |
| `derived_args` 是 `lambda params: {...}`，只产出**一个**实参 | `tool_registry.py:278-282`、`:514-520` | 可包装「要一个 dict/list 当实参」的函数，**但一次只补一个** |
| 规则 2 门禁：名字命中 `_LEN_WORDS`（含 `spacing`/`width`/`height`/`distance`…）必须以 `_mm` 结尾 | `tool_registry.py:147-150`、`:412-420` | 本模块通篇用**米**的 `_m` 后缀 ⇒ 这类形参会**被门禁当场拦下**，需改名或进 `_LEN_SUFFIX_EXEMPT` |
| 规则 3 门禁：`x`/`y`/`z`/`point`/`coordinate` 等裸坐标名直接 `GateError`；`selection` 必须是 `str` | `tool_registry.py:93`、`:379-400` | 本段函数**均无**裸 `x`/`y` 形参（唯一坐标类形参 `model_size_m` / `center` / `title_block_*` 都是整体量或整体点，不是分量） |
| `omitted_params` 存在 | `tool_registry.py:291`、`:315` | 形参**对象**被有意省略时，可声明为不暴露 |

**一句话判据**：形参若是「COM 对象 / VARIANT / SafeArray / `*args` 回调用法」而**不是**注入的宿主对象 ⇒ `Param` 表达不了 ⇒ 不能直接挂。

---

## 三、第 1 段逐个 `def` 盘点（24 条）

| # | 函数名 | 行号 | 一句话用途 | 建 / 读 | 能否挂成 MCP 工具 | 若不能，卡在哪 |
|---|---|---|---|---|---|---|
| 1 | `_safe_member` | 102 | 读任一 COM 成员，抛异常或返回 None 时一律吞掉换成 `default` | 读 | **不能** | 形参 `obj` 是**任意 COM 对象**（`Param` 无对应类型）；且它只是防御性 helper，单独暴露成工具没有意义 |
| 2 | `_as_sequence` | 113 | 把 COM 数组 / tuple / 单对象统一成 list | 读（纯数据整理） | **不能** | 形参 `value` 可能是 COM 数组（SafeArray）；纯 helper 无外部语义 |
| 3 | `_normalise_box` | 122 | 把 COM `Outline`/`GetBox` 数组或 dict 统一成 `{left,bottom,right,top}` | 读（纯数据整理） | **不能** | 同上：`value` 可为 COM 数组；helper 无外部语义 |
| 4 | `_annotation_box` | 148 | 取注解（`GetAnnotation`）的二维包围盒并归一化 | 读 | **不能** | 形参 `owner` 是尺寸/注释/表格注解 COM 对象 |
| 5 | `_view_display_dimensions` | 154 | 兼容数组接口与 `GetFirstDisplayDimension5` 链，取视图里全部真实 `DisplayDimension` | 读 | **不能** | 形参 `view` 是 `IView` COM 对象；返回 COM 对象数组（工具只能返 JSON） |
| 6 | `auto_arrange_drawing_dimensions` | 166 | 逐页逐视图选中全部尺寸注解，调官方 `IModelDocExtension.AlignDimensions` 按模式与间距自动排列 | **建**（改图纸） | **能（需包装）** | 形参本身只有 `drawing_model`（可 `inject="model"`，但注入关键字名须为 `model`，需 `param_alias`/改包装层形参名）+ 两个标量 ⇒ **形参层面无障碍**。卡点两条：① `spacing_m` 命中 `_LEN_WORDS` 里的 `spacing` 而不以 `_mm` 结尾 ⇒ **过不了规则 2 门禁**（需改名或进豁免表）；② `mode` 是字符串枚举，须在 `Param.description` 里写全 8 个合法值 |
| 7 | `_finite_positive` | 275 | 把 COM 数值转成有限正数，失败则回落到保守默认值并回报是否有效 | 读（纯计算） | **不能** | 内部 helper；返回 `(值, bool)` 元组，非 JSON 友好契约 |
| 8 | `_dimension_text_evidence` | 286 | 收集尺寸的前缀/后缀/标注文本片段；缺主值时用保守占位，不伪造格式化文本 | 读 | **不能** | 形参 `display_dimension` 是 `IDisplayDimension` COM 对象 |
| 9 | `estimate_dimension_text_box` | 313 | 用 `IAnnotation` 锚点 + `ITextFormat` 字高保守估算尺寸文字的轴对齐外接方框（标 `source=estimated`） | 读 | **需包装** | 形参 `display_dimension` 是 **COM 对象**（需用声明式 `selection: str` 先选中、再靠 `derived_args` 补成实参）；另 `padding_m` 名字含长度语义但不在 `_LEN_WORDS`，规则 2 门禁**不会拦**，但与本模块 `_m` 口径需自述一致 |
| 10 | `line_units` | 348 | 估算单行字宽（全角按 1 字高、半角按 0.62 字高） | 读（纯计算） | **不能** | **嵌套**在 `estimate_dimension_text_box` 内部，不是模块级 API；形参 `line` 为字符串片段，单独暴露无意义 |
| 11 | `select_drawing_template` | 406 | 按图幅 + GB/T 标识 + 本地化字样给本机 `.slddrt` 候选打分，选出图框模板路径 | 读（文件系统） | **能** | **本段唯一形参完全可挂的函数**：全部形参是 `candidates`（路径串列表）+ `paper_size`/`require_gbt` 三个标量，无 COM 对象。唯一待办：确认 `Param.kind` 用 `List[str]` 时 Pydantic 可用（本仓库既有惯例是重复成多个标量入参或走 `derived_args`） |
| 12 | `plan_standard_view_layout` | 453 | 纯算术：按图幅、投影法、模型外形、标题栏尺寸算出三视图中心点与比例，且不侵入标题栏 | 读（纯计算） | **需包装** | 形参全是标量/元组 ⇒ **本身能挂**；卡在门禁：`title_block_width_m` / `title_block_height_m` 命中 `_LEN_WORDS` 里的 `width`/`height` 而不以 `_mm` 结尾 ⇒ **规则 2 必拦**；`requested_scale` 接受 `str("1:2")` 或 `float` 两种量纲 ⇒ 需拆成两个互斥入参或 `extra_op` |
| 13 | `view_record` | 548 | 生成单个视图的中心点与边界框记录 | 读（纯数据） | **不能** | **嵌套**在 `plan_standard_view_layout` 内部 |
| 14 | `_scale_ratio` | 590 | 用 `Fraction.limit_denominator(1000)` 把浮点比例压成 SolidWorks 认的整数比 | 读（纯计算） | **不能** | helper；返回 tuple，非工具契约 |
| 15 | `_apply_view_layout` | 596 | 把已建视图移到规划中心并设独立比例，随后**回读**位置做一致性校验（不一致抛错） | **建**（改视图） | **需包装** | 形参 `view`（COM 对象）、`item`（dict）、`numerator`/`denominator`（int）⇒ `Param` 只能覆盖后三者；且 `item` 需由 `layout` 派生 ⇒ 要 `derived_args` |
| 16 | `_normalise_orientation` | 631 | 把 SolidWorks 视图方向名（中英）归一成 `front`/`top`/`right` 键 | 读（纯字符串） | **不能** | 内部 helper，`aliases` 映射不应对外暴露为工具 |
| 17 | `_view_position` | 650 | 读工程图视图中心位置（float, float）或 None | 读 | **不能** | 形参 `view` 是 COM 对象 |
| 18 | `_set_view_center` | 661 | 移动视图中心并回读校验，供按真实包围盒二次排布复用 | **建**（改视图） | **需包装** | 形参 `view`（COM）、`center`（list[float]，MCP 客户端能传但形参名 `center` 需按规则 3 自述为「整体点」）；核心动作 `SetViewPosition` 在模块内，未在 MCP 工具面上暴露 |
| 19 | `_refine_standard_view_spacing` | 678 | 按 SolidWorks **实际** `GetOutline` 包围盒二次排布，消除三视图间确认重叠 | **建**（改视图） | **需包装** | 形参 `view_objects`（dict[str, IView] COM 对象）与 `view_records`（list[dict]）⇒ 两者都不是 `Param` 能表达的标量；内部还调用 COM 写操作 |
| 20 | `move_if_needed` | 694 | 沿某轴把视图移到目标值，回读新中心并更新边界盒记录 | **建**（改视图） | **不能** | **嵌套**在 `_refine_standard_view_spacing` 内部，闭包捕获 `boxes`/`records` |
| 21 | `_collect_drawing_views` | 738 | 同时走 `Sheet.GetViews` 与 `GetFirstView`→`GetNextView` 链，取出真实模型视图列表 | 读 | **不能** | 形参 `drawing_model` 可注入，但返回 **COM 对象列表**（工具只能返 JSON）⇒ 必须再配一层「解析成 JSON」的包装函数 |
| 22 | `_map_native_standard_views` | 755 | 依据方向名、基准视图关系与原始位置，把一堆视图映射成第三角三视图 | 读 | **不能** | 形参 `views`（COM 对象列表）；返回 `(dict[orientation→COM对象], diagnostics, str)` 三元组，其中含 COM 对象 |
| 23 | `_map_standard_views_from_sheet_views` | 790 | 从整张图纸全部视图里筛出前/俯/右三个标准视图并映射 | 读 | **不能** | 形参 `sheet_views`（COM 对象列表）；委托给 `_map_native_standard_views`，返回同样含 COM 对象 |
| 24 | `create_adaptive_standard_views` | 806 | 按预先算好的布局创建前/俯/右三视图；`CreateDrawViewFromModelView3` 失败时回退到 `CreateFirstAngleViews2`/`Create3rdAngleViews2`，再按投影法重定位 + 二次排布 + 回读 | **建**（改图纸） | **能（需包装）** | 形参 `drawing_model`（可 `inject="model"`）+ `part_path`(str) + `layout`(dict) ⇒ 形参层面可包装（`layout` 走 `derived_args`，或退化为直接接 `plan_standard_view_layout` 的输出）。⚠ 它返回的 dict 里嵌的是 **回读后的视图记录**（纯数据，可 JSON 化）⇒ 这一点有利。真正卡点是**它需要前一步 `plan_standard_view_layout` 的产物作为实参**，单挂一个工具会让调用方无法自洽 ⇒ 建议与 #12 合并成一个 `solidworks_create_standard_views` |

---

## 四、本段小结（可核对的事实）

| 分类 | 个数 | 函数名 |
|---|---|---|
| **能直接挂**（形参全是标量 / 字符串 / 列表） | **1** | `select_drawing_template` |
| **需包装**（形参含 COM 对象或 dict 实参，但可经 `inject` + `derived_args` / `extra_op` 解决） | **4** | `auto_arrange_drawing_dimensions`、`estimate_dimension_text_box`、`plan_standard_view_layout`、`create_adaptive_standard_views` |
| **不能** · 嵌套 `def`（闭包内函数，不可独立成工具） | **3** | `line_units`@348、`view_record`@548、`move_if_needed`@694 |
| **不能** · 顶层但形参含 COM 对象 / SafeArray / COM 对象列表，或返回值含 COM 对象 | **16** | `_safe_member`、`_as_sequence`、`_normalise_box`、`_annotation_box`、`_view_display_dimensions`、`_finite_positive`、`_dimension_text_evidence`、`_scale_ratio`、`_apply_view_layout`、`_normalise_orientation`、`_view_position`、`_set_view_center`、`_refine_standard_view_spacing`、`_collect_drawing_views`、`_map_native_standard_views`、`_map_standard_views_from_sheet_views` |
| **合计** | **24** | 1 + 4 + 3 + 16 = 24 ✓ |

- **建 / 读分布**：**建** 6 个（#6 `auto_arrange_drawing_dimensions` · #15 `_apply_view_layout` · #18 `_set_view_center` · #19 `_refine_standard_view_spacing` · #20 `move_if_needed` · #24 `create_adaptive_standard_views`），**读 / 纯计算** 18 个，合计 24。
- **当前 MCP 注册面**：`grep drawing_workflow mcp-server/*.py` 只命中 2 处，**均为注释引用**（`tool_specs_batch19.py:7` 与 `register_capabilities.py:125`，指向的是第 1707 行的 `inspect_drawing_structure`，不在本段）⇒ **本段 24 个函数目前一个都没有挂成 MCP 工具**。

## 五、本段未查到 / 不做的判断

- `Param.kind` 用 `List[str]` 是否被本仓库门禁放行：**未查到**显式规则；本段只在此处标注为待确认（#11），不下断言。
- 各函数在真机上的实测状态：**未查**（本次只读静态扫描，不跑 SolidWorks）⇒ 本文件不对任何函数写「已验证」。