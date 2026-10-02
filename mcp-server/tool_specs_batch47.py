
# ── 24h 计划 段 6 续（Spec Kit `168` 的批次声明）：**放样** ──────────────────────────
# ★★★★★ 2026-10-01（轮 313）真机（`output/loft-evidence.json`）**PASS 3/3**：
#   · 同平面两轮廓 ⇒ **建成 `放样1`**（树 7→8 · 官方 18 参）✓
#   · 两平面（前视 + 上视）⇒ **建成 `放样1`** ✓
#   · 未选中 ⇒ **显式拒绝**（★ 提示"至少 2 个轮廓 · mark=1"）✓
#   ⚠ **未验**：★ `CreateMassProperty().Volume` 回 **0.0**（★ 所以"棱台体积 7000 mm³"那个
#     几何推出的期望值**没有对上**）—— ★ **如实标"未真机验证体积"**，★ 不写成"通过"。
# ★★ **它补的是核实的真缺**：★ 全仓 grep `loft` ⇒ **工具 0 · 函数 0**（`sweep` 同样 0），
#   ★ 而**放样与扫描是 SolidWorks 最基本的两种特征**；★ 四家并集里有 **`loft`**（Slacker-LLC 提供）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch47.py —— 本文件
# 定位:   段 6 续：放样（★ 补「四家有我们没有」的真缺）。
# 官方签名依据: `C:\swapi\types\IFeatureManager\InsertProtrusionBlend2.md`
#   （**18 参** · 回 `Feature` · Remarks 给 mark：1=轮廓 / 2=引导线 / 4=中心线 / 8=起端相切向量）·
#   ★ 反射 arity 表 `scripts/sw_api_sldworks.py:4426` = **18**（★ 两源一致）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec

SPECS_BATCH47 = [
    ToolSpec(
        name="solidworks_part_loft",
        title="Create Loft Feature",
        module="sw_loft",
        function="create_loft_report",
        inject="model",
        params=[
            Param("closed", bool, default=False,
                  description="闭合放样（★ 首尾相连成一个环；★ 少于 3 个轮廓时引导线必须闭合）"),
            Param("use_selected_profiles", bool, default=True,
                  description="用当前选中的轮廓（★ 官方要求 mark=1，且**顺序**决定结果）"),
        ],
        doc="★ **用选中的草图轮廓放样** —— 走 `IFeatureManager.InsertProtrusionBlend2`（官方 **18 参**）。"
            "★ 官方 Remarks：轮廓要**按期望的顺序**先选中，mark=**1**（引导线 mark=2 · 中心线 mark=4 · "
            "起端相切向量 mark=8）；★ 引导线与中心线**可选**。"
            "★★ 判据（规则 6）：**特征树多了新特征**。"
            "★ 真机证据：同平面与两平面两种情形都建成 `放样1`；未选中 ⇒ 显式拒绝（提示至少 2 个轮廓）。"
            "⚠ **未真机验证**：质量属性里的**体积**（★ 真机上回 0.0，所以「棱台体积 7000 mm³」那个"
            "期望值没有对上）—— ★ 不要把本工具的体积当可靠读数。",
    ),
]
