"""★ 批次 83：由 Bunny 扇出产出、**经门禁**（`tools/check_bunny_toolspec_rows.py`）过滤后的 ToolSpec 声明。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   sw_simulation · sw_simulation_loads · sw_simulation_study
# 定位:   ★ 规格 `specs/204-tool-ramp/spec.md` 的批 83；
#         ★★ **本文件由 `tools/build_toolspec_batch_from_rows.py` 生成** ——
#         行来自 Bunny 子代理（**只读官方源与仓库**），而**判据、门禁、真机、提交归主线** ✓
# 官方依据: 逐行的 `official_file` / `official_signature` 见下表（★ 每条都是官方页的逐字签名）
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
        module="sw_simulation_study", function="get_loads_manager_of",
        inject="study",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 sw_simulation_study.py）：`查不到 —— C:\\swapi\\types\\ 下 566 个接口目录里没有任何 cosworks 接口（无 ICWStudy / ICWLoadsAndRestraintsManager 目录），故 ICWStudy 的成员页不存在，本函数没有可逐字抄的官方 **Signature** 行。真源逐字（D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt:2556，## `。★ 真源是**本仓** `scripts/sw_simulation_study.py` 的 `get_loads_manager_of`（★ 它不是 SolidWorks API 成员，故无官方页）—— 本函数是 repo_original 的**纯别名**：sw_simulation_study.py:360-362 函数体只有一行 `return get_study_manager_of(study)`，真正实现是同文件 :353-357 的 `get_com_member(study, 'LoadsAndRestraintsManager')`。其上方来源块 :337-352 逐字写着",
    ),
    ToolSpec(
        name="solidworks_simulation_get_results",
        title="取算例的结果对象",
        module="sw_simulation_study", function="get_results_of",
        inject="study",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 sw_simulation_study.py）：`查不到 —— C:\\swapi\\types\\ 下无 ICWStudy 目录（C:\\swapi 未收录 cosworks 任何接口），故没有 ICWStudy 成员页可抄。真源逐字（D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt:2565，## ICWStudy 段，出厂程序集纯元数据反射）：「 CWResults get_Results()」—— 零参属性 ge`。★ 真源是**本仓** `scripts/sw_simulation_study.py` 的 `get_results_of`（★ 它不是 SolidWorks API 成员，故无官方页）—— repo_original：sw_simulation_study.py:365-369 函数体只做 `get_com_member(study, 'Results')`，外加一道 `study is None → ValueError` 守卫。来源块 :337-352 逐字「CWResults get_Results()」并带 ⚠「这些属性在**有求解结果后**才有意义；**未求解时取 Results",
    ),
    ToolSpec(
        name="solidworks_simulation_solve_memory_preflight",
        title="求解前内存闸（按真实单元数/节点数估自由度与内存，超预算就拒）",
        module="sw_simulation", function="solve_memory_preflight",
        inject="",
        params=[
            Param("element_count", int, default=0, description="第一个形参。`ICWMesh.ElementCount` 的回读值（源码 scripts/sw_simulation.py:1625、:1631）。★ 无量纲的计数，按规则 2 不加 _mm 后缀。★ 它与 `node_count` 不是正整数时直接回 ok=False「网格没建成」（:1642-1646）。"),
            Param("node_count", int, default=0, description="关键字专用形参。`ICWMesh.NodeCount` 的回读值（源码 :1626、:1632）。★ 无量纲的计数。★ 给了就优先用它算自由度（**DOF ≈ 3 × 节点数**，每节点 3 个平动自由度，:1613/:1620/:1637），比回落到按单元数估更准；为 None 或 0 时回落到 DOF ≈ 4.2 × 单元数（:1640-1641）。★ `ICWMesh.NodeCount` 本身的官方页是 C:\\cworks_vb6\\CosmosWorksLib~CWMesh~NodeCount.html（第 56 行 `Public Property NodeCount As Lo"),
            Param("memory_budget_gb", float, default=0.0, description="关键字专用形参。内存上限，单位 **GB**（源码 :1627、:1648）。★ 它是**内存容量、不是长度** ⇒ 规则 2 的 `_mm` 不适用；沿用 mcp-server/tool_specs_batch78.py:78 同一参数的既有命名，不改名、不加 param_alias。★ 传 None ⇒ 走 `default_solve_memory_budget_gb()` = min(物理内存/2, 16.0) GB（源码 :1261、:1264-1289，ctypes GlobalMemoryStatusEx）。★ 估内存 > 预算即 ok=False「别跑」（:1683-1691）"),
            Param("solver_name", str, default="", description="关键字专用形参。求解器名，例如 'FFEPlus' / 'Intel Direct Sparse'（源码 :1612、:1659）。★ 它**只影响返回值里的 `★_适用性` 提示、不影响任何数值**；按**子串**匹配而非精确等值（:1662-1663，源码注释逐字写「真机上那个名字是 `Intel Direct Sparse`（带空格的组合名）」）。★ ⚠ 千万不要因为它像 0/1 就给数值类型：源码 :1657-1658 逐字警告「不要写 `solver_name or ''` —— `SolverType = 0`（automatic）是**合法值**，而 `0 or ''` ⇒ `'"),
        ],
        doc="★ 官方签名（逐字，来自 sw_simulation.py）：`查不到（非 SolidWorks API 成员）`。★ 官方签名：查不到，且**不该**查到 —— 这是本仓自研的纯计算闸（无 COM、无 sw_connect、无 select），`C:\\cworks_vb6` 与 `C:\\swapi` 下都没有 MeshSafetyRestore / SolveMemoryPreflight 这样的成员。★ 官方只对**换算规则**发言，且**作用域极窄**：那句「1GB per 2,000,000 dof」在手册里写的主语是 **iterative FFEPlus solver**，源码 :1652-1682 已把这层限制做成返回值里的 `★_适用性` 字段（automatic / FFEPlus / 直",
    ),
    ToolSpec(
        name="solidworks_simulation_get_edge_weld_connector",
        title="Get the Edge Weld Connector at an Index from the Loads Manager",
        module="sw_simulation_loads", function="get_edge_weld_connector",
        inject="manager",
        params=[
            Param("index", int, default=0, description="官方 NIndex —— 边焊连接件在 ICWLoadsAndRestraintsManager 里的序号。★ 无量纲（整数序号，不是长度，故按规则 2 不加 _mm）。★ 官方 Remarks 明确两点：(a) 先调 ICWLoadsAndRestraintsManager::Count 才能定出 NIndex；(b) Simulation Study 树里的上下位置与 NIndex **不对应**，映射要靠 GetLoadsAndRestraints 建立 ⇒ 本工具不替调用方枚举。"),
        ],
        doc="★ 官方签名（逐字，来自 ICWLoadsAndRestraintsManager~GetEdgeWeldConnector.txt）：`Function GetEdgeWeldConnector( _ ByVal NIndex As System.Integer, _ ByRef ErrorCode As System.Integer _ ) As CWEdgeWeldConnector`。★ 官方页**不在 C:\\swapi\\types\\ 下**（该树只收录 SolidWorks 核心 API；实测 Get-ChildItem 'C:\\swapi\\types' 无任何 ICW* 接口目录 ⇒ Simulation/CosWorks 加载项接口族查不到，故 q1 的路径形态与常见条目不同）；本页在 CHM cosworks 册里，正文以 JSON 转义嵌在 <script> 标签中（模块 docstring L8-L15 记载这一坑），official_file 指向本仓已抽好的纯文本副本（工具 tools\\extract_cosworks_docs.py），签名在该文件里逐字可",
    ),
]
