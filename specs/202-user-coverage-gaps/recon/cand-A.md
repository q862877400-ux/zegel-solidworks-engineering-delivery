# 候选 A · 最小包装层（`scripts/` 下新建薄再导出模块，ToolSpec 指向它）

> **交付边界**：本文件是**候选设计**，不是实现。落地时新建两个文件 ——
> `scripts/sw_drawing_ops.py`（薄再导出）+ `mcp-server/tool_specs_batch73.py`（6 条 ToolSpec）。
> ★ 本轮**只写了这一个候选文件**：未注册、未改任何已有文件、未跑 SolidWorks / 未跑 pytest。
> ⚠⚠ **本文件原来那一版是另一个写法**（「零新代码，直接 `module="sw_drawing"` 直挂」）——
> 那与本轮指定的**角度**（必须在 `scripts/` 下新建薄包装层）不同，故按指定角度重写；
> 被替换版里**仍然成立**的逐行取证（registry 调用契约、门禁读码结论、`stitched` 判定）已并入本版。

---

## 一、方案说明

### 1.1 角度的落点：**一个不写逻辑、只列名字的 `scripts/` 模块**

注册器的导入契约（`mcp-server/tool_registry.py:524`，逐字）：

```python
mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
```

⇒ `module` **只能是 `scripts/` 下的合法模块名**；subskill 父目录 `solidworks-engineering-drawing`
**带连字符**（非合法标识符）⇒ 进不了 `module`。本仓已铺的桥 `scripts/sw_drawing.py`
用 `importlib.util.spec_from_file_location` 按**文件路径**加载那个实现，再逐个
`globals()[_name] = getattr(_MODULE, _name)` 导出（`scripts/sw_drawing.py:19-29`）。

本角度的做法是**在桥之上再加一层薄再导出**：`scripts/sw_drawing_ops.py` 显式列出需要的名字，
ToolSpec 的 `module` 指向它。

★ **诚实说明（不夸大这个角度的价值）**：直接写 `module="sw_drawing"` **也能取到这些函数**
（旁证：`tests/test_sw_drawing_structure.py:6-17` 就是 `from scripts.sw_drawing import auto_insert_center_marks …`）。
选"再加一层"的三个理由，都不是"否则跑不起来"：

1. **显式锁名**：`scripts/sw_drawing.py:25-27` 的 `__all__` 是从实现里**反射式**取的
   （无 `__all__` 时取全部非下划线名）。⇒ 实现端一次改名/删名，工具面会**静默换人**。
   薄模块把名字写成**字面量清单**，导入期即炸。
2. **单一落点**：后续真要加「读回 / 判据 / 单位换算」时只动这一个文件，不必回去改
   `subskills/` 里那份共享实现（那份还被 `server.py` 与测试共用）。
3. **命名一致**：本仓既有包装层一律 `*_ops.py` / `*_edit_ops.py` / `*_ref_ops.py`
   （`sw_sketch_edit_ops` · `sw_surface_ref_ops` · `sw_sketch_modify_ops`）⇒ `sw_drawing_ops` 合群。

### 1.2 薄包装模块长这样（**零逻辑、零 COM、零单位换算**）

```python
"""★ 工程图 8 项功能的薄再导出层：ToolSpec 只指向本模块。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（ToolSpec 声明层的落点）· 规格 `specs/202-user-coverage-gaps`
# 文件:   scripts/sw_drawing_ops.py（候选 A，未落地）
# 定位:   把 `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`
#         里**已有实现**的 6 个工程图函数，按名字再导出一遍。
#   ★ 本文件**不含任何逻辑**：不换算、不判据、不选面、不兜底。
#   ★ 之所以要有这一层（而不是 ToolSpec 直接写 `module="sw_drawing"`）：
#     `scripts/sw_drawing.py:25-27` 的 `__all__` 是**反射式**取的
#     ⇒ 实现端改名/删名会让工具面**静默换人**；这里写字面量清单，导入期即炸。
#   ★ 单位换算（毫米→米）**不在这里**，而在 ToolSpec 的 `derived_args`
#     —— 规则 2 要求「换算只在边界做一次」，注册器边界就是那一次
#     （`mcp-server/tool_registry.py:278-285` 明写「单位换算也放这里」）。
# 官方签名依据: 逐个函数的来源块在 `drawing_workflow.py` 各 def 处；
#   本文件不新增任何 COM 调用。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级：全部函数沿用其自身来源块的等级（`add_detail_view` 自述"未在本机实测" ⇒ `stitched`）。
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

try:
    from .sw_drawing import (
        add_detail_view,
        add_note,
        add_section_view,
        add_sheet,
        auto_insert_center_marks,
        set_sheet_format,
    )
except ImportError:      # pragma: no cover - 直接以 scripts/ 为根导入时
    from sw_drawing import (  # type: ignore
        add_detail_view,
        add_note,
        add_section_view,
        add_sheet,
        auto_insert_center_marks,
        set_sheet_format,
    )

__all__ = [
    "add_detail_view",
    "add_note",
    "add_section_view",
    "add_sheet",
    "auto_insert_center_marks",
    "set_sheet_format",
]
```

### 1.3 挂得上的**硬天花板**（读 `tool_registry.py:490-525` 的调用体得出）

```python
kwargs = {}
for p in spec.params:                                    # 表面参数 → 目标形参（param_alias 可映成 None）
    ...
kwargs[inject_as or inj] = resolver(params)              # ★ 注入键 = inject 字符串本身
...
mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
return getattr(mod, spec.function)(**kwargs)             # ★ 只用关键字传参
```

⇒ 两个必要条件，缺一不可：

1. **注入键 = `inject` 字符串 = 目标函数首参的**字面名**。`RESOLVERS` 里已有
   `"drawing_model": resolve_model`（`mcp-server/register_capabilities.py:136`）⇒
   只有首参**叫 `drawing_model`** 的函数能吃这个注入（写 `"model"` 会
   `RuntimeError: 声明了 inject=… 但注册时没给对应的解析器`，`tool_registry.py:502-506`）。
2. **其余形参必须是 JSON 可表达的类型**（`Param.kind` 只做类型注解，跑 Pydantic）。
   ⇒ 首参是 **COM 对象**的函数，声明式挂不了 —— 这是**架构性**的，不是参数没找对。
   ★ 附带好消息：调用是 `(**kwargs)`，所以 `add_detail_view` 里 `*` 之后的
   **keyword-only 形参**照样能传。

### 1.4 与另两个角度的差别

> ⚠ 我**看不到**另外两个候选的文件，下面按**轴**对比，不臆测它们的细节。

| 轴 | 本角度（薄再导出） | 对照轴 |
|---|---|---|
| 新增文件 | `scripts/sw_drawing_ops.py`（**零逻辑**） | 另两角度多半要落**带逻辑**的包装/适配模块 |
| 目标函数 | **原样再导出**，一个字都不改 | 加厚包装多半会改写函数体、补回读/报告化 |
| 单位换算 | 放在 **ToolSpec `derived_args`**（注册器边界，唯一一次） | 放在包装函数体内 |
| 注册器契约 | **不动** `tool_registry.py` / `register_capabilities.py` | 改注册器/解析器的角度会动它们 |
| 缺口处理 | 挂不了的**如实标出来并写清天花板**，不夹带修复 | 加厚包装会顺手把缺口补上（值更大，改动面也更大） |

一句话：**本角度的价值是"一张可信的挂载清单 + 一层锁名的薄壳"；代价是孔表 / 修订表 / 表面粗糙度三项在本角度下交付为 0 条工具。**

---

## 二、逐项判定（8 项功能 → 6 条工具 / 3 项挂不了）

| # | 功能 | 落地函数（**已逐行读 def**） | 判定 |
|---|---|---|---|
| 1 | 剖面视图 | `add_section_view(drawing_model, x, y)` — `drawing_workflow.py:998` | ✅ 挂 |
| 2 | 局部视图 | `add_detail_view(drawing_model, x, y, scale=2.0, *, style, label, show_type, full_outline, jagged_outline, no_outline, shape_intensity)` — `:1022-1035` | ✅ 挂 |
| 3 | 中心符号线 | `auto_insert_center_marks(drawing_model, requirements)` — `:1883` | ✅ 挂 |
| 4 | 孔表 | **无** | ❌ 挂不了（见 §四·R1） |
| 5 | 修订表 | **无** | ❌ 挂不了（见 §四·R1） |
| 6 | 表面粗糙度 | **本仓无实现** | ❌ 挂不了（见 §四·R2） |
| 7 | 注释 | `add_note(drawing_model, x, y, text)` — `:1238` | ✅ 挂 |
| 8 | 图纸格式 / 模板 | `set_sheet_format(drawing_model, format_path)` — `:1400`；`add_sheet(drawing_model, paper_size=7, template_path="", first_angle=True)` — `:1411` | ✅ 挂（**拆 2 条**：改当前页图框 / 新建页） |

⇒ **题述「已实现 8 项」实际只有 5 项能接成工具**；本角度交付 **6 条**（第 8 项拆两条）。

---

## 三、完整可粘贴的 ToolSpec 代码块

> ★ 每条 `params` 都**照 `drawing_workflow.py` 的 def 行逐字抄**，行号标在注释里。
> ★ 落点文件名 `mcp-server/tool_specs_batch73.py`（**候选，未落地、未注册**）。

```python
"""★ 覆盖面缺口批（第二批）：工程图 5 项功能的薄包装层（指向 sw_drawing_ops）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（ToolSpec 声明层）· 规格 `specs/202-user-coverage-gaps`
# 文件:   mcp-server/tool_specs_batch73.py（候选 A，未落地）
# 定位:   把 `scripts/sw_drawing_ops.py`（薄再导出）里那 6 个**原样**函数接成 MCP 工具。
#
#   ★★ 本批**只声明**，不改任何实现、也不动注册器契约：
#      · `module="sw_drawing_ops"` —— ★ 因为 `tool_registry.py:524` 要求 `module`
#        只能是 `scripts/` 下的合法模块名，而 subskill 父目录 `solidworks-engineering-drawing`
#        **带连字符**（非合法标识符）⇒ 必须经 `scripts/` 这一层（该层已有桥 `scripts/sw_drawing.py`，
#        本批再叠一个**零逻辑**的薄再导出 `scripts/sw_drawing_ops.py`）。
#      · `inject="drawing_model"` —— ★ 必须写这个名字：`RESOLVERS` 里是
#        `register_capabilities.py:136` 的 `"drawing_model": resolve_model`
#        （工程图文档同样是 `IModelDoc2` ⇒ 复用 `resolve_model`，与 `asm_model` 同一手法）；
#        写 `"model"` 会因注入键不匹配而 `TypeError`（`tool_registry.py:507` 把注入
#        写成 `kwargs[inject_as or inj]`，键就是 inject 字符串）。
#
#   ★★ 可挂性的硬天花板（`tool_registry.py:507` + `:525`）：
#      · 注入以 `kwargs["drawing_model"]` 落位，且目标函数**只收关键字实参**
#        ⇒ **首参必须字面名为 `drawing_model``；
#      · `Param.kind` 只能表达 JSON 可反序列化的类型
#        ⇒ **首参是 COM 对象的函数一律声明式挂不了**（本批 §四 的 R1/R2）。
#
#   ⚠ 三项**不接**（逐条取证见本文件 §四）：
#      孔表 / 修订表（官方入口是 `IView.InsertHoleTable3` / `ISheet.InsertRevisionTable2`，
#      本仓**无实现**；而 `drawing_workflow.insert_table_annotation` 的 `table_type`
#      落在官方的 **AnchorType** 槽里，建不出这两种表）· 表面粗糙度（本仓**无任何实现**）。
#   许可:   本仓库 MIT。无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

from tool_registry import Param, ToolSpec

_MODULE = "sw_drawing_ops"


# ── 共用：毫米 → 米的边界换算（规则 2：换算**只做一次**，就在这）─────────
# ★ 实现侧 `x` / `y` 吃的是**米**：`add_note` 的 docstring :1242-1243 逐字写「（米）」；
#   官方 `IView.InsertHoleTable3` 的参数说明也逐字写 "X coordinate **in meters**"。
# ★ `param_alias` 把 `x_mm` / `y_mm` 映成 `None` = **不直传给目标函数**
#   （`tool_registry.py:495`），因此 `derived_args` 产出的 `x` / `y` 不会撞名
#   （`:517-522` 的 clash 检查）。
# ⚠ 风险见本文件 §四·R3：模块级共享函数，被 4 条工具引用。
def _xy_m(p):
    return {"x": float(p.x_mm) / 1000.0, "y": float(p.y_mm) / 1000.0}


_BATCH73: list[ToolSpec] = [
    # ── 1. 剖面视图 ────────────────────────────────────────────────
    #: def add_section_view(drawing_model, x, y)   —— drawing_workflow.py:998
    ToolSpec(
        name="solidworks_drawing_section_view",
        title="Drawing Section View",
        module=_MODULE, function="add_section_view",
        inject="drawing_model",
        param_alias={"x_mm": None, "y_mm": None},
        derived_args=_xy_m,
        params=[
            Param("x_mm", float, description="剖视图放置点 X（**毫米**；实现收的是**米**，"
                                             "本层换算一次 ⇒ /1000）。"),
            Param("y_mm", float, description="剖视图放置点 Y（**毫米**；同上）。"),
        ],
        doc="★ **剖面视图**：`drawing_workflow.py:998` `add_section_view(drawing_model, x, y)`"
            " → `IDrawingDoc.CreateSectionViewAt5(x, y, 0, \"\", 0, None, 0)`（官方 **7 参**，逐位对上）。"
            "★ 官方 Remarks 逐字：「**Before calling this method, select the section line or lines** "
            "to use as a section line.」⇒ ★ **调用前必须在界面上选好剖切线**；"
            "本实现**不做选择**（规则 3 也禁止裸坐标选），工具层同样替不了它。"
            "★ 形参逐字只有 `drawing_model, x, y` 三个 ⇒ 表面不多给（z / SectionLabel / Options / "
            "ExcludedComponents / SectionDepth 在实现里是**写死的常量**）。"
            "⚠ 见本批 §四·R4：`ExcludedComponents` 传的是 `None`，而官方形参是 `System.object`。",
    ),

    # ── 2. 局部视图 ────────────────────────────────────────────────
    #: def add_detail_view(drawing_model, x, y, scale=2.0, *, style=…, label="", show_type=…,
    #:                    full_outline=False, jagged_outline=False, no_outline=False,
    #:                    shape_intensity=0)   —— drawing_workflow.py:1022-1035
    ToolSpec(
        name="solidworks_drawing_detail_view",
        title="Drawing Detail View",
        module=_MODULE, function="add_detail_view",
        inject="drawing_model",
        param_alias={"x_mm": None, "y_mm": None},
        derived_args=_xy_m,
        params=[
            Param("x_mm", float, description="详图放置点 X（**毫米**；实现收米）。"),
            Param("y_mm", float, description="详图放置点 Y（**毫米**；同上）。"),
            Param("scale", float, default=2.0,
                  description="比例**分子 Scale1**；分母 Scale2 在实现里固定传 1.0 ⇒ "
                              "`scale=2` 即 2:1（来源块 :1013-1014）。"
                              "⚠ 它是**无量纲比值**、不是长度 ⇒ 表面**不加** `_mm`"
                              "（且 `_LEN_WORDS` 也不含 `scale`，门禁不会拦）。"),
            Param("style", int, default=0,
                  description="详图样式 `swDetViewStyle_e`（实现默认 `DET_VIEW_STYLES[\"standard\"]`，"
                              ":61-67 静态照录官方全 5 项）：0=standard · 1=broken · 2=leader · "
                              "3=noleader · 4=connected。"),
            Param("label", str, default="",
                  description="标签文字（官方第 7 参 `LabelIn`；默认空串）。"),
            Param("show_type", int, default=0,
                  description="圆/轮廓显示 `swDetCircleShowType_e`（实现默认 "
                              "`DET_CIRCLE_SHOW_TYPES[\"profile\"]`，:78-82 官方全 3 项）："
                              "0=profile · 1=circle · 2=dont_show。"),
            Param("full_outline", bool, default=False,
                  description="完整轮廓（官方 `FullOutline`）。"),
            Param("jagged_outline", bool, default=False,
                  description="锯齿轮廓（官方 `JaggedOutline`）。"),
            Param("no_outline", bool, default=False,
                  description="无轮廓（官方 `NoOutline`）。"),
            Param("shape_intensity", int, default=0,
                  description="锯齿轮廓强度，官方有效范围 1(最强)–5(最弱)，**仅当** "
                              "`jagged_outline=True` 且 `no_outline=False` 时生效"
                              "（来源块 :1019-1020）⇒ 默认 0 = 不生效。"),
        ],
        doc="★ **局部视图 / 详图**：`drawing_workflow.py:1022` `add_detail_view(...)`"
            " → `IDrawingDoc.CreateDetailViewAt4`，官方 **12 参**，实现**补齐到 12 参**"
            "（来源块 :1012 逐字：原实现只传 7 个）。"
            "★ `*` 之后的形参是 keyword-only —— **注册器是 `f(**kwargs)` 调用（:525）⇒ 照样传得进去**。"
            "⚠⚠ 来源块**自述**：「本函数为静态签名比对后修正，**未在本机实测**（见 AGENTS.md 铁律 2）」"
            "（:1018 / :1045）⇒ 按铁律 6，本工具**只能记 `stitched`，不得记 `verified`**。",
    ),

    # ── 3. 中心符号线 ──────────────────────────────────────────────
    #: def auto_insert_center_marks(drawing_model, requirements) -> dict  —— :1883
    ToolSpec(
        name="solidworks_drawing_center_marks",
        title="Drawing Center Marks (Auto)",
        module=_MODULE, function="auto_insert_center_marks",
        inject="drawing_model",
        params=[
            Param("requirements", list,
                  description="要求列表，**每项一个 dict**，键逐字取自实现 `:1900-1904`："
                              "`id`(str) · `view`(str) · `count`(int) · `targets`(list[str])。"
                              "★ `view` 经 `_normalise_orientation`(:631-647) 归一，"
                              "**合法值只有 3 个**：`front` / `top` / `right`"
                              "（别名含 `frontview` / `前视` / `主视` / `上视` / `俯视` / `右视`）。"
                              "★ `targets` 取值域 = `AUTO_CENTER_MARK_TARGETS`(:45-49) 全量 3 项："
                              "`holes`(1) · `fillets`(2) · `slots`(4)（内部按位或）。"
                              "★ 传**空列表** ⇒ 实现走 `status=\"not_requested\"` 直接返回，**不动模型**。"),
        ],
        doc="★ **中心标记 / 中心符号线**：`drawing_workflow.py:1883` "
            "`auto_insert_center_marks(drawing_model, requirements)` → `IView.AutoInsertCenterMarks2`。"
            "★ **判据是「实体数量回读」**（docstring :1884：before/after/created_count）"
            "，不是返回值 ⇒ 规则 6 已在实现内满足。"
            "★ 函数**自己**按 `_map_standard_views_from_sheet_views` 匹配标准视图 ⇒ "
            "表面**不传**任何选择器（规则 3 在这一格不是问题）。"
            "⚠ 图纸上没有对应方位的标准视图 ⇒ 每条 requirement 回 "
            "`error_code=\"DRAWING_CENTER_MARK_REQUIREMENT_UNRESOLVED\"`；"
            "回 `DRAWING_CENTER_MARK_DRAWING_SAVE_REQUIRED` ⇒ **图纸没保存，先存盘再跑**。",
    ),

    # ── 4. 注释 ────────────────────────────────────────────────────
    #: def add_note(drawing_model, x, y, text)   —— :1238
    ToolSpec(
        name="solidworks_drawing_note",
        title="Drawing Note",
        module=_MODULE, function="add_note",
        inject="drawing_model",
        param_alias={"x_mm": None, "y_mm": None},
        derived_args=_xy_m,
        params=[
            Param("x_mm", float, description="注释锚点 X（**毫米**；实现 docstring :1242 逐字写「（米）」）。"),
            Param("y_mm", float, description="注释锚点 Y（**毫米**；docstring :1243）。"),
            Param("text", str, description="写入图纸的非空文字。"
                                           "★ 实现对空/纯空白与非有限坐标**不抛异常**，"
                                           "而是回 `status=\"failed\"` · "
                                           "`error_code=\"DRAWING_NOTE_INPUT_INVALID\"`（:1247-1254）。"),
        ],
        doc="★ **工程图文字注释**：`drawing_workflow.py:1238` `add_note(drawing_model, x, y, text)`"
            " → `IModelDoc2.InsertNote`，随后 `_set_annotation_position` 定位 + `ForceRebuild3`"
            " + 回读（:1263-1267）。"
            "★ 返回**可审计 dict**（COM 回读文字、坐标、边界），**不是 COM 对象** ⇒ MCP 表面可直接读。",
    ),

    # ── 5. 图纸格式（图框）· 改当前页 ──────────────────────────────
    #: def set_sheet_format(drawing_model, format_path)   —— :1400
    ToolSpec(
        name="solidworks_drawing_sheet_format",
        title="Drawing Sheet Format (Template)",
        module=_MODULE, function="set_sheet_format",
        inject="drawing_model",
        params=[
            Param("format_path", str,
                  description="图纸格式文件路径（`.slddrt`）—— 实现直传 `ISheet.SetTemplateName`，"
                              "本工具**不做存在性校验**（官方未给预检步骤）。"),
        ],
        doc="★ **图纸格式 / 图框**：`drawing_workflow.py:1400` "
            "`set_sheet_format(drawing_model, format_path)`"
            " → `drawing_model.GetCurrentSheet().SetTemplateName(format_path)`。"
            "★ 作用于**当前图纸页**（`GetCurrentSheet`）；**新建页**是下一条。"
            "⚠ 见本批 §四·R5：本函数**不 rebuild、不回读**，成功与否只有官方那个 bool 返回值 —— "
            "与「不静默成功」的纪律有张力；本角度**保持薄、不改实现**，如实标出。",
    ),

    # ── 6. 新增图纸页 ──────────────────────────────────────────────
    #: def add_sheet(drawing_model, paper_size=7, template_path="", first_angle=True)   —— :1411
    ToolSpec(
        name="solidworks_drawing_sheet_add",
        title="Drawing Add Sheet",
        module=_MODULE, function="add_sheet",
        inject="drawing_model",
        params=[
            Param("paper_size", int, default=7,
                  description="纸张大小（docstring :1417-1418 的表逐字照抄）："
                              "0=A · 1=B · 2=C · 3=D · 4=E · 5=A4 · 6=A3 · **7=A2** · 8=A1 · 9=A0。"
                              "⚠ 这张表与 SolidWorks 的 `swPaperSize_e` **不是同一套编号**；"
                              "本工具**原样透传**实现里的表，不做换算（出处见 §四·R6）。"),
            Param("template_path", str, default="",
                  description="图纸格式模板路径（`.slddrt`），空串 = 不指定。"),
            Param("first_angle", bool, default=True,
                  description="第一角投影为 True（实现直传 `NewSheet4` 的 `bool(first_angle)`）。"
                              "★ 刻意用 `bool` 而不是 `projection: str`：注册器 `check_spec` 对 "
                              "`kind is bool` **豁免**规则 2 的长度/角度后缀检查"
                              "（`tool_registry.py:412` / `:423`）⇒ 这个名字不会被门禁拦。"),
        ],
        doc="★ **新增图纸页**：`drawing_workflow.py:1411` "
            "`add_sheet(drawing_model, paper_size=7, template_path=\"\", first_angle=True)`"
            " → `IDrawingDoc.NewSheet4`（官方 16 参，实现逐位全填）。"
            "★ 与第 5 条分工：本条**建页**，`set_sheet_format` **改当前页的图框**。",
    ),

    # ── ✗ 故意**不挂**的：孔表 / 修订表 ─────────────────────────────
    #  ToolSpec(
    #      name="solidworks_drawing_hole_table",
    #      title="Drawing Hole Table",
    #      module=_MODULE, function="insert_table_annotation",
    #      inject="drawing_model",
    #      # ★★ 下面这个拼法是**错的**，写出来是为了把**为什么错**钉在代码里：
    #      #   `insert_table_annotation(drawing_model, x, y, table_type, row, column, *, template, use_anchor_point)`
    #      #   官方 `InsertTableAnnotation2` 的签名逐字是
    #      #   `(Bool UseAnchorPoint, Double X, Double Y, Int AnchorType, String TableTemplate, Int Rows, Int Columns)`
    #      #   ⇒ 实现把它叫 `table_type` 的那个 int 落在**官方 AnchorType 槽**里
    #      #      （`C:\swapi\types\IDrawingDoc\InsertTableAnnotation2.md:14`、`:20`）。
    #      #   官方 `swTableAnnotationType_e`（HoleChart=1 / RevisionBlock=3）**查得到**
    #      #   （`C:\swapi\enums\swTableAnnotationType_e.md:23,25`），但它**不是**这个参数的取值域。
    #      #   ⇒ 传 1 或 3 **建不出孔表/修订表**（只会换锚点）。
    #      #   真入口是 `IView.InsertHoleTable3`（`C:\swapi\types\IView\InsertHoleTable3.md:14`）
    #      #   与 `ISheet.InsertRevisionTable2`（`...\ISheet\InsertRevisionTable2.md:14`），
    #      #   宿主分别是 **IView / ISheet** ⇒ 本仓**无实现**，且不是 `drawing_model` 上能直挂的入口。
    #      #   ⇒ 要接这一格，必须**补实现**（角度 B 的活），不在本薄层范围内。
    #      #  )
]

#: ★★ 注册器按 `SPECS_*` 找
SPECS_BATCH73 = _BATCH73
```

---

## 四、风险与未决

### R1 ★★ 孔表 / 修订表**挂不了** —— 且**不是**"首参是 COM 对象"那条老原因，是**更靠前的一层**

三段证据，逐条可复核：

1. **唯一那个"通用表注解"入口选错了参数槽**。`drawing_workflow.py:2306`
   `insert_table_annotation(drawing_model, x, y, table_type, row, column, *, template, use_anchor_point)`
   → `:2326-2329` 走 `InsertTableAnnotation(float(x), float(y), int(table_type), int(row), int(column))`。
   ★ 官方签名逐字：`InsertTableAnnotation(Double X, Double Y, Int AnchorType, Int Rows, Int Columns)`
   （`C:\swapi\types\IDrawingDoc\InsertTableAnnotation.md:14`，第 3 个 int 是 **AnchorType**）。
   ⇒ 实现叫 `table_type` 的那个数**落在锚点槽**里，**建不出孔表，也建不出修订表**。
   ★ 而且 `swTableAnnotationType_e`（HoleChart=1 / RevisionBlock=3）**是查得到的**
   （`C:\swapi\enums\swTableAnnotationType_e.md:23,25`）⇒ 实现来源块 :2412-2413 那句
   「其枚举在两套官方源里都查不到」**是错的**（但纠正它也不改变结论：那个枚举管的是
   `swTableAnnotation` 其它成员，**不是** `AnchorType`）。
2. **官方真正的入口本仓没有实现**：`IView.InsertHoleTable3`（9 参，`C:\swapi\types\IView\InsertHoleTable3.md:14`）
   与 `ISheet.InsertRevisionTable2`（7 参，`C:\swapi\types\ISheet\InsertRevisionTable2.md:14`）。
   ★ 宿主是 **IView / ISheet**，不是 `IModelDoc2` ⇒ 即便补实现，也得先从 `drawing_model` 取出视图/图纸页。
   ★ 另注：`InsertHoleTable3` 的第 9 参 `ManualTags` 是 `System.object` **数组** ⇒
   与已知事实 47/68 同族，pywin32 迟到绑定下**到不了**（`ManualTags` 留空是否豁免，未核）。
3. **"改修订行"那组函数首参是 COM 对象**，声明式挂不了（§1.3 的第 2 个必要条件）：
   `add_revision(revision_table, revision)` `:2489` · `delete_revision(revision_table, index, mark_deleted)` `:2496`
   · `get_current_revision(revision_table)` `:2503` · `get_hole_table(table)` `:2425`
   · `get_revision_table_feature(table)` `:2446` —— 首参分别是
   `IRevisionTableFeature` / `IHoleTableAnnotation` / `IRevisionTableAnnotation`。

⇒ **孔表 / 修订表两项，在本角度下交付 0 条工具**；要接必须**补实现**（另两个角度的活）。

### R2 ★ 表面粗糙度**本仓无实现**（不是"挂不上"，是"没有函数可导出"）

- 全 `subskills/solidworks-engineering-drawing/` grep `粗糙|Roughness|SurfaceFinish` ⇒ **3 处命中，全是散文**：
  `SKILL.md:41` · `references/review.md:19` · `references/api-lookup.md:11`（后两者是**文档里列 API 名字**）。
- `drawing_workflow.py` **0 处**；`scripts/` 下 `InsertSurfaceFinishSymbol*` 只出现在
  `scripts/sw_api_sldworks.py` 的**参数个数索引表**（`:3649/:5735/:6363/:6785`）与
  `scripts/sw_drawing_view.py:275` 的同类索引里，**没有包装函数**。
- 官方入口查得到：`C:\swapi\types\IDrawingDoc\InsertSurfaceFinishSymbol.md` ·
  `...\IModelDoc2\InsertSurfaceFinishSymbol2.md` · `...\IModelDocExtension\InsertSurfaceFinishSymbol3.md`。
- ⇒ 按铁律 5：**如实标注"无实现"，不编签名、不出工具。**

### R3 `_xy_m` 是共享的单一换算点（接受，但要点名）

模块级一个函数被 **4 条**工具引用 ⇒ 改一处动四条。这是本角度"少写代码"的代价，
**必须在评审里点名**，否则后人会以为每条各自换算。

### R4 `add_section_view` 的 `ExcludedComponents=None`（未核）

官方形参是 `System.object`，实现直传 `None`（`:1000`）。pywin32 对这类槽常要求
空 Dispatch `VARIANT`（已知事实 12 / 33 同族）。⇒ **该实现到不到得了未核**；
`tools/prove_drawing_batch.py:664` 有 `case_v2_section_view(sw, excluded="empty_dispatch"/"empty_array")`
的对照探针，但**本轮按指示没跑**。本角度**不改实现**，如实标注。

### R5 `set_sheet_format` 没有判据

`:1400-1408` 就是两行：`GetCurrentSheet().SetTemplateName(path)`，**不 rebuild、不回读**。
官方那个 bool 返回值按本项目纪律不可信 ⇒ 失败会静默。保持薄层不改实现，但工具 `doc` 里写明。

### R6 `add_sheet` 的 `paper_size` 表出处没读到

docstring `:1417-1418` 自带 `0=A … 9=A0`、默认 `7=A2`（与模块顶部 `PAPER_SIZES` 的 `A2:7` 一致）。
★ 但它**不是** SolidWorks `swPaperSize_e` 的编号 ⇒ 按铁律 5 记为「本轮未核实出处」，**原样透传**。

### R7 门禁读码结论（**未实证**，本轮没跑 `check_spec`）

- `x_mm` / `y_mm` **能过规则 3**：`_BARE_COORD_NAMES`（`:93`）是精确表 `{"x","y","z","point","coordinate"}`，
  不含 `x_mm`；`_looks_like_coord_component` 在 `:128` 对 `_mm` 结尾**直接放行**。
- ⚠ **同一文件 `:125-126` 的注释**却声称"`x_mm`/`y_mm`/`z_mm` 被规则 3 拦、两条规则自相矛盾"
  ⇒ **注释与代码不一致**。本方案按**代码**走，并把这条注释矛盾列为待清理项。
- 长度/角度后缀：`scale`（`_LEN_WORDS` 不含它）、`shape_intensity`、`paper_size`、`count` 均不触发。

### R8 `Param("requirements", list)` 未在本仓实证

本仓见过的复杂参数只有 `dict`（`mcp-server/tool_specs_batch41.py:58,69` 的 `Param("spec", dict, …)`）。
`list` 走 Pydantic v2 裸 `list` ⇒ 推断为 `list[Any]`、JSON schema `{"type":"array"}`，**未实测**。

### R9 静态可解析性（本轮未做）

`requirements` 的 dict 键由**运行时** `requirement.get("id")` 之类消费，静态抓不到
⇒ 即便门禁跑起来，这条的**键名契约无人看守**。⇒ 建议同批补一条纯数据测试
（照 `tests/test_sw_drawing_structure.py` 的 `FakeView` 套路，零 COM）。
**本轮按指示未新增任何测试文件。**

### R10 尚未落地

`scripts/sw_drawing_ops.py` 与 `mcp-server/tool_specs_batch73.py` **都还没建**
（本轮只写了这一个候选文件）⇒ 上面 6 条 ToolSpec **从未被 import、从未跑过 `check_spec`**。

---

## 五、附录：本轮读过的源（便于复核）

| 读的东西 | 位置 |
|---|---|
| 8 个功能的 def 行 + 表注解族来源块 | `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py:978-1076 / 1238-1267 / 1400-1423 / 1883-1993 / 2306-2350 / 2396-2503` |
| 枚举常量（详图样式 / 圆类型 / 中心标记目标 / BOM 类型） | 同上 `:21-99`（各自带官方出处块） |
| 已有桥 | `scripts/sw_drawing.py:12-29` |
| 导入契约 / `Param` / `ToolSpec` / 门禁 / 调用体 | `mcp-server/tool_registry.py:93-140, 217-318, 321-431, 449-533` |
| `drawing_model` 解析器 | `mcp-server/register_capabilities.py:112-136` |
| ToolSpec 写法样例 | `mcp-server/tool_specs_batch72.py:40-100`；`tool_specs_batch41.py:42-76`；`tool_specs_batch17.py:104-127` |
| 官方 `InsertTableAnnotation` / `…2` | `C:\swapi\types\IDrawingDoc\InsertTableAnnotation.md:12-14` · `InsertTableAnnotation2.md:14-24` |
| 官方孔表 / 修订表入口 | `C:\swapi\types\IView\InsertHoleTable3.md:14` · `C:\swapi\types\ISheet\InsertRevisionTable2.md:14` |
| 官方 `swTableAnnotationType_e`（**推翻实现来源块的一句话**） | `C:\swapi\enums\swTableAnnotationType_e.md:18-29` |
| 官方表面粗糙度入口（三处，只列名字未取用） | `C:\swapi\types\IDrawingDoc\InsertSurfaceFinishSymbol.md` · `IDrawingDoc2/…2.md` · `IModelDocExtension/…3.md` |
| 桥的可达性旁证 | `tests/test_sw_drawing_structure.py:6-17` |
