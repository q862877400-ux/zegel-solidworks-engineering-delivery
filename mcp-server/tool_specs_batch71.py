"""★ B7 特征下拉的声明式工具（★ 只登记真机建成的那些）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（ToolSpec 声明层）
# 文件:   mcp-server/tool_specs_batch71.py
# 定位:   ★ 2026-10-03（轮 481）★ `specs/201-toolbar-gaps` 的 **B7**。
#   实现层在 `scripts/sw_curve_and_split.py`；★ 真机证据 `output/b7a-curve-split-evidence.json`。
#
#   ====================  ================================================  ==========  ========
#   工具栏原文             官方成员                                          真机        登记
#   ====================  ================================================  ==========  ========
#   通过参考点的曲线        `InsertCurveFileBegin/Point/End`（三步式）         ✅           ✅
#   配合参考               `InsertMateReference2`（**12 参**）               ✅           ✗（见下）
#   分割线（投影）          `InsertSplitLineProject`                         ❌           ✗
#   分割线（轮廓）          `InsertSplitLineSil`                             ❌           ✗
#   ====================  ================================================  ==========  ========
#
#   ★★ **配合参考为什么不登记成工具**（★ 与"没建成"无关，★ 它**建成了**）：★ 它的第 2 个形参
#     `PrimaryReferenceEntity` 的类型是 **`IEntity`（一个 COM 对象）** —— ★ 而 `ToolSpec` 的
#     `Param` 只表达**基本类型**（float / int / bool / str）⇒ ★ **表达不了"传一个实体对象"**。
#     ★ 本仓的既有做法是走**声明式选择器**（`selection` 参数 + `sw_selection_spec` 解析）
#       ⇒ ★ 那一层要另加（★ 不是现在草率塞一个 `str` 参数假装它是实体）。
#     ★★ 故：**实现层已有**（真机建成），**工具层留待接声明式选择器** ⇒ ★ 不假装。
#
#   ★★★ **两条分割线为什么还没成**：真机上都是"**树无增量**"。★ 而它们**不要求 mark**
#     （★ 官方 Remarks 没给 mark 表）⇒ ★ 前置是"**要有可投影的草图 / 可选的面**"，
#     ★ 探针里的前置**显然还不够** ⇒ ★ 下一轮按 `Create_Ref_Plane` 那次的教训
#       （★ **选完立刻调**、★ 并把选中数带进证据）再试 ✓
#
# 官方依据（三源）:
#   · `C:\\swapi\\types\\IModelDoc2\\InsertCurveFileBegin.md`（`void ()`）
#   · `C:\\swapi\\types\\IModelDoc2\\InsertCurveFilePoint.md`（`bool (X, Y, Z)`）
#   · `C:\\swapi\\types\\IModelDoc2\\InsertCurveFileEnd.md`（`bool ()`）
#   · `C:\\swapi\\types\\IFeatureManager\\InsertMateReference2.md`（★ **12 参**逐字）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

from tool_registry import Param, ToolSpec

_BATCH71: list[ToolSpec] = [
    ToolSpec(
        name="solidworks_insert_curve_through_points",
        title="Insert Curve Through Points",
        module="sw_curve_and_split", function="insert_curve_through_points",
        inject="model",
        param_alias={"points_mm": "points_mm"},
        params=[
            Param("points_mm", list, description="点的列表，每项 `[x, y, z]`（**毫米**，至少 2 个）。"
                                               "★ 官方 X/Y/Z 只说 \"value for the point\"、**没给单位** ⇒ "
                                               "本工具按 SolidWorks API 惯例当作**米**、在边界换算一次"
                                               "（规则 2），★ 并把该假设写进返回值。"),
        ],
        doc="★ 通过参考点的曲线：`InsertCurveFileBegin()` → `InsertCurveFilePoint(X,Y,Z)`×N → "
            "`InsertCurveFileEnd()`（★ **三步式**，★ 别只调中间那个）。"
            "★ 真机建成：树新增 `曲线1`（★ 顺带验证了「按米换算」这个假设是对的）。"
            "★ 判据 = `Point`/`End` 的返回值 **且** 特征树增量。",
    ),
]

#: ★★ 注册器按 `SPECS_*` 找
SPECS_BATCH71 = _BATCH71
