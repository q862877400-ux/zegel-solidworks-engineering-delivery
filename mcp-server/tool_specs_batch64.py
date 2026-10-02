
# ── 200 轮计划 v3 · 段 1 收口：**连接件族的第三条（link）** ──────────────────────────
# ★★★★★ 2026-10-03（轮 458–459）★ 来源：**事实 372 / 373 / 374** —— 而这是那条链的**终点**。
#
# ★★ **它为什么此前建不成**（★ 五次全失败 ⇒ 而真因**两层**）：
#   ```
#   ① ★ **形态错**：★ `AddLinkConnector` 的形参名是 **`VertexPointforFirst/SecondLocation`**
#      ⇒ ★★ 它要**顶点**，★ 而我此前传的是**面 / 组件** ⚠（★ 事实 341 那五种给法全 `0→0`）
#   ② ★ **out 参数**：★ 官方是 **arity 3**（含 `ByRef ErrorCode`）⇒
#      ★★ 而**本仓的 `_check` 早已统一补 `out_i4()`**（★ 轮 348 修的）✓
#   ```
# ★★★ **真机（事实 373）**：★ `Count` **0 → 1**（★ 而★ 带对照：**同一体**上的两个顶点**也成**）✓
#   ★★ 而★ **本仓的包装**（`add_link_connector`）**本来就是对的** ——
#     ★ 我一度以为"它只传 2 个实参要修"，★ 而**读了 `_check` 的实现**才发现它自动补 out（★ 事实 374）✓
#
# ★★ **本工具为什么收**声明式选择器****（★ 规则 3 的判断 · 事实 367 那条）：
#   ```
#   ★ `add_link_connector(manager, objA, objB)` **吃两个 COM 对象** ⇒ **没法入参数表达**
#   ★★ 故本工具让调用方给两个**声明式选择器**，★ 而对象**在能力层内部解析**
#      （★ `sw_selection_spec.resolve_entity` · ★ `kind = "VERTEX"`）✓
#   ```
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch64.py —— 本文件
# 定位:   把 `add_link_connector_report` 挂成 MCP 工具（★ 段 1「救回 B 组两条连接件」的收口）。
# 官方依据: `SolidWorks.Interop.cosworks.ICWLoadsAndRestraintsManager.AddLinkConnector`
#   （★ arity 3 · 形参名 `VertexPointforFirstLocation` / `VertexPointforSecondLocation` / `ByRef ErrorCode`）·
#   本仓 `scripts/sw_simulation_loads.py` 的 `add_link_connector_report` / `add_link_connector` / `_check` ·
#   `scripts/sw_selection_spec.py` 的 `ENTITY_KINDS`（★ 含 `VERTEX`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec
from tool_specs_batch29 import _STUDY, _consumed, _derive_model

__all__ = ["SPECS_BATCH64"]

_VERT = ("Declarative selector for a **VERTEX** — ★ `index:<n>`（体上第 n 个顶点，从 0 开始）· "
         "`__current_selection__`（用当前选区里的第一个，**不重选**）· 或一个 COM 对象。"
         "★★ **不接受裸坐标**（★ 规则 3）。★ 它由 `sw_selection_spec.resolve_entity` 解析 ——"
         "★ 解析不了会**抛**（★ 而不是静默不选）。")

SPECS_BATCH64 = [
    ToolSpec(
        name="solidworks_simulation_apply_link_connector",
        title="Apply a Link Connector (between two vertices)",
        module="sw_simulation_loads", function="add_link_connector_report",
        inject="manager",
        #: ★★ 只声明 `study_name` 被消费（★ 本工具**不读选区** —— 它用两个选择器自己解析）
        param_alias=_consumed("study_name"),
        derived_args=_derive_model,
        params=[
            Param("study_name", str, default="", description=_STUDY),
            Param("first", str, description="★ 第一个顶点的选择器。" + _VERT),
            Param("second", str, description="★ 第二个顶点的选择器。" + _VERT),
            Param("first_body_index", int, default=0,
                  description="★ 第一个选择器里的 `index:<n>` 落在**第几个体**上（★ 0 基）"),
            Param("second_body_index", int, default=0,
                  description="★ 同上（★ 第二个）—— ★★ 而两个顶点**可以在同一个体上**"
                              "（★ 真机验过 · 事实 373）"),
        ],
        doc=("Add a **LINK CONNECTOR** between two **vertices** and return a READ-BACK report. "
             "★★ **它要的是「顶点」** —— ★ 官方形参名就是 `VertexPointforFirst/SecondLocation`。"
             "⚠★ **不要传面 / 组件**（★ 那一族是 `AddRigidConnector` 收面、`AddPinConnector` 收组件）——"
             "★ 传错会**静默不建**（★ 事实 341 那五次就是这么来的）。"
             "★ `ok` 的判据是**回读**：载荷与约束计数 **恰好 +1**（★ **不是**返回值 —— 事实 8）。"),
    ),
]
