"""★ 批次 109（v4）：规格 220 · 装配序列/说明书 —— ★ 直接指向**已有的真函数**，不新增包装。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（实现 = scripts/sw_delivery.py 的 collect_assembly_bom，**早已存在*
# *）
# 文件:   mcp-server/tool_specs_batch109.py
# 定位:   ★ 补一格用户可感知功能：★ **装配/装配序列·说明书**（生成器关键词 assembly_se
#           quence）✓
# 官方依据: ★★ 如实交代：★ 官方 **没有**「装配序列」成员（`C:\swapi\types` 里只有**序号*
#           *类成员，★ 那是 **BOM 行号** ✗）⇒ ★ 本工具**不是**官方同名功能的包装 ✗，★ 而
#           是把**用户心智里的「装配说明书」**  用本仓**既有、真实**的能力做出来 ✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **1 个工具** ⇒ 工具数 475 → 476
# ★★★ 等级如实：★★ 尚未真机验证 ⇒ ★ 台账**不提 level**（红线⑥）✓
# ★★★ **本版的关键**（★ 五轮教训换来的）：★ 目标函数**直接用现成的** `collect_assembly_b
# om` ——
#   ★ 它的**首参就叫 `model`** ✓ ⇒ ★ 参数绑定门禁天然满足 ✓
#   ★★ 于是**不需要新模块、不需要追加包装** ⇒ ★ 落地链缩短到"写这一个文件 + 挂接" ✓
# ★★ 引号纪律：★ 本文件里中文引号**一律用「」**（★ 事实 560 —— ★ 我为这条栽过 4 次）✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

SPECS_BATCH109 = [
    ToolSpec(
        name="solidworks_assembly_sequence_report",
        title="Assembly Sequence / Manual — BOM rows as ordered assembly steps",
        module="sw_delivery",
        function="collect_assembly_bom",
        inject="model",
        params=[
            Param(
                "include_excluded",
                bool,
                default=False,
                required=False,
                description="是否把被排除的件也算进件表（默认 false）",
            ),
        ],
        read_only=True,
        doc="★ **装配说明书（装配序列）**—— ★ 回一份**按行序排列的装配件表**（★ 每行 = 一个装配步骤）✓ "
        "★ 真实来源：★ `sw_delivery.collect_assembly_bom`（**真实 BOM**，★ 早已在本仓且可用 ✓）"
        "★★ **如实标注（不许冒充）**：★ **官方 API 里没有「装配序列」这个成员** —— "
        "★ `C:\\swapi\\types` 里只查到**序号**类成员（★ 那是 **BOM 行号** ✗）"
        "⇒ ★ 本工具给的是**用户心智里的「装配说明书」**（件表 + 行序 + 数量 + 配置），"
        "★ **不是** SolidWorks 那个不存在的功能 ✓ "
        "★ 判据：★ 回的是**结构化行**（★ 读不到就回空表，★ 不假装有内容 ✓）"
        "★★ 等级 `stitched` —— ★ 尚未真机验证（★ 红线⑥）✓",
    ),
]
