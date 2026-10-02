
# ── 24h 计划 段 6 续（Spec Kit `171` 的批次声明）：**包覆** ──────────────────────────
# ★★★★★ 2026-10-01（轮 331）真机（`output/wrap-evidence.json`）**PASS 3/3**：
#   ★ 三种 `wrap_type` 都建成 **`包覆1`**（★ 判据 = **读返回对象的 `Name` 与 `GetTypeName2`**）。
# ★★ **它补的是核实的真缺**：★ 全仓 grep `wrap` ⇒ **工具 0 · 函数 0**
#   （★ 同批核出的另三条真缺：`sensor` / `units` / `undo`）。
#
# ⚠ **两处如实标注**（★ 不写成"全支持"）：
#   ① ★ **`Type` 参数被静默忽略** —— 传 0（Emboss）/ 1（Engrave）/ 2（Scribe）建出来的
#      **类型名全是 `Emboss`**（★ 与 `revolve_boss` 的 `axis_sketch_name` 是同一类"签名里有、实际不生效"）。
#      ⇒ ★ **本工具只声明支持 Emboss**。
#   ② ★ **`Method` / `MeshFactor`（第 4/5 参）取值表没查到**（★ 铁律 5：查不到就说不查不到）
#      ⇒ 用 0，★ 并在工具说明里写明未核。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch50.py —— 本文件
# 定位:   段 6 续：包覆（★ 补「四家有我们没有」的真缺）。
# 官方签名依据: `C:\swapi\types\IFeatureManager\InsertWrapFeature2.md`
#   （**5 参**：Type / Thickness / ReverseDir / Method / MeshFactor · mark 1=面 · 2=拔模方向 · 4=草图）·
#   `C:\swapi\enums\swWrapSketchType_e.md` + 反射（0=Emboss · 1=Engrave · 2=Scribe）·
#   `C:\swapi\examples\Create_Wrap_Feature_on_Multiple_Faces_Example_VB.md`（★ 调用序）·
#   ★ 反射 arity `scripts/sw_api_sldworks.py:4481`（`InsertWrapFeature2` = **5**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec

SPECS_BATCH50 = [
    ToolSpec(
        name="solidworks_part_wrap",
        title="Create Wrap Feature",
        module="sw_wrap",
        function="create_wrap_report",
        inject="model",
        params=[
            Param("wrap_type", str, default="emboss",
                  description="包覆类型：emboss（凸起）/ deboss（凹陷，官方名 Engrave）/ scribe（划痕）。"
                              "⚠ **真机实测：传 deboss/scribe 建出来的类型名仍是 `Emboss`** "
                              "⇒ ★ 只有 `emboss` 被真机证实过"),
            Param("thickness_mm", float, default=1.0, description="厚度（**毫米**）"),
            Param("reverse", bool, default=False, description="反向"),
        ],
        doc="★ **对已选中的「草图（mark=4）+ 面（mark=1）」建包覆特征** —— 走官方 "
            "`IFeatureManager.InsertWrapFeature2`（**5 参**）。"
            "★ 官方要求：★ **草图 mark = 4**（★ 且**必须是 2D 草图**，官方原话 「3D sketches are invalid」）· "
            "★ **面 mark = 1** · ★ 拔模方向 mark = 2（仅 Emboss/Engrave 用）。"
            "★★ 判据 = **读返回对象的 `Name` 与 `GetTypeName2`** —— ★ 真机：返回 `包覆1` · "
            "类型名 **`Emboss`**；⚠ 而 `feature_names()` 的**前后 diff 是空的**"
            "（★ 所以「树 diff」不是可靠判据）。"
            "⚠ **未验**：`Type` 传非 emboss 时**类型名不变**（★ 参数被静默忽略）· "
            "`Method` / `MeshFactor`（第 4/5 参）**取值表没查到**（用 0）。",
    ),
]
