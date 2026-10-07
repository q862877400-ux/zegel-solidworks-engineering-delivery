
# ── 24h 计划 段 6 续（Spec Kit `167` 的批次声明）：**几何量测** ──────────────────────
# ★★★★★ 2026-10-01（轮 311）真机（`output/measure-evidence.json`）**PASS 3/3** ——
#   ★★ **三个期望值全部由几何推出、且全部精确对上**：
#   · 两个平行面（20×20 板 · 厚 10）⇒ `distance = **10.0 mm**`（★ 板厚）·
#     `applicable = [distance, normal_distance, angle, total_area, delta_x, delta_y, delta_z]` ·
#     而 `area = -1`（★ 两个面时面积不适用 —— ★ 官方约定）
#   · 单个面 ⇒ `area = **400.0 mm²**`（20×20）· `perimeter = **80.0 mm**`（4×20）
#   · 未选中 ⇒ **显式拒绝**
# ★★ **本批为什么是「别人有我们没有」**：★ 我们有 `part_mass_properties`（整体质量属性），
#   而**逐几何量测**全仓为 0（grep `measure`/`volume`/`area`/`distance` 均 0）——
#   ★★ 而四家强候选里正有 `measure` 与 `measure_distance`（★ 本批**一次补两条**）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch46.py —— 本文件
# 定位:   段 6 续：几何量测（★ 补「四家有我们没有」的真缺）。
# 官方签名依据: `C:\swapi\types\IModelDocExtension\CreateMeasure.md`（`Measure CreateMeasure()`）·
#   `C:\swapi\types\IMeasure\`（33 成员）· ★ 官方示例 `Measure_Selected_Entities_Example_VB.md`（调用序）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec

SPECS_BATCH46 = [
    ToolSpec(
        name="solidworks_measure_selection",
        title="Measure Selected Entities",
        module="sw_measure",
        function="measure_selection_report",
        inject="model",
        params=[
            Param("arc_option", int, default=1,
                  description="圆弧距离口径：0 = 中心到中心 · 1 = 最小距离 · 2 = 最大距离（官方示例给的语义）"),
            #: ★★ 2026-10-07（接手轮 · 规格 216 T-216-07）**加声明式选区入口** ——
            #:   ★ 起因：★ 本工具的语义**就是"量调用方选中的东西"**，★ 而解析器**会清空选区**（事实 503）
            #:     ⇒ ★ 模型**没法**把要量的东西选好 ⇒ ★ 经工具层**必然失败** ✗
            #:   ★★ 与圆顶那次不同：★ 圆顶"给哪个面"可以随便定，★ 而**"量什么"是调用方的意图**
            #:     ⇒ ★★ **绝不能由函数乱造** ⇒ ★ 让调用方**声明**（规则 3）✓
            Param("selection", str, description="★ 声明式选择器（规则 3：不收坐标）：`index:<n>` 或 "
                                                "`__current_selection__`。",
                  required=False, default=""),
            Param("selection_kind", str, description="`FACE` / `EDGE` / `VERTEX`（★ 与你要量的对象一致）。",
                  required=False, default="FACE"),
        ],
        doc="★ **量声明式选区里的实体**（逐几何量测）—— 走 `IModelDocExtension.CreateMeasure` → `IMeasure`。"
            "★★ **用 `selection` + `selection_kind` 说明量什么**（★ 规则 3：**不收坐标**；"
            "★ 函数在**注入之后**自己重建选区 —— ★ 事实 503：注入解析器会清空选区）。"
            "★ 调用序照官方示例：`Extension` → `CreateMeasure` → 设 `ArcOption` → `Calculate` → 读数。"
            "★ 回的 `values` 含 `distance` / `normal_distance` / `angle` / `length` / `area` / `perimeter` / "
            "`delta_x` / `delta_y` / `delta_z` 等；判定含 `is_intersect` / `is_parallel` / `is_perpendicular`。"
            "★★ 约定：**-1 表示「这项对当前选择不适用」** —— 本工具如实保留 -1，"
            "并另给 `applicable` 列出真量到的项。"
            "★ 真机期望（几何推出，全部对上）：两面 ⇒ `distance` 10.0mm · 单面 ⇒ `area` 400mm² · "
            "`perimeter` 80mm。★ 未选中 ⇒ 显式拒绝。"
            "⚠ 量测要先选中（规则 3：本工具不传坐标，选中由声明式选择那族负责）。",
    ),
]
