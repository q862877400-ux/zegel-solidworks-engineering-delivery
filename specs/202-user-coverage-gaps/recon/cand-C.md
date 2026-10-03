# 候选 C · 批次续接（沿用 `tool_specs_batch*` 既有骨架，按能力域分组）

> 本文件是**候选设计**，不是实现。落地时新建 `mcp-server/tool_specs_batch73.py`（并在
> `register_capabilities.py:140` 的 `BATCH_MODULES` 末尾加一行）。
> ★ **未注册、未改任何已有文件、未跑 SolidWorks / pytest**（本轮全部结论来自读源码）。

---

## 一、方案说明

### 1.1 本角度的做法：**不加新层，只加一个批次文件**

题述 8 项功能在 `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`（2746 行）里**都已实现**，
桥 `scripts/sw_drawing.py` 已把它们按名字导出到 `scripts.sw_drawing.*`。
所以本角度的工作**只有一个形态**：写一个**和 `mcp-server/tool_specs_batch72.py` 同骨架**的新批次文件
（同一行 docstring → 同一个「来源」六字段块 → `_BATCH73: list[ToolSpec]` → `SPECS_BATCH73 = _BATCH73`），
文件内部**按能力域分成 4 组**，组与组之间用注释横幅隔开。

批次编号取 **73**：`tool_specs_batch72.py` 是现存最大编号，而 `register_capabilities.py:140` 的
`BATCH_MODULES` 是**按注册顺序**的元组 ⇒ 续 73 是最小增量、不动任何既有行。

### 1.2 4 个能力域（分组即本角度的主张）

| 组 | 能力域 | 落进来的工具 | 域的判据（为什么这么分） |
|---|---|---|---|
| **A** | **视图几何** —— 在图纸上**造出新视图对象** | `create_section_view` · `create_detail_view` | 两条都返回**新建的视图对象**（`CreateSectionViewAt5` / `CreateDetailViewAt4` 的返回值），而视图是工程图里唯一"有尺寸、有位置、有比例"的一类实体 ⇒ 位置与比例参数在这一域里成对出现 |
| **B** | **专业标注** —— 往**已有视图**上挂符号/文字 | `auto_insert_center_marks` · `insert_note` | 两条都不产生新视图，只往 `IView`/图纸上挂 `IAnnotation`；中心符号线靠**实体回读**判成败（`before_count/after_count`），注释靠 `GetText` 回读 ⇒ 这域的共同特征是「**必须可回读**」 |
| **C** | **表注解** —— 孔表 / 修订表 / 通用表**同一条路** | `insert_table_annotation` | 这三张表在官方 API 里是**同一个入口** `InsertTableAnnotation(2)`，只由 `Type` 区分；本仓**也只有这一个函数**（`drawing_workflow.py:2306`）⇒ **一个工具覆盖三项**，不拆 |
| **D** | **图纸页与图框** —— 页的**增/设/配置回读** | `set_sheet_format` · `add_sheet` · `setup_sheet` | 三条都作用在 `ISheet`/`NewSheet4`/`SetupSheet6` 上，参数里出现**图幅码**、**投影法**、**`.slddrt` 路径** ⇒ 这域的共同特征是「**参数是图纸页属性，不是几何**」 |

★ 分组**不是**按「函数在文件里的行号」排的（那样 A 组会散在 998/1022/1883/1238 四处），
也不是按「能挂/不能挂」排的（那是候选 A 的分法）。按域排的好处是：**接手的人按域读，
就知道哪几个能力在一次调用里能连着做完**（例如 A 组两条都吃图纸坐标毫米，B 组两条都不吃）。

### 1.3 与另两个角度的差别

| | 候选 A（最小包装层） | **候选 C（本文件）** | 另两个角度（B/C 之外的两个） |
|---|---|---|---|
| **主命题** | 「**零新代码**，包装层就是 ToolSpec 声明本身」；重点论证**可挂性的硬天花板** | 「**批次文件的形态**」：骨架照 batch72 抄、按能力域分组、批次号续 73 | 推测方向：**补实现层**（把吃 COM 对象的函数重写成吃 `drawing_model`）/ **加注入解析器**（给 `RESOLVERS` 增键） |
| **8 条的取法** | 含 `create_standard_views`（无 `list` 型入参） | 含 `setup_sheet`（**要 `list[str]` 入参**）—— 见 §3.2，这是**故意选的**，为的是把 D 域补齐 | —— |
| **工具名** | `solidworks_drawing_section_view`（域 + 名词） | `solidworks_drawing_create_section_view`（域 + **动词**，与目标函数名同词根）⇒ 覆盖率脚本按功能关键词子串计分时命中率更高 | —— |
| **它回答的问题** | 「**能不能挂**」 | 「**挂成什么样、怎么分组、落进哪个文件**」 | —— |
| **它不做的事** | 不夹带实现层/解析器 | **同样不夹带** —— 挂不了的照实写「挂不了」并写清天花板在 `tool_registry.py:507` 的注入键 | 那两个角度**正是**会去动实现层/解析器的 |

★ 一句话：**A 是"能不能"，C 是"长什么样"**。两者结论一致的地方（挂得了 8 条、挂不了的全是首参是 COM 对象的）
在本文件里**重新独立核过一遍**，出处逐条标了行号。

### 1.4 逐条挂载依据（全部读源码，行号为准）

| # | 工具 | `module` | `function` | 实现 `def` 行 | 注入 | 是否需换算/别名 |
|---|---|---|---|---|---|---|
| 1 | `solidworks_drawing_create_section_view` | `sw_drawing` | `add_section_view` | `drawing_workflow.py:998` | `drawing_model` | `x`/`y` 是**裸坐标**且实现吃**米** ⇒ `x_mm`/`y_mm` 消费掉、`derived_args` 换算 |
| 2 | `solidworks_drawing_create_detail_view` | `sw_drawing` | `add_detail_view` | `:1022-1035`（多行 `def`） | `drawing_model` | 同上 |
| 3 | `solidworks_drawing_auto_insert_center_marks` | `sw_drawing` | `auto_insert_center_marks` | `:1883` | `drawing_model` | 否（`requirements` 同名直传） |
| 4 | `solidworks_drawing_insert_note` | `sw_drawing` | `add_note` | `:1238` | `drawing_model` | `x`/`y` 换算（docstring 明写「米」） |
| 5 | `solidworks_drawing_insert_table_annotation` | `sw_drawing` | `insert_table_annotation` | `:2306-2316` | `drawing_model` | `x`/`y` 换算（单位存疑，见 §3.3） |
| 6 | `solidworks_drawing_set_sheet_format` | `sw_drawing` | `set_sheet_format` | `:1400` | `drawing_model` | 否 |
| 7 | `solidworks_drawing_add_sheet` | `sw_drawing` | `add_sheet` | `:1411` | `drawing_model` | `first_angle` 形参名**触角规则 2**（含 `angle`）⇒ 对外改叫 `projection`，`derived_args` 还原成 bool |
| 8 | `solidworks_drawing_setup_sheet` | `sw_drawing` | `setup_current_sheet` | `:2042` | `drawing_model` | 否（形参名就是 `paper_size` / `projection` / `require_gbt`） |

★ 三条硬约束都逐字核过：
- `tool_registry.py:524` `mod = __import__("scripts.%s" % spec.module, …)` ⇒ `module` 只能是 `scripts/` 下的模块名；
  subskill 父目录 `solidworks-engineering-drawing` 带连字符 ⇒ 进不去 ⇒ **`module="sw_drawing"` 是唯一解**（桥已在 `scripts/sw_drawing.py:19-29`）。
- `tool_registry.py:507` `kwargs[inject_as or inj] = resolver(params)`，而 `register()`（`:559`）**不往下传 `inject_as`**
  ⇒ 注入键**字面上等于 `inject`** ⇒ 必须写 `inject="drawing_model"`（否则 `TypeError: unexpected keyword argument 'model'`）。
- `register_capabilities.py:136` 已有 `"drawing_model": resolve_model` ⇒ 注入名在 `RESOLVERS` 里，不需要改任何东西。

---

## 二、完整可粘贴的 ToolSpec 代码块（8 条）

> ★ 落点：新建 `mcp-server/tool_specs_batch73.py`，内容如下（**整段**）。
> ★ 每条 `params` 逐个照 `drawing_workflow.py` 的 `def` 行抄；形参名以「源码里的名字」为准，
>   对外面叫别的（`x_mm`、`projection`）一律用 `param_alias` + `derived_args` 显式改写，**不改实现**。

```python
"""★ 覆盖面缺口批（第二批）：工程图 8 项（按能力域分 4 组）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（ToolSpec 声明层）· 规格 `specs/202-user-coverage-gaps`
# 文件:   mcp-server/tool_specs_batch73.py（候选 C，未落地）
# 定位:   ★ 续 `tool_specs_batch72.py`（现存最大编号）★
#   · 骨架照 batch72 抄：一行 docstring → 本来源块 → `_BATCH73` → `SPECS_BATCH73`。
#   · 注册只需在 `register_capabilities.py:140` 的 `BATCH_MODULES` 末尾加一行
#     `"tool_specs_batch73"`（那个元组按注册顺序，续号即最小增量）。
#   · ★ 4 个能力域分组（注释横幅 A/B/C/D）：视图几何 · 专业标注 · 表注解 · 图纸页与图框。
#     分组判据见 `specs/202-user-coverage-gaps/recon/cand-C.md` §1.2（按域，不按行号、不按可挂性）。
#
#   ★★ 三条硬约束（逐字核过，不是推断）：
#     ① `tool_registry.py:524` `mod = __import__("scripts.%s" % spec.module, fromlist=…)`
#        ⇒ `module` 只能是 `scripts/` 下的模块名；而实现文件的父目录
#        `solidworks-engineering-drawing` **带连字符**（非合法标识符）⇒ 进不去。
#        ★ 桥 `scripts/sw_drawing.py:19-29` 已用 `spec_from_file_location` 按**路径**加载并
#          `globals()[_name] = getattr(_MODULE, _name)` 逐个导出 ⇒ `module="sw_drawing"` 合法。
#     ② `tool_registry.py:507` `kwargs[inject_as or inj] = resolver(params)`，
#        而 `register()`（`:559`）**不往下传 `inject_as`** ⇒ 注入键**字面上 = `inject` 的值**
#        ⇒ 必须 `inject="drawing_model"`（实现首参就叫 `drawing_model`，不是 `model`；
#          写 `"model"` 会 `TypeError: unexpected keyword argument 'model'`）。
#     ③ `register_capabilities.py:136` 已有 `"drawing_model": resolve_model`
#        ⇒ **不需要动 RESOLVERS**（与 `asm_model` 同一手法）。
#
#   ★ 门禁已在设计阶段对过（`tool_registry.check_spec` + `scripts/check_param_binding.py`）：
#     · 规则 3：`x`/`y` 是裸坐标黑名单成员 ⇒ 对外一律改叫 `x_mm`/`y_mm`，
#       再用 `_consumed()` 把它们**标记为不直传**（`param_alias` 值 = `None`），
#       由 `derived_args` 生成真形参 `x`/`y`（照 batch4 的 `_consumed` 同一手法）。
#     · 规则 2：`add_sheet` 的形参 `first_angle` 含 `angle` 而不以 `_deg` 结尾 ⇒ 会被拦
#       ⇒ 对外改叫 `projection`（值域 `first_angle` / `third_angle`），`derived_args` 转回 bool。
#       ⚠ **没有改 `tool_registry.py` 的豁免表**（本次不碰任何已有文件）。
#     · 参数绑定门禁①：`Param.name` ∈ 形参表 **或** ∈ `param_alias` ⇒ 消费型参数满足；
#       ②：`param_alias` 的非 None 目标 ∈ 形参表 ⇒ 本批只用 `None`，自动满足。
#
#   官方依据（三源，指**被搬运函数**用的官方成员，各自在实现文件里有自己的来源块）：
#     · `IDrawingDoc.CreateSectionViewAt5` / `CreateDetailViewAt4`
#       ⇒ `recon/api/CreateSectionViewAt5.md`、`recon/api/CreateDetailViewAt4.md`
#     · `IDrawingDoc.InsertNote` ⇒ `recon/api/InsertNote.md`
#     · `IDrawingDoc.SetupSheet6`（`setup_current_sheet`）/ `NewSheet4`（`add_sheet`）
#       ⇒ `recon/api/SetupSheet5.md`（★ 只读到 SetupSheet5，**SetupSheet6 的页没读到** ⇒ 见 §3.3）
#     · `IView.AutoInsertCenterMarks2` / `ISheet.SetTemplateName` / `IDrawingDoc.InsertTableAnnotation(2)`
#       · `IView` 中心标记枚举 `swAutoInsertCenterMarkTypes_e` 在实现里已录（`:45-49`，holes=1/fillets=2/slots=4）
#   许可:   本仓库 MIT。★ **无第三方代码引入**（不外抄任何项目文本）。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

from tool_registry import Param, ToolSpec

#: ★ 与 batch4 同一手法：毫米 → 米的换算**只在这一处**做一次（规则 2）。
_MM = 0.001


def _consumed(*names: str) -> dict:
    """构造 `param_alias`：这些入参**由 `derived_args` 消费**，不作为关键字直传给目标函数。

    ⚠ 为什么必须显式：`tool_registry.py:493-498` 会把每个**声明**参数按名字塞进 kwargs，
    而目标函数的真形参叫 `x`/`y`（裸坐标，规则 3 禁止对外暴露）⇒ 不消费就会
    `TypeError: unexpected keyword argument 'x_mm'`。
    """
    return {n: None for n in names}


def _xy(p) -> dict:
    """把对外的 `x_mm`/`y_mm` 换成实现的图纸坐标（**米**）。

    ⚠ 单位依据：`add_note` 的 docstring 逐字写「@param x 注释锚点 X 坐标（**米**）」
      （`drawing_workflow.py:1242`）⇒ SolidWorks 图纸坐标是米。
      换算**只在这里做一次**，工具表面一律毫米（规则 2）。
    """
    return {"x": float(p.x_mm) * _MM, "y": float(p.y_mm) * _MM}


def _first_angle(p) -> dict:
    """把对外的 `projection`（字符串）还原成实现的 `first_angle`（bool）。

    ⚠ 为什么绕这一下：真形参名 `first_angle` 里含 `angle`，而 `check_spec` 的规则 2
      角度那一半要求这类参数以 `_deg` 结尾 ⇒ 直接暴露会被门禁拦下。
      **不改成 `_deg`**（它是投影法、不是角度）⇒ 改叫 `projection`，值域写进 Param 描述。
    """
    return {"first_angle": str(p.projection).strip().lower() == "first_angle"}


_BATCH73: list[ToolSpec] = [
    # ══════════════════════════════════════════════════════════════════
    # A 域 · 视图几何 —— 产出**新的视图对象**；位置与比例参数成对出现
    # ══════════════════════════════════════════════════════════════════
    # 签名: def add_section_view(drawing_model, x, y)     ← drawing_workflow.py:998
    ToolSpec(
        name="solidworks_drawing_create_section_view",
        title="Create Section View",
        module="sw_drawing", function="add_section_view",
        inject="drawing_model",
        param_alias=_consumed("x_mm", "y_mm"),
        derived_args=_xy,
        idempotent=False,     # ★ 每调一次多一个视图 ⇒ 不幂等（本仓 72 个批次里首次显式写，见 §3.3）
        params=[
            Param("x_mm", float, description="剖视图在图纸上的 X 位置，**毫米**。"
                                             "★ 实现吃**米**，换算在 `derived_args` 里做一次。"),
            Param("y_mm", float, description="剖视图在图纸上的 Y 位置，**毫米**（同上换算）。"),
        ],
        doc="★ **剖面视图**：`IDrawingDoc.CreateSectionViewAt5(x, y, 0, \"\", 0, None, 0)`。"
            "⚠⚠ **前置**：实现 docstring 逐字写「在**当前选择的剖切线**位置创建剖视图」"
            "⇒ 图纸上必须已有剖切线，否则返回空；本工具**不代为画剖切线**。"
            "⚠ 第 4 参传 `\"\"`（剖面名留空）、第 5 参 `0`、第 6 参 `None` —— "
            "★ 官方 `CreateSectionViewAt5` 的完整形参表**本轮没读到**，这几个实参是实现里写死的，"
            "★ 本工具**只搬运、不解释**（铁律 5）。",
    ),
    # 签名: def add_detail_view(drawing_model, x, y, scale=2.0, *, style=…, label="",
    #                          show_type=…, full_outline=False, jagged_outline=False,
    #                          no_outline=False, shape_intensity=0)   ← :1022-1035（多行 def）
    ToolSpec(
        name="solidworks_drawing_create_detail_view",
        title="Create Detail View",
        module="sw_drawing", function="add_detail_view",
        inject="drawing_model",
        param_alias=_consumed("x_mm", "y_mm"),
        derived_args=_xy,
        idempotent=False,
        params=[
            Param("x_mm", float, description="局部视图在图纸上的 X 位置，**毫米**（实现吃米）。"),
            Param("y_mm", float, description="局部视图在图纸上的 Y 位置，**毫米**（实现吃米）。"),
            Param("scale", float, default=2.0,
                  description="比例**分子** `Scale1`；实现把 `Scale2` 固定传 1.0 "
                              "⇒ `scale=2` 就是 2:1。⚠ 它是比例不是长度 ⇒ **不加 `_mm`**。"),
            Param("style", int, default=0,
                  description="官方 `swDetViewStyle_e`（实现 `DET_VIEW_STYLES`，`:61-67`）："
                              "0=standard · 1=broken · 2=leader · 3=noleader · 4=connected。"),
            Param("show_type", int, default=0,
                  description="官方 `swDetCircleShowType_e`（实现 `DET_CIRCLE_SHOW_TYPES`，`:78-82`）："
                              "0=profile · 1=circle · 2=dont_show。"),
            Param("label", str, default="",
                  description="详图标签文字（官方第 7 参 `LabelIn`）；空串 = 不给标签。"),
            Param("full_outline", bool, default=False, description="官方 `FullOutline`。"),
            Param("jagged_outline", bool, default=False, description="官方 `JaggedOutline`。"),
            Param("no_outline", bool, default=False, description="官方 `NoOutline`。"),
            Param("shape_intensity", int, default=0,
                  description="官方 `ShapeIntensity`，**有效范围 1(最强)–5(最弱)**，"
                              "且**仅在** `jagged_outline=True` 且 `no_outline=False` 时生效；"
                              "默认 0 = 不生效。"),
        ],
        doc="★ **局部视图 / 详图**：`IDrawingDoc.CreateDetailViewAt4`（官方 **12 个参数**）。"
            "★ 实现来源块逐字记着它**曾经只传 7 个实参**、后按 `C:\\swapi\\types\\IDrawingDoc\\"
            "CreateDetailViewAt4.md` 补齐到 12 参 ⇒ 本工具按补齐后的形状搬运。"
            "⚠ 实现来源块自己写明：**静态签名比对后修正，未在本机实测**（铁律 2）⇒ 本工具同为 `stitched`。"
            "⚠ 详情**必须先在界面上圈出要放大的区域**（官方流程：画详图圆 → 再调本入口）；"
            "本工具**只负责放置，不负责画那个圆**。",
    ),

    # ══════════════════════════════════════════════════════════════════
    # B 域 · 专业标注 —— 往**已有视图**挂符号/文字；两条都必须可回读
    # ══════════════════════════════════════════════════════════════════
    # 签名: def auto_insert_center_marks(drawing_model, requirements) -> dict   ← :1883
    ToolSpec(
        name="solidworks_drawing_auto_insert_center_marks",
        title="Auto Insert Center Marks",
        module="sw_drawing", function="auto_insert_center_marks",
        inject="drawing_model",
        idempotent=False,
        params=[
            Param("requirements", list,
                  description="★ **结构化入参**（本仓无先例，见 cand-C §3.2）：一个 dict 的列表，"
                              "每个元素是 `{\"id\": str, \"view\": str, \"count\": int, "
                              "\"targets\": [str]}`。"
                              "· `view` 取值经实现 `_normalise_orientation`（`:631-647`）归一，"
                              "认 `front`/`top`/`right` 及其中文别名 前视·上视·右视。"
                              "· `targets` 取 `holes` / `fillets` / `slots`"
                              "（官方 `swAutoInsertCenterMarkTypes_e`，实现 `:45-49` 已录成 1/2/4，"
                              "内部按位或）。"
                              "· `count` = 期望的标记数量（小于已有数量时**不重复插**）。"
                              "空列表 ⇒ 直接返回 `not_requested`，不报错。"),
        ],
        doc="★ **中心符号线 / 中心标记**：`IView.AutoInsertCenterMarks2(…)`。"
            "★ 判据 = **实体数量回读**（`before_count` / `after_count` / `created_count`），"
            "**不是** API 返回值 —— 这与本仓「COM 返回值不可信」的纪律同源。"
            "⚠ 实现会在插入前 `ActivateView`；图纸**没保存**时可能回 "
            "`DRAWING_CENTER_MARK_DRAWING_SAVE_REQUIRED`（`retryable=True`）。"
            "⚠ 任一条 requirement 解析不到（视图名不匹配 / `count<=0` / targets 全不认识）"
            "⇒ 该条 `status=failed`、**不抛异常**，所以返回值里每条都要单独看。",
    ),
    # 签名: def add_note(drawing_model, x, y, text)   ← :1238
    ToolSpec(
        name="solidworks_drawing_insert_note",
        title="Insert Drawing Note",
        module="sw_drawing", function="add_note",
        inject="drawing_model",
        param_alias=_consumed("x_mm", "y_mm"),
        derived_args=_xy,
        idempotent=False,
        params=[
            Param("x_mm", float, description="注释锚点 X，**毫米**。"
                                             "★ 实现 docstring 逐字写「坐标（**米**）」⇒ 换算一次。"),
            Param("y_mm", float, description="注释锚点 Y，**毫米**（同上）。"),
            Param("text", str,
                  description="要写入图纸的文字。⚠ 空串 / 纯空白 ⇒ 直接返回 "
                              "`DRAWING_NOTE_INPUT_INVALID`（`created=False`，**不抛**）。"),
        ],
        doc="★ **工程图文字注释**：`IModelDoc2.InsertNote(text)` → 设位置 → `ForceRebuild3` → 回读。"
            "★ 返回**可审计证据**：COM 回读文字 `text` + `position_m`（**米**）+ 边界 `box`。"
            "⚠ 边界要在**视图重新枚举之后**才是准的 —— 实现注释逐字写着「边界仍必须在视图重枚举后的"
            "结构审查阶段读取」⇒ 单看这里的 `box` 会低估。",
    ),

    # ══════════════════════════════════════════════════════════════════
    # C 域 · 表注解 —— 孔表 / 修订表 / 通用表 / BOM **共用同一个官方入口**
    # ══════════════════════════════════════════════════════════════════
    # 签名: def insert_table_annotation(drawing_model, x: float, y: float, table_type: int,
    #                                  row: int = 0, column: int = 0, *,
    #                                  template: str = "", use_anchor_point: bool = False)
    #        ← drawing_workflow.py:2306-2316（多行 def）
    ToolSpec(
        name="solidworks_drawing_insert_table_annotation",
        title="Insert Table Annotation (Hole / Revision / General)",
        module="sw_drawing", function="insert_table_annotation",
        inject="drawing_model",
        param_alias=_consumed("x_mm", "y_mm"),
        derived_args=_xy,
        idempotent=False,
        params=[
            Param("x_mm", float, description="表左上角 X，**毫米**。⚠ 单位存疑，见 §3.3。"),
            Param("y_mm", float, description="表左上角 Y，**毫米**。⚠ 单位存疑，见 §3.3。"),
            Param("table_type", int,
                  description="★ **官方 `Int32 Type`，决定表的种类**（孔表 / 修订表 / 通用表 / BOM）。"
                              "⚠⚠ **取值表两套官方源都查不到** —— 实现来源块逐字写「其枚举在两套官方源里"
                              "都查不到（`sw_know` 检索无对应枚举定义）…**只做透传、不设默认类型**」。"
                              "⇒ ★ **本工具不提供默认值，也不猜**：请按官方文档填，或先自己核。"),
            Param("row", int, default=0, description="官方 `Row`（插入时的行位）；默认 0 = 让 SW 自己定。"),
            Param("column", int, default=0, description="官方 `Column`；默认 0 = 让 SW 自己定。"),
            Param("template", str, default="",
                  description="★ **给非空值就走 7 参的 `InsertTableAnnotation2`，给空串走 5 参的 "
                              "`InsertTableAnnotation`** —— 两条是不同官方入口，不是同一入口的两种调用。"),
            Param("use_anchor_point", bool, default=False,
                  description="仅 `InsertTableAnnotation2`（`template` 非空）那一条用得上：官方 `UseAnchorPoint`。"),
        ],
        doc="★ **表注解**：孔表 / 修订表 / 通用表 / BOM **共用这一个官方入口**"
            "（`IDrawingDoc.InsertTableAnnotation(2)`），只由 `Type` 区分。"
            "★ 所以**「孔表」和「修订表」在本仓是同一条路、同一个工具** —— "
            "把它们拆成两个工具就等于**硬编码一个查不到的枚举值**，本工具明确不做这件事。"
            "⚠⚠ `table_type` 的取值表**查不到**（两套官方源都没有）⇒ 只透传（铁律 5）。"
            "⚠ 返回的是 COM 表注解对象；**要改单元格还要再走一层**"
            "（`read_table_text` / `set_table_row_hidden` / `sort_table` …），"
            "★ 而那一层的首参是**表对象** ⇒ **本批挂不了**（见 §3.1）。",
    ),

    # ══════════════════════════════════════════════════════════════════
    # D 域 · 图纸页与图框 —— 参数是**页属性**（图幅码 / 投影法 / .slddrt），不是几何
    # ══════════════════════════════════════════════════════════════════
    # 签名: def set_sheet_format(drawing_model, format_path)   ← :1400
    ToolSpec(
        name="solidworks_drawing_set_sheet_format",
        title="Set Sheet Format (Title Block Template)",
        module="sw_drawing", function="set_sheet_format",
        inject="drawing_model",
        params=[
            Param("format_path", str,
                  description="图纸格式文件路径（**`.slddrt`**）。⚠ 实现**不检查存在性** —— "
                              "路径不存在时的表现由 SolidWorks 决定，本工具不预判。"),
        ],
        doc="★ **图纸格式 / 图框**：`GetCurrentSheet().SetTemplateName(format_path)`。"
            "★ 只作用在**当前页**（`GetCurrentSheet`）。"
            "⚠ 与 `solidworks_drawing_setup_sheet` 的分工：那个走 `SetupSheet6`（**连图幅一起设**），"
            "这个**只换图框、不动图幅**。",
    ),
    # 签名: def add_sheet(drawing_model, paper_size=7, template_path="", first_angle=True)
    #        ← :1411
    ToolSpec(
        name="solidworks_drawing_add_sheet",
        title="Add Drawing Sheet",
        module="sw_drawing", function="add_sheet",
        inject="drawing_model",
        param_alias=_consumed("projection"),
        derived_args=_first_angle,
        idempotent=False,     # ★ 每调一次多一页 ⇒ 不幂等
        params=[
            Param("paper_size", int, default=7,
                  description="官方图幅码：0=A · 1=B · 2=C · 3=D · 4=E · 5=A4 · **6=A3** · "
                              "7=A2（★ 本工具的默认值 = 实现默认值 7 = **A2**，不是 A3）· "
                              "8=A1 · 9=A0。⚠ 这张表来自实现 docstring（`:1416-1419`），"
                              "★ **未与官方枚举独立核对过**。"),
            Param("template_path", str, default="",
                  description="图纸格式模板路径（`.slddrt`）；空串 = 不带图框。"),
            Param("projection", str, default="first_angle",
                  description="投影法：`\"first_angle\"`（第一角法）或 `\"third_angle\"`（第三角法）。"
                              "⚠ 对外叫 `projection` 而不叫 `first_angle` —— 后者含 `angle`、"
                              "会被规则 2 的角度那一半拦下（它不是角度）。"),
        ],
        doc="★ **加图纸页**：`IDrawingDoc.NewSheet4(\"\", paper_size, 12, 1.0, 1.0, "
            "first_angle, template_path, 0, 0, \"\", 0, 0, 0, 0, 0, 0)`。"
            "★ 注意：实现**把投影法放在第 6 参**，而 `sw_dwgProjectionType_e` 的官方含义"
            "本轮**没读到** ⇒ 只搬运、不解释。"
            "★ 想「选本机 A3 图框 + 建横向 A3 页」请用 `solidworks_drawing_setup_sheet`"
            "（它会先按候选打分选模板再 `SetupSheet6`，并回读证据）。",
    ),
    # 签名: def setup_current_sheet(drawing_model, template_candidates, *,
    #                              paper_size="A3", projection="first_angle", require_gbt=True)
    #        ← :2042（多行 def）
    ToolSpec(
        name="solidworks_drawing_setup_sheet",
        title="Setup Current Sheet (Template Selected, With Evidence)",
        module="sw_drawing", function="setup_current_sheet",
        inject="drawing_model",
        params=[
            Param("template_candidates", list,
                  description="★ **候选 `.slddrt` 路径的列表**（本仓 list 型入参无先例，见 §3.2）。"
                              "实现按「文件存在 +8 / 是 .slddrt +4 / 文件名含图幅 +2 / GB·国标 +1 / "
                              "本地化目录 +2」打分，取最高分。"
                              "⚠ 候选为**空** ⇒ 直接 `blocked`，不创建。"),
            Param("paper_size", str, default="A3",
                  description="图幅字符串，取 `A4`/`A3`/`A2`/`A1`/`A0`（实现 `PAPER_SIZES` `:21-27`）；"
                              "其它值 ⇒ **抛 `ValueError`**。"),
            Param("projection", str, default="first_angle",
                  description="`first_angle` 或 `third_angle`；其它值 ⇒ **抛 `ValueError`**"
                              "（实现自己会验，本工具不重复）。"),
            Param("require_gbt", bool, default=True,
                  description="True = 候选里必须有 GB/T 字样（`gbt` / `国标` / `gb`）；"
                              "False = 只要是 .slddrt 且文件名含图幅。"),
        ],
        doc="★ **按配置设置当前图纸页并回读证据**：选模板 → `IDrawingDoc.SetupSheet6(...)`。"
            "★ 返回里带 `status`（pass/blocked/failed）· `stage` · `retryable` · `sheet_name` · "
            "`projection` · `manual_review_required`。"
            "⚠⚠ 实现**只把文件名当证据**，逐字写「**不把命名匹配宣称为模板内容已合规**」，"
            "返回里 `gbt_content_verified` 恒为 `False` ⇒ 命中 GB/T 名字**不等于**图框内容合规。"
            "⚠ 实现来源块用的入口是 `SetupSheet6`，而 `recon/api/` 下**只有 `SetupSheet5.md`、"
            "没有 SetupSheet6 的页** ⇒ ★ 本工具的官方依据**不完整**（见 §3.3）。",
    ),
]

#: ★★ 注册器按 `SPECS_*` 找（与 batch72 同一收尾）
SPECS_BATCH73 = _BATCH73
```

★ 落地时**还要**加的一行（本次不改任何已有文件，故只写在方案里）：
`register_capabilities.py` 的 `BATCH_MODULES` 元组末尾加 `"tool_specs_batch73",`。

---

## 三、风险与未决

### 3.1 ★ 挂不了的（首参是 COM 对象 —— 架构性，不是参数没找对）

判据在 `tool_registry.py:507` + `:499-507`：注入键**只能**是 `RESOLVERS` 的键（现有 **6** 个：
`model` / `sw_app` / `study` / `asm_model` / `manager` / `drawing_model`），
而**所有注入键产出的都是「文档 / 应用 / 研究」这一类宿主对象** ——
**没有任何一个产出「表注解对象」或「视图对象」**。

| 能力 | 函数（`def` 行） | 首参 | 为什么挂不了 |
|---|---|---|---|
| 孔表（取底层表） | `get_hole_table(table)` `:2425` | 表注解对象 | 没有 `table` 解析器 |
| 孔表（公共读写/排序） | `read_table_text(table,row,column)` `:2351` · `get_table_shape(table)` `:2358` · `set_table_row_hidden(table,row,hidden)` `:2370` · `set_table_column_hidden` `:2377` · `delete_table_row` `:2384` · `delete_table_column` `:2390` · `sort_table(table,option,reverse)` `:2468` · `get_table_custom_property_column(table,column)` `:2453` · `set_table_custom_property_column(table,column,property_name)` `:2460` | 表对象 | 同上 |
| 修订表（增删读） | `add_revision(revision_table, revision)` `:2489` · `delete_revision(revision_table,index,mark_deleted)` `:2496` · `get_current_revision(revision_table)` `:2503` | 修订表对象 | 同上 |
| 其它表族 | `get_general_table` `:2418` · `get_bend_table` `:2432` · `get_weldment_cutlist_table` `:2439` · `get_revision_table_feature` `:2446` | 表注解对象 | 同上 |
| 剖面线相关 | `get_section_view_data(section_view)` `:2533` · `set_section_style(...)` `:2540` · `activate_annotation_view(annotation_view,…)` `:2648` · `get_annotation_view_evidence(annotation_view)` `:2656` · `create_section_view_data(model)` `:2718` · `create_feature_manager_section_view(model,section_data)` `:2729` · `get_feature_manager_section_data(model,name)` `:2737` · `remove_feature_manager_section_view(model)` `:2743` | 视图 / 标注视图 / `ISectionViewData` 对象 | 没有对应解析器；且 `section_data` 是**指针型**成员（`I` 前缀族，与已知事实 47 同族） |
| 尺寸标注 | `insert_dimensions(drawing_model, view=None)` `:1079` | `view` 是视图对象 | `view=None` 时可挂（标注全部视图），但**挂了就只能标全部**、没有"只标某个视图"的表面 ⇒ 本批**不挂**，留作后续决策 |
| **表面粗糙度（插入侧）** | —— | —— | ★ **`drawing_workflow.py` 里根本没有插入实现**：全文件只有 `surface_finish_symbols` 这个**读侧**字段（`:1660` / `:1695` / `:1701` / `:1725`）；`InsertSurfaceFinishSymbol3` 只出现在 `references/api-lookup.md:11` 的**清单**里 ⇒ **没有函数可挂**。读侧已由 `solidworks_inspect_drawing` 覆盖（`tool_specs_batch19.py:7` 逐字写「其实现的内核正是 `drawing_workflow.inspect_drawing_structure`」） |

⇒ **要解锁后两类只有两条路**：① 给 `RESOLVERS` 加解析器（角度 C）；② 把这些函数重写成吃
`drawing_model` 的薄封装（角度 B）。**本角度两条都不选，只把天花板标出来。**

### 3.2 ★ 门禁形状的风险（本批引入的两个"无先例"形态）

| 形态 | 出现在 | 为什么是风险 | 本批的处置 |
|---|---|---|---|
| `list` 型入参 | #3 `requirements` · #5 `template_candidates` · #8 `template_candidates` | ★ 本仓 72 个批次文件里**没有一条 `list` 型入参**；`register_capabilities.py` 里 batch14 的注记逐字写「本批也**不暴露** views/expected_outputs（**list 型无先例**）」。`build_input_model` 只是把它当 Pydantic 注解（`tool_registry.py:456-471`）⇒ **不会崩**，但**门禁没覆盖过这个形态** | 如实声明为无先例；两个 `template_candidates` 我都给了**默认值/空列表语义由实现兜住**（空 ⇒ `blocked`，不抛），避免调用方必须先造列表才能试 |
| `idempotent=False` | #1 #2 #3 #4 #5 #7 | ★ **本仓 72 个批次文件里没有一处显式写过它** ⇒ 这一行是**首次使用**，现有测试**没有覆盖** | 写了，并在工具 doc 里说明"每调一次多一个 X"。若评审认为"没覆盖就不该用"，**删掉这 6 行即可**（`idempotentHint` 会退回默认 `True`，只是提示不准，不影响功能） |

### 3.3 未决（逐条，需要人拍板或补查）

1. **`insert_table_annotation` 的 `x`/`y` 单位**：本函数**既没在 docstring 也没在来源块里写单位**。
   我按"图纸坐标 = 米"处理（依据是同文件 `add_note` 的 docstring 明确写「米」）⇒ **这是推断，不是核实**。
   若实际是别的量纲，#5 会差 1000×。
2. **`SetupSheet6` 的官方依据不完整**：`recon/api/` 下只有 `SetupSheet5.md`，没有 `SetupSheet6`。
   `drawing_workflow.py:1509-1518` 那段 `SetupSheet6` 的实参表是**照反射写的** ⇒ #8 的 20 个实参顺序**未经官方页复核**。
3. **`CreateSectionViewAt5` 的形参表本轮没读到** ⇒ #1 只搬运 `("", 0, None, 0)` 这几个写死值，不解释。
4. **`table_type` 取值表查不到**（两套官方源都没有）⇒ #5 逼调用方自己填。**若要拆成"孔表工具/修订表工具"两个，必须先补这个枚举**，
   否则就是编造。
5. **`add_sheet` 的图幅码表**来自实现 docstring（`:1416-1419`），未与官方 `swDwgPaperSizes_e` 独立核对
   （且与 batch19 真机探针里 `paperSize=6 ⇒ A4` 的读数**看起来方向相反**，需核）。
6. **工具名与覆盖率关键词**：`solidworks_drawing_insert_table_annotation` 名字里**没有** `hole` / `revision`
   ⇒ 若覆盖率脚本按功能关键词**子串**计分，"孔表 / 修订表"这两项**不会**被记到这条工具名下。
   我选择**跟目标函数名对齐**（可追溯），不为了计分改名。**这是取舍，要人拍板。**
7. **8 条 ≠ 8 项能力**：题述 8 项里，**表面粗糙度 0 条新工具**（无插入实现、读侧已被 `solidworks_inspect_drawing` 覆盖），
   **孔表与修订表合并成 1 条**（同一个官方入口 + 枚举查不到），而 **D 域给了 3 条**补足到 8。
   ⇒ 若要求"一项能力一条工具"的严格 1:1，**这一批交不出 8 条**，只能交 7 条（去掉 `setup_sheet`）。
8. **未跑真机**：本轮**没跑 SolidWorks、没跑 pytest、没注册**。8 条里 `add_detail_view` 的实现来源块
   **自己就写着"未在本机实测"**，`insert_table_annotation` 那一组也写着"照官方签名新写、未实测"
   ⇒ 这批的验证等级应是 **`stitched`**，不是 `verified`（AGENTS.md 停止条件第 6 条）。