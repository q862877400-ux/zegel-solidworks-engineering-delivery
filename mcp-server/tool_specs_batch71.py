"""★ B7 特征下拉的声明式工具（★ 只登记真机建成的那些）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（ToolSpec 声明层）
# 文件:   mcp-server/tool_specs_batch71.py
# 定位:   ★ 2026-10-03（轮 481）★ `specs/201-toolbar-gaps` 的 **B7**。
# 实现层在 `scripts/sw_curve_and_split.py`；★ 真机证据 `output/b7a-curve-split-evidence.
# json`。
#
# ====================  ================================================  ==========  ==
# ======
# 工具栏原文             官方成员                                          真机
# 登记
# ====================  ================================================  ==========  ==
# ======
# 通过参考点的曲线        `InsertCurveFileBegin/Point/End`（三步式）         ✅
#   ✅
# 配合参考               `InsertMateReference2`（**12 参**）               ✅
# ✗（见下）
# 分割线（投影）          `InsertSplitLineProject`                         ✅（★ 已更正
# ）  ✗
# 分割线（轮廓）          `InsertSplitLineSil`                             ✅（★ 已更正
# ）  ✗
# ====================  ================================================  ==========  ==
# ======
#
# ★★ **配合参考为什么不登记成工具**（★ 与"没建成"无关，★ 它**建成了**）：★ 它的第 2 个形
# 参
#     `PrimaryReferenceEntity` 的类型是 **`IEntity`（一个 COM 对象）** —— ★ 而 `ToolSpec` 的
# `Param` 只表达**基本类型**（float / int / bool / str）⇒ ★ **表达不了"传一个实体对象"**
# 。
#     ★ 本仓的既有做法是走**声明式选择器**（`selection` 参数 + `sw_selection_spec` 解析）
#       ⇒ ★ 那一层要另加（★ 不是现在草率塞一个 `str` 参数假装它是实体）。
#     ★★ 故：**实现层已有**（真机建成），**工具层留待接声明式选择器** ⇒ ★ 不假装。
#
#   ★★★ **两条分割线：2026-10-03（接手轮）真机都建成了** —— ★ 而此前那句归因是**错的**。
#     ⚠ **此前这里逐字写着**：「真机上都是"树无增量"。★ 而它们**不要求 mark**
#       （★ 官方 Remarks 没给 mark 表）⇒ ★ 前置是"要有可投影的草图 / 可选的面"」——
#       ★★ **「官方 Remarks 没给 mark 表」是假的**：两页的 `## Remarks` **都给了 mark 表**
#       （★ 投影型：草图 4 / 面 1；★ 轮廓型：方向项 2 / 面 1）。
#       ⇒ ★ 于是失败被**归因成了"能力不成"**，★ 而真因是**我没照官方 Remarks 选**。
#     ★★ **更正后的真机读数**（★ 两个证据文件都在 `output/`）：
#       · **投影型**：草图 mark 4 + 面 mark 1，且**投影草图所在面要在实体之外**、与目标面平行
#         ⇒ 建成 `分割线1`（`GetTypeName2` = `PLine`）· 面数 6→7 · 该面 1 环→2 环
#       · **轮廓型**：**方向项 mark 2** + 面 mark 1，且**视线不能顺着回转轴**
#         ⇒ 建成 `分割线1` · 面数 +1 · 圆柱侧面 2 环 → 两张各 1 环
#     ⇒ ★ 这两条**已具备登记成工具的条件**（★ 判据、前置、几何前提都已写明）；
#       ★ 未登记的原因**只剩一个**：★ 它们的"选择"要由调用方在**工具层之外**先做好
#       （★ 与"配合参考"同族）⇒ ★ 要接**声明式选择器**那一层，★ 不在本轮草率塞。
#     ★ 门禁 `scripts/check_official_md_claims.py` 现在守着这一类断言（★ 事实 484）。
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
        module="sw_curve_and_split",
        function="insert_curve_through_points",
        inject="model",
        param_alias={"points_mm": "points_mm"},
        params=[
            Param(
                "points_mm",
                list,
                description=(
                    "Points as [x, y, z] triples in millimetres; the API coordinate unit is assumed to be metres, conve"
                    "rted once here and echoed back in the report."
                ),
            ),
        ],
        evidence=(
            "★ 通过参考点的曲线：`InsertCurveFileBegin()` → `InsertCurveFilePoint(X,Y,Z)`×N → `InsertCurveFileEnd()`（★"
            " **三步式**，★ 别只调中间那个）。★ 真机建成：树新增 `曲线1`（★ 顺带验证了「按米换算」这个假设是对的）。★ "
            "判据 = `Point`/`End` 的返回值 **且** 特征树增量。"
        ),
        doc=(
            "Insert a curve through a list of XYZ points using the begin, point, end call sequence. It writes a curve f"
            "eature and does not save the document; all three calls run, and success needs both their returns and a new"
            " feature in the tree."
        ),
    ),
]

#: ★★ 注册器按 `SPECS_*` 找
SPECS_BATCH71 = _BATCH71
