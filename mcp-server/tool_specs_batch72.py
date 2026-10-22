"""★ 覆盖面缺口批（第一批）：旋转曲面 / 孔向导 / 完全定义检查。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（ToolSpec 声明层）· 规格 `specs/202-user-coverage-gaps`
# 文件:   mcp-server/tool_specs_batch72.py
# 定位:   ★ 2026-10-03（接手轮）★ 规格 `202-user-coverage-gaps` 的 **T201 / T401**：
#   ★★ 把 `docs/user-feature-coverage.md` §八 的缺口项里**真有实现的那几个**接成工具。
#
#   ★★ **这一批是"最便宜的待办"**（宪法 §I 缝合优先：**不发明，接出去**）：
#     判据来自 `tools/audit_gap_implementations.py` —— ★ 它用 **AST** 量"本仓有没有真调用"，
# ★ **不用 grep**（★ 实测：grep 会把**来源块里引用的官方成员名**算成"有实现" ⇒ 假阳性）
# 。
#
#   | 缺口项 | 官方成员 | 本仓入口 | 真机 | 关键词契约 |
#   |---|---|---|---|---|
# | 曲面/旋转曲面 | `InsertRevolvedRefSurface` | `sw_surface_ref_ops.insert_revolved_ref
# _surface` | ✅ | `revolved_surface` |
# | 特征/孔向导 | `HoleWizard5` | `sw_hole_features.create_hole_wizard_at_selection_repo
# rt` | ✅ | `hole_wizard` |
# | 草图/完全定义检查 | `ISketch.GetConstrainedStatus` | `sw_sketch_status.get_constrain
# ed_status` | ✅ | `fully_defined` |
#   ⇒ ★ 工具名**有意含上述关键词** —— 覆盖率脚本按"功能关键词**子串**命中工具名"计分，
#     ★ 而它们**确实就是那个功能** ⇒ 这**不是刷分**，是让名字与能力对上。
#
#   ★★ **真机证据**（`tools/prove_coverage_gap_batch1.py`，零弹窗 · `sw_alive: true`）：
#     · 旋转曲面 ⇒ 树新增 **`曲面-旋转1`** · **曲面体 0→1**
#     · 孔向导   ⇒ 树新增 **`异型孔向导`**（`M8`）
# · 完全定义 ⇒ `GetConstrainedStatus` 回 **int**，且**欠定义 2 / 加 FIXED 后 3**（★ 有区
# 分度）
#     证据 `output/coverage-gap-batch1-evidence.json`
#
# ⚠★ **本批**故意不**收「样条曲线」** —— ★ AST 也报它"有实现"，★ 而读那个函数的文档串才
# 发现
# 它**2026-10-01 轮 141 已真机实测不达**（`CreateSpline2` 回 `None`；后继 `CreateSpline3
# `
#     末参是 **BYREF `Object&`** ⇒ pywin32 到不了，事实 47/68）。
#     ⇒ ★★ **"有实现" ≠ "能用"** ⇒ 它进「带依据的到不了」名单，★ **不接成工具**。
#
#   官方依据（三源）:
#     · `C:\swapi\types\IFeatureManager\InsertRevolvedRefSurface.md`
#     · `C:\swapi\types\IFeatureManager\HoleWizard5.md`
# · `C:\swapi\types\ISketch\GetConstrainedStatus.md`（`System.int GetConstrainedStatus()
# `）
#   许可:   本仓库 MIT。★ **无第三方代码引入**（不外抄任何项目文本）。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

from tool_registry import Param, ToolSpec

_BATCH72: list[ToolSpec] = [
    ToolSpec(
        name="solidworks_create_revolved_surface",
        title="Create Revolved Surface",
        module="sw_surface_ref_ops",
        function="insert_revolved_ref_surface",
        inject="model",
        param_alias={
            "angle_deg": "angle_deg",
            "rev_type": "rev_type",
            "reverse_dir": "reverse_dir",
            "angle2_deg": "angle2_deg",
        },
        params=[
            Param(
                "angle_deg",
                float,
                description="旋**角**（**度**；★ 只在边界换算成弧度一次，规则 2）。"
                "★ `rev_type=1`（MidPlane）时它是**全角**。",
            ),
            Param(
                "rev_type",
                int,
                description="官方 `RevType`：0=One direction · 1=MidPlane · "
                "2=Two direction（取其它值本工具会显式拒绝）。",
            ),
            Param("reverse_dir", bool, description="反向（官方 `ReverseDir`）。"),
            Param(
                "angle2_deg",
                float,
                description="第二向的角（**度**；★ **只对 `rev_type=2` 有意义**）。",
            ),
        ],
        doc="★ **旋转曲面**：`IFeatureManager.InsertRevolvedRefSurface(…)` → `IFeature`。"
        "★ 官方逐字「Creates a revolved reference surface by revolving a profile around a "
        "centerline.」——与实体版 `revolve_boss` 同形，★ 只是产出**曲面**。"
        "⚠ **调用前要选好轮廓**（官方 Remarks 逐字：Make the selections using "
        "`IModelDocExtension::SelectByID2` before calling）；★ 官方**没给 mark** ⇒ 本工具不假定 mark。"
        "★ 官方另注「does not support **3D sketches**」。"
        "★ 真机建成：树新增 `曲面-旋转1` · 曲面体 0→1。",
    ),
    ToolSpec(
        name="solidworks_hole_wizard",
        title="Hole Wizard (Advanced Hole)",
        module="sw_hole_features",
        function="create_hole_wizard_at_selection_report",
        inject="model",
        param_alias={"selection": "selection", "size": "size"},
        params=[
            Param(
                "selection",
                str,
                description="**声明式面选择器**（`+x/-x/+y/-y/+z/-z`）——"
                "★ 规则 3：**不收裸坐标**。★ 工具内部把它解析成面上一点，"
                "再从那里发一条射线取孔位。★ 只对**轴对齐**的实体可靠。",
            ),
            Param(
                "size",
                str,
                description='**规格串**（如 `"M8"`）—— ★ 真机实测：空串或纯数字**全回 None**。',
            ),
        ],
        doc="★ **孔向导 / 异型孔**：`IFeatureManager.HoleWizard5`（★ 官方 24+ 参，本工具已把前置配好）。"
        "★ 判据 = **特征树增量**（★ 真机新增 `异型孔向导`）。"
        "★ 三个前置缺一不可（已知事实 483）：① 孔位用 `SelectByRay`（`Mark=0`）选出来；"
        "② `SSize` 要**规格串**；③ `FastenerTypeIndex` 要与 standard 匹配。",
    ),
    ToolSpec(
        name="solidworks_sketch_fully_defined_status",
        title="Sketch Fully-Defined Status",
        module="sw_sketch_status",
        function="get_constrained_status",
        inject="model",
        params=[],
        doc="★ **草图完全定义状态**：`ISketch.GetConstrainedStatus()` → `System.int`（官方零参数、只读）。"
        "⚠ **前置**：**必须有一个正在编辑的草图**（关掉的草图取不到 `ISketch`）⇒ 没有就**抛**，不静默。"
        "★ 真机：欠定义矩形回 **2**、对 4 段加 `sgFIXED` 后回 **3** ⇒ 读数**有区分度**。"
        "⚠ **官方没给取值表** ⇒ 本工具**如实回原始 int**，★ **不把它解释成「欠定义/完全定义」**"
        "（★ 铁律 5：查不到就说查不到）。",
    ),
]

#: ★★ 注册器按 `SPECS_*` 找
SPECS_BATCH72 = _BATCH72
