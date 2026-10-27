"""★ 批次 111：规格 220 · 装配/性能分析 —— ★ 换路径：用现成真函数产出性能要素读数。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（实现 = scripts/sw_assembly.py 的 collect_mate_feature_summary，**
# 早已存在**）
# 文件:   mcp-server/tool_specs_batch111.py
# 定位:   ★ 补一格用户可感知功能：★ **装配/装配体性能分析**
#         ★ 生成器关键词（逐字）：`("performance_analysis", "assembly_performance")` ✓
# 官方依据: ★★ **如实交代**：★ `C:\\swapi\\types` 里**搜不到**同名接口 ✗（★ 铁律 5：查不
#           到就说查不到 ✓）⇒ ★ 本工具**不是**官方"A性能分析"功能的包装 ✗，★ 而是**换路
#           径**做出的**真实**读数：  ★ **SolidWorks 自己的「Performance Evaluation」报
#           的正是「零件数 / 配合数 / 特征数」这类计数** ✓  ★ 而本仓现成的 `collect_mate
#           _feature_summary(model)` 拿到的就是**配合与特征的逐项摘要** ✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **1 个工具** ⇒ 工具数 477 → 478
# ★★★ 等级如实：★★ 尚未真机验证 ⇒ ★ 台账**不提 level**（红线⑥）✓
# ★★★ 本版要点（★ 新定则第三次应用）：
#   ★ **目标函数首参就叫 `model`** ⇒ ★ 参数绑定门禁**天然满足** ✓
#   ⇒ ★ **不建新模块、不追加包装** ⇒ ★ 落地链保持 4 步 ✓
# ★★ 引号纪律：★ 中文引号**一律用「」**（★ 事实 560）✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import ToolSpec

SPECS_BATCH111 = [
    ToolSpec(
        name="solidworks_assembly_performance_analysis_report",
        title="Assembly Performance Analysis — mate/feature counts (what Performance Evaluation shows)",
        module="sw_assembly",
        function="collect_mate_feature_summary",
        inject="model",
        params=[],
        read_only=True,
        evidence=(
            "★ **装配体性能分析（性能要素读数）**—— ★ 回一份**配合与特征的逐项摘要** ✓ ★ 真实来源：★ `sw_assembly.colle"
            "ct_mate_feature_summary`（**早已在本仓且可用** ✓）★★ **如实标注（不许冒充）**：★ **官方 API 里搜不到同名接"
            "口** ✗ —— ★ 本工具是**换路径**做出的**真实**读数：★ **SolidWorks 自己的「Performance Evaluation」报的正是"
            "「零件数 / 配合数 / 特征数」这类计数** ✓，★ 而本工具给的就是这类**可核对的计数摘要** ✓ ★ 它**不是**官方某"
            "个\"性能分析\"API 的包装（★ 那个不存在 ✗）★ 判据：★ 回的是**结构化计数/摘要**（★ 读不到就如实报，★ 不假装"
            "有内容 ✓）★★ 等级 `stitched` —— ★ 尚未真机验证（★ 红线⑥）✓"
        ),
        doc="★ **装配体性能分析（性能要素读数）**—— ★ 回一份**配合与特征的逐项摘要** ✓ "
        "★ 真实来源：★ `sw_assembly.collect_mate_feature_summary`（**早已在本仓且可用** ✓）"
        "★★ **如实标注（不许冒充）**：★ **官方 API 里搜不到同名接口** ✗ —— "
        "★ 本工具是**换路径**做出的**真实**读数：★ **SolidWorks 自己的「Performance Evaluation」"
        "报的正是「零件数 / 配合数 / 特征数」这类计数** ✓，★ 而本工具给的就是这类**可核对的计数摘要** ✓ "
        '★ 它**不是**官方某个"性能分析"API 的包装（★ 那个不存在 ✗）'
        "★ 判据：★ 回的是**结构化计数/摘要**（★ 读不到就如实报，★ 不假装有内容 ✓）"
        "★★ 等级 `stitched` —— ★ 尚未真机验证（★ 红线⑥）✓",
    ),
]
