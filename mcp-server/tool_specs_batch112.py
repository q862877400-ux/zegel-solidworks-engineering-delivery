"""★ 批次 112：规格 220（续）· 焊件/圆角焊缝 —— ★ 从零真做的实现（sw_weld_bead.py）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（实现 = scripts/sw_weld_bead.py，第 46 轮从零写）
# 文件:   mcp-server/tool_specs_batch112.py
# 定位:   ★ 补一格用户可感知功能：★ **焊件/圆角焊缝**（⇒ ★ **焊件 7/7 = 第 10 个 100%
#           的域**）
#         ★ 生成器关键词（逐字）：`("fillet_bead", "weld_bead")` ✓
# 官方依据: ★★ **三样都读过**（★ 铁律 4）：
# · 入口：★ **`IFeatureManager::InsertFilletBeadFeature2`** ✓（★ v1 官方逐字 **Obsolete*
# * ⇒ 只用 v2 ✓）
#   · 第 12 行逐字：★「…fills the gap between the **pre-selected part bodies**, if any.」
# ⇒ ★★ **前置 = 预先选中的实体** ✓（★ **不是「面集合」** ✗ —— ★ 台账那句二手概括是错的 ✓
# ）
#   · 签名 16 参**逐字**（★ Type1·Size1·Length1·PenetrationType1·PenetrationValue1·Pitch·
# Type2·Size2·Length2·PenetrationType2·PenetrationValue2·Flag·EdgeNum1·DeSelEdge1·EdgeNu
# m2·DeSelEdge2 ✓）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **1 个工具** ⇒ 工具数 478 → 479
# ★★★ 等级如实：★★ 尚未真机验证 ⇒ ★ 台账**不提 level**（★ 红线⑥）✓
# ★★ 参数契约：★ `inject='model'` 与目标函数首参名**一致** ✓（★ 第 22–24 轮门禁读数逼出
# 来的定则 ✓）
# ★★ 引号纪律：★ 中文引号**一律用「」**（★ 事实 560 —— ★ 我为这条栽过 4 次）✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

SPECS_BATCH112 = [
    ToolSpec(
        name="solidworks_weld_fillet_bead_report",
        title="Fillet Weld Bead (official InsertFilletBeadFeature2, 16 params)",
        module="sw_weld_bead",
        function="insert_fillet_bead_report",
        inject="model",
        params=[
            Param(
                "edge_index_1",
                int,
                default=0,
                required=False,
                description="Zero-based index of the first intersecting edge. Defaults to 0.",
            ),
            Param(
                "edge_index_2",
                int,
                default=1,
                required=False,
                description="Zero-based index of the second intersecting edge. Defaults to 1.",
            ),
            Param(
                "size_mm",
                float,
                default=5.0,
                required=False,
                description="Weld leg size in millimetres, used for both sides. Defaults to 5.0.",
            ),
            Param(
                "length_mm",
                float,
                default=0.0,
                required=False,
                description="Weld length in millimetres, where 0 means the whole edge. Defaults to 0.0.",
            ),
            Param(
                "bead_type_1",
                int,
                default=0,
                required=False,
                description="First-side bead type: 0=full length, 1=intermittent, 2=staggered. Defaults to 0.",
            ),
            Param(
                "bead_type_2",
                int,
                default=0,
                required=False,
                description="Second-side bead type: 0=full length, 1=intermittent, 2=staggered. Defaults to 0.",
            ),
            Param(
                "penetration_type_1",
                int,
                default=0,
                required=False,
                description="First-side penetration: 0=full, 1=partial, 2=none. Defaults to 0.",
            ),
            Param(
                "penetration_type_2",
                int,
                default=0,
                required=False,
                description="Second-side penetration: 0=full, 1=partial, 2=none. Defaults to 0.",
            ),
            Param(
                "penetration_value_1",
                float,
                default=0.0,
                required=False,
                description=(
                    "First-side penetration value in millimetres, used only when penetration_type_1 is 1. Defaults to 0"
                    ".0."
                ),
            ),
            Param(
                "penetration_value_2",
                float,
                default=0.0,
                required=False,
                description=(
                    "Second-side penetration value in millimetres, used only when penetration_type_2 is 1. Defaults to "
                    "0.0."
                ),
            ),
            Param(
                "pitch_mm",
                float,
                default=0.0,
                required=False,
                description="Pitch in millimetres, used for intermittent or staggered beads. Defaults to 0.0.",
            ),
            Param(
                "flag",
                int,
                default=1,
                required=False,
                description=(
                    "Weld flag: 0=single side without tangent propagation, 1=both sides, 2=tangent propagation, 3=both "
                    "sides with tangent propagation. Defaults to 1."
                ),
            ),
        ],
        evidence=(
            "★ **圆角焊缝**（★ 官方 `IFeatureManager::InsertFilletBeadFeature2`，★ **16 参**）⇒ ★ 回一份**回读报告** ✓ "
            "★★ **如实标注**：★ 官方 **v1（`InsertFilletBeadFeature`）已 `Obsolete`** ✗ ⇒ ★ 本工具只用 **v2** ✓；★ 前置"
            "是**预先选中的实体**（★ 官方第 12 行逐字 `pre-selected part bodies` ✓）—— ★ 而选**边**的动作用 **`IEntity."
            "Select4`**（★ 事实 32：★ 按点 `SelectByID2` 对某些实体**永远选不上** ✗）；★ 且**由函数自己选**（★ 事实 503"
            "：★ 注入解析器**会清空选区** ⇒ ★\"调用方先选好\"**不成立** ✓）★★ **判据 = 特征树回读增量 ≥ 1**（★ 事实 8："
            "★ **不看返回值** —— ★ 返回值 `None` **不代表失败** ✓）★ 单位：★ 入参**毫米**，★ 内部转米（★ 事实 2）✓ ★★ "
            "等级 `stitched` —— ★ **尚未真机验证**（★ 红线⑥）✓"
        ),
        doc=(
            "Insert a fillet weld bead and report whether the feature tree grew. Creates a weldment feature; the two ed"
            "ge indices select the intersecting edges, sizes are in millimetres and converted to metres, and it is not "
            "yet verified on a real machine, so a returned None does not prove failure."
        ),
    ),
]
