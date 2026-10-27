"""★ 批次 108：规格 220 · PDM 相邻证据读侧（把 sw_pdm.collect_pdm_evidence 暴露成工具）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（实现与来源块在 scripts/sw_pdm.py）
# 文件:   specs/220-user-coverage-closeout/ 的 目标栏第 15 轮「下一步」
# 定位:   ★ 补一格用户可感知功能：★ **其他/PDM**（生成器关键词 ("pdm","edm")）
#         ★★ **真实现已在**（scripts/sw_pdm.py 的 collect_pdm_evidence）—— ★ 本批只**暴露** ✓
# 官方依据: ★ 见 scripts/sw_pdm.py 的来源块（逐成员记着接口/成员）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **1 个工具** ⇒ 工具数 474 → 475
# ★★★ 等级如实：★★ 本工具**尚未真机验证** ⇒ 台账该条**不提 level**（红线⑥）✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import ToolSpec

SPECS_BATCH108 = [
    ToolSpec(
        name="solidworks_pdm_evidence_report",
        title="Read PDM-adjacent Evidence (custom properties / configs / external refs)",
        module="sw_pdm_report",
        function="collect_pdm_evidence_report",
        inject="model",
        params=[],
        read_only=True,
        evidence=(
            "★ **读一份文档的 PDM 相邻证据**（★ 读侧）—— ★ 把文档的**自定义属性 / 配置 / 外部引用**汇总成一份可核对的结"
            "构化报告 ✓ ★★ 与既有 `solidworks_document_dependencies` 的关系：那个只列**引用清单**；★ 这个给的是**整份 P"
            "DM 相邻证据**（属性 + 配置 + 引用）⇒ ★ 更宽 ✓ ⚠★ **如实标注（不许冒充）**：★ 本工具是 **PDM 相邻**，★ **不"
            "是** SolidWorks PDM Professional（★ 那需要 **PDM 许可证**，★ 本仓的 `pdm` 台账条目仍是 `not_implemented`）"
            "✓ ★ 判据：★ 回的是结构化证据（★ 读不到就如实报，★ 不假装有内容）✓"
        ),
        doc=(
            "Report the PDM-adjacent evidence of a document: custom properties, configurations and references. Read-onl"
            "y; it is not SolidWorks PDM Professional, which needs a PDM licence, and it reports a field it cannot read"
            " instead of filling in a value."
        ),
    ),
]
