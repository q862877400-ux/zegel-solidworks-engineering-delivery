# 扫描 S3-1 · subskill 函数能力盘点（第 1 段）

**扫描对象**：`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`
**扫描方式**：只读静态扫描（未运行 SolidWorks、未跑 pytest、未改动仓库任何其它文件）。
⚠ 本文件在本次写入前**已存在一份同范围（S3-1 第 1 段）旧稿**；本次按分工重扫后覆盖。
该文件**已被 git 跟踪**（`git ls-files` 命中，且写入前工作区干净）⇒ 旧稿保留在 git 历史里，可随时取回。

---

## 一、我的段落边界（以实际读到的 `def` 行号为准）

| 项 | 值 |
|---|---|
| 文件总行数 | 2746 |
| 名义三等分边界 | 2746 / 3 = 915.33 ⇒ 第 1 段名义第 1–915 行 |
| 落在名义边界内的**最后一个** `def` | 第 **806** 行 `create_adaptive_standard_views`（函数体到第 938 行） |
| 紧随其后的**第一个** `def` | 第 **941** 行 `create_standard_views` ⇒ **属第 2 段** |
| ★ 本段实际覆盖 | **第 1 – 940 行**（止于下一个 `def` 之前） |
| ★ 本段 `def` 数量 | **24**（21 个顶层 + 3 个嵌套） |

> 本段 24 个 `def` 的行号：102, 113, 122, 148, 154, 166, 275, 286, 313, **348**(嵌套), 406, 453, **548**(嵌套), 590, 596, 631, 650, 661, 678, **694**(嵌套), 738, 755, 790, 806。

---

## 二、判定「能否挂成 MCP 工具」的依据（读 `mcp-server/tool_registry.py` 源码，不是印象）

| 依据 | 源码位置 | 含义 |
|---|---|---|
| `Param.kind` 是 Python 类型注解，文档串只列 `str / float / int / bool` | `tool_registry.py:221-232` | ★ 本次判定的**主判据**：形参若是 COM 对象 / 字典 / 序列 / 变参回调 ⇒ `Param` 表达不了 |
| `build_input_model` 把 `p.kind` **原样**塞进 Pydantic 字段 | `tool_registry.py:463`、`:465` | 入参类型最终就是 MCP 客户端要能填的类型 |
| `derived_args` 只补「额外实参」，产出 dict 会并进关键字实参 | `tool_registry.py:278-285`、`:317`、`:514-520` | 可用来把标量拼成「dict / 列表 / COM 子对象」实参 |
| `inject` 注入的是**宿主对象**，注册时可用 `inject_as` 覆盖关键字名 | `tool_registry.py:263-267`、`:477`、`:507`（`kwargs[inject_as or inj] = resolver(params)`） | ⇒ 像 `drawing_model` 这种**形参名与约定名 `model` 不同**的，仍可注入 |
| 规则 2（长度）门禁：`_LEN_WORDS` 命中且不以 `_mm` 结尾 ⇒ `GateError` | `_LEN_WORDS` 在 `:147-150`；判定在 `:412-420` | 词表只有 11 个：`radius / diameter / depth / thickness / distance / width / height / length / offset / spacing / pitch` |
| 规则 2（角度）门禁：`_ANGLE_WORDS = angle / degrees / draft` | `:158`、`:423-431` | 本段**未命中**任何一条 |
| 规则 3（裸坐标）门禁 | `:93`、`:96-136`（`x/y/z/point/coordinate` + `x1/cx/major_x` 形态；以 `_mm` 结尾豁免） | 本段**无**形参命中 ⇒ 规则 3 对本段不构成障碍 |
| `omitted_params` 可显式声明「有意不暴露」的形参 | `:291-300`、`:315` | 对象类形参还有一条「显式省略」的路 |

**一句话判据**：形参里出现 `Param.kind` 表达不了的东西（COM 对象、dict、序列、`*args`），或过不了规则 2/3 的 `check_spec` ⇒ 不能**直接**挂；能靠 `inject` / `derived_args` / 改名字补齐的记「**需包装**」；两者都补不齐（嵌套函数、纯泛化 helper）记「**不能**」。

---

## 三、第 1 段逐个 `def` 盘点（24 条）

| # | 函数名 | 定义行号 | 一句话用途 | 建 / 读 | 能否挂成 MCP 工具 | 若不能，卡在哪 |
|---|---|---|---|---|---|---|
| 1 | `_safe_member` | 102 | 通过 `get_com_member` 读任一 COM 成员，obj 为 None 或抛异常就返回 `default` | 读 | **不能** | 形参 `obj` 是**任意 COM 对象**（`Param` 无此类型），且第 3 参是 `*args` **变参回调用法**（`:102` `def _safe_member(obj, name, *args, default=None)`）⇒ 签名不固定，无法声明 |
| 2 | `_as_sequence` | 113 | 把 COM 数组 / tuple / 单对象 / None 统一成 `list` | 读（纯数据整理） | **不能** | 形参 `value` 形态不定（`:115-119` 逐形态分支），`Param` 只能声明确定类型；且返回语义依赖调用点，无对外契约 |
| 3 | `_normalise_box` | 122 | 把 COM `Outline`/`GetBox` 数组或 dict 统一成 `{left,bottom,right,top}` | 读（纯数据整理） | **不能** | 同上：`value` 可为 dict（`:124`）也可为 COM 数组（`:130`）⇒ 类型不定 |
| 4 | `_annotation_box` | 148 | 读 `GetAnnotation().GetBox()` 得到尺寸/注释/表格注解的二维包围盒 | 读 | **需包装** | 形参 `owner` 是尺寸 / 注释 / 表格的 COM 对象；`inject` 只能注**活动文档**、注不到子对象 ⇒ 需加一层「声明式 `selection: str` + `derived_args` 解析出该注解」 |
| 5 | `_view_display_dimensions` | 154 | 兼容数组接口与 `GetFirstDisplayDimension5`→`GetNextDisplayDimension` 链，取视图内全部 `DisplayDimension` | 读 | **需包装** | 形参 `view` 是 `IView` COM 对象（同 #4）；且**返回值是 COM 对象列表**，工具面只能返 JSON ⇒ 还得配「解析成 dict」层 |
| 6 | `auto_arrange_drawing_dimensions` | 166 | 逐页逐视图 `Select2` 选中全部尺寸注解，再调官方 `IModelDocExtension.AlignDimensions` 按模式 + 间距重排 | **建** | **需包装** | 形参只有 `drawing_model`（可用 `inject_as="drawing_model"` 注）+ `spacing_m: float` + `mode: str` ⇒ **类型层面无障碍**。★ 真正的卡点是**规则 2 门禁**：`spacing_m` 命中 `_LEN_WORDS` 里的 `spacing`（`tool_registry.py:149`）却不以 `_mm` 结尾 ⇒ `check_spec` 在 `:412-420` 直接 `GateError`，要么改名 `spacing_mm`（并在派生层 `/1000`），要么进 `_LEN_SUFFIX_EXEMPT` 并写明理由 |
| 7 | `_finite_positive` | 275 | 把 COM 数值转成有限正数，失败回落到保守默认值并回报是否有效 | 读（纯计算） | **能**（形参层面） | 两个形参都是 `float`、`:281` 用 `math.isfinite` 过滤 ⇒ `Param` 完全表达得了。⚠ 但它是**私有纯 helper**（返回 `(值, bool)` 元组），挂成工具没有对外语义 |
| 8 | `_dimension_text_evidence` | 286 | 读 `GetText(0..4)` 收集尺寸的前缀/后缀/标注文本片段；主值缺失时用保守占位、不伪造格式化值 | 读 | **需包装** | 形参 `display_dimension` 是 `IDisplayDimension` COM 对象 ⇒ 同 #4，需声明式选择器 + `derived_args` |
| 9 | `estimate_dimension_text_box` | 313 | 用 `IAnnotation` 锚点 + `ITextFormat` 字高/字宽因子保守估算尺寸文字的轴对齐外接方框（输出标 `source=estimated`） | 读 | **需包装** | 形参 `display_dimension` 是 COM 对象（同 #4）。★ 规则 2 **不拦** `padding_m`：「padding」不在 `_LEN_WORDS` 的 11 词里（`:147-150`）—— 这是「词表没收录」而不是「已豁免」 |
| 10 | `line_units` | 348 | 估算单行字宽：全角字符按 1 个字高、半角按 0.62 字高 | 读（纯计算） | **不能** | **嵌套**在 `estimate_dimension_text_box` 内部（`:348`），不是模块级符号，模块路径寻址不到 |
| 11 | `select_drawing_template` | 406 | 按「图幅匹配 + GB/T 字样 + 本地化字样 + 是否存在」给本机 `.slddrt` 候选打分并选出图框模板路径 | 读（文件系统） | **需包装** | 形参 `candidates` 是**路径列表**（`:415` `for raw_path in candidates or []`）⇒ `Param.kind` 的官方口径只有四种标量。⚠ 序列类型能否过门禁**未查到显式规则**（`build_input_model` 只是把它当 Pydantic 注解用）⇒ 按未确认处理，判「需包装」（如改成单条 `template_path: str` 或 `candidates_json: str`） |
| 12 | `plan_standard_view_layout` | 453 | 纯算术：按图幅 / 投影法 / 模型外形 / 标题栏尺寸算三视图中心点与比例，保证不侵入标题栏 | 读（纯计算） | **需包装** | ① `model_size_m` 是**三元组**（`:473` 解包 `width,height,depth`）⇒ `Param` 表达不了，需拆成三个 `_mm` 标量；② ★ 规则 2 **必拦**：`title_block_width_m` 命中 `width`、`title_block_height_m` 命中 `height`（`:147-150` + `:412-420`）；③ `requested_scale` 同时接受 `str("1:2")` 与 `float` 两种量纲（`:505-509`）⇒ 需拆成互斥入参或走 `extra_op` |
| 13 | `view_record` | 548 | 生成单个视图的中心点与边界框记录 | 读（纯数据） | **不能** | **嵌套**在 `plan_standard_view_layout` 内部 |
| 14 | `_scale_ratio` | 590 | 用 `Fraction(...).limit_denominator(1000)` 把浮点比例压成 SolidWorks 认的整数比（分子, 分母） | 读（纯计算） | **能**（形参层面） | 单个 `float` 形参 ⇒ 无障碍。⚠ 私有 helper；返回 tuple，由调用方（`:584`、`:810`）消费 |
| 15 | `_apply_view_layout` | 596 | 把已建视图移到规划中心、设独立比例（`ScaleRatio` + `SetViewPosition`），并**回读位置**做一致性校验（不一致抛 `RuntimeError`） | **建** | **需包装** | 形参 `view` 是 `IView` COM 对象、`item` 是 **dict**（`:598` `item["center"]`）⇒ 两者都不是 `Param` 类型；`item` 需由 `layout` 派生 ⇒ 走 `derived_args`。★ 注意内部 `:604` 构造 `VARIANT(VT_ARRAY|VT_R8, center)` 的 SafeArray —— 那在函数体内，不在形参上 |
| 16 | `_normalise_orientation` | 631 | 把 SolidWorks 视图方向名（中英，`*Front`/前视/主视…）归一成 `front`/`top`/`right` 键 | 读（纯字符串） | **能**（形参层面） | 单个 `str` 形参 ⇒ 无障碍。⚠ 私有 helper，`aliases` 表（`:634-646`）属实现细节，不宜对外暴露 |
| 17 | `_view_position` | 650 | 读工程图视图中心位置，返回 `(x, y)` 或 `None` | 读 | **需包装** | 形参 `view` 是 COM 对象（`:652` `_safe_member(view,"Position",...)`）⇒ 同 #4 |
| 18 | `_set_view_center` | 661 | 移动视图中心并**回读校验**（偏差 > 1e-5 抛错），供按真实包围盒二次排布复用 | **建** | **需包装** | 形参 `view` 是 COM 对象、`center` 是**两点列表**（`:664` 构 `VARIANT(VT_ARRAY|VT_R8)`）⇒ 均非 `Param` 类型。规则 3 不会拦 `center`（`:140` 明确「`center` 只登记不判」） |
| 19 | `_refine_standard_view_spacing` | 678 | 按 SolidWorks **实际** `GetOutline` 包围盒二次排布，消除三视图之间的确认重叠 | **建** | **需包装** | 形参 `view_objects` 是 `dict[str, IView]`（`:683`）、`view_records` 是 `list[dict]`（`:690`）⇒ 两者都不是标量；且函数内部调 COM 写操作 |
| 20 | `move_if_needed` | 694 | 沿某一轴把视图移到目标值，回读新中心并同步更新边界盒记录 | **建** | **不能** | **嵌套**在 `_refine_standard_view_spacing` 内部，闭包捕获 `boxes` / `records` / `view_objects`，脱离闭包没有独立语义 |
| 21 | `_collect_drawing_views` | 738 | 同时走 `Sheet.GetViews` 与 `GetFirstView`→`GetNextView` 链，取当前页真实模型视图 | 读 | **需包装** | `drawing_model` 可 `inject`；但**返回 COM 对象列表**（`:741`、`:752`）⇒ 工具面只能返 JSON，必须再包一层「解析成 dict」 |
| 22 | `_map_native_standard_views` | 755 | 依据方向名 → 基准视图关系 → 原始位置三条线索，把一堆视图映射成第三角三视图 | 读 | **需包装** | 形参 `views` 是 COM 对象列表；**返回值本身就含 COM 对象**（`:774`/`:786` 返回 `dict[orientation→view 对象]`）⇒ 返回契约就不成立 |
| 23 | `_map_standard_views_from_sheet_views` | 790 | 从整张图纸全部视图里筛出前 / 俯 / 右三个标准视图并映射 | 读 | **需包装** | 形参 `sheet_views` 是 COM 对象列表；委托 #22 ⇒ 同样的返回含 COM 对象问题 |
| 24 | `create_adaptive_standard_views` | 806 | 按预计算布局创建前/俯/右三视图：`CreateDrawViewFromModelView3` 失败时回退 `CreateFirstAngleViews2`/`Create3rdAngleViews2`，再按投影法重定位 + 二次排布 + 回读 | **建** | **需包装** | `drawing_model` 可 `inject_as` 注入、`part_path: str` 没问题，但 `layout` 是 **dict**（`:810` `layout.get(...)`、`:811` 遍历 `layout["views"]`）⇒ 需 `derived_args` 由标量组装。⚠ 另：它的返回值是纯 dict（视图回读记录）⇒ **返回契约有利**；它唯一的前置是 #12 的产物，单挂会让调用方不自洽 ⇒ 建议与 #12 合成一个工具 |

---

## 四、本段小结（可核对的事实）

| 分类 | 个数 | 函数名 |
|---|---|---|
| **能**（形参全是标量，且规则 2/3 门禁不拦） | **3** | `_finite_positive`@275、`_scale_ratio`@590、`_normalise_orientation`@631（★ 三者都是**私有纯 helper**，暴露成工具无对外语义） |
| **需包装**（形参含 COM 对象 / dict / 列表 / 元组，但可经 `inject` + `derived_args` + 改名补齐） | **15** | `_annotation_box`、`_view_display_dimensions`、`auto_arrange_drawing_dimensions`、`_dimension_text_evidence`、`estimate_dimension_text_box`、`select_drawing_template`、`plan_standard_view_layout`、`_apply_view_layout`、`_view_position`、`_set_view_center`、`_refine_standard_view_spacing`、`_collect_drawing_views`、`_map_native_standard_views`、`_map_standard_views_from_sheet_views`、`create_adaptive_standard_views` |
| **不能** · 嵌套 `def`（闭包内，模块级不可寻址） | **3** | `line_units`@348、`view_record`@548、`move_if_needed`@694 |
| **不能** · 顶层但签名不可声明（COM 对象 + `*args` 变参 / 类型不定） | **3** | `_safe_member`@102、`_as_sequence`@113、`_normalise_box`@122 |
| **合计** | **24** | 3 + 15 + 3 + 3 = 24 ✓ |

- **建 / 读分布**：**建** 6 个（#6 `auto_arrange_drawing_dimensions` · #15 `_apply_view_layout` · #18 `_set_view_center` · #19 `_refine_standard_view_spacing` · #20 `move_if_needed` · #24 `create_adaptive_standard_views`）；**读 / 纯计算** 18 个。合计 24 ✓。
- **规则 2 / 3 门禁对本段的实际命中**：规则 2 命中 3 个形参 —— `spacing_m`@166、`title_block_width_m`@453、`title_block_height_m`@453；规则 2 角度侧 0 命中；规则 3 裸坐标 0 命中。
- **当前 MCP 注册面**：`grep drawing_workflow mcp-server/` 只命中 2 处，**均为注释引用**（`register_capabilities.py:125`、`tool_specs_batch19.py:7`，指向第 1707 行的 `inspect_drawing_structure`，不在本段）⇒ **本段 24 个函数目前一个都未挂成 MCP 工具**。

## 五、本段「查不到 / 不下断言」的地方

- `Param.kind` 用 `List[str]`（或任何非四标量类型）能否过 `check_spec`：**未查到**显式规则 ⇒ #11 只按「需包装」记，不写「不能」。
- 各函数在真机上的实测状态：**未查**（本次只读静态扫描，没跑 SolidWorks）⇒ 本文件不对任何函数写「已验证」。
- `inject_as` 在**具体注册入口**是否被本仓库实际用过：**未查**（只确认了 `tool_registry.py:477`、`:507` 存在该形参与该用法）⇒ 上面凡写「可用 `inject_as` 注入」的，都是按该源码路径得出的，不是按某条真机记录。