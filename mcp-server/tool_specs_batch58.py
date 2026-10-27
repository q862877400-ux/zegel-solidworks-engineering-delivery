# ── 24h 计划 v2 · 段 5：**仿真载荷族**（轮 408 恢复 4 条）─────────────────────────────
# ───
# ★★★★ 2026-10-03（轮 408）★ **本轮的起点是"抄官方声明"**（★ 收敛报告写的下一步，★ 不是
# 继续试参数）：
#   从 CHM 抄出 `ICWLoadsAndRestraintsManager` 的六条 VB 声明 ——
#   ```
#   Function AddXxx(ByVal DispArray As System.Object, ByRef ErrorCode As System.Integer)
#   ```
#   ⇒ ★★ **六条签名一模一样**，且与**已能用的** `AddElasticConnector` **同形**
#     ⇒ ★ **形态没错 ⇒ 失败在别处**。
#   ★★ 而更强的线索来自**载荷的性质**：★ 对流 / 热流 / 热功率 / 温度 / 辐射是**热载荷**
#     ⇒ ★ **而我轮 402 一直在 `static` 算例上试它们** ⚠
#   ⇒ ★ 把**算例类型**变成变量（`study_type=3` = thermal）⇒ ★★ **真机：4 条全部建成** ✓✓✓
#
# ★★★★ **所以轮 402 的「另 5 条未建成」是误判 —— 真因是算例类型不对。**
#   真机（`output/thermal-loads-evidence.json` · `verdict: pass`）：
#   ```
#   convection       计数 0 → 1   ✓
#   heat_flux        计数 1 → 2   ✓
#   heat_power       计数 2 → 3   ✓
#   radiation        计数 3 → 4   ✓
#   temperature      ✗ com_error(-2147352561, '非选择性的参数。')  ← ★ **缺必填参数**
#   elastic_connector ✗ 在**热算例**下反而不成（★ 它要 static）
#   ```
#
# ★★ **两条要写进文档的事实**：
#   ① ★ **这 4 条要求算例是 `thermal`（`study_type=3`）** —— ★ 建算例请用
# `create_static_study(sw, name, study_type=3)`（★ 那个函数名是历史的，它收 `study_type`
# ）。
#   ② ★ **`elastic_connector` 相反：它在 `static` 下成、在 `thermal` 下不成** ⇒
#      ★★ **各载荷对算例类型的要求不同，要分别记**（★ 不能一概而论）。
#
# ⚠★ **上面那行「`temperature` ✗」已经**过时**** —— ★★ **2026-10-04（接手轮）更正**
#   （★ 处置 `JUDGE-C_D_E.md` 的 🔴 **#16** · `E-4 #3` —— ★ 裁判逐字：
#    「★ 文件头写「`temperature` 仍不注册」、★ 同文件却**已注册**且 arity 仍停在
#      被怀疑过时的 CHM 声明上」）✓
#   ★ **该条**已注册****：★ 本文件下面就有
#     `"solidworks_simulation_apply_temperature"` ⇒ ★ **同文件自相矛盾** ✓
#   ★★ **而 arity 那句也要更正** —— ★ 我读了**出厂类型库的反射 dump**：
#     · ★ `_raw/**/iface_cosworks.txt:1533-1534` 逐字：
#       `CWTemperature AddTemperature(Object, Int32&)` ⇒ ★★ **2 个参数** ✓
#       ⇒ ★★★ **与 CHM 那页的「2 条」**一致** ⇒ **CHM 没写错、也不是"2021 版过时"** ✓
#     · ★★ 而**反射 dump 里**有它**（★ 10 处命中，含 `members_2021.txt` 与
#       `iface_cosworks.txt`）⇒ ★ ★**原来那句「反射 dump 里都没有这个名字」是错的** ✓
#     · ★★★ 真正缺的是**本仓生成的 `ARITY` 表**（`sw_api_sldworks.py`）——
#       它里**没有** `AddTemperature` ⇒ ★★★★ **所以那是**那张表的覆盖缺口**、
#       ★ 不是「这个成员不存在」** ✓
#   ★★★ **⇒ 「不猜」这条结论仍然成立**（★ 铁律 5），★ 而**依据要换**：
#     不是"查不到"，★ 而是"**真机缺参数** + **本仓 ARITY 表没收录**" ✓
#   ★★★★ **⇒ 下一步（具体到动作）**：★ 用**活的类型库**（`comtypes`）读它的真实参数表，
#     或补 `ARITY` 表的覆盖 —— ★ **而不再需要查 CHM 的示例**（★ 那份与反射一致）✓
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch58.py —— 本文件
# 定位:   24h 计划 v2 段 5：把 4 条热载荷 + 弹性连接挂成 MCP 工具。
# 官方签名依据: CHM `ICWLoadsAndRestraintsManager~Add{Convection,HeatFlux,HeatPower,Radi
# ation,
# ElasticConnector}.html` 的 VB 声明（**逐字抄自**：`AddXxx(DispArray As Object, ByRef E
# rrorCode)`）·
#   `swsAnalysisStudyTypeThermal = 3`（`scripts/sw_simulation.SWS_ANALYSIS_STUDY_TYPES`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param

#: ★★ 复用 batch29 的骨架（`_spec` 里 `module="sw_simulation_loads"`、`inject="manager"`
#: 、
#:   `pre_call=_select_face`、`derived_args=_derive_model` 一整套都在里面）。
from tool_specs_batch29 import _spec

_READBACK = (
    "★ `ok` 的判据是**回读**：载荷/约束计数**恰好 +1**，★ **不是**返回值。"
    "⚠ 需要 Simulation 加载项（首次调用会自动加载）。"
)
_THERMAL = (
    "⚠★ **本载荷要求算例是「热算例」**（`study_type=3`）—— ★ 在**静力算例**上"
    "实测**不涨计数**（★ 真机对照：轮 408）。建算例请用 "
    "`create_static_study(sw, name, study_type=3)`。"
)

SPECS_BATCH58 = [
    _spec(
        "solidworks_simulation_apply_convection",
        "Apply a Convection Load",
        "apply_convection_report",
        (
                        "Apply a convection load to the selected faces of a thermal simulation study. Creates one load "
                        "in the study and does not save the document; the ok flag comes from the load count rising by e"
                        "xactly one rather than from the return value, and a static study leaves the count unchanged, s"
                        "o create a thermal study first."
                    ),
        [
            Param("study_name", str, default="", description=(
                                                     "Name of an existing study; empty means the first study in the doc"
                                                     "ument. Defaults to empty."
                                                 )),
            Param("selection", str, description=(
                                        "Declarative face selection the load applies to: '__current_selection__' for th"
                                        "e current selection or 'index:<n>' for the n-th face on the body."
                                    )),
        ],
    ),
    _spec(
        "solidworks_simulation_apply_heat_flux",
        "Apply a Heat Flux Load",
        "apply_heat_flux_report",
        (
                        "Apply a heat flux load to the selected faces of a thermal simulation study. Creates one load i"
                        "n the study and does not save the document; the ok flag comes from the load count rising by ex"
                        "actly one rather than from the return value, and a static study leaves the count unchanged, so"
                        " create a thermal study first."
                    ),
        [
            Param("study_name", str, default="", description=(
                                                     "Name of an existing study; empty means the first study in the doc"
                                                     "ument. Defaults to empty."
                                                 )),
            Param("selection", str, description=(
                                        "Declarative face selection the load applies to: '__current_selection__' for th"
                                        "e current selection or 'index:<n>' for the n-th face on the body."
                                    )),
        ],
    ),
    _spec(
        "solidworks_simulation_apply_heat_power",
        "Apply a Heat Power Load",
        "apply_heat_power_report",
        (
                        "Apply a heat power load to the selected faces of a thermal simulation study. Creates one load "
                        "in the study and does not save the document; the ok flag comes from the load count rising by e"
                        "xactly one rather than from the return value, and a static study leaves the count unchanged, s"
                        "o create a thermal study first."
                    ),
        [
            Param("study_name", str, default="", description=(
                                                     "Name of an existing study; empty means the first study in the doc"
                                                     "ument. Defaults to empty."
                                                 )),
            Param("selection", str, description=(
                                        "Declarative face selection the load applies to: '__current_selection__' for th"
                                        "e current selection or 'index:<n>' for the n-th face on the body."
                                    )),
        ],
    ),
    _spec(
        "solidworks_simulation_apply_radiation",
        "Apply a Radiation Load",
        "apply_radiation_report",
        (
                        "Apply a radiation load to the selected faces of a thermal simulation study. Creates one load i"
                        "n the study and does not save the document; the ok flag comes from the load count rising by ex"
                        "actly one rather than from the return value, and a static study leaves the count unchanged, so"
                        " create a thermal study first."
                    ),
        [
            Param("study_name", str, default="", description=(
                                                     "Name of an existing study; empty means the first study in the doc"
                                                     "ument. Defaults to empty."
                                                 )),
            Param("selection", str, description=(
                                        "Declarative face selection the load applies to: '__current_selection__' for th"
                                        "e current selection or 'index:<n>' for the n-th face on the body."
                                    )),
            Param(
                "radiation_type",
                int,
                default=0,
                description=(
                    "Radiation type enum; the numeric values are not published in the local sources. Defaults to 0."
                ),
            ),
        ],
    ),
    _spec(
        "solidworks_simulation_apply_elastic_connector",
        "Add an Elastic Connector",
        "apply_elastic_connector_report",
        (
                        "Add an elastic connector between the selected faces of a static simulation study. Creates one "
                        "load in the study and does not save the document; the ok flag comes from the load count rising"
                        " by exactly one rather than from the return value, and unlike the thermal loads this one takes"
                        " a static study and not a thermal one."
                    ),
        [
            Param("study_name", str, default="", description=(
                                                     "Name of an existing study; empty means the first study in the doc"
                                                     "ument. Defaults to empty."
                                                 )),
            Param("selection", str, description=(
                                        "Declarative face selection the load applies to: '__current_selection__' for th"
                                        "e current selection or 'index:<n>' for the n-th face on the body."
                                    )),
        ],
    ),
    _spec(
        "solidworks_simulation_apply_temperature",
        "Apply a Temperature Load",
        "apply_temperature_report",
        (
                        "Apply a temperature load to the selected faces of a thermal simulation study. Creates one load"
                        " in the study and does not save the document; the ok flag comes from the load count rising by "
                        "exactly one rather than from the return value, and a static study leaves the count unchanged, "
                        "so create a thermal study first."
                    ),
        [
            Param("study_name", str, default="", description=(
                                                     "Name of an existing study; empty means the first study in the doc"
                                                     "ument. Defaults to empty."
                                                 )),
            Param("selection", str, description=(
                                        "Declarative face selection the load applies to: '__current_selection__' for th"
                                        "e current selection or 'index:<n>' for the n-th face on the body."
                                    )),
        ],
    ),
]
