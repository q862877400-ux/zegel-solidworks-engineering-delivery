"""★ 批次 83：由 Bunny 扇出产出、**经门禁**（`tools/check_bunny_toolspec_rows.py`）过滤后的 ToolSpec 声明。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   sw_simulation · sw_simulation_loads · sw_simulation_study
# 定位:   ★ 规格 `specs/204-tool-ramp/spec.md` 的批 83；
#         ★★ **本文件由 `tools/build_toolspec_batch_from_rows.py` 生成** ——
#         行来自 Bunny 子代理（**只读官方源与仓库**），而**判据、门禁、真机、提交归主线** ✓
# 官方依据: 逐行的 `official_file` / `official_signature` 见下表（★ 每条都是官方页的逐字
#           签名）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **4 个工具**
# ⚠ 生成器**只收 `exposable=True` 且门禁 0 问题的行**（★ 被门禁挡下的 0 行见 `output/`）
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH83"]

SPECS_BATCH83 = [
    ToolSpec(
        name="solidworks_simulation_get_loads_manager",
        title="取算例的载荷与夹具管理器",
        module="sw_simulation_study",
        function="get_loads_manager_of",
        inject="study",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 sw_simulation_study.py）：`查不到 —— C:\\swapi\\types\\ 下 566 个接口目录里没有任何"
            " cosworks 接口（无 ICWStudy / ICWLoadsAndRestraintsManager 目录），故 ICWStudy 的成员页不存在，本函数没有"
            "可逐字抄的官方 **Signature** 行。真源逐字（D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt:2556，## `。★ 真"
            "源是**本仓** `scripts/sw_simulation_study.py` 的 `get_loads_manager_of`（★ 它不是 SolidWorks API 成员，故"
            "无官方页）—— 本函数是 repo_original 的**纯别名**：sw_simulation_study.py:360-362 函数体只有一行 `return ge"
            "t_study_manager_of(study)`，真正实现是同文件 :353-357 的 `get_com_member(study, 'LoadsAndRestraintsManager"
            "')`。其上方来源块 :337-352 逐字写着"
        ),
        doc=(
            "Get the loads and restraints manager of a simulation study. Read-only; the load and restraint tools act th"
            "rough this manager, so it is the entry point to them, and it is only meaningful once the study exists."
        ),
    ),
    ToolSpec(
        name="solidworks_simulation_get_results",
        title="取算例的结果对象",
        module="sw_simulation_study",
        function="get_results_of",
        inject="study",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 sw_simulation_study.py）：`查不到 —— C:\\swapi\\types\\ 下无 ICWStudy 目录（C:\\swa"
            "pi 未收录 cosworks 任何接口），故没有 ICWStudy 成员页可抄。真源逐字（D:\\AI\\SW\\_raw\\reflect\\iface_cosw"
            "orks.txt:2565，## ICWStudy 段，出厂程序集纯元数据反射）：「 CWResults get_Results()」—— 零参属性 ge`。★ 真"
            "源是**本仓** `scripts/sw_simulation_study.py` 的 `get_results_of`（★ 它不是 SolidWorks API 成员，故无官方"
            "页）—— repo_original：sw_simulation_study.py:365-369 函数体只做 `get_com_member(study, 'Results')`，外加一"
            "道 `study is None → ValueError` 守卫。来源块 :337-352 逐字「CWResults get_Results()」并带 ⚠「这些属性在**"
            "有求解结果后**才有意义；**未求解时取 Results"
        ),
        doc=(
            "Get the results object of a simulation study. Read-only; the results object only carries data after the st"
            "udy has been solved, and a missing study raises instead of returning nothing."
        ),
    ),
    ToolSpec(
        name="solidworks_simulation_solve_memory_preflight",
        title="求解前内存闸（按真实单元数/节点数估自由度与内存，超预算就拒）",
        module="sw_simulation",
        function="solve_memory_preflight",
        inject="",
        params=[
            Param(
                "element_count",
                int,
                default=0,
                description=(
                    "Element count read back from the mesh; a non-positive value here and in node_count together mean n"
                    "o mesh was built. Defaults to 0."
                ),
            ),
            Param(
                "node_count",
                int,
                default=0,
                description=(
                    "Node count read back from the mesh; when it is positive it drives the estimate, counting three tra"
                    "nslational degrees of freedom per node. Defaults to 0."
                ),
            ),
            Param(
                "memory_budget_gb",
                float,
                default=0.0,
                description=(
                    "Memory budget in gigabytes; the fallback to half the physical memory capped at 16 GB applies only "
                    "when no value is passed at all, so pass a real budget here. Defaults to 0.0."
                ),
            ),
            Param(
                "solver_name",
                str,
                default="",
                description=(
                    "Solver name such as FFEPlus or Intel Direct Sparse; it only changes the applicability note in the "
                    "result and is matched as a substring. Defaults to empty."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_simulation.py）：`查不到（非 SolidWorks API 成员）`。★ 官方签名：查不到，且**不"
            "该**查到 —— 这是本仓自研的纯计算闸（无 COM、无 sw_connect、无 select），`C:\\cworks_vb6` 与 `C:\\swapi` 下"
            "都没有 MeshSafetyRestore / SolveMemoryPreflight 这样的成员。★ 官方只对**换算规则**发言，且**作用域极窄**："
            "那句「1GB per 2,000,000 dof」在手册里写的主语是 **iterative FFEPlus solver**，源码 :1652-1682 已把这层限制"
            "做成返回值里的 `★_适用性` 字段（automatic / FFEPlus / 直"
        ),
        doc=(
            "Check whether a solve would fit in memory before running the solver. Read-only and needs no SolidWorks ses"
            "sion; it estimates degrees of freedom from the node count, falling back to the element count, and reports "
            "refusal when the estimate exceeds the budget."
        ),
    ),
    ToolSpec(
        name="solidworks_simulation_get_edge_weld_connector",
        title="Get the Edge Weld Connector at an Index from the Loads Manager",
        module="sw_simulation_loads",
        function="get_edge_weld_connector",
        inject="manager",
        params=[
            Param(
                "index",
                int,
                default=0,
                description=(
                    "Connector index in the loads and restraints manager; count the connectors first, and note that the"
                    " study tree order does not correspond to it. Defaults to 0."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 ICWLoadsAndRestraintsManager~GetEdgeWeldConnector.txt）：`Function GetEdgeWeldConne"
            "ctor( _ ByVal NIndex As System.Integer, _ ByRef ErrorCode As System.Integer _ ) As CWEdgeWeldConnector`。★"
            " 官方页**不在 C:\\swapi\\types\\ 下**（该树只收录 SolidWorks 核心 API；实测 Get-ChildItem 'C:\\swapi\\type"
            "s' 无任何 ICW* 接口目录 ⇒ Simulation/CosWorks 加载项接口族查不到，故 q1 的路径形态与常见条目不同）；本页在"
            " CHM cosworks 册里，正文以 JSON 转义嵌在 <script> 标签中（模块 docstring L8-L15 记载这一坑），official_fil"
            "e 指向本仓已抽好的纯文本副本（工具 tools\\extract_cosworks_docs.py），签名在该文件里逐字可"
        ),
        doc=(
            "Get one edge weld connector of a simulation study by index. Read-only; the index is the connector's place "
            "in the loads and restraints manager, which does not match its place in the study tree."
        ),
    ),
]
