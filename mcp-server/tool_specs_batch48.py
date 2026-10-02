
# ── 24h 计划 段 6 续（Spec Kit `169` 的批次声明）：**扫描** ──────────────────────────
# ★★★★★ 2026-10-01（轮 315）真机（`output/sweep-evidence.json`）：
#   · ★★ **通过**：`CreateDefinition(swFmSweep=17)` → `ISweepFeatureData` → `CreateFeature`
#     ⇒ **建成 `扫描1`** · ★ **类型名 = `Sweep`** ✓
#   · ★ **负例通过**：未选轮廓/路径 ⇒ **显式拒绝**（★ 并报出 mark1/mark4 计数）
#   · ⚠ **未通过**：`Right Plane` 上画路径的那一例（★ 因为**路径起点不在轮廓平面上** ——
#     ★ 官方原文「the starting point of the sweep path must lie on the plane of the profile」
#     ⇒ ★ **那是几何约束，不是 API 问题**，★ 如实记进限制）
#   · ⚠ `AccessSelections(model, _empty_callout())` ⇒ **`0x80010105` 服务器出现意外情况**
#     ⇒ ★★ **那是事实 47 那个后端限制错误码**；★ **而真机实测：即使它报错，特征仍然建成**
#       ⇒ ★★★ **所以它**不是必需的**** —— ★ 本包装仍然试它，★ **但不拿它当判据**。
# ★★ **它补的是核实的第二个真缺**：★ 全仓 grep `sweep` ⇒ **工具 0 · 函数 0**（`loft` 同样 0），
#   ★ 而**扫描与放样是 SolidWorks 最基本的两种特征**；★ 四家并集里有 **`sweep`**（Slacker-LLC）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch48.py —— 本文件
# 定位:   段 6 续：扫描（★ 补「四家有我们没有」的真缺 —— 与 `loft` 同批）。
# 官方签名依据: `C:\swapi\docs\Programming with the SOLIDWORKS API\Sweep Features and SweepFeatureData Objects.md`
#   （★ 轮廓 mark=1 · 路径 mark=4 · 引导线 mark=2 · 方向向量 mark=128 · CreateDefinition(swFmSweep)）·
#   `C:\swapi\types\IFeatureManager\CreateDefinition.md`（swFmSweep = 17）·
#   `C:\swapi\types\ISweepFeatureData\`（54 成员）· ★ 反射 `sw_api_sldworks.py`（swFmSweep = 17 / swFmSweepCut = 18）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec

SPECS_BATCH48 = [
    ToolSpec(
        name="solidworks_part_sweep",
        title="Create Sweep Feature",
        module="sw_sweep",
        function="create_sweep_report",
        inject="model",
        params=[
            Param("cut", bool, default=False,
                  description="True 建**扫描切除**（swFmSweepCut=18）· False 建**扫描凸台**（swFmSweep=17）"),
        ],
        doc="★ **用选中的「轮廓 + 路径」建扫描特征** —— 走官方**现代入口** "
            "`IFeatureManager.CreateDefinition(swFmSweep=17)` → `ISweepFeatureData` → `CreateFeature`"
            "（★ `InsertProtrusionSwept*` 整族已被 SOLIDWORKS 2018 标为 **obsolete**）。"
            "★ 官方专文给的 mark：**轮廓 = 1** · **路径 = 4** · 引导线 = 2 · 方向向量 = 128。"
            "⚠ 官方硬约束：**路径的起点必须落在轮廓所在平面上**（1 方向扫描）—— 真机上违反它就会建不成。"
            "★★ 判据（事实 242：挑只依赖被测对象的那个）：**特征树多了新特征** **且** "
            "**类型名 = `Sweep`**。★ 真机证据：建成 `扫描1`（type=`Sweep`）· 未选中 ⇒ 显式拒绝。"
            "⚠ `AccessSelections` 在本机报 `0x80010105`（事实 47 的后端限制）——★ 而**它非必需**："
            "真机上它报错时特征仍建成，所以本工具**不拿它当判据**。",
    ),
]
