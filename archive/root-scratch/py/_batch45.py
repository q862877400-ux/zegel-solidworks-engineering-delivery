
# ── 24h 计划 段 6 续（Spec Kit `166` 的批次声明）：**曲面特征（第一条）** ──────────────
# ★★★★★ 2026-10-01（轮 308）真机（`output/surface-feature-evidence.json`）：
#   · ★★ **通过**：`create_extruded_surface_report(doc, 10.0)` ⇒ **`曲面-拉伸1`** · 特征树 `6 → 7` · 22 参
#   · ★ **负例通过**：`depth_mm=-5.0` ⇒ **显式拒绝**
#   · ⚠ **未通过**：`through_all=True` ⇒ 特征树 `7 → 7`（★ **没建成**）——
#     ★ **如实标"未通过"**，★ 且**不猜参数**（★ `swEndConditions_e` 的取值要查了再改，铁律 4）。
# ★★ **本批为什么重要**：★ 它把「**不做曲面族**」那条结论拆成两半 ——
#   ★ `IModeler.Create*Surface`（造**曲面体**）**仍然不做**（事实 40 成立）；
#   ★★ `IFeatureManager.FeatureExtruRefSurface3`（建**曲面特征**）**做了，且真机通过**。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch45.py —— 本文件
# 定位:   段 6 续：把 `sw_surface_features` 的「曲面-拉伸」包装挂成 MCP 工具。
# 官方签名依据: `C:\swapi\types\IFeatureManager\FeatureExtruRefSurface3.md`（22 参 · 回 void）·
#   `scripts/sw_api_sldworks.py:4300`（反射 arity 22）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec

SPECS_BATCH45 = [
    ToolSpec(
        name="solidworks_surface_create_extruded",
        title="Create Extruded Surface Feature",
        module="sw_surface_features",
        function="create_extruded_surface_report",
        inject="model",
        params=[
            Param("depth_mm", float, description="拉伸深度（毫米）—— ★ 规则 2：换算只在本工具边界做一次"),
            Param("sketch_name", str, default="", description="草图名；留空 = 用当前草图（★ 不传坐标）"),
            Param("through_all", bool, default=False,
                  description="⚠ **未真机验证**：贯穿（★ 真机上特征树没变，★ 已如实记为未通过）"),
        ],
        doc="★ **用已有草图建「曲面-拉伸」特征** —— 走 `IFeatureManager.FeatureExtruRefSurface3`"
            "（官方 **22 个参数** · ★★ **返回 `void`**）。"
            "★★ 判据**不是返回值**，而是「**特征树真的多了**」（规则 6：不静默成功）。"
            "★ 真机证据：10 mm 深度 ⇒ 建成 `曲面-拉伸1`（树 6→7）· 负例 `-5.0` ⇒ 显式拒绝。"
            "⚠ 与 `sw_surface.py` 的「`IModeler.Create*Surface` 造曲面**体**」是**两条不同的路** ——"
            "后者在本机返回值跨次都变（事实 40），本条**不走那条**。",
    ),
]
