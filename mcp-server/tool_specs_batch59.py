# ── 24h 计划 v2 · 段 6：**导出**（本批只注册一条）─────────────────────────────────────
# ─
# ★★★★ 2026-10-03（轮 403）来源：`tools/triage_real_gaps.py` 的五层证据给出 `sw_export`
# 的 5 条「该挂」，
#   ★ **逐个核过**（★ 不靠再加弱规则）：
# · `export_to_bmp`  ⇒ ★ **不是缺口** —— 已由 `export_bmp_report`（工具 `solidworks_expo
# rt_bmp`）
#                          覆盖，★ 只是**基础名不同**（`export_bmp` vs `export_to_bmp`）。
# · `batch_export` / `set_mass_property_override` ⇒ ★ 各自需要 `sw_app` 注入 / COM 前置
# 链 ⇒ **后批**。
#
# ★★ **本批的 `export_image` 真机 PASS**（`exists=true` · `size_bytes=67997` · `grew_or_
# created=true`）
#   —— ★ 而它**之所以能成，是因为本轮真机先抓到一个真 bug 并修掉了**：
#   ★★ `export_to_image` 里用了 `out_i4()`（本项目的**标量出参包装**），
# ★ 而 `sw_export.py` **漏了导入它** ⇒ 一调就 `NameError: name 'out_i4' is not defined`
# 。
# ★★ **静态语法门禁抓不到**（那是**运行期**的 NameError）—— ★ 而这也正是它**一直没被挂成
# 工具**的原因：
#     ★ **谁碰谁崩**。★ 已补 `from sw_connect import … out_i4`。
#
# ★★ **`export_flat_pattern_dxf` 本批不注册**：★ 它的前置是**钣金件**，
# 而真机在**非钣金件**上得到的是**正确的显式拒绝**（`ValueError: 导出展开 DXF 前必须先保
# 存钣金零件`）
#   ⇒ ★ 按硬约束⑥「**验不过的回退、不许留在柜台上**」**不注册**；
#   ★ 而**包装与探针保留**（★ 下次先造一个钣金件即可接上）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch59.py —— 本文件（新）
# 定位:   24h 计划 v2 段 6：把 `export_image_report` 挂成 MCP 工具。
# 官方签名依据: `IModelDocExtension.SaveAs3`（★ 图片过滤器）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec

_PATH = (
    "绝对输出路径。★ **判据是 READ-BACK**：文件必须**存在且非空**，"
    "★ 并附 `size_before` / `grew_or_created`（★ 区分「这次真导出了」与「旧文件本来就在」）。"
)

SPECS_BATCH59 = [
    ToolSpec(
        name="solidworks_export_image",
        title="Export the Current View as an Image",
        module="sw_export",
        inject="model",
        function="export_image_report",
        params=[
            Param(
                "output_path", str, description="Absolute output path; the file extension selects PNG or JPG."
            ),
        ],
        evidence=(
            "★ **把当前视图存成图片**（PNG / JPG，走官方 `IModelDocExtension.SaveAs3`）。★★ 判据**不是返回值**而是**文"
            "件**：`ok = 无异常 且 文件存在 且 size > 0`。★ 另回 `size_before` / `grew_or_created` —— ★ 免得把「旧文件"
            "本来就在」当成导出成功。★ 真机证据：一张 PNG ⇒ `exists=true` · `size_bytes=67997` · `grew_or_created=true`"
            "。⚠ 尺寸**不可指定**（`SaveAs3` 没有尺寸入参）⇒ ★ 按**当前视图**。（★ 要指定像素尺寸请用 `solidworks_expor"
            "t_bmp`。）"
        ),
        doc=(
            "Export the current view to a PNG or JPG image file. Writes the image file to output_path. The criterion is"
            " that the file exists and is not empty, and the image size cannot be chosen because the current view is ca"
            "ptured as it is."
        ),
    ),
]
