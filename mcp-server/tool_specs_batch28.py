"""第二十八批 MCP 工具声明：**网格 / 求解 / 研究读数** 4 个（24h 计划 · 段 1.2 / Spec Kit `142`）。

## ★★★ 本批让仿真链**贯通**（段 1.1 补了"建研究"，本批补"网格 → 跑 → 读数"）
```
★ 段 1.1（`specs/141`）补了「建研究」；本批补后半段：
     **网格 → 求解 → 读数**
⇒ ★★ 加上已有的载荷族（W7），仿真链**从"能建"到"能算出结果"** 全通。
```

## ★★★★★ 本批的核心：把本项目的**铁律**搬进工具的表面
```
★ `tools/capture_simulation_evidence.py` 里写着一条铁律：
    「**COM 返回值凡不能自证，一律以回读为判据**（本项目已累计四处「返回码撒谎」）」
  而它的判据表：
    | 网格 | `CreateMesh` 返回 0 **且** `ElementCount` 为一个（小的）正整数 |
    | 求解 | **不是** `RunAnalysis` 的返回码，而是 `study.Results` 非空 + `GetPlotCount > 0` |
⇒ ★★ 而 `create_mesh` / `run_analysis` **都只回一个 int 返回码** ⇒ **不能自证**
⇒ ★★★ 所以本批**不直接挂它们**，而是包成**回读报告**：
     · `create_mesh_report` ⇒ `ok` 由 **`element_count > 0`** 决定
     · `run_analysis_report` ⇒ `ok` 由 **`results_present` + `plot_count`** 决定
     · 两者都**显式声明** `return_is_trustworthy: False`
   ⇒ ★ **让调用方在接口层面就无法误用返回码** —— 这比在文档里写一句"别信返回码"硬得多。
```

## ★ §5.0 先找后搓的结果
```
① 四家 live 测试 ⇒ 没有仿真求解的判据
② ★ **自己的仓库** ⇒ ★★ **有，而且是现成的**：`tools/capture_simulation_evidence.py` 的判据表
   （连同"铁律"那句话）⇒ ★ **本批的判据与薄函数形状全部照它**，没有新搓。
```

## ★ 四个工具
```
① `solidworks_simulation_mesh_size`          ← `mesh_size_report`（★ 包 `(float,float)` 元组）
② `solidworks_simulation_create_mesh`        ← `create_mesh_report`（★ 回读报告）
③ `solidworks_simulation_run_analysis`       ← `run_analysis_report`（★ 回读报告）
④ `solidworks_simulation_collect_evidence`   ← `collect_study_evidence`（★ **已经是 dict，直接挂**）
```

## ★ 参数命名（规则 2）
```
`units` 是官方 `swsUnit_e` 枚举 ⇒ **不是长度** ⇒ 不加 `_mm` 后缀（★ 规则 2 只管长度/角度参数）。
⚠ 而 `element_size` / `tolerance` **是长度** ⇒ ★ 对外名带 `_mm` + `param_alias` 改名
  （★ 141 的教训：**对外名 ≠ 形参名就必须写 alias**，且**新门禁会盯着**）。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植）
# 文件:   mcp-server/tool_specs_batch28.py
# 定位:   「孤立能力暴露」第二十八批 / 24h 计划 段 1.2（Spec Kit `142`）。
# 官方签名依据: 不适用（只做参数搬运 + 回读包装）；ShapeFunction 依据见 `scripts/sw_simulation.py`
#          的来源块（`ICWStudy.CreateMesh` / `RunAnalysis` / `Mesh.ElementCount` / `Results.GetPlotCount`）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH28"]

_STUDY = (
    'Name of an EXISTING simulation study (e.g. "Study 1" / "算例 1"). '
    "⚠ Leave empty to use the FIRST study — create one first with "
    "solidworks_simulation_create_study."
)
_UNITS = (
    "Official swsUnit_e value (0 = SI, 1 = English, 2 = Metric). "
    "★ It is an enum, NOT a length, so it carries no unit suffix."
)
_SEL = (
    "Declarative selection — reserved for the mesh/analysis family; not used by these "
    "four tools (they act on the whole study)."
)


SPECS_BATCH28 = [
    ToolSpec(
        name="solidworks_simulation_mesh_size",
        title="Get the Suggested Mesh Element Size",
        module="sw_simulation",
        function="mesh_size_report",
        inject="study",
        param_alias={"study_name": None},
        params=[
            Param("study_name", str, default="", description=(
                                                     "Name of an existing simulation study; empty uses the first study "
                                                     "in the document. Defaults to empty."
                                                 )),
            Param("units", int, default=-1, description=(
                                                "Unit code: 0=SI, 1=English, 2=Metric; -1 returns values in the documen"
                                                "t length unit. Defaults to -1."
                                            )),
        ],
        evidence=(
            "Return the suggested mesh `{element_size, tolerance, units}` for a study. ★ The default units = -1 yields "
            "MILLIMETRE-scale values (verified in this repo) and nothing is converted — the `units` value is echoed bac"
            "k so the caller can tell."
        ),
        doc=(
            "Read the suggested element size and tolerance for a simulation study. Read-only; units defaults to -1, whi"
            "ch yields millimetre-scale values, and nothing is converted, so the units value is echoed back for the cal"
            "ler to check."
        ),
    ),
    ToolSpec(
        name="solidworks_simulation_create_mesh",
        title="Create the Mesh for a Study",
        module="sw_simulation",
        function="create_mesh_report",
        inject="study",
        param_alias={
            "study_name": None,
            "element_size_mm": "element_size",
            "tolerance_mm": "tolerance",
        },
        params=[
            Param("study_name", str, default="", description=(
                                                     "Name of an existing simulation study; empty uses the first study "
                                                     "in the document. Defaults to empty."
                                                 )),
            Param("units", int, default=0, description="Unit code: 0=SI, 1=English, 2=Metric. Defaults to 0."),
            Param(
                "element_size_mm",
                float,
                default=0.0,
                description="Global element size in millimetres; 0 lets SolidWorks choose. Defaults to 0.",
            ),
            Param(
                "tolerance_mm",
                float,
                default=0.0,
                description=(
                    "Mesh tolerance in millimetres; 0 lets SolidWorks choose, and the official default is 5 percent of "
                    "the element size. Defaults to 0."
                ),
            ),
        ],
        evidence=(
            "Mesh the study and return a READ-BACK report `{ok, return_code, return_is_trustworthy, element_count}`. ★★"
            " Judge success by `ok`, which is derived from `element_count > 0` — NOT from the return code (this repo's "
            "rule: COM return values that cannot prove themselves are never trusted; `return_is_trustworthy` is always "
            "false)."
        ),
        doc=(
            "Mesh a simulation study and report the read-back result. It creates the mesh on the study and does not sav"
            "e the document; judge success by ok, which comes from a positive element count, never by the return code, "
            "because that code cannot prove itself."
        ),
    ),
    ToolSpec(
        name="solidworks_simulation_run_analysis",
        title="Run the Study and Report Read-Back Results",
        module="sw_simulation",
        function="run_analysis_report",
        inject="study",
        param_alias={"study_name": None},
        params=[
            Param("study_name", str, default="", description=(
                                                     "Name of an existing simulation study; empty uses the first study "
                                                     "in the document. Defaults to empty."
                                                 )),
        ],
        evidence=(
            "Run the study and return a READ-BACK report `{ok, return_code, return_is_trustworthy, results_present, plo"
            "t_count, plot_names}`. ★★ Judge success by `ok` (= results present AND plot_count > 0), NOT by the return "
            "code — this repo has documented four separate cases of a COM return code lying."
        ),
        doc=(
            "Run the solver for a simulation study and report the read-back result. It creates results and plots on the"
            " study and does not save the document; judge success by ok, which means results exist and the plot count i"
            "s above zero, never by the return code."
        ),
    ),
    ToolSpec(
        name="solidworks_simulation_collect_evidence",
        title="Collect Simulation Study Evidence",
        module="sw_simulation",
        function="collect_study_evidence",
        inject="sw_app",
        params=[],
        evidence=(
            "Return a JSON-able summary of every study in the active document: per-study `name / type / state / entity_"
            "count / analysis_type / mesh_type / configuration / is_active / loads_and_restraints`, plus `cosmos_versio"
            "n`, `study_count` and `active_study_index`. ★ Reading only."
        ),
        doc=(
            "Read every simulation study in the active document into an audit summary. Read-only; each study reports it"
            "s name, type, state, entity count, analysis type, mesh type, configuration, active flag and load counts, a"
            "nd the document reports the cosmos version, study count and active index. It deliberately does not read re"
            "sult values."
        ),
    ),
]
