"""★ 批次 78：**仿真的安全入口** 2 个 —— 建网格的唯一推荐入口 + 本研究求解器读数。

（★ 目标：★ **别人部署本项目之后，拿到的是安全那条路**，而不是要自己知道该设哪些旋钮）
"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其源码里）
# 文件:   `scripts/sw_simulation.py` 的 `create_mesh_safely` / `static_solver_type_repor
# t`
#         `tools/probe_mesh_profile_matrix.py`（★ 四档对照 —— 安全档的依据）
#         `docs/known-facts.md` 事实 526 / 528 / 529
# 定位:   ★★★★ **为什么要有这一批**（★ 2026-10-04 · 业主原话的两个层次）：
#   ```
# ★ 业主：★「修好，而且要**站在未来别的人使用我们项目的时候也能生效**的角度**根因修复**
# 」
#   ```
#   ★★ 事实 526/528 把"网格爆内存"与"求解不出结果"两条都修在了**能力层与探针**里 ——
#     ★ 而**工具层**（别人真正会调的那一层）拿到的仍是**裸的** `create_mesh_report`：
#       · 不设安全档 ⇒ 曲率自适应 + `MinElementSize=0` ⇒ **网格规模不受控**；
#       · 不做求解前内存闸 ⇒ **内存超预算也照样跑**；
#       · 不过忙检 ⇒ **SolidWorks 正忙时照样下发调用**（★ 事实 526 的卡死路径）。
#   ⇒ ★ 所以本批把**那条安全链**做成**一个工具**：★ `..._create_mesh_safely`
#     （量闸 → 安全档 → 建网格 → 真读数 → 内存闸 → **还原设置**）✓
#   ★★ 另一个（`..._solver_type`）解决一条**容易被过度外推**的事：★ 那条内存换算
#     「每 2e6 自由度 1 GB」**出自 FFEPlus**，而真机跑的是 **Intel Direct Sparse**
#     ⇒ ★ 先让调用方**看得见本研究用的是哪个求解器**（★ 事实 529）✓
# 官方依据: `ICWMesh` 的 `Quality`/`MesherType`（`swsMeshQuality_e` / `swsMesherType_e`
#           ）·`ICWStaticStudyOptions.SolverType`（`swsSolverType_e`）·`c_meshing_option
#           s.htm` / `c_Element_Size_in_Curvature_Based_Mesher.htm`（本机官方手册）
# 许可:   本仓库 MIT。★ 无第三方代码引入（`THIRD-PARTY-NOTICES.md` 不因本批变动）。
# ⚠ 未验证项：★ `memory_budget_gb` 的取值只影响**拒绝阈值**、不影响几何；
#   ★ 本批两个工具都在真机上跑过（证据见 `output/mesh-profile-matrix-evidence.json`
#   与 `output/analysis-run-long-timeout-evidence.json`）✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH78"]

#: ★ 与既有多批同形：`study_name` 由解析器消费（不传给目标函数），空名 = 取第一个研究
_STUDY = (
    'Name of an EXISTING simulation study (e.g. "Study 1" / "算例 1"). '
    "Leave empty to use the FIRST study."
)
_UNITS = (
    "swsUnit_e: 0=SI (metre) / 1=English / 2=Metric (MILLIMETRE). "
    "★ Measured in this repo: `units=2` returns MILLIMETRE-scale values while "
    "`units=0/-1` return values 1000x larger — the VALUE and the UNITS must match."
)


def _derive_model(params):  # noqa: ARG001
    """★ 把活动文档作为 `model=` 补进实参。

    ★★ **为什么必须有它**（★ 2026-10-04 真机踩出来的）：★ 量预算前置闸要的是**零件文档**
      （它要读包围盒）—— ★ 而第一版把 **`study`** 传了进去 ⇒ ★ 那道闸在**错误的对象**上取包围盒
      ⇒ ★★ **静默失效**（内部 `except` 收成"判据自身出错、不因此阻断"）
      ⇒ ★ "量预算前置闸"**看起来在跑、实际没判**（事实 40 的老毛病）✓
    """
    from scripts.sw_connect import connect_solidworks

    _sw, model, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    if model is None:
        raise RuntimeError(
            "没有活动文档 —— 请先打开一个零件（★ 量预算闸要读它的包围盒）"
        )
    return {"model": model}


SPECS_BATCH78 = [
    ToolSpec(
        name="solidworks_simulation_create_mesh_safely",
        title="Create the Mesh the SAFE Way (budget gate + safety profile + restore)",
        module="sw_simulation",
        function="create_mesh_safely",
        inject="study",
        param_alias={
            "study_name": None,
            "element_size_mm": "element_size",
            "tolerance_mm": "tolerance",
        },
        params=[
            Param("study_name", str, default="", description=(
                                                     "Name of an existing study, for example Study 1; empty uses the fi"
                                                     "rst study in the document. Defaults to empty."
                                                 )),
            Param("units", int, default=2, description=(
                                               "Unit system: 0=SI metre, 1=English, 2=Metric millimetre, and the value "
                                               "must match the unit of element_size_mm. Defaults to 2."
                                           )),
            Param(
                "element_size_mm",
                float,
                default=0.0,
                description="Global element size in millimetres, where 0 lets SolidWorks choose. Defaults to 0.0.",
            ),
            Param(
                "tolerance_mm",
                float,
                default=0.0,
                description="Mesh tolerance in millimetres, where 0 uses the document default. Defaults to 0.0.",
            ),
            Param(
                "memory_budget_gb",
                float,
                default=None,
                description=(
                    "Refuse to build the mesh when the estimated solve memory exceeds this many gigabytes. Defaults to "
                    "unset, which uses the document default."
                ),
            ),
        ],
        derived_args=_derive_model,
        evidence=(
            "**THE RECOMMENDED WAY to mesh a study.** One call does seven things, all measured: ① element-size sanity g"
            "ate (two-sided: too big = degenerate, too small = memory blow-up) → ② **mesh safety profile** (`Quality=Dr"
            "aft` + `MesherType=Standard`, i.e. turns OFF the curvature-based mesher that refines without a lower bound"
            ") → ③ build the mesh → ④ read the REAL `ElementCount`/`NodeCount` → ⑤ **pre-solve memory gate** → ⑥ **rest"
            "ore the study's mesh settings** → ⑦ return an evidence-ready report. ★★ Measured on a real machine (100x60"
            "x20 mm plate): the factory settings gave 11301 nodes, the safety profile gave **1492 nodes (7.6x fewer)** "
            "and meshed in 0.3-0.8 s. ⚠ The estimate uses the official **FFEPlus** rule (1 GB per 2,000,000 DOF); if th"
            "e study solves with a direct solver that rule does not apply — check `solidworks_simulation_solver_type`. "
            "★★ Read `blocked` when `ok` is false: it says WHICH gate refused (`MESH_SIZE_UNSANE` / `MESH_SAFETY_APPLY_"
            "FAILED` / `MESH_FAILED` / `SOLVE_MEMORY_BUDGET`)."
        ),
        doc=(
            "Mesh a study behind an element-size gate and a pre-solve memory gate. Modifies the study's mesh and then r"
            "estores its mesh settings; read blocked when ok is false, since it names the gate that refused, and the me"
            "mory estimate assumes the FFEPlus rule."
        ),
    ),
    ToolSpec(
        name="solidworks_simulation_solver_type",
        title="Read Which Solver the Study Uses (so the memory rule is not over-applied)",
        module="sw_simulation",
        function="static_solver_type_report",
        inject="study",
        param_alias={"study_name": None},
        params=[
            Param("study_name", str, default="", description=(
                                                     "Name of an existing study; empty uses the first study in the docu"
                                                     "ment. Defaults to empty."
                                                 )),
        ],
        evidence=(
            "Return `{ok, value, name, reason}` for `ICWStaticStudyOptions.SolverType` (`swsSolverType_e`: automatic 0 "
            "/ direct_sparse 1 / ffeplus 2 / casi 5 / abaqus 6 / intel 7 / intel_cluster 8). ★★ **Why it matters**: the"
            " repo's solve-memory estimate uses the official **FFEPlus** rule (\"1 GB per 2,000,000 degrees of freedom"
            "\"), and that rule is FFEPlus-specific. Measured here: `SolverType` read back as `automatic (0)` while the"
            " solver actually chosen at solve time was **Intel Direct Sparse** — a direct solver, for which this repo h"
            "as NO official memory rule. ⚠ When the read fails, `ok` is false with a reason — it never guesses a defaul"
            "t."
        ),
        doc=(
            "Read which solver a static study will use, for example FFEPlus or a direct solver. Read-only; the value ca"
            "n read back as automatic while a direct solver is chosen at solve time, and when the read fails ok is fals"
            "e with a reason instead of a guessed default."
        ),
    ),
]
