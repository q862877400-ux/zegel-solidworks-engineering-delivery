# ── 24h 计划 v2 · 段 3：**零件/草图的读与自动标注**（`sw_part` 的 2 条真缺口）─────────
# ─
# ★★★★ 2026-10-03（轮 399）来源：`tools/triage_real_gaps.py`（★ 已补到**五层证据**）判定
#  `sw_part`
# 只剩 **4 条**「该挂」，本批先挂**无单位歧义**的 2 条；另 2 条（`add_dimension` / `line
# ar_pattern`）
# ★★ **留到下一轮先测单位** —— 它们的包装**不做换算**而官方 API 吃**米**（★ 文档却说毫米
# ）⇒
#   ★ 在测清楚之前挂出去会把"单位"这个错**固化进工具面**（★ 规则 2 的反面教材）。
#
# ★★ **本轮的第五层证据（空存根检测）抓到一条假能力**：`sw_part.hole_wizard` 有名字、有
# 参数、
# 有文档串（"异型孔向导（简化版）"），★ 而**函数体只有一个 `pass`** ⇒ ★★ 挂出去**必然什
# 么都不发生**，
# 而且比 `sketch_spline` 那种"会报错"的更糟 —— **它会静默成功** ⇒ 已标「不做」并写进证据
# 。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch55.py —— 本文件（新）
# 定位:   24h 计划 v2 段 3：把 `sw_part` 的"读草图名"与"自动标注"挂成 MCP 工具。
# 官方签名依据: `ISketch.AutoDimension2`（★ 5 参，见 `scripts/sw_part.auto_dimension_ske
# tch`）·
# `IModelDoc2.GetActiveSketch2` / `ISketchManager.ActiveSketch`（★ 见 `current_sketch_na
# me`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec

SPECS_BATCH55 = [
    ToolSpec(
        name="solidworks_current_sketch_name",
        title="Current Sketch Name",
        module="sw_part",
        inject="model",
        function="current_sketch_name",
        read_only=True,
        params=[
            Param(
                "fallback",
                str,
                default="Sketch1",
                description="取不到时的回退名（⚠ ★ 中文 UI 下真名是「草图1」而回退是"
                "「Sketch1」—— ★ 所以**回退值不等于真名**，用它去找草图会找不到；"
                "★ 要**稳健取草图**请用 `solidworks_sketch_*` 那族（它们走中英文候选 + 特征树兜底））",
            ),
        ],
        evidence=(
            "★ **读当前活动草图的特征名**。⚠ 它**在草图已关闭时**会回 `fallback`（★ 默认 `Sketch1`）—— ★ 那**不是**真名"
            "（中文 UI 是「草图1」）。★★ 所以：**要按名字去取草图对象时，不要用本工具的返回值** —— ★ 用 `scripts/sw_ske"
            "tch.resolve_sketch`（中英文候选 + 特征树兜底，语言无关）。"
        ),
        doc="★ **读当前活动草图的特征名**。⚠ 它**在草图已关闭时**会回 `fallback`（★ 默认 "
        "`Sketch1`）—— ★ 那**不是**真名（中文 UI 是「草图1」）。"
        "★★ 所以：**要按名字去取草图对象时，不要用本工具的返回值** —— "
        "★ 用 `scripts/sw_sketch.resolve_sketch`（中英文候选 + 特征树兜底，语言无关）。",
    ),
    ToolSpec(
        name="solidworks_auto_dimension_sketch",
        title="Auto-Dimension the Sketch",
        module="sw_part",
        inject="model",
        function="auto_dimension_sketch",
        evidence=(
            "★ **按官方 `ISketch.AutoDimension2` 流程给当前草图建真实模型尺寸** ——★ 生成的尺寸是**真实的 `DisplayDimens"
            "ion`**（★ 可被工程图导入并复核），★ 不是草图里画几条线。★ 回 `{status, status_code, error_code, selected}`"
            "：★ `status` = `pass` / `blocked` / `failed`；★★ `blocked` + `SKETCH_NOT_ACTIVE` = **没有活动草图**（★ 先 "
            "`solidworks_sketch_start`）。"
        ),
        doc="★ **按官方 `ISketch.AutoDimension2` 流程给当前草图建真实模型尺寸** ——"
        "★ 生成的尺寸是**真实的 `DisplayDimension`**（★ 可被工程图导入并复核），"
        "★ 不是草图里画几条线。"
        "★ 回 `{status, status_code, error_code, selected}`：★ `status` = `pass` / `blocked` / `failed`；"
        "★★ `blocked` + `SKETCH_NOT_ACTIVE` = **没有活动草图**（★ 先 `solidworks_sketch_start`）。",
    ),
]
