'''★ 批次 112：规格 220（续）· 焊件/圆角焊缝 —— ★ 从零真做的实现（sw_weld_bead.py）。'''
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
        name='solidworks_weld_fillet_bead_report',
        title='Fillet Weld Bead (official InsertFilletBeadFeature2, 16 params)',
        module='sw_weld_bead', function='insert_fillet_bead_report',
        inject='model',
        params=[
            Param('edge_index_1', int, default=0, required=False,
                  description='第一侧**相交边**的序号（★ 声明式；★ 取边序号，不收坐标 —— 规则 3）'),
            Param('edge_index_2', int, default=1, required=False,
                  description='第二侧**相交边**的序号（★ 声明式）'),
            Param('size_mm', float, default=5.0, required=False,
                  description='焊脚尺寸（毫米；官方 Size1/Size2）'),
            Param('length_mm', float, default=0.0, required=False,
                  description='焊缝长度（毫米；0 = 整长；官方 Length1/Length2）'),
            Param('bead_type_1', int, default=0, required=False,
                  description='第一侧类型（官方 Type1：0=Full length · 1=Intermittent · 2=Staggered）'),
            Param('bead_type_2', int, default=0, required=False,
                  description='第二侧类型（官方 Type2，同上三档）'),
            Param('penetration_type_1', int, default=0, required=False,
                  description='第一侧熔透（官方 PenetrationType1：0=Full · 1=Partial · 2=No）'),
            Param('penetration_type_2', int, default=0, required=False,
                  description='第二侧熔透（官方 PenetrationType2，同上三档）'),
            Param('penetration_value_1', float, default=0.0, required=False,
                  description='第一侧熔透值（毫米；仅 PenetrationType1=1 时有效）'),
            Param('penetration_value_2', float, default=0.0, required=False,
                  description='第二侧熔透值（毫米；仅 PenetrationType2=1 时有效）'),
            Param('pitch_mm', float, default=0.0, required=False,
                  description='节距（毫米；断续/交错时有效；官方 Pitch）'),
            Param('flag', int, default=1, required=False,
                  description='官方 Flag：0=单边无相切传播 · 1=双边 · 2=相切传播 · 3=双边且相切传播'),
        ],
        doc='★ **圆角焊缝**（★ 官方 `IFeatureManager::InsertFilletBeadFeature2`，★ **16 参**）⇒ ★ 回一份**回读报告** ✓ '
            '★★ **如实标注**：★ 官方 **v1（`InsertFilletBeadFeature`）已 `Obsolete`** ✗ ⇒ ★ 本工具只用 **v2** ✓；'
            '★ 前置是**预先选中的实体**（★ 官方第 12 行逐字 `pre-selected part bodies` ✓）'
            '—— ★ 而选**边**的动作用 **`IEntity.Select4`**（★ 事实 32：★ 按点 `SelectByID2` 对某些实体**永远选不上** ✗）；'
            '★ 且**由函数自己选**（★ 事实 503：★ 注入解析器**会清空选区** ⇒ ★"调用方先选好"**不成立** ✓）'
            '★★ **判据 = 特征树回读增量 ≥ 1**（★ 事实 8：★ **不看返回值** —— ★ 返回值 `None` **不代表失败** ✓）'
            '★ 单位：★ 入参**毫米**，★ 内部转米（★ 事实 2）✓ '
            '★★ 等级 `stitched` —— ★ **尚未真机验证**（★ 红线⑥）✓',
    ),
]
