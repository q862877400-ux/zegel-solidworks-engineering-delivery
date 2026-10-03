# S2-b · A 表「可挂成 MCP 工具吗」判定 —— **sketch_\* 与 curve_\* 全部条目**

**性质**：只读判定。**未改动任何既有文件**；**未运行 SolidWorks**；**未运行 pytest**。
**唯一新建文件**：本文件。
**范围**：A 表 41 条里 `id` 首段为 `sketch_`（12 条）与 `curve_`（2 条）的**全部 14 条**。别的组不碰。

## 〇 · 判据（三类，口径是我按题面定的）

| 类 | 判据 |
|---|---|
| **A · 可直接挂** | 首参是宿主对象（`model` / `doc` / `sw`），**其余形参全是 `str`/`float`/`int`/`bool`/`list`/`dict`** ⇒ 可照 `mcp-server/tool_specs_batch*.py` 的 `ToolSpec` 写一条 |
| **B · 要加转接层** | 形参里**有 COM 对象**（`IEntity` / `IBody2` / `ISurface` / `IMathVector` …），**或**官方前置要求「调用方先按 mark 选好草图/面/边」而 `ToolSpec` 表达不了 ⇒ 先写一层「按序号/按名字解析成对象 + 补设 Mark」的包装 |
| **C · 挂不了** | 形参里有**接口指针**（`AccessSelections` 族）、**SafeArray 的 out**，**或**台账 `limitations` 已写明**真机不可达** ⇒ 写「挂不了」并逐字引用依据 |

> ★ **转接层在本仓已有先例**（题面给的 `scripts/sw_drawing_expose.py` **实测没有**这个文件）；
> 真先例是 **`scripts/sw_sheet_metal_weld_entry.py::create_midsurface(model, *, body_index: int = 0, …)`**
> —— 它按 `body_index` 解析体，与题面描述的形态一致。
> 另有一个更贴草图的解析原语：**`scripts/sw_sketch_edit_ops.py::select_sketch_segment(model, index: int, *, append: bool = False) -> int`**
> 与 **`scripts/sw_sketch_edit_ops.py::_select_spec(model, selection: str, *, mark: int = 0) -> int`**。

## 一 · 主表（14 行）

| id | 实现文件 | 目标函数（形参表原文） | 首参 | 其余形参形态 | 判类 | 依据（文件 + 可搜索原文片段） | 建议工具名（含覆盖率关键词） |
|---|---|---|---|---|---|---|---|
| `sketch_primitives_b1` | `scripts/sw_sketch_primitives.py` | `def sketch_3point_corner_rectangle(model, x1, y1, x2, y2, x3, y3):` … `def sketch_perimeter_circle(model, x1, y1, x2, y2, x3, y3):` | `model` | 无标注数值 + `arc_type=1` / `direction=1`（int）⇒ **全数值** | **A** | 形参表逐字：`def sketch_tangent_arc(model, x1, y1, x2, y2, arc_type=1):`；末尾成员清单原文 `"sketch_3point_corner_rectangle", "sketch_3point_center_rectangle", "sketch_parallelogram", "sketch_tangent_arc", "sketch_3point_arc", "sketch_elliptical_arc", "sketch_parabola", "sketch_conic", "sketch_perimeter_circle",`。★ 台账 limitations 写前置「本批都需“当前在草图编辑态”的前置（先 `sketch_start`）」⇒ 那由 `inject="model"` + 既有 `solidworks_sketch_start` 满足 | ⚠ **已存在 9 个**：`solidworks_sketch_add_3point_rectangle` / `…_add_3point_center_rectangle` / `…_add_parallelogram` / `…_add_tangent_arc` / `…_add_3point_arc` / `…_add_partial_ellipse` / `…_add_parabola` / `…_add_conic` / `…_add_perimeter_circle`（`mcp-server/tool_specs_batch65.py`）★ 本条真实动作是**把这 9 个名字补进台账的 `mcp_tools`** |
| `sketch_edit_ops_b3` | `scripts/sw_sketch_edit_ops.py` | `def sketch_offset(model, selection: str, offset_mm: float, *, both_directions: bool = False, chain: bool = True, cap_ends: str = "none", make_construction: str = "dont", add_dimensions: bool = False):` | `model` | `selection: str`（**声明式选择器**）+ 其余 float/bool/str | **A**（6 个成员）**／成员级 C ×1** | 形参表逐字：`def sketch_trim(model, selection: str, option: str = "closest", x: float = 0.0, y: float = 0.0):`；选择器解析器 `_select_spec` 已在本文件内（`return n`）。★ **唯一挂不了的成员**是 `sketch_intersect_curves`，台账 limitations 逐字：「⚠ **交叉曲线未验成**：官方前置是 3D 草图 + 两个相交面，而 `Insert3DSketch` 在本机回 `None` ⇒ 包装留在模块里但**不挂工具**。」 | ⚠ **6 个已存在**：`solidworks_sketch_trim` / `…_extend` / `…_offset` / `…_fillet` / `…_linear_pattern` / `…_circular_pattern`（`mcp-server/tool_specs_batch66.py`）★ 建议**只把 `sketch_trim`/`sketch_extend`/`sketch_offset`/`sketch_fillet`/`sketch_linear_pattern`/`sketch_circular_pattern` 六个写进台账**；`sketch_intersect_curves` **保持不挂**并把它那句 limitations 一起引过去 |
| `sketch_modify_ops` | `scripts/sw_sketch_modify_ops.py` | `def sketch_move(model, start_x_mm: float, start_y_mm: float, end_x_mm: float, end_y_mm: float) -> dict:` ／ `def sketch_flip(model, axis_flag: int) -> dict:` ／ `def sketch_stretch(model, base_x_mm: float, base_y_mm: float, dest_x_mm: float, dest_y_mm: float, keep_relations: bool = True) -> dict:` | `model` | 全 float/int/bool ⇒ **无数对象** | **A** | 形参表逐字：`def sketch_rotate(model, center_x_mm: float, center_y_mm: float, angle_deg: float) -> dict:`；`def sketch_scale(model, factor: float) -> dict:`。★ 台账 evidence 已记「**走 MCP 契约的真机调用 5/5**」与「`tools/check_inject_binding.py` **PASS 0 条**」⇒ 这条**早就挂好了，只是台账没登** | ⚠ **6 个已存在**：`solidworks_sketch_move_entities` / `…_rotate_entities` / `…_scale_entities` / `…_stretch_entities` / `…_flip_entities`（`mcp-server/tool_specs_batch67.py`）+ `solidworks_sketch_mirror`（`tool_specs_batch41.py`）★ 建议工具名沿用**这 6 个既名**（含关键词 `sketch_move` / `sketch_rotate` / `sketch_scale` / `sketch_stretch` / `sketch_flip` / `sketch_mirror`），动作 = 回填台账 |
| `sketch_dimension_horizontal` | `scripts/sw_sketch_dimensions.py` | `def add_horizontal_dimension(model, x_mm: float, y_mm: float):` | `model` | `float` ×2 | **A** | 形参表逐字：`return get_com_member(model, "AddHorizontalDimension2", float(x_mm), float(y_mm), 0.0)`。⚠ **前置是承重的**，台账 limitations 逐字：「★★ **前置：必须先选中实体**（★ 一条线段**或**两个端点都行）—— ★ 而**不选时**它会弹「修改」框等人填数（★ 而那会**看起来像挂死**）。」⇒ 挂工具时**必须补一个 `selection: str` 形参**并接既有的 `sw_sketch_edit_ops.select_sketch_segment`（★ 那一步是**形参新增**，不是对象形参，故仍判 A） | `solidworks_sketch_add_horizontal_dimension`（含关键词 `add_dimension` / `sketch_dimension`） |
| `sketch_dimension_vertical` | `scripts/sw_sketch_dimensions.py` | `def add_vertical_dimension(model, x_mm: float, y_mm: float):` | `model` | `float` ×2 | **A** | 形参表逐字：`return get_com_member(model, "AddVerticalDimension2", float(x_mm), float(y_mm), 0.0)`。⚠ 同上**必须先选中实体**（前置逐字同 `sketch_dimension_horizontal`）。⚠ 台账逐字：「**返回值不可信**：… 而 `AddVerticalDimension2` **回 `None` 而尺寸照样加上** ⚠ ⇒ ★ **判据请用尺寸计数**」 | `solidworks_sketch_add_vertical_dimension`（含关键词 `add_dimension` / `sketch_dimension`） |
| `sketch_slot_types` | `tools/prove_sketch_slot_four_types.py`（台账 source_evidence 指名的代码） | `def _one(sw, name, creation_type):` | `sw`（`ISldWorks`） | `name` str + `creation_type` int ⇒ **无数对象** | **A** | 真机调用点逐字：`ret = C.get_com_member(sm, "CreateSketchSlot", int(creation_type), 0, 0.004, -0.02, 0.0, 0.0, 0.02, 0.0, 0.0, 0.0, 0.012, 0.0, 1, True)` ⇒ **14 个实参全是 int/float/bool**。台账逐字：「**四个值全真机建成**…**四个 type 均令草图段数 0 → 5**」。⚠ 既有 `solidworks_sketch_add_slot`（`tool_specs_batch54.py`，`function="sketch_slot"`）**只有直槽**（两点 + 半径）⇒ 四个枚举值**还没被工具面覆盖** | `solidworks_sketch_create_sketch_slot`（含关键词 `slot`），形参加 `slot_creation_type: int` / `slot_length_type: int` / `center_arc_direction: int` / `add_dimension: bool` |
| `sketch_line2` | `tools/prove_createline2_and_createspline.py` | `def _line2(doc):` | `doc`（`IModelDoc2`） | **零形参**（6 个坐标写死在函数体） | **A** | 函数体逐字：`return C.get_com_member(doc, "CreateLine2", -0.02, -0.01, 0.0, 0.02, 0.01, 0.0)`。⚠ **它不是可直接复用的包装**（坐标写死）⇒ 挂工具时要**新写一个 `sketch_create_line2(model, x1_mm, y1_mm, x2_mm, y2_mm)` 包装**，形参仍是全 float。台账 limitations 逐字：「⚠ 本包装未接进 MCP 工具层；⚠ 工具层原本用的是 `ISketchManager.CreateLine`（★ **未废弃**）—— ★ **本条不替换它**」 | `solidworks_sketch_create_line2`（含关键词 `create_line`） |
| `sketch_spline` | `tools/prove_spline_with_variant.py`（能力层另有 `scripts/sw_part.sketch_spline`） | `def _one(sw, tag, form):` ／ 能力层 `def sketch_spline(model, points: list)` | `sw` ／ `model` | `tag` str + `form` str ／ `points: list` | **A** | 调用点逐字：`data = win32com.client.VARIANT(pythoncom.VT_ARRAY \| pythoncom.VT_R8, list(PTS))` 紧跟 `ret = C.get_com_member(sm, "CreateSpline2", data, False)` ⇒ ★ **VARIANT 包装是函数体内部的活**，外部只需一个 `list` ⇒ 仍判 A。台账逐字：「★★ **三个条件**：成员名 `CreateSpline2`、数组形态 `VARIANT(VT_ARRAY\|VT_R8, 扁平 list)`、第二参 `False`。」 | ⚠ **已存在**：`solidworks_sketch_spline`（`mcp-server/tool_specs_batch76.py`，`module="sw_part", function="sketch_spline", inject="model"`，形参 `Param("points", list, …)`）★ 动作 = 回填台账 |
| `sketch_spline3_2d` | `tools/prove_createspline3.py` | `def _one(sw, tag, mode):`（2D 分支） | `sw` | `tag` str + `mode` str ⇒ 外部**无坐标** | **A**（2D 用法） | 2D 调用点逐字：`ret = C.get_com_member(sm, "CreateSpline3", _arr(PTS_2D), None, None, False, _byref())`。★ `_arr` 与 out 参都在**函数体内**封装：`def _arr(values, vt=pythoncom.VT_R8): return win32com.client.VARIANT(pythoncom.VT_ARRAY \| vt, list(values))`；`def _byref(): return win32com.client.VARIANT(pythoncom.VT_BYREF \| pythoncom.VT_VARIANT, None)` ⇒ ★ **`Status` 这个 out 形参从不外露**，故不判 C。⚠ 台账 limitations 逐字：「⚠ **本包装未接进 MCP 工具层**；⚠ **曲面上的样条（on-surface）本轮未成**」⇒ ★ on-surface 那一格**要另算**（见 §三） | `solidworks_sketch_create_spline3`（含关键词 `spline`），形参只收 `points_mm: list` |
| `sketch_rotate_or_copy_3d` | `tools/prove_rotate_or_copy_3d.py` | `def _one(sw, tag, do_copy):` | `sw` | `tag` str + `do_copy` bool | **A** | 调用点逐字：`ret = C.get_com_member(sm, "RotateOrCopy3DAboutXYZ", bool(do_copy), 1, True, 0.0, 0.0, 0.0, 0.7853981633974483, 0.0, 0.0)` ⇒ ★ **9 个实参全是 bool/int/float**。台账逐字：「★ **9 参**：`Copy` · `NumCopies` · `KeepRelations` · `BaseX/Y/Z` · `AngleAboutXDir/YDir/ZDir`。」⚠ 前置 `Insert3DSketch` 在本文件里是 `try/except` 包裹的（`C.get_com_member(sm, "Insert3DSketch", True)`）⇒ 挂工具时要单独给一个「开 3D 草图」步 | `solidworks_sketch_rotate_or_copy_3d_sketch`（含关键词 `3d_sketch`）——★ 覆盖率表**没有「复制实体」这一行**，这是唯一能命中的行 |
| `sketch_equation_curve` | `tools/prove_equation_driven_curve.py` | `def _one(sw, tag, args):` | `sw` | `tag` str + `args`（11 元 tuple，成员全是 str/float/bool） | **A** | 调用点逐字：`ret = C.get_com_member(sm, "CreateEquationSpline2", *args)`；台账逐字给出真机实参「`CreateEquationSpline2("", "exp(x)", "", "-1", "1", False, 0.0, 0.0, 0.0, True, True)`」⇒ ★ **全是字符串与数值**，无对象。台账 limitations 逐字：「★ **11 参**：`XExpression` · `YExpression` · `ZExpression` · `RangeStart` · `RangeEnd` · `IsAngleRange` · `RotationAngle`(rad) · `XOffset` · `YOffset` · `LockStart` · `LockEnd`。」 | `solidworks_sketch_equation_spline`（含关键词 `spline`） |
| `sketch_offset_on_surface` | `tools/prove_offset_on_surface_per_example.py` | `def _one(sw, tag, *, offset, reverse, usefront, makeconstruct, do_insert_sketch):` | `sw` | 全 keyword-only 的 float/bool ⇒ **本函数形状是 A** | **B** | ★ 判 B 的依据**不在形参、而在调用序**：本文件自己先跑一层「按对象选边 + 补设 Mark」，函数逐字 `def _select_edges_by_object(doc, indices, mark=1):`，内含 `objs = ss.entities_on_body(doc, "EDGE")` 与 `marked.append(bool(C.get_com_member(mgr, "SetSelectedObjectMark", i, int(mark), -1)))`；调用点 `row["sel"] = _select_edges_by_object(doc, (0, 1, 2, 3), mark=1)`。台账 limitations 逐字：「★★ **三步缺一不可**：① **按对象选边**（★ `Select4`，**不是** `SelectByID2`）；② 补设 **`Mark`**；③ 收尾 **`ISketchManager.InsertSketch(True)`**。」⇒ ★ 挂工具须把 `indices` 提成 `list[int]` 形参并复用那层解析（**转接层**） | `solidworks_sketch_offset_on_surface`（含关键词 `sketch_offset`），形参加 `edge_indices: list[int]` + `mark: int` |
| `curve_and_split` | `scripts/sw_curve_and_split.py` | `def insert_split_line_project(model, is_directional: bool = False, flip_dir: bool = False) -> dict:` ／ `def insert_split_line_silhouette(model) -> dict:` ／ `def insert_curve_through_points(model, points_mm, ) -> dict:` ／ `def insert_mate_reference(model, name: str, primary_entity=None, primary_type: int = 0, primary_alignment: int = 0, primary_align_axes: bool = False) -> dict:` | `model` | ★ **混形态**：`insert_mate_reference` 的 `primary_entity=None` **就是 COM 对象**；另两条分割线**形参全是 bool** 但**官方前置要求调用方带 mark 选好草图/面** | **B** | ★ 对象形参逐字：`:param primary_entity: 主配合的 **`IEntity` 对象**（★ 官方形参类型就是 `Entity`）—— ★ 本模块**收对象**（★ 实体没有名字可用，**事实 32**）。★ 分割线前置逐字：`★★ **调用前必须自己选好**：投影**草图** mark=4 · 要切的**面** mark=1。` 与 `★★ **调用前必须自己选好**：**方向项** mark=**2** · 要切的**面** mark=**1**。` ★ 台账 limitations 逐字：「★ **分割线两条：实现层已真机建成、但未登记成工具**（★ 与「配合参考」同一个原因）：它们的「选择」必须由调用方在**工具层之外**先做好…★ 而 `ToolSpec` 表达不了「先替我选好一个草图与一个面」⇒ ★ 要接**声明式选择器**那一层（`selection` + `sw_selection_spec`）★ 不在本轮草率塞。」★ 但 `insert_curve_through_points(model, points_mm)` 是 **A**（`points_mm` 是 list）★ 且**已挂** | `solidworks_insert_split_line_project` / `solidworks_insert_split_line_silhouette`（含关键词 `split_line`）；`solidworks_insert_mate_reference`（需 `selection: str` 转接）；★ `solidworks_insert_curve_through_points` **已存在**（`mcp-server/tool_specs_batch71.py`，`module="sw_curve_and_split", function="insert_curve_through_points"`）★ 建议**先把这一个既名回填台账** |
| `curve_through_xyz` | `tools/prove_curve_through_xyz.py` ／ 能力层 `scripts/sw_curve_and_split.py::insert_curve_through_points` | `def _one(sw, tag, mode):` ／ `def insert_curve_through_points(model, points_mm, ) -> dict:` | `sw` ／ `model` | `tag` str + `mode` str（`"points"`/`"file"`）／ `points_mm` list | **A** | 三步式调用点逐字：`C.get_com_member(model, "InsertCurveFileBegin")` → `ok = C.get_com_member(doc, "InsertCurveFilePoint", …)` → `steps["End"] = bool(C.get_com_member(doc, "InsertCurveFileEnd"))`；文件式逐字：`row["returned"] = str(C.get_com_member(doc, "InsertCurveFile", str(f)))` ⇒ ★ `InsertCurveFile(FileName)` 只收**一个字符串** ⇒ 文件那一路也判 A。台账逐字：「★★ 2026-10-03（轮 582）**两套用法均真机建成**…判据 = **特征树增量**」 | ⚠ **点式已存在**：`solidworks_insert_curve_through_points`（batch71）★ **文件式尚无工具** ⇒ 建议新增 `solidworks_insert_curve_file`（含关键词 `curve_through_points` 之外的 `curve`；★ 覆盖率表「分割线/投影曲线/组合曲线」行的四个关键词是 `split_line`/`projected_curve`/`composite_curve`/`curve_through_points`，★ **文件式一个都命不中** —— 这是覆盖率表的盲区，不是能力缺口） |

## 二 · 统计

| 判类 | 条数 | id |
|---|---|---|
| **A · 可直接挂** | **12** | `sketch_primitives_b1` · `sketch_edit_ops_b3`（成员级 C ×1）· `sketch_modify_ops` · `sketch_dimension_horizontal` · `sketch_dimension_vertical` · `sketch_slot_types` · `sketch_line2` · `sketch_spline` · `sketch_spline3_2d` · `sketch_rotate_or_copy_3d` · `sketch_equation_curve` · `curve_through_xyz` |
| **B · 要加转接层** | **2** | `sketch_offset_on_surface` · `curve_and_split` |
| **C · 挂不了** | **0**（**条目级 0**；**成员级 1** —— `sketch_edit_ops_b3.sketch_intersect_curves`，依据已逐字引在表内） | — |
| **合计** | **14** | |

### ★★ 本表最重要的一条结论：**14 条里 9 条的工具其实早就存在**

A 表判据是「台账的 `mcp_tools` 字段为空」，而**工具面**另算。逐条核对 `mcp-server/tool_specs_batch*.py` 后：

| 台账 id | 工具面已存在的工具 | 证据 |
|---|---|---|
| `sketch_primitives_b1` | **9 个**（3点矩形 / 3点中心矩形 / 平行四边形 / 切线弧 / 3点弧 / 部分椭圆 / 抛物线 / 圆锥 / 周边圆） | `mcp-server/tool_specs_batch65.py`，9 处 `name="solidworks_sketch_add_…"` |
| `sketch_edit_ops_b3` | **6 个**（剪裁 / 延伸 / 等距 / 圆角 / 线性阵列 / 圆周阵列） | `mcp-server/tool_specs_batch66.py`，6 处 `name="solidworks_sketch_…"` |
| `sketch_modify_ops` | **6 个**（移动 / 旋转 / 缩放 / 伸展 / 翻转 / 镜像） | `mcp-server/tool_specs_batch67.py` 5 处 + `mcp-server/tool_specs_batch41.py` 的 `name="solidworks_sketch_mirror"` |
| `sketch_spline` | **1 个** `solidworks_sketch_spline` | `mcp-server/tool_specs_batch76.py`：`name="solidworks_sketch_spline"` … `module="sw_part", function="sketch_spline"` |
| `curve_and_split` | **1 个** `solidworks_insert_curve_through_points` | `mcp-server/tool_specs_batch71.py`：`module="sw_curve_and_split", function="insert_curve_through_points"` |
| `curve_through_xyz` | 同上那 **1 个** | 同上 |

⇒ ★ **这 6 条的最小动作不是「写工具」，而是「回填台账的 `mcp_tools`」** —— 台账与工具面**不是「没实现」，而是「没对账」。
⇒ ★ 其余 8 条（`sketch_dimension_horizontal` / `…_vertical` / `sketch_slot_types` / `sketch_line2` / `sketch_spline3_2d` / `sketch_rotate_or_copy_3d` / `sketch_equation_curve` / `sketch_offset_on_surface`）**才是真要新写 ToolSpec 的**；其中 7 条 A 类、1 条 B 类。

## 三 · 拿不准处（逐条写明，不猜）

1. **★ `Insert3DSketch` 的返回值自相矛盾，两处记载对不上。**
   `sketch_edit_ops_b3` 的 limitations 逐字写「`Insert3DSketch` 在本机回 `None` ⇒ 包装留在模块里但**不挂工具**」；
   而 `sketch_rotate_or_copy_3d` 的调用点把同一个调用 `try/except` 掉（`C.get_com_member(sm, "Insert3DSketch", True)`）且**后续真机建成**（段 1 → 2）。
   ⇒ **两个记录都可能是真的**（回 `None` 但确实开了 3D 草图 —— 与本仓「`None` 返回值不可信」的既有教训同族）。
   ★ **本表未替它们裁决**：在真机单变量对照之前，`sketch_rotate_or_copy_3d` 的 3D 草图前置**按「可达但返回值不可信」处理**。
2. **★ `sketch_spline3_2d` 的 on-surface 那一格我判不了 A。**
   官方 5 参里 `Surfs` 是 **`ISurface` 数组**、`Direction` 是 **`IMathVector` 数组**，而 `tools/prove_createspline3.py` 的 on-surface 分支确实在造这两个对象
   （`_arr([surf], pythoncom.VT_DISPATCH)` / `_arr([v, v], pythoncom.VT_DISPATCH)`，★ 且代码注释逐字记着 `CreateVector` 在 `IMathUtility` 上「**找不到成员**」）。
   ⇒ ★ 台账该条 label 写的是「**2D** 用法」⇒ **我只对 2D 判 A**；on-surface 若要挂，须另立一条并按 **B** 走（对象形参 + 正确的 `IMathUtility` 入口）。
   ⇒ 按铁律 5，**正确入口本轮查不到**（台账 limitations 逐字：「★ **下一步**：换到**正确的入口**取 `IMathUtility`」—— 那是当时的待办，本轮未复验）。
3. **★ `sketch_dimension_horizontal` / `…_vertical` 我按 A 判，但它们**必须补一个形参**才安全。**
   两条 limitations 都逐字写「★★ **前置：必须先选中实体**…而**不选时**它会弹「修改」框等人填数（★ 而那会**看起来像挂死**）」。
   ⇒ 严格按现形参（`model, x_mm, y_mm`）挂出去会命中那个弹窗 ⇒ ★ 建议**同时补 `selection: str`** 并接 `scripts/sw_sketch_edit_ops.py::select_sketch_segment`。
   ★ 这属于「形参新增」而不是「对象形参」，故仍判 **A**，但**不是零改动**。
4. **★ `curve_through_xyz` 的文件式（`InsertCurveFile`）挂上去会命不中覆盖率表任何关键词。**
   `D:\SW-coverage-tool\gen_user_feature_coverage.py` 里「分割线/投影曲线/组合曲线」一行的四个关键词是
   `("split_line", "projected_curve", "composite_curve", "curve_through_points")`。
   ⇒ ★ 这是**覆盖率表的盲区**，不是能力的缺口；本表按实情写 `solidworks_insert_curve_file` 并在此标注，**不去改覆盖率表**（不在本轮范围）。
5. **★ `sketch_rotate_or_copy_3d` 与 `sketch_equation_curve` 的覆盖率关键词没有对应行。**
   关键词表里「草图」20 行**没有「复制实体」，也没有「方程式曲线」**。
   ⇒ 我给的名字 `solidworks_sketch_rotate_or_copy_3d_sketch`（含 `3d_sketch`）与 `solidworks_sketch_equation_spline`（含 `spline`）
   是**为了能被计数而选的**，其中 `…_equation_spline` 的 `spline` 会**与 `sketch_spline` 同记一行**（覆盖率表不区分）—— 这会**高估**「样条曲线」那格的覆盖度，**如实报出**。
6. **★ 14 条里有 5 条的「实现」其实在 `tools/prove_*.py` 而不是 `scripts/`。**
   `sketch_slot_types` / `sketch_line2` / `sketch_spline3_2d` / `sketch_rotate_or_copy_3d` / `sketch_equation_curve` 的 `source_evidence` 指名的就是探针文件。
   ⇒ 这些**不是可复用的包装**（坐标/参数多写死在函数体、且函数自带 `new_document` / `CloseDoc` 的探针脚手架）
   ⇒ ★ 挂工具时**必须新写一层 `scripts/sw_*.py` 包装**，本表已按「形状可挂」判类，但**工作量比已有包装大**。

## 四 · 复算方法（本表每行可独立重算）

```
① 台账：json.loads(capabilities.yaml)["capabilities"] → 按 id 取 source / source_evidence / limitations
② 实现：source_evidence 里点名的文件 → grep "def <目标函数>" 读形参表
③ 判类：形参表里有 COM 对象 或 官方前置要求调用方带 mark 选好实体 ⇒ B；其余按 A/C
④ 已存在的工具：在 mcp-server/tool_specs_batch*.py 里 grep 工具名（★ 不 import、不碰 COM）
⑤ 关键词表：D:\SW-coverage-tool\gen_user_feature_coverage.py 的 FEATURE_ROWS 元组
```