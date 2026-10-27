# ── 24h 计划 v2 · 段 4：**孔族**（按孔位批量建孔）────────────────────────────────────
# ★★★★ 2026-10-03（轮 401）来源：`tools/triage_real_gaps.py` 判定 `sw_hole_features` 的
# 3 条「该挂」里，
#   ★ **只有 `create_hole_pattern` 挂得成** —— 另两条（`configure_straight_tap` /
#   `configure_tapered_tap`）**吃 COM 元素对象**（`IStraightTapElementData` /
#   `ITaperedTapElementData`），★★ 而本仓**没有任何路径能从孔特征拿到那个元素**
#   （★ 它们只在 mock 测试里出现过）⇒ ★ MCP 层**给不出** ⇒ 记「内部件」并写清理由。
#
# ★★ **这一条为什么要包装**：`create_hole_pattern(model, positions, creator, **kwargs)`
# 收的是
#   **一个可调用对象** —— ★ 而 MCP 层**给不出函数** ⇒ 包装把它换成**具名的种类** `kind`。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch57.py —— 本文件（新）
# 定位:   24h 计划 v2 段 4：把 `sw_hole_features.hole_pattern_report` 挂成 MCP 工具。
# 官方签名依据: `IFeatureManager.HoleWizard5`（各 `create_*_hole` 走它）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec

SPECS_BATCH57 = [
    ToolSpec(
        name="solidworks_hole_pattern",
        title="Create Holes at Explicit Positions",
        module="sw_hole_features",
        inject="model",
        function="hole_pattern_report",
        params=[
            Param(
                "positions",
                list,
                description=(
                    "Hole centres as [x_mm, y_mm] pairs in millimetres on the sketch plane; coordinates are the documen"
                    "ted exception for sketch geometry."
                ),
            ),
            Param(
                "kind",
                str,
                default="through",
                description="Hole kind: through for a through hole or blind for a blind hole. Defaults to through.",
            ),
            Param("diameter_mm", float, default=8.0, description="Hole diameter in millimetres. Defaults to 8."),
            Param(
                "depth_mm",
                float,
                default=None,
                description=(
                    "Blind-hole depth in millimetres, required when kind is blind. Defaults to unset, which means no de"
                    "pth is given."
                ),
            ),
            Param(
                "plane_name",
                str,
                default="Front Plane",
                description="Sketch plane name, in English or in the localized names. Defaults to Front Plane.",
            ),
            Param(
                "name",
                str,
                default="孔",
                description=(
                    "Prefix for the hole feature names, with a number suffix added per hole; it defaults to this interf"
                    "ace's word for hole."
                ),
            ),
        ],
        evidence=(
            "★ **按显式孔位一次创建一组孔**（★ 官方走 `HoleWizard5` 那族）。★★ 它把 `create_hole_pattern` 的 **`creator"
            "` 可调用对象**换成**具名的 `kind`** ——★ 因为 MCP 层给不出函数对象。★★ 判据**两条都要**：★ 每个孔位都回了证"
            "据 **且** **特征树真的长了**（★ 规则 6）——★ 只回证据而树不动 ⇒ `ok=false` 并写明（★ 本会话已见过「回对象而"
            "什么都没发生」的空存根）。⚠ 本工具只支持 `through` / `blind`：★ `counterbore` / `countersink` 另有必填参数"
            "，未暴露。"
        ),
        doc=(
            "Create one hole per explicit position in the active part. It writes hole features and does not save the do"
            "cument; both criteria must hold, meaning every position returns evidence and the feature tree really grows"
            ", and only through and blind holes are supported."
        ),
    ),
]
