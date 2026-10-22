
# ── 24h 计划 段 6 续（Spec Kit `164` 的批次声明）：**图纸比例的读与写** ──────────────
# ★ ★★★★ 2026-10-01（轮 301）真机 **PASS 5/5**（★ 证据 `output/sheet-scale-evidence.json
# `）：
#   · 正例：`1:5` ✓ · `1:2` ✓ · `1:1` ✓（★ 三个都 `readback_matches: true`）
#   · 负例：`numerator=3` ⇒ **显式拒绝并列出合法值** ✓ · `-1:5` ⇒ **显式拒绝** ✓
# ★★ 本批工具（2 个）：
# 1. `solidworks_drawing_sheet_scale`（读）—— 走官方 Remarks 指定的 `ISheet.GetPropertie
# s`；
#   2. `solidworks_drawing_set_sheet_scale`（写）—— 走 `ISheet.SetScale`，**带回读判据**。
# ★★★ **而它补上了一个真空**：★ 本会话曾证明 **`IView.ScaleRatio` 读得到、写不进**（事实
#  227/294）
#   ⇒ ★★ **而图纸比例**写得进****（`ISheet.SetScale` 回 `True` 且读回真的变了）
# ⇒ ★ **所以"想改比例"的正解是改**图纸**的比例**（★ 视图默认 `UseSheetScale=True`，会跟
# 着变）。
# ⚠ **未在本机实测**：★ 无（★ 上面 5 项都是真机结果）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch44.py —— 本文件
# 定位:   段 6 续：把 `sw_drawing_query` 新加的两个"图纸比例"包装挂成 MCP 工具。
# 官方签名依据: `C:\swapi\types\ISheet\SetScale.md`（4 参 · 回 bool ·
#   "You can get the two scale values from the sheet by using ISheet::GetProperties"）·
#   `C:\swapi\types\ISheet\GetProperties.md`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec

SPECS_BATCH44 = [
    ToolSpec(
        name="solidworks_drawing_sheet_scale",
        title="Read Drawing Sheet Scale",
        module="sw_drawing_query",
        function="get_sheet_scale_report",
        inject="model",
        params=[
            Param("sheet_name", str, default="", description="图纸名；留空 = 当前图纸（★ 声明式：不传坐标）"),
        ],
        doc="★ **读工程图图纸的比例** —— 走官方 Remarks 指定的 `ISheet.GetProperties`，"
            "取其中两个数作为比例的分子/分母 ⇒ 回 `ratio_text`（如 `1:5`）。"
            "⚠ 顺序是真机定的：`GetProperties` 的第 4 个元素是 Denominator、第 5 个是 Numerator。",
    ),
    ToolSpec(
        name="solidworks_drawing_set_sheet_scale",
        title="Set Drawing Sheet Scale",
        module="sw_drawing_query",
        function="set_sheet_scale_report",
        inject="model",
        params=[
            Param("numerator", float, description="比例前项 —— ★ 真机限制：**只接受 1**（图纸比例只能是 1:n）"),
            Param("denominator", float, description="比例后项，必须 > 0"),
            Param("scale_anno_position", bool, default=False, description="是否同时缩放注释位置"),
            Param("scale_anno_text_height", bool, default=False, description="是否同时缩放注释字高"),
            Param("sheet_name", str, default="", description="图纸名；留空 = 当前图纸"),
        ],
        doc="★ **设工程图图纸的比例并回读** —— 走 `ISheet.SetScale(numerator, denominator, "
            "scale_anno_position, scale_anno_text_height)`（官方 4 参 · 回 bool）。"
            "★ 判据：**它回真、且回读的两个数真的变了**（规则 6：不静默成功）。"
            "⚠ `numerator != 1` 会被**显式拒绝**（★ 真机三组证据：`(1,5)→1:5` · `(3,7)→1:7` · `(2,1)→1:1`）。",
    ),
]
