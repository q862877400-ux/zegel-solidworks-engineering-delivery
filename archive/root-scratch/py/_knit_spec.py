
# ── 24h 计划 段 6 续（Spec Kit `166` 续的批次声明）：**缝合曲面** ──────────────────────
# ★★★★★ 2026-10-01（轮 309）真机（`output/surface-knit-evidence.json`）**PASS 2/2**：
#   · ★★ `knit_surfaces_report(doc, 0.0001)` ⇒ **新特征 `曲面-缝合1`** · 选中 **8** 张面 ·
#     **body `2 → 1`** ✓（★ 判据两条都要 —— 规则 6）
#   · ★ 负例：容差 `5.0` ⇒ **显式拒绝**，★ 并**列出官方上下限**（0.0001 ～ 0.1 mm）
# ★★ **对应四家缺口名 `knit_surfaces`**。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch45.py —— 追加本声明
# 定位:   段 6 续：把 `sw_surface_features.knit_surfaces_report` 挂成 MCP 工具。
# 官方签名依据: `C:\swapi\types\IFeatureManager\InsertSewRefSurface.md`
#   （5 参 · Remarks：mark = 1 · 容差 0.0001–0.1 mm）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────

_SPEC_KNIT = ToolSpec(
    name="solidworks_surface_knit",
    title="Knit Selected Surfaces",
    module="sw_surface_features",
    function="knit_surfaces_report",
    inject="model",
    params=[
        Param("knit_tolerance_mm", float, default=0.0001,
              description="缝合容差（毫米）—— ★ 官方给的范围 **0.0001 ～ 0.1 mm**（规则 2：边界换算一次）"),
        Param("try_to_form_solid", bool, default=False,
              description="尝试形成实体（★ 勾上则缝合后直接变实体）"),
    ],
    doc="★ **把曲面缝成一张** —— 走 `IFeatureManager.InsertSewRefSurface`（官方 **5 参**）。"
        "★ 官方 Remarks：选中项要 **selection mark = 1**，而**缝合容差的有效范围是 0.0001 ～ 0.1 mm**。"
        "★★ 判据（规则 6）：**特征树多出新特征** **且** **body 数变少**（真机：`曲面-缝合1` · 2→1）。"
        "★ 它按**对象**选面（实体没有名字 —— 事实 32），★ 选中数**回读** `GetSelectedObjectCount2(-1)`"
        "（★ 不信返回值 —— 事实 8）。",
)

SPECS_BATCH45 = SPECS_BATCH45 + [_SPEC_KNIT]
