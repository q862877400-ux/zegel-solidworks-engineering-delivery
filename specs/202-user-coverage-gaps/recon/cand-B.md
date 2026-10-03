# 候选 B · 直连再导出模块（`module="sw_drawing"`，复用既有 importlib 桥）

> 本文件是**候选设计**，不是实现。落地时新建 `mcp-server/tool_specs_batch73.py`。
> ★ **未注册、未改任何已有文件、未跑 SolidWorks / 未跑 pytest。**
> ★ 全部结论都带出处（文件:行号）；读不到的写「读不到」，没有编造。

---

## 一、方案说明

### 1.1 合法链条：为什么 `module="sw_drawing"` 是唯一可行的写法

| 环节 | 事实 | 出处 |
|---|---|---|
| 注册器导入契约 | `mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])` ⇒ `module` **只能是 `scripts/` 下的模块名** | `mcp-server/tool_registry.py:524` |
| 为什么不能直接写 subskill | 父目录 `solidworks-engineering-drawing` **带连字符**，不是合法标识符，`scripts.solidworks-engineering-drawing` 无法 `__import__` | 目录名即上述 |
| 桥已存在 | `scripts/sw_drawing.py` 用 `importlib.util.spec_from_file_location` 按**文件路径**加载 `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py` | `scripts/sw_drawing.py:12-23` |
| 桥导出的是**函数本身** | `for _name in __all__: globals()[_name] = getattr(_MODULE, _name)` ⇒ `scripts.sw_drawing.<函数名>` 真的可取到 | `scripts/sw_drawing.py:25-29` |
| 已有旁证 | `from scripts.sw_drawing import (add_a3_sheet, auto_insert_center_marks, …)` | `tests/test_sw_drawing_structure.py:6-17` |
| 注入名 | `RESOLVERS` 已有 `"drawing_model": resolve_model` ⇒ `inject="drawing_model"` | `mcp-server/register_capabilities.py:136` |
| 注入键 = 形参名 | `kwargs[inject_as or inj] = resolver(params)` ⇒ 注入键就是 `drawing_model`，**恰好**等于这些函数的首参名 | `mcp-server/tool_registry.py:507` |

⇒ **`module="sw_drawing"` + `function=<drawing_workflow 的函数名>` + `inject="drawing_model"` 三个字段就够，零新增 `.py`。**

### 1.2 ★ 本角度**独有**的四个账：复用这座桥要付什么（这是本方案与另两个角度真正的分界）

复用别人的桥，就得替桥的边界负责。以下四条是逐行读 `scripts/sw_drawing.py` + `drawing_workflow.py` 得出的，**另外两个角度（补实现 / 加注入解析器）完全不会碰到**：

**(a) `drawing_workflow.py` 没有 `__all__` ⇒ 走的是兜底分支，导出集比「函数」宽得多。**
`sw_drawing.py:25-27`：`__all__ = list(getattr(_MODULE, "__all__", ()))`；若为空则
`__all__ = [name for name in vars(_MODULE) if not name.startswith("_")]`。
`drawing_workflow.py` 全文 **grep `__all__` = 0 命中** ⇒ **兜底分支生效**，于是
`math` / `re` / `Fraction` / `Path` / `pythoncom` / `VARIANT` / `import_com_dependencies` /
`create_empty_dispatch_variant` / `get_com_member` / `LABELLED_VIEW_TYPES` /
`PAPER_SIZES` / `BOM_TYPES` / … 一并被 re-export 进 `scripts.sw_drawing` 命名空间。
（`_win32com` 以 `_` 开头，被排除。）
⇒ **风险**：将来谁给 `drawing_workflow.py` 补一个**不完整**的 `__all__`，兜底立刻失效，
本文件的 8 个 `function` 名会**一起消失**，而 `ToolSpec` 是**注册期**才解析的 ⇒ 表现为
「整批工具没注册」，不是「某一条坏了」。**这条耦合必须写进落地点的注释。**

**(b) 再导出后函数对象的 `__module__` 是 `"solidworks_drawing_workflow"`，不是 `scripts.sw_drawing`。**
`spec_from_file_location("solidworks_drawing_workflow", …)`（`sw_drawing.py:19`）决定了这一点。
⇒ 任何按 `func.__module__` 归因来源的工具/日志/门禁会看到一个**不存在于 `scripts/` 下**的模块名。
⇒ 另外，**两个名字指向同一个函数对象**（同一份内存），在 `scripts.sw_drawing` 上 monkey-patch
会同时影响从 `drawing_workflow` 直接导入的调用方。

**(c) ★ `drawing_workflow.py` 用了 `Any` 却从未 import，靠 Python 3.14 的惰性注解才不炸。**
`Any` 只出现在 2358 / 2656 两行的返回注解 `-> dict[str, Any]`，文件里
**没有 `from typing import Any`，也没有 `from __future__ import annotations`**（1-20 行已读）。
⇒ 这两行在 **def 时**本该 `NameError`；本机不炸**只因为 Python 3.14 的 PEP 649 把注解改成惰性求值**。
已实测确认（本机 `python --version` = **3.14.7**；纯 CPython 语义检查 `def f(x) -> dict[str, Any]` 通过）。
⇒ **风险**：同一份代码在 **Python ≤ 3.13** 上 `import scripts.sw_drawing` 直接 `NameError: name 'Any' is not defined`。
现有测试恰好只在本机跑 ⇒ 这条**平时看不出来**。**本方案把它列为「拿不准处」而不是「已解决」。**

**(d) 首次 `__import__("scripts.sw_drawing")` 会执行 `import_com_dependencies()`，但**不会**连 SolidWorks。**
`drawing_workflow.py:18` 在模块顶层调用 `import_com_dependencies()`（`scripts/sw_preflight.py:165-174`），
它做的是 `ensure_com_dependencies()` + `importlib.import_module("pythoncom")` / `"win32com.client"`。
`discover_installation` / `solidworks_installed` **不在这条路径上**（`sw_preflight.py:182/196` 是独立函数）。
⇒ 后果只是：**pywin32 必须在位**，且这个导入发生在**第一次调用工具时**，不在注册时。

### 1.3 与另两个角度的差别

- 我在本轮之前读过同目录的 `cand-A.md`（候选 A）。它和我**共用同一个结论**——`module="sw_drawing"` 合法——但它的论证重心不同：
  - **A 的重心**是 `tool_registry.py:490-525` 的调用体，推出「可挂性天花板」（首参必须是 `drawing_model` + 其余形参必须是标量/`list`/`dict`），并据此拒绝一切包装层。
  - **B（本方案）的重心**是 §1.2 那四笔**桥本身的账**（`__all__` 兜底、`__module__` 漂移、PEP 649 前提、导入时机）。这些**在 A 的框架里根本不会被问到**，而它们恰恰是「复用桥」这条路线**独有**的责任。
- 与「补实现」角度的差别：那一路会把 `add_revision` / `get_hole_table` / `set_section_style` 重写成吃 `drawing_model` 的版本，从而多挂若干条。
  **本方案不补实现** ⇒ 这几条在本文档里**必然挂不了**。这是路线选择的结果，**不是漏查**（见 §三，逐条给了首参签名）。
- 与「加注入解析器」角度的差别：那一路会给 `RESOLVERS` 增 `revision_table` / `section_data` 之类的解析器，从而能喂 COM 形参。
  **本方案不动 `RESOLVERS`**（只用已有的 `drawing_model`），也不新增 `resolve_*` 函数。

### 1.4 参数契约：两条硬门禁 + 一次单位换算

**(i) 规则 3 禁止裸坐标参数名** ⇒ 目标函数的 `x` / `y` **不能直接声明**：
`_BARE_COORD_NAMES = {"x","y","z","point","coordinate"}`（`tool_registry.py:93`），
且 `_looks_like_coord_component` 的形式① `^[xyz]\d*$` 会命中（`tool_registry.py:106`）。
★ 但 **`x_mm` / `y_mm` 是合法出口**：`tool_registry.py:128` 明确「以 `_mm` 结尾的坐标不是裸坐标」，
且轮 433 已把 `x_mm`/`y_mm`/`z_mm` 从黑名单里删掉（理由记在 `tool_registry.py:82-92`：规则 2 与规则 3 在这三个名字上自相矛盾）。

**(ii) 于是单位换算落在 `derived_args`**（这是「不加一行实现代码」能保住规则 2 的唯一位置）：
`param_alias={"x_mm": None}` 让 `x_mm` **不进目标函数**（`tool_registry.py:495-496`），
`derived_args` 再补出 `x` / `y`。二者不冲突——注册器明写「派生实参**不得覆盖**已直传的参数名」
（`tool_registry.py:515-522`），而此时 `x`/`y` 并不在 `kwargs` 里。
★ 换算是**必需**的，不是洁癖：官方 X/Y 是**米**。

> 官方单位证据（三处交叉）：
> · `C:\swapi\examples\Create_Section_View_and_Get_Some_Data_Example_VB.md:46` → `CreateSectionViewAt5(0.1604082711061, 0.2048687170364, …)`
> · `C:\swapi\examples\Create_Detail_Circle_and_Detail_View_Example_VB.md:53` → `CreateDetailViewAt4(0.22305342706156, 7.62140266484527E-02, …)`
> · `drawing_workflow.py:1242-1243` 的 `add_note` docstring 逐字写「注释锚点 X 坐标（**米**）」「（**米**）」
> ⇒ 表面收毫米，边界换算成米，只做一次（规则 2）。

**(iii) 逐条对照的形参来源（`def` 行行号）**

| 工具 | `def` 行 | 真实签名（逐字） |
|---|---|---|
| 剖面视图 | `drawing_workflow.py:998` | `add_section_view(drawing_model, x, y)` |
| 局部视图 | `drawing_workflow.py:1022-1035` | `add_detail_view(drawing_model, x, y, scale=2.0, *, style=DET_VIEW_STYLES["standard"], label="", show_type=DET_CIRCLE_SHOW_TYPES["profile"], full_outline=False, jagged_outline=False, no_outline=False, shape_intensity=0)` |
| 中心符号线 | `drawing_workflow.py:1883` | `auto_insert_center_marks(drawing_model, requirements) -> dict` |
| 表注解（孔表/修订表/BOM） | `drawing_workflow.py:2306-2316` | `insert_table_annotation(drawing_model, x: float, y: float, table_type: int, row: int = 0, column: int = 0, *, template: str = "", use_anchor_point: bool = False)` |
| 注释 | `drawing_workflow.py:1238` | `add_note(drawing_model, x, y, text)` |
| 图纸格式 | `drawing_workflow.py:1400` | `set_sheet_format(drawing_model, format_path)` |
| 加图纸 | `drawing_workflow.py:1411` | `add_sheet(drawing_model, paper_size=7, template_path="", first_angle=True)` |
| A3 图纸/模板 | `drawing_workflow.py:1426` | `add_a3_sheet(drawing_model, template_candidates, *, require_gbt=True, projection="first_angle") -> dict` |

★ 逐条对过 `tool_registry.py:375-431` 的三道门禁：参数名无重复、不触规则 3、不触规则 2
（`first_angle` 命中 `_ANGLE_WORDS` 的 `angle`，但 `kind is bool` 被 `tool_registry.py:412` 显式豁免；
`paper_size` / `scale` 不含 `_LEN_WORDS` 里的任何词）。
★ `list` 作为 `Param.kind` 是**已验证可用**的形态（`tool_specs_batch57.py:28` `positions: list`、
`tool_specs_batch36.py:124` `bom_rows: list`；`build_input_model` 直接把它塞进 Pydantic 注解，`tool_registry.py:458-465`）。

---

## 二、完整可粘贴的 ToolSpec 代码块（8 条）

> ★ 落地点：`mcp-server/tool_specs_batch73.py`。★ **本文件只是候选，不注册、不改已有文件。**
> ★ 8 条覆盖 7 项功能（图纸格式拆成「设格式」/「加图纸」/「A3 模板」三条，因为它们的形参类型各不相同）；
>   第 8 项「表面粗糙度」**无实现可挂**，见 §三。

```python
"""★ 覆盖面缺口批（第二批）：工程图 8 项 —— 直连再导出模块（module="sw_drawing"）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（ToolSpec 声明层）· 规格 `specs/202-user-coverage-gaps`
# 文件:   mcp-server/tool_specs_batch73.py（候选 B，未落地）
# 定位:   候选 B 的落地件 —— 把 subskill `subskills/solidworks-engineering-drawing/
#         scripts/drawing_workflow.py` 里**已有实现**的工程图能力接成 MCP 工具，
#         ★ `module` **直接写 `sw_drawing`**（复用 `scripts/sw_drawing.py` 那座
#         `importlib` 再导出桥），**不改任何已有文件**。
# 官方依据（三源交叉）:
#     · C:\swapi\types\IDrawingDoc\CreateSectionViewAt5.md   （剖面视图，7 参）
#     · C:\swapi\types\IDrawingDoc\CreateDetailViewAt4.md     （局部视图，12 参）
#     · examples\Create_Section_View_and_Get_Some_Data_Example_VB.md:46
#       examples\Create_Detail_Circle_and_Detail_View_Example_VB.md:53
#       ⇒ ★★ X/Y 官方示例给的是 **0.16 / 0.076 量级 ⇒ 米**（规则 2 的换算依据）
# 桥的依据: scripts/sw_drawing.py:12-29（spec_from_file_location + globals() 逐个导出）
#           mcp-server/tool_registry.py:524（`__import__("scripts.%s" % spec.module)` 契约）
#           mcp-server/register_capabilities.py:136（RESOLVERS 已有 "drawing_model"）
# 许可:   本仓库 MIT。★ **零第三方代码引入**。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────

from __future__ import annotations

from tool_registry import Param, ToolSpec


# ★★ 规则 2 的换算**只发生在这里一次**（毫米 → 米）。
#    `x_mm` / `y_mm` 在 param_alias 里映成 None ⇒ 不直传；
#    由本函数补出目标函数的真实形参名 `x` / `y`（`tool_registry.py:495-496 / 514-523`）。
def _mm_to_m(params):
    return {"x": params.x_mm / 1000.0, "y": params.y_mm / 1000.0}


# ── 1/8 剖面视图 ──────────────────────────────────────────────────────
#   def 出处: drawing_workflow.py:998  add_section_view(drawing_model, x, y)
#   官方:     IDrawingDoc.CreateSectionViewAt5(X, Y, Z, SectionLabel, Options,
#                                              ExcludedComponents, SectionDepth)
_THE8: list[ToolSpec] = [
    ToolSpec(
        name="solidworks_add_section_view",
        title="Create Section View",
        module="sw_drawing", function="add_section_view",
        inject="drawing_model",
        param_alias={"x_mm": None, "y_mm": None},
        derived_args=_mm_to_m,
        params=[
            Param("x_mm", float, description="剖视图中心在图纸上的 X（**毫米**；★ 边界换算成米，"
                                            "官方 `CreateSectionViewAt5` 收米）。"),
            Param("y_mm", float, description="剖视图中心在图纸上的 Y（**毫米**；同上换算）。"),
        ],
        doc="★ **剖面视图**：`IDrawingDoc.CreateSectionViewAt5(x, y, 0, \"\", 0, None, 0)`。"
            "⚠ **官方前置（Remarks 逐字）**：「Before calling this method, select the section line or "
            "lines to use as a section line.」⇒ 剖切线必须**先由调用方选中**；本工具不代选。"
            "⚠ 官方另注「runs silently; the end-user is not prompted for a label」⇒ 标签名要用 "
            "`IView::GetSection` + `IDrSection::SetLabel2` 另设，本工具不设。"
            "★ 实现把 `Options` 固定传 0、`ExcludedComponents` 传 `None`、`SectionDepth` 传 0"
            "（`drawing_workflow.py:1000`）⇒ **本工具不暴露这三个参数**。",
    ),
    # ── 2/8 局部视图 ──────────────────────────────────────────────────
    #   def 出处: drawing_workflow.py:1022-1035
    #   官方 12 参: (X, Y, Z, Style, Scale1, Scale2, LabelIn, Showtype,
    #                FullOutline, JaggedOutline, NoOutline, ShapeIntensity)
    ToolSpec(
        name="solidworks_add_detail_view",
        title="Create Detail View",
        module="sw_drawing", function="add_detail_view",
        inject="drawing_model",
        param_alias={"x_mm": None, "y_mm": None},
        derived_args=_mm_to_m,
        params=[
            Param("x_mm", float, description="局部视图 X（**毫米**；★ 边界换算成米）。"),
            Param("y_mm", float, description="局部视图 Y（**毫米**；★ 边界换算成米）。"),
            Param("scale", float, default=2.0,
                  description="比例**分子** `Scale1`；★ 分母 `Scale2` 实现固定传 1.0 ⇒ "
                              "`scale=2.0` 即 2:1（`drawing_workflow.py:1065-1066`）。"),
            Param("style", int, default=0,
                  description="详图样式 `swDetViewStyle_e`：0=standard · 1=broken · 2=leader · "
                              "3=noleader · 4=connected（`drawing_workflow.py:61-67` 照录官方 5 项）。"),
            Param("label", str, default="",
                  description="详图标签 `LabelIn`；留空则由 SolidWorks 用默认字母。"),
            Param("show_type", int, default=0,
                  description="圆/轮廓类型 `swDetCircleShowType_e`：0=profile · 1=circle · "
                              "2=dont_show（`drawing_workflow.py:78-82`）。"),
            Param("full_outline", bool, default=False,
                  description="True 显示完整轮廓；官方注明**仅当 NoOutline 为 False 时有效**。"),
            Param("jagged_outline", bool, default=False,
                  description="True 显示锯齿轮廓；官方注明**仅当 NoOutline 为 False 时有效**。"),
            Param("no_outline", bool, default=False, description="True 不显示轮廓。"),
            Param("shape_intensity", int, default=0,
                  description="锯齿强度，官方有效范围 **1(最强)–5(最弱)**，且**仅当 "
                              "`jagged_outline=True` 且 `no_outline=False` 时生效**。"
                              "★ 默认 0 = 「不生效」（非越界取值，见 drawing_workflow.py:1019-1020）。"),
        ],
        doc="★ **局部放大视图（局部详图）**：`IDrawingDoc.CreateDetailViewAt4`（官方 **12 个参数**，"
            "`C:\\swapi\\types\\IDrawingDoc\\CreateDetailViewAt4.md`）。"
            "⚠ **官方前置**：调用前须已选中要放大的**区域/圆**；本工具不代选。"
            "★ 真机状态：**未实测** —— `drawing_workflow.py:1018` 自己写着「本函数为静态签名比对后修正，"
            "未在本机实测（见 AGENTS.md 铁律 2）」。",
    ),
    # ── 3/8 中心符号线 ────────────────────────────────────────────────
    #   def 出处: drawing_workflow.py:1883  auto_insert_center_marks(drawing_model, requirements)
    ToolSpec(
        name="solidworks_auto_insert_center_marks",
        title="Auto Insert Center Marks",
        module="sw_drawing", function="auto_insert_center_marks",
        inject="drawing_model",
        params=[
            Param("requirements", list,
                  description="需求列表，每项 `{id, view, count, targets}`："
                              "`view` 是方位名（前视/上视/…，`_normalise_orientation` 归一）；"
                              "`count` 是**期望实体数**（实现按它与插入前实体数比较，决定要不要补插）；"
                              "`targets` 取 `holes` / `fillets` / `slots`（对应 "
                              "`swAutoInsertCenterMarkTypes_e` 的 1/2/4，多项按位或，"
                              "`drawing_workflow.py:45-49`）。"
                              "★ 列表为空 ⇒ 返回 `status=\"not_requested\"`，**不报错**"
                              "（`drawing_workflow.py:1886-1893`）。"),
        ],
        doc="★ **中心符号线**：按视图自动插入中心标记，**以实体数量回读为成功依据**"
            "（`drawing_workflow.py:1884`）。逐条要求解析不了时返回 "
            "`error_code=\"DRAWING_CENTER_MARK_REQUIREMENT_UNRESOLVED\"` 而不是抛异常。"
            "⚠ 视图与需求的映射走 `_map_standard_views_from_sheet_views`（`drawing_workflow.py:1897`）"
            "⇒ **依赖当前图纸页上已有可识别的标准视图**。",
    ),
    # ── 4/8 表注解：孔表 / 修订表 / BOM 的**插入**入口 ──────────────────
    #   def 出处: drawing_workflow.py:2306-2316
    ToolSpec(
        name="solidworks_insert_table_annotation",
        title="Insert Table Annotation (Hole / Revision / BOM)",
        module="sw_drawing", function="insert_table_annotation",
        inject="drawing_model",
        param_alias={"x_mm": None, "y_mm": None},
        derived_args=_mm_to_m,
        params=[
            Param("x_mm", float, description="表在图纸上的 X（**毫米**；★ 边界换算成米）。"),
            Param("y_mm", float, description="表在图纸上的 Y（**毫米**；★ 边界换算成米）。"),
            Param("table_type", int,
                  description="表种类（官方 `InsertTableAnnotation` 的 Int32 `Type`）。"
                              "★★ **本工具不设默认值，两套官方源都查不到该枚举**"
                              "（`drawing_workflow.py:2300-2302` 逐字：「其枚举在两套官方源里都查不到"
                              "（sw_know 检索无对应枚举定义），故本模块**只做透传、不设默认类型**」）"
                              "⇒ **必填、且取值由调用方按官方文档指定**。"),
            Param("row", int, default=0, description="起始行；0 表示不指定。"),
            Param("column", int, default=0, description="起始列；0 表示不指定。"),
            Param("template", str, default="",
                  description="给了它走 **7 参版本** `InsertTableAnnotation2`（多一个锚点开关）；"
                              "留空走 **5 参版本** `InsertTableAnnotation`（`drawing_workflow.py:2320-2329`）。"),
            Param("use_anchor_point", bool, default=False,
                  description="是否用锚点定位（**仅在给了 `template` 时才被传下去**）。"),
        ],
        doc="★ **表注解插入**（孔表 / 修订表 / BOM 共用这一个官方入口，种类由 `table_type` 决定）。"
            "⚠⚠ **本工具只覆盖「插入」**；表**读不到**就改不了 —— ★ 孔表 / 修订表的**编辑族全部挂不了**，"
            "原因见 `specs/202-user-coverage-gaps/recon/cand-B.md` §三。"
            "★ 真机状态：**未实测**（`drawing_workflow.py:2304`：「本组为照官方签名新写，未在本机实测」）。",
    ),
    # ── 5/8 注释 ──────────────────────────────────────────────────────
    #   def 出处: drawing_workflow.py:1238  add_note(drawing_model, x, y, text)
    ToolSpec(
        name="solidworks_add_note",
        title="Add Drawing Note",
        module="sw_drawing", function="add_note",
        inject="drawing_model",
        param_alias={"x_mm": None, "y_mm": None},
        derived_args=_mm_to_m,
        params=[
            Param("x_mm", float, description="注释锚点 X（**毫米**；★ 实现吃**米**，"
                                            "`drawing_workflow.py:1242` 逐字「（米）」）。"),
            Param("y_mm", float, description="注释锚点 Y（**毫米**；同上）。"),
            Param("text", str, description="写入图纸的非空文字。★ 空白或非有限坐标 ⇒ 返回 "
                                          "`error_code=\"DRAWING_NOTE_INPUT_INVALID\"`，不抛异常"
                                          "（`drawing_workflow.py:1248-1254`）。"),
        ],
        doc="★ **工程图文字注释**：`InsertNote(text)` + 定位 + 回读。"
            "★ 成功判据是**回读**（COM 文字 == 期望文字，且锚点坐标吻合，容差 1e-6），"
            "**不是** API 返回值（`drawing_workflow.py:1268-1275`）。"
            "⚠ 坐标单位：官方与实现都是**米**，本工具表面收**毫米**并在边界换算一次。",
    ),
    # ── 6/8 图纸格式 ──────────────────────────────────────────────────
    #   def 出处: drawing_workflow.py:1400  set_sheet_format(drawing_model, format_path)
    ToolSpec(
        name="solidworks_set_sheet_format",
        title="Set Drawing Sheet Format",
        module="sw_drawing", function="set_sheet_format",
        inject="drawing_model",
        params=[
            Param("format_path", str, description="图纸格式文件路径（`.slddrt`）；"
                                                  "实现直传 `ISheet.SetTemplateName`"
                                                  "（`drawing_workflow.py:1407-1408`）。"),
        ],
        doc="★ **图纸格式（图框）**：把**当前图纸页**的模板换成给定的 `.slddrt`。"
            "⚠ 只作用于 `GetCurrentSheet()` ⇒ **多页图纸要先切到目标页**。"
            "⚠ 返回值直传 `SetTemplateName`，本仓**未实测**其 bool 的可信度 ⇒ "
            "**别把返回值当成功判据**（本仓纪律：不能自证的 COM 返回值一律不信）。",
    ),
    # ── 7/8 加图纸 ────────────────────────────────────────────────────
    #   def 出处: drawing_workflow.py:1411  add_sheet(drawing_model, paper_size=7, ...)
    ToolSpec(
        name="solidworks_add_sheet",
        title="Add Drawing Sheet",
        module="sw_drawing", function="add_sheet",
        inject="drawing_model",
        params=[
            Param("paper_size", int, default=7,
                  description="纸张代码：**0=A 1=B 2=C 3=D 4=E 5=A4 6=A3 7=A2 8=A1 9=A0**"
                              "（`drawing_workflow.py:1416-1418`）。★ 默认 **7 = A2**。"),
            Param("template_path", str, default="", description="图框模板路径（`.slddrt`）；留空用文档默认。"),
            Param("first_angle", bool, default=True,
                  description="True = 第一角法投影；False = 第三角法。"),
        ],
        doc="★ **新增图纸页**：`IModelDoc2.NewSheet4(\"\", paper_size, 12, 1.0, 1.0, "
            "first_angle, template_path, 0, 0, \"\", 0, 0, 0, 0, 0, 0)`"
            "（`drawing_workflow.py:1421-1423`）⇒ ★ 第 3 参固定 12、第 4/5 参固定 1.0、"
            "其后 7 个尾参固定 0/\"\" ⇒ **本工具不暴露它们**。"
            "⚠ 与 `solidworks_add_a3_sheet` 的区别：那条**先在本机候选里选图框**再按 A3 建页。",
    ),
    # ── 8/8 A3 图纸 + 模板选择 ────────────────────────────────────────
    #   def 出处: drawing_workflow.py:1426
    ToolSpec(
        name="solidworks_add_a3_sheet",
        title="Add A3 Drawing Sheet (GB/T Template Selection)",
        module="sw_drawing", function="add_a3_sheet",
        inject="drawing_model",
        params=[
            Param("template_candidates", list,
                  description="本机图框候选路径**列表**（`.slddrt`）。实现按 "
                              "「存在(8) + 是 slddrt(4) + 文件名含图幅(2) + GB/T 标识(1) + "
                              "简体中文目录(2)」打分选最优（`drawing_workflow.py:415-431`）。"
                              "★ 选不出时返回 `stage=\"preflight\", created=False, retryable=True`，"
                              "**不抛异常**（`drawing_workflow.py:1429-1435`）。"),
            Param("require_gbt", bool, default=True,
                  description="是否要求候选带 GB/T 标识（`gbt` / `国标` / `gb(t)` 词形，"
                              "`drawing_workflow.py:422-425`）。"),
            Param("projection", str, default="first_angle",
                  description="投影法：`first_angle` 或 `third_angle`；★ 实现只做 "
                              "`str(...).lower() == \"first_angle\"` 判断"
                              "（`drawing_workflow.py:1440`），**其它值一律按第三角法**。"),
        ],
        doc="★ **A3 工程图页 + 本机 GB/T 图框选择**：先 `select_drawing_template` 选模板"
            "（`drawing_workflow.py:406`），再用 `add_sheet` 建页（`drawing_workflow.py:1436-1441`）。"
            "⚠ 模块自己写明选模板**只看文件名与扩展名**，**不宣称模板内容已合规**"
            "（`drawing_workflow.py:409`）。★ 本仓**未实测**。",
    ),
]

#: ★★ 注册器按 `SPECS_*` 找（参照 `mcp-server/tool_specs_batch72.py:100`）
SPECS_BATCH73 = _THE8
```

---

## 三、风险与未决

### 3.1 挂得了的：8 条（见 §二代码块）

### 3.2 ★ 挂不了的：逐条给首参签名与原因

| 功能 | 函数（`def` 行） | 首参 | 为什么挂不了 |
|---|---|---|---|
| **表面粗糙度（surface finish）** | —— | —— | ★★ **本仓根本没有创建实现**。全文 grep `roughness` 只命中 `drawing_workflow.py` 的 **4 处「读证据」**（1660 / 1695 / 1701 / 1725 行的 `surface_finish_symbols` 键），**没有一处调用 `InsertSurfaceFinishSymbol*`**；全仓 grep 该成员名只在 `scripts/sw_api_sldworks.py`（反射/API 字典）里命中，`scripts/` 与 subskill **零调用**。⇒ **无实现可挂，不是参数问题**。⚠ `scripts/sw_render_material.py` 的 `Roughness` 是**外观材质**反射率，与工程图粗糙度符号**无关**，不要认错。 |
| 修订表（编辑） | `add_revision(revision_table, revision)`（`drawing_workflow.py:2489`） | `IRevisionTableAnnotation` **COM 对象** | `Param.kind` 只能表达 JSON 标量 / `list` / `dict`；`derived_args` 只拿得到 `params`（JSON）⇒ **造不出 COM 对象**。 |
| 修订表（读/删） | `get_current_revision(revision_table)`（2503）/ `delete_revision(revision_table, index, mark_deleted)`（2496）/ `get_revision_table_feature(table)`（2446） | 同上 COM 对象 | 同上 |
| 孔表（读） | `get_hole_table(table)`（`drawing_workflow.py:2425`） | `IHoleTableAnnotation` **COM 对象** | 同上。★ **注意**：`solidworks_insert_table_annotation` 只能**插入**孔表，**读不回来** ⇒ 插完仍然改不了。 |
| 通用表 / 折弯表 / 下料表 | `get_general_table`(2418) / `get_bend_table`(2432) / `get_weldment_cutlist_table`(2439) | COM 对象 | 同上 |
| 表编辑族 | `read_table_text`(2351) / `get_table_shape`(2358) / `set_table_row_hidden`(2370) / `set_table_column_hidden`(2377) / `delete_table_row`(2384) / `delete_table_column`(2390) / `sort_table`(2468) / `get_table_custom_property_column`(2453) / `set_table_custom_property_column`(2460) | COM 对象 | 同上 |
| 剖面样式 | `set_section_style(section_data, *, …)`（`drawing_workflow.py:2540-2556`） | `ISectionViewData` **COM 对象** | 同上。★ 且它 14 个形参全是 keyword-only 的 `bool \| None` / `int \| None` / `float \| None`，`None` 语义是「**不设**」（`drawing_workflow.py:2566-2592`）⇒ 即使能挂，`Param` 的默认值体系表达不了 `None = 跳过` 这个语义。 |
| 取剖面定义 | `get_section_view_data(section_view)`（2533） | 视图 COM 对象 | 同上 |

⇒ 这两类要解决，只能走**另两个角度**：① 给实现补一个吃 `drawing_model` 的包装；
② 给 `RESOLVERS` 加 `revision_table` / `section_data` 之类的解析器。**本方案明确不做。**

### 3.3 未实测 / 拿不准

1. ★★ **Python 版本前提（最要紧的一条）** —— 见 §1.2(c)。`drawing_workflow.py` 用了未 import 的 `Any`
   且无 `from __future__ import annotations`，**只因本机是 Python 3.14.7（PEP 649 惰性注解）才不炸**。
   **在 ≤3.13 上 `import scripts.sw_drawing` 会 `NameError`。** 我已实测确认「3.14 上注解不求值」，
   但**没有在 3.13 上实际验证过会炸** —— 这一步属于「推出来」，不是量出来的。
   ⇒ 落地时建议在文件头写死一行「本批要求 Python ≥ 3.14」，或给实现补 `from typing import Any`。
2. **§1.2(a) 的 `__all__` 兜底耦合** —— 落地时**必须在 `tool_specs_batch73.py` 的来源块里写明**：
   这 8 条依赖「`drawing_workflow.py` 没有 `__all__`」这个**当前状态**。补一个不完整的 `__all__` 会整批消失。
3. **§1.2(b) 的 `__module__` 漂移** —— 已确认机制（`spec_from_file_location` 的第 2 参），但
   **本仓是否真有按 `__module__` 归因的门禁，我没有逐个查**（只看到 `scripts/sw_api_sldworks.py` 是反射字典，
   不是门禁）。⇒ **「会不会踩到某个门禁」是拿不准处。**
4. **`table_type` 的取值** —— 两套官方源都查不到该枚举（实现自己的注释就写了）。
   本方案**如实必填、不给默认值**，不做猜测。
5. **未跑真机** —— 本轮**没有**跑 SolidWorks、**没有**跑 pytest。
   所有「真机状态」均按实现文件里的自述照录：剖面视图 / 局部视图 / 表注解 / A3 页 4 条**未实测**。
6. **`solidworks_add_section_view` 的剖切线** —— 官方前置要求「先选中剖切线」。
   本方案的 `pre_call` **故意留空**（`ToolSpec.pre_call` 机制见 `tool_registry.py:288-291`）——
   因为「怎么选中一条剖切线」在本仓是**规则 3 的选面难题**，不属于本角度。⇒ **调用方必须自己先选中**。

### 3.4 落地时必须一并做的两件事（否则本方案会静默半残）

1. **按 `mcp-server/register_capabilities.py` 的既有写法导入本 `SPECS_BATCH73`**（本文件**没有**改动该文件）。
2. **§3.3-1 的 Python 版本前提**至少写进 `tool_specs_batch73.py` 的文件头注释。

---

## 附：与本轮任务给定事实的逐条核对

| 给定事实 | 本方案的核对结果 |
|---|---|
| `drawing_workflow.py` 约 2746 行，8 项功能已实现 | ✅ 行数一致（2746）。★ 但「8 项」里 **表面粗糙度只实现了「读证据」**，创建实现**不存在** —— §3.2 第 1 行 |
| 这些函数首参叫 `drawing_model` | ✅ 8 条全部逐行确认（§1.4 表） |
| `tool_registry.py:524` 的导入契约 | ✅ 逐字确认 |
| subskill 父目录带连字符写不进 `module` | ✅ 因此只能走 `scripts/sw_drawing.py` 这座桥 |
| `scripts/sw_drawing.py` 用 `spec_from_file_location` + `globals()[name]` 导出 | ✅ 逐行确认（12-29 行） |
| `tests/test_sw_drawing_structure.py:9` 的旁证 | ✅ 确认（实际是 **6-17 行**的 import 块，含 `auto_insert_center_marks`） |
| `RESOLVERS` 已有 `"drawing_model": resolve_model` | ✅ `register_capabilities.py:136` |
| ToolSpec 写法参照 `tool_specs_batch72.py`，末尾 `SPECS_BATCH72 = _BATCH72` | ✅ 本文件末尾 `SPECS_BATCH73 = _THE8`，同名同形 |