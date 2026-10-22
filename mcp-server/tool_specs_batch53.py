# ── 24h 计划 v2 · 段 1：**选择底座**（`sw_selection_spec` 的 6 条真缺口）──────────────
# ──
# ★★★★ 2026-10-03（轮 397）来源：`tools/triage_real_gaps.py` 判定的 **76 条「该挂」**里
#   杠杆最高的一族 —— ★ **选择是每一次真机验证都要用的东西**（★ 与事实 32 / 8 直接相关）。
#
# ★ **本批 6 条的形态分两类**（★ 这是分诊之外的**第二层判断**，逐条写清）：
#   ```
#   ① 直接可挂（返回已经是 JSON 安全的值：dict / int）—— 4 条
#      get_selection_count · select_entity_by_index · resolve_selection · selection_point
#      ★ 其中 `selection_point` 本来就回 `{ok, point_mm, selection_count, error}` ⇒ 零改造
#   ② 需要 report 包装（★ 返回值里有 **COM 对象** ⇒ MCP 层过不去）—— 2 条
#      select_object（**吃**一个 COM 对象）· resolve_entity（**吐**一个 COM 对象）
#      ⇒ 已在 `scripts/sw_selection_spec.py` 尾部加 `select_by_selector_report` /
#        `resolve_entity_report`（★ 只回 JSON）
#   ```
#
# ★★ **判据统一用回读计数**（★ 事实 8：`SelectByID2` / `Select4` 的 bool 返回值不可信，
#    只有 `ISelectionMgr.GetSelectedObjectCount2(-1)` 的回读算数）。
# ★ 规则 2：★ `selection_point` 回的是**毫米**（`point_mm`），★ 不在工具层再换算。
# ★ 规则 3：★ 对外只暴露**声明式选择器字符串**（`__current_selection__` / `index:<n>`）
# ，
#   ★ **不传坐标、不传 COM 对象**。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch53.py —— 本文件（新）
# 定位:   24h 计划 v2 段 1：把 `sw_selection_spec` 的选择底座族挂成 MCP 工具。
# 官方签名依据: `ISelectionMgr.GetSelectedObjectCount2`（回读计数）· `IEntity.Select4`（
# 按对象选）·
#   `IModelDocExtension.SelectByID2`（★ 对边/面**按名字选不中** —— 事实 32）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec

SPECS_BATCH53 = [
    ToolSpec(
        name="solidworks_selection_count",
        title="Selection Count",
        module="sw_selection_spec",
        function="get_selection_count",
        inject="model",
        read_only=True,
        doc="★ **回读当前选区计数**（`ISelectionMgr.GetSelectedObjectCount2(-1)`）。"
            "★★ 它是**选择类判据的唯一来源** —— 事实 8：`SelectByID2` / `Select4` 的 bool 返回值"
            "不可信（实测 12 次全 false 而计数 = 12）⇒ ★ **判「选没选中」永远看本工具的回读数**。",
        param_alias={},
        params=[],
    ),
    ToolSpec(
        name="solidworks_select_entity_by_index",
        title="Select Entity By Index",
        module="sw_selection_spec",
        function="select_entity_by_index",
        inject="model",
        doc="★ **按序号选中体上的一个实体**（`kind` = `EDGE` / `FACE` / `VERTEX`，`index` 从 0 起）。"
            "★ 走 `IEntity.Select4`（★ 事实 32：对边/面**按名字选不中**，按**对象**选才行）。"
            "★ 返回**回读到的选区计数**。"
            "⚠ 序号顺序官方**未承诺稳定**（★ 见 `entities_on_body`）⇒ 不要把它当跨重建的持久引用。",
        param_alias={},
        params=[
            Param("kind", str, description="实体种类：EDGE / FACE / VERTEX"),
            Param("index", int, description="体上的序号（★ 从 0 开始，本模块的约定）"),
            Param("body_index", int, default=0, description="第几个体（★ 从 0 开始）"),
            Param("append", bool, default=False, description="True = 追加到现有选区"),
        ],
    ),
    ToolSpec(
        name="solidworks_resolve_selection",
        title="Resolve Selection (count)",
        module="sw_selection_spec",
        function="resolve_selection",
        inject="model",
        doc="★ **把声明式选择器解析并选中**，只回报**回读到的选区计数**。"
            "★ 选择器：`__current_selection__`（用当前选区第一个，**不重选**）· `index:<n>`（体上第 n 个）。"
            "★ 计数为 0 时**抛错**（★ 本项目一贯纪律：选不中就报错，不静默继续）。",
        param_alias={},
        params=[
            Param("selector", str, description="声明式选择器：__current_selection__ 或 index:<n>"),
            Param("kind", str, default="EDGE", description="实体种类：EDGE / FACE / VERTEX"),
            Param("body_index", int, default=0, description="第几个体（★ 从 0 开始）"),
        ],
    ),
    ToolSpec(
        name="solidworks_selection_point",
        title="Selection Point (mm)",
        module="sw_selection_spec",
        function="selection_point",
        inject="model",
        read_only=True,
        doc="★ **读当前选区那个点的坐标**（★ **毫米**，规则 2）。"
            "★★ 用途：★ 孔族吃 `center`（一个坐标元组）⇒ 包一层「**先选点、再建孔**」"
            "⇒ ★ **工具层的参数里就没有坐标了**（★ 规则 3 的精神）。"
            "★ 回 `{ok, point_mm, selection_count, error}`；⚠ **不猜**："
            "★ `GetSelectionPoint` 取不到就 `ok=False` 并写明原因（★ 铁律 5）。",
        param_alias={},
        params=[],
    ),
    ToolSpec(
        name="solidworks_select_by_selector",
        title="Select By Selector",
        module="sw_selection_spec",
        function="select_by_selector_report",
        inject="model",
        doc="★ **用声明式选择器选中一个实体** —— ★ MCP 可用的形态（★ 只回 JSON，**不回 COM 对象**）。"
            "★ 它把 `select_object`（吃 COM 对象）与 `resolve_entity`（吐 COM 对象）**接起来**。"
            "★★ 判据是 `count`（★ 事实 8：`Select4` 的返回值不可信，只有回读算数）；"
            "★ 计数为 0 时 `ok=False` **并写明原因**。",
        param_alias={},
        params=[
            Param("selector", str, description="声明式选择器：__current_selection__ 或 index:<n>"),
            Param("kind", str, default="EDGE", description="实体种类：EDGE / FACE / VERTEX"),
            Param("body_index", int, default=0, description="第几个体（★ 从 0 开始）"),
            Param("append", bool, default=False, description="True = 追加到现有选区"),
        ],
    ),
    ToolSpec(
        name="solidworks_resolve_entity",
        title="Resolve Entity (report)",
        module="sw_selection_spec",
        function="resolve_entity_report",
        inject="model",
        read_only=True,
        doc="★ **解析声明式选择器并回报结果**（★ 只回 JSON —— 把 COM 对象挡在里面）。"
            "★ `resolve_entity` 本身**返回 COM 对象** ⇒ MCP 层过不去 ⇒ 本工具换成可核对的描述。"
            "★ 回 `{ok, selector, kind, count, resolved}`：★ `resolved` = 解析出了对象；"
            "★★ 而**是否真的在选区里**看 `count`（★ **解析出来 ≠ 选中**）；"
            "★ 而 `__current_selection__` 是**不重选**的 ⇒ 那种情况下 `resolved=True` 而 `count=0` 是正常的。",
        param_alias={},
        params=[
            Param("selector", str, description="声明式选择器：__current_selection__ 或 index:<n>"),
            Param("kind", str, default="EDGE", description="实体种类：EDGE / FACE / VERTEX"),
            Param("body_index", int, default=0, description="第几个体（★ 从 0 开始）"),
        ],
    ),
]
