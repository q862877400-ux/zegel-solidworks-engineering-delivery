# 候选 A · 最小包装层（声明式直挂，零新代码）

> 本文件是**候选设计**，不是实现。落地时新建 `mcp-server/tool_specs_batch73.py`。
> ★ 未注册、未改任何已有文件、未跑 SolidWorks / pytest。

---

## 一、方案说明

### 1.1 核心论点：这一批**不需要任何包装代码**

另两个角度多半会新增一层 `scripts/sw_drawing_bridge.py` / `scripts/sw_drawing_mcp.py` 之类的适配模块。
本方案**明确拒绝**这么做，理由是**桥已经铺好了，而且它导出的是函数本身**：

| 事实 | 出处（已核实） |
|---|---|
| `scripts/sw_drawing.py` 用 `spec_from_file_location` 按**路径**加载 subskill 实现 | `scripts/sw_drawing.py:19` |
| 逐个 `globals()[_name] = getattr(_MODULE, _name)` 导出 `__all__` | `scripts/sw_drawing.py:25-29` |
| `module` 必须是 `scripts/` 下的合法模块名 ⇒ 父目录带连字符**不能**直接进 `module` | `mcp-server/tool_registry.py:524` |
| ⇒ 于是 `module="sw_drawing"` **合法**，`scripts.sw_drawing.<函数名>` **可取到** | 同上 |

`register_capabilities.py:136` 已有 `"drawing_model": resolve_model` ⇒ `inject="drawing_model"` 可用。

**所以「包装层」= `ToolSpec` 声明本身。** 本方案的全部工作量是写 `params` / `param_alias` / `derived_args` / `doc`
四类元数据，**零新增 `.py` 实现文件、零新增函数**。这是「最小」的真实含义，也是它与另两个角度的差别：
那两个角度必然要落一个 `.py`，本角度一个都不落。

### 1.2 可挂性的**硬天花板**（本角度最重要的推论）

读 `tool_registry.py:490-525` 的调用体：

```python
kwargs = {}
for p in spec.params: ...                       # 表面参数 → 目标形参
...
kwargs[inject_as or inj] = resolver(params)     # 注入键 = inject 字符串
...
mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
return getattr(mod, spec.function)(**kwargs)    # ★ 只用关键字传参
```

⇒ **两个必要条件，缺一不可**：

1. **注入键 = `inject` 字符串 = 目标函数的真实形参名** ⇒ 只有首参**字面名为 `drawing_model`** 的函数能吃
   `inject="drawing_model"`。
2. **其余形参必须能用 JSON 标量 / `list` / `dict` 表达**（`Param.kind` 只做类型注解，跑 Pydantic）。

⇒ **凡首参是 COM 对象的函数（本仓一批全是），声明式挂不上** —— 这是**架构性**的，不是参数没找对。
（与已知事实 47 同一族：`I` 前缀指针变体在 pywin32 迟到绑定下到不了。）

### 1.3 与另两个角度的差别（一句话版）

- 角度 B 大概会**补实现**（把 `get_hole_table` 等重写成吃 `drawing_model` 的版本）。
- 角度 C 大概会**加注入解析器**（给 `RESOLVERS` 加 `table` / `section_data` 之类的解析器）。
- **本角度一条都不做**：能声明的直接声明，不能声明的**如实标「挂不了」并写清天花板在哪**，
  把「要不要补实现 / 加解析器」这个决定**留给后续决策**，不偷偷夹带。

---

## 二、完整可粘贴的 ToolSpec 代码块（8 条）

> ★ 每条 `params` 都**照 `drawing_workflow.py` 的定义行逐字抄**，行号在注释里标出。
> ★ 单位换算只做一次、且只发生在 `derived_args`（规则 2 要求的那一次），实现内部吃**米**。

```python
"""★ 覆盖面缺口批（第二批）：工程图 8 项最小包装层（声明式直挂 sw_drawing）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（ToolSpec 声明层）· 规格 `specs/202-user-coverage-gaps`
# 文件:   mcp-server/tool_specs_batch73.py（候选 A，未落地）
# 定位:   把 `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`
#         里**已有实现**的工程图能力接成 MCP 工具。
#
#   ★★ 本批**不写任何包装代码** —— `scripts/sw_drawing.py` 已用
#      `importlib.util.spec_from_file_location` 按路径加载该实现并逐个导出公开名，
#      故 `module="sw_drawing"` 直接可用（父目录带连字符进不了 `module`）。
#
#   ★★ 可挂性的硬天花板（`mcp-server/tool_registry.py:507,525`）：
#      · 注入以 `kwargs["drawing_model"]` 落位，且目标函数**只收关键字实参**
#        ⇒ **首参必须字面名为 `drawing_model`**；
#      · `Param.kind` 只能表达 JSON 标量 / list / dict
#        ⇒ **首参是 COM 对象的函数一律声明式挂不了**（见 §三）。
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

from tool_registry import Param, ToolSpec


# ── 共用：毫米 → 米的边界换算（规则 2：换算**只做一次**）──────────────
# ★ 实现侧 `x` / `y` 是**米**（drawing_workflow.py:1242-1243 的 docstring 明写「米」），
#   而 MCP 表面按规则 2 用 `_mm` ⇒ 这里 /1000.0。
# ★ `param_alias` 把 `x_mm` / `y_mm` 映成 None = **由解析器消费、不直传**，
#   因此 `derived_args` 产出的 `x` / `y` 不会与之撞名（registry:517 的 clash 检查）。
def _xy_m(p):
    return {"x": float(p.x_mm) / 1000.0, "y": float(p.y_mm) / 1000.0}


_BATCH73: list[ToolSpec] = [
    # ── 1. 剖面视图 ────────────────────────────────────────────────
    ToolSpec(
        name="solidworks_drawing_section_view",
        title="Drawing Section View",
        module="sw_drawing", function="add_section_view",
        inject="drawing_model",
        param_alias={"x_mm": None, "y_mm": None},
        derived_args=_xy_m,
        params=[
            Param("x_mm", float, description="剖视图放置点 X（**毫米**；实现收的是**米**，"
                                             "本层换算一次 ⇒ /1000）。"),
            Param("y_mm", float, description="剖视图放置点 Y（**毫米**；同上）。"),
        ],
        doc="★ **剖面视图**：`drawing_workflow.py:998` `add_section_view(drawing_model, x, y)`"
            " → `IDrawingDoc.CreateSectionViewAt5(x, y, 0, \"\", 0, None, 0)`。"
            "★ 形参逐字只有 `drawing_model, x, y` **三个**，无 scale / 无 label ⇒ 表面也不多给。",
    ),

    # ── 2. 局部视图 ────────────────────────────────────────────────
    ToolSpec(
        name="solidworks_drawing_detail_view",
        title="Drawing Detail View",
        module="sw_drawing", function="add_detail_view",
        inject="drawing_model",
        param_alias={"x_mm": None, "y_mm": None},
        derived_args=_xy_m,
        params=[
            Param("x_mm", float, description="详图放置点 X（**毫米**；实现收米）。"),
            Param("y_mm", float, description="详图放置点 Y（**毫米**；实现收米）。"),
            Param("scale", float, default=2.0,
                  description="比例**分子 Scale1**；分母 Scale2 固定传 1.0 ⇒ `scale=2` 即 2:1。"
                              "⚠ 实现未规定它有「无量纲比值」这一层 ⇒ 表面**不加** `_mm`。"),
            Param("style", int, default=0,
                  description="详图样式 `swDetViewStyle_e`（实现默认 `DET_VIEW_STYLES[\"standard\"]`）："
                              "0=standard · 1=broken · 2=leader · 3=noleader · 4=connected"
                              "（drawing_workflow.py:61-67 静态照录官方 5 项）。"),
            Param("label", str, default="",
                  description="标签文字（官方第 7 参 `LabelIn`）。"),
            Param("show_type", int, default=0,
                  description="圆/轮廓显示 `swDetCircleShowType_e`（实现默认 "
                              "`DET_CIRCLE_SHOW_TYPES[\"profile\"]`）：0=profile · 1=circle · 2=dont_show"
                              "（drawing_workflow.py:78-82，官方 3 项）。"),
            Param("full_outline", bool, default=False, description="完整轮廓（官方 `FullOutline`）。"),
            Param("jagged_outline", bool, default=False, description="锯齿轮廓（官方 `JaggedOutline`）。"),
            Param("no_outline", bool, default=False, description="无轮廓（官方 `NoOutline`）。"),
            Param("shape_intensity", int, default=0,
                  description="锯齿轮廓强度，官方有效范围 1(最强)–5(最弱)，"
                              "**仅当** `jagged_outline=True` 且 `no_outline=False` 时生效"
                              "（drawing_workflow.py:1019-1020）；默认 0 = 不生效。"),
        ],
        doc="★ **局部视图 / 详图**：`drawing_workflow.py:1022` `add_detail_view(...)`"
            " → `IDrawingDoc.CreateDetailViewAt4`，官方 **12 个参数**，实现**补齐到 12 参**"
            "（修正前只传 7 个）。"
            "⚠⚠ **来源块自述「本函数为静态签名比对后修正，未在本机实测」（:1018, :1045）**"
            " ⇒ 按铁律 6，本工具**不得**标 `verified`，只能 `stitched`。",
    ),

    # ── 3. 中心符号线 ──────────────────────────────────────────────
    ToolSpec(
        name="solidworks_drawing_center_marks",
        title="Drawing Center Marks (Auto)",
        module="sw_drawing", function="auto_insert_center_marks",
        inject="drawing_model",
        params=[
            Param("requirements", list,
                  description="要求列表，**每项是一个 dict**，键逐字取自实现："
                              "`id`(str) · `view`(str) · `count`(int) · `targets`(list[str])。"
                              "`view` 取值经 `_normalise_orientation`(:631-647) 归一到 "
                              "front/top/right（中英别名表见该函数）；"
                              "`targets` 取值域 **`AUTO_CENTER_MARK_TARGETS`(:45-49) 全量 3 项**："
                              "`holes`(1) · `fillets`(2) · `slots`(4)。"
                              "★ 传**空列表** ⇒ 实现走 `status=\"not_requested\"` 直接返回，不动模型。"),
        ],
        doc="★ **中心标记（中心符号线）**：`drawing_workflow.py:1883` "
            "`auto_insert_center_marks(drawing_model, requirements)`。"
            "★ **判据是「实体数量回读」**（docstring:1884），不是返回值 ⇒ 规则 6 已在实现内满足。"
            "★ 函数**自己**按 `_map_standard_views_from_sheet_views` 找视图 ⇒ 表面**不传**任何选择器。",
    ),

    # ── 4. 注释 ────────────────────────────────────────────────────
    ToolSpec(
        name="solidworks_drawing_note",
        title="Drawing Note",
        module="sw_drawing", function="add_note",
        inject="drawing_model",
        param_alias={"x_mm": None, "y_mm": None},
        derived_args=_xy_m,
        params=[
            Param("x_mm", float, description="注释锚点 X（**毫米**；docstring:1242 明写实现收**米**）。"),
            Param("y_mm", float, description="注释锚点 Y（**毫米**；docstring:1243）。"),
            Param("text", str, description="写入图纸的非空文字。★ 实现对空/纯空白与 "
                                           "非有限坐标**不抛异常**，而是回 `status=\"failed\"` · "
                                           "`error_code=\"DRAWING_NOTE_INPUT_INVALID\"`（:1248-1254）。"),
        ],
        doc="★ **工程图文字注释**：`drawing_workflow.py:1238` `add_note(drawing_model, x, y, text)`"
            " → `IModelDoc2.InsertNote`，随后 `_set_annotation_position` 定位 + `ForceRebuild3`。"
            "★ 返回**可审计 dict**（COM 回读文字、坐标、边界），不是 COM 对象。",
    ),

    # ── 5. 图纸格式（图框）─────────────────────────────────────────
    ToolSpec(
        name="solidworks_drawing_sheet_format",
        title="Drawing Sheet Format",
        module="sw_drawing", function="set_sheet_format",
        inject="drawing_model",
        params=[
            Param("format_path", str,
                  description="图纸格式文件路径（`.slddrt`）—— 实现直传 `ISheet.SetTemplateName`，"
                              "本工具**不做存在性校验**（官方未给预检步骤）。"),
        ],
        doc="★ **图纸格式 / 图框**：`drawing_workflow.py:1400` `set_sheet_format(drawing_model, format_path)`"
            " → `drawing_model.GetCurrentSheet().SetTemplateName(format_path)`。"
            "★ 作用于**当前图纸页**（`GetCurrentSheet`），不是新建页 —— 建页是下面第 6 条。",
    ),

    # ── 6. 新增图纸页 ──────────────────────────────────────────────
    ToolSpec(
        name="solidworks_drawing_sheet_add",
        title="Drawing Add Sheet",
        module="sw_drawing", function="add_sheet",
        inject="drawing_model",
        params=[
            Param("paper_size", int, default=7,
                  description="纸张大小（docstring:1417-1418 的枚举表逐字照抄）："
                              "0=A · 1=B · 2=C · 3=D · 4=E · 5=A4 · 6=A3 · **7=A2** · 8=A1 · 9=A0。"
                              "★ 注意与 SolidWorks 的 `swPaperSize_e` **不是同一套编号**，"
                              "本工具**原样透传**实现里的这张表，不做换算。"),
            Param("template_path", str, default="",
                  description="图纸格式模板路径（`.slddrt`），空串表示不指定。"),
            Param("first_angle", bool, default=True,
                  description="★ 第一角投影为 True（实现直传 `NewSheet4` 的 `bool(first_angle)`）。"
                              "★ 本工具**故意**用 bool 而不是 `projection: str` —— "
                              "registry.py:412,423 对 `kind is bool` **豁免**规则 2 的长度/角度后缀检查，"
                              "故 `first_angle` 这个名字不会被门禁拦。"),
        ],
        doc="★ **新增图纸页**：`drawing_workflow.py:1411` `add_sheet(drawing_model, paper_size=7, "
            "template_path=\"\", first_angle=True)` → `IDrawingDoc.NewSheet4`（官方 16 参，实现全填）。"
            "★ 与第 5 条分工：本条**建页**，`set_sheet_format` **改当前页的图框**。",
    ),

    # ── 7. 表注解（孔表 / 修订表的唯一声明式入口）───────────────────
    ToolSpec(
        name="solidworks_drawing_insert_table_annotation",
        title="Drawing Insert Table Annotation",
        module="sw_drawing", function="insert_table_annotation",
        inject="drawing_model",
        param_alias={"x_mm": None, "y_mm": None},
        derived_args=_xy_m,
        params=[
            Param("x_mm", float, description="表注解放置点 X（**毫米**；实现收米）。"),
            Param("y_mm", float, description="表注解放置点 Y（**毫米**；实现收米）。"),
            Param("table_type", int,
                  description="★ **官方枚举值本仓查不到** —— 来源块 :2412-2413 明写"
                              "「`InsertTableAnnotation` 的 Int32 Type 决定表种类，"
                              "其枚举**在两套官方源里都查不到**，故本模块只透传、不设默认类型」。"
                              "⇒ 本工具**照实透传**，surface 上不编一张取值表。"),
            Param("row", int, default=0, description="起始行号（官方未说明 0 基还是 1 基 ⇒ 原样透传）。"),
            Param("column", int, default=0, description="起始列号（同上）。"),
            Param("template", str, default="",
                  description="★ 非空 ⇒ 走 `InsertTableAnnotation2`（**7 参**，多 `UseAnchorPoint`）；"
                              "空 ⇒ 走 `InsertTableAnnotation`（**5 参**）。分支在实现里（:2320-2329）。"),
            Param("use_anchor_point", bool, default=False,
                  description="仅 `template` 非空时生效 —— `InsertTableAnnotation2` 的 "
                              "`UseAnchorPoint`（实现 :2315 关键字专用）。"),
        ],
        doc="★ **表注解入口**：`drawing_workflow.py:2306` `insert_table_annotation(...)`。"
            "★ **为什么必须挂这一条**：孔表族与修订表族的其余 5 个函数"
            "（`get_hole_table` / `get_revision_table_feature` / `add_revision` / "
            "`delete_revision` / `get_current_revision`）**首参全是 COM 对象**，"
            "声明式**挂不了**（见 §三）⇒ 本条是它们**唯一**声明式可达的上游入口。"
            "⚠ 它**返回 COM 对象**，MCP 表面无法把它传给下一条工具 ⇒ 链条到此**断开**。",
    ),

    # ── 8. 标准三视图 ──────────────────────────────────────────────
    ToolSpec(
        name="solidworks_drawing_standard_views",
        title="Drawing Standard 3rd-Angle Views",
        module="sw_drawing", function="create_standard_views",
        inject="drawing_model",
        params=[
            Param("part_path", str,
                  description="零件文件路径（绝对路径），实现直传 `Create3rdAngleViews2`。"),
        ],
        doc="★ **标准三视图（第三角）**：`drawing_workflow.py:941` "
            "`create_standard_views(drawing_model, part_path)` → `IDrawingDoc.Create3rdAngleViews2`。"
            "★ **本条不在题述 8 项之内**，是本角度为凑满「最小可用闭环」挑的同模块**同签名形态**"
            "（首参 `drawing_model` + 纯标量余参）的第 8 条 —— 选它的唯一理由是它**零适配成本**。"
            "⚠ 另有 `create_standard_views_with_projection(drawing_model, part_path, projection=...)`"
            "(:952) 支持第一/第三角，**参数面更宽**，若评审倾向「一次到位」应**换用那一条**替代本条。",
    ),
]

#: ★★ 注册器按 `SPECS_*` 找
SPECS_BATCH73 = _BATCH73
```

---

## 三、风险与未决

### 3.1 ★ 挂不了的（首参是 COM 对象 —— 架构性，不是参数没找对）

下列 5 个函数**签名逐字已读**（`drawing_workflow.py:2425 / 2446 / 2489 / 2496 / 2503`）：

| 函数 | 首参 | 结论 |
|---|---|---|
| `get_hole_table(table)` | COM `IHoleTableAnnotation` | **挂不了** |
| `get_revision_table_feature(table)` | COM `IRevisionTableAnnotation` | **挂不了** |
| `add_revision(revision_table, revision)` | COM `IRevisionTableFeature` | **挂不了** |
| `delete_revision(revision_table, index, mark_deleted)` | COM | **挂不了** |
| `get_current_revision(revision_table)` | COM | **挂不了** |
| （同类）`set_section_style(section_data, *, ...)` | COM `ISectionViewData` | **挂不了** |

**原因（不是猜）**：`registry.py:507` 把注入写成 `kwargs["drawing_model"]`，
`:525` 用 `getattr(mod, fn)(**kwargs)` 调用 ⇒ 若首参叫 `table`，工具就必须声明
`Param("table", <COM 类型>)`，而 `Param.kind` 只做类型注解、Pydantic 只能反序列化 JSON
⇒ **COM 对象在 MCP 表面不存在对应类型**。
解法只有两条，都**不是**本角度该做的：① 给 `RESOLVERS` 加一个「上一步返回的 COM 对象」解析器
（跨调用状态，本仓目前没有）；② 重写成吃 `drawing_model` 的版本（即角度 B）。

⇒ **孔表 / 修订表两项，在本角度下交付为 0 条工具。**

### 3.2 ★ 根本不存在实现的（题述 8 项之一）

**表面粗糙度** —— 我在 `subskills/` 全目录 grep `Roughness|roughness|粗糙`，**只有 2 处命中，
且两处都是散文**：

- `subskills/solidworks-engineering-drawing/SKILL.md:41` —— 讲**审查器**接受哪几类专业标注实体；
- `subskills/solidworks-engineering-drawing/references/review.md:19` —— 同上，讲审查口径。

`drawing_workflow.py` 里 **0 处**。⇒ **既没有创建函数、也没有读取封装**
⇒ 按铁律 5（查不到就说查不到）**如实标注：本项无实现，不出工具，不编签名。**

⇒ **题述「已实现 8 项」实际可对上的只有 6 项**；本文件 8 条工具里，
前 6 条覆盖 **5 项**（剖面 / 局部 / 中心符号线 / 注释 / 图纸格式），第 7 条是孔表+修订表的**上游入口**，
第 8 条是同模块补充项。

### 3.3 未决与风险（逐条）

1. **`derived_args` 的 mm→m 是本方案唯一的单位转换点**，落在 `_xy_m`。
   ⚠ **风险**：`_xy_m` 是模块级**共享**函数，被 4 条工具引用 ⇒ 改一处动四条。
   本角度**接受**这个耦合（少写代码是本角度的目的），但**必须**在代码评审里点名。
2. **`x_mm` / `y_mm` 能过规则 3 门禁**：`registry.py:128` `if low.endswith("_mm"): return False`
   ⇒ `_looks_like_coord_component` 对 `_mm` 结尾**直接放行**；`_BARE_COORD_NAMES`(:93) 是
   `{"x","y","z","point","coordinate"}` 精确表，**不含** `x_mm`。
   ⚠ **但同一文件 :125-126 的注释声称「`x_mm`/`y_mm`/`z_mm` 被规则 2 要求、又被规则 3 拦，两条规则自相矛盾」**
   ⇒ **注释与代码不一致**。本方案按**代码**（可执行）走，**同时把这条注释矛盾列为待清理项**，
   不要让评审误以为我读的是注释。
3. **`add_detail_view` 的验证等级**：其来源块自述「静态签名比对后修正，**未在本机实测**」
   （:1018, :1045）⇒ 新工具**必须**记 `stitched`，**不得**记 `verified`（铁律 6 / 停止条件 6）。
   同族来源块（表注解那一整组 :2416、:2487、:2349）也都写着「未在本机实测」。
4. **`table_type` 的取值域查不到**（:2412-2413 明写两套官方源都没有）⇒ surface 上**不给**取值表，
   只透传。若评审要求「有取值表才准上」，这一条应**暂缓**而不是编一张。
5. **`row` / `column` 的基（0 基还是 1 基）官方未说明**（:2346-2347）⇒ 原样透传，不做 ±1 猜测。
6. **`add_sheet` 的 `paper_size` 与 `swPaperSize_e` 不是同一套编号**（docstring:1417-1418 是本模块自带的表）。
   ⚠ **未决**：这张表的**出处本轮没读到** ⇒ 按铁律 5 记为「未核实」，但**不阻断**
   （原样透传实现里的值，不做换算）。
7. **第 8 条（标准三视图）是自己挑的**，理由已在 `doc` 里写明；若评审要求严格 1:1 对应题述 8 项，
   应**删掉它**、让文件变成 7 条，而不是硬凑。
8. **`param_alias` 的 `None` 语义已在代码里核对**（:495「由解析器消费，不进目标函数」）⇒
   `x_mm`/`y_mm` 不会直传，`derived_args` 的 `x`/`y` 不撞名（:517-522 的 clash 检查）。
9. **未验证**：`ToolSpec` 代码块**没有导入过、没有跑过 `check_spec`**（本轮按指示不跑测试）。
   ⇒ 上面 3.3-2 那条门禁判据是**读代码**得出的，**未实证**。

### 3.4 与另两个角度的差异定位（一句话）

> 本角度**只做声明、不补实现、不加解析器**；它的价值是把「**哪些能挂、哪些物理上挂不了、哪一项压根没实现**」
> 一次性摊在桌面上；代价是孔表 / 修订表 / 表面粗糙度**三项在本角度下交付为空**
> —— 这是**如实暴露缺口**，不是漏做。