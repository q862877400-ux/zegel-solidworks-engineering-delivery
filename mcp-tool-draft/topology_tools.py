"""T-011 最小可跑示例 —— 把护城河域（拓扑优化）的 3 个函数暴露成 MCP 工具。

# ⚠⚠ **本文件是独立草稿，没有接入在跑的 MCP 服务** ⚠⚠
#
# 为什么不做接入：
#   `mcp-server/server.py` 正是**本会话 `mcp__solidworks__*` 工具的来源**。
#   改它会改变**正在运行的** MCP 表面；而「单源运行」原则下（AGENTS.md 已知事实 24：
#   多个进程抢同一 COM 连接会死锁）重启 MCP 服务需要确保没有任务在跑。
#   ⇒ **接入与否由人决定时机**（见 `docs/T-011-expose-capabilities-assessment.md` §六）。
#
# 接入方式（三步，照 `server.py` 既有工具的写法）：
#   1. 把下面两个 **输入模型** 复制进 `server.py` 的模型区（`BaseInput` 之后）
#   2. 把下面三个 **`@mcp.tool` 函数**复制进 `server.py` 的工具区
#   3. 重启 MCP 服务；然后跑 `python scripts/validate_mcp.py` 与五项门禁
#
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把**已有**能力暴露成 MCP 工具，不新增能力）
# 文件:   D:\\AI\\SW\\mcp-tool-draft\\topology_tools.py
# 定位:   specs/002-merge-template 的 T-011；解决 AGENTS.md 已知事实 25
#         （「上游 MCP 只引用 25 个 scripts 模块，我们后补的 58 个一个都没进，交集 = 0」）。
#         三个工具分别包装 scripts/sw_topology.py 的 create_topology_study /
#         set_topology_goal / collect_topology_evidence —— 它们的实现**已存在**且
#         set_topology_goal 已真机验证（同一研究连续三次成功），本文件只做**包装**。
# 官方签名依据: 复用 sw_topology 内部已核过的官方签名（ICWStudyManager.CreateNewStudy3 /
#         ICWTopologyStudyManager.CreateGoal / GetMassConstraint 等），
#         本文件不引入任何新的 COM 调用。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本文件**不是**可直接 import 的模块（缺 `mcp` / `BaseInput` 等宿主符号），
#   它是**供复制**的草稿 ⇒ 不做语法外的自测。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

# ─────────────────────────────────────────────────────────────────────
# 【第 1 步】输入模型 —— 复制进 server.py 的模型区
# ─────────────────────────────────────────────────────────────────────
# 注意：命名照 union-conventions 规则 1（域在前、动在后）：
#   solidworks_topology_<动作>        ← 域 = topology
# 参数命名照规则 2：长度 _mm 后缀、角度 _deg 后缀。


class SolidworksTopologyCreateStudyInput(BaseInput):
    """Input for creating a SOLIDWORKS Simulation topology study on the active part."""

    study_name: str = Field(
        default="Topology Study 1",
        min_length=1,
        max_length=120,
        description="Study name. An existing study with the same name is deleted first.",
    )
    mesh_type: int = Field(
        default=0,
        ge=0,
        le=4,
        description="swsMeshType: 0=solid, 1=mid_surface, 2=surfaces, 3=mixed, 4=beam.",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.JSON, description="Return format."
    )


class SolidworksTopologySetGoalInput(BaseInput):
    """Input for setting the topology goal and its constraints.

    At least one of ``mass_reduce_percent`` / ``factor_of_safety`` must be given
    （否则研究没有约束，求解会退化成无意义的均匀材料分布）。
    """

    study_name: Optional[str] = Field(
        default=None,
        max_length=120,
        description="Target study name; omit to use the active study.",
    )
    goal_type: int = Field(
        default=0,
        ge=0,
        le=2,
        description=(
            "swsTopologyGoalType: 0=MaximizeStiffness, 1=MinimizeMaximumDisplacement, "
            "2=MinimizeMass. ⚠ Goals 0 and 1 **automatically create** a mass constraint; "
            "this tool reuses that one instead of creating a second (a second would make "
            "EndEdit return error 7 = OnlyOneMassConstraintCanBeDefined)."
        ),
    )
    mass_reduce_percent: Optional[float] = Field(
        default=None,
        gt=0.0,
        le=100.0,
        description="Reduce mass by this percentage (75 means 'remove 75%').",
    )
    factor_of_safety: Optional[float] = Field(
        default=None,
        gt=0.0,
        description="Stress must not exceed yield / this factor (official tutorial uses 80).",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.JSON, description="Return format."
    )


# ─────────────────────────────────────────────────────────────────────
# 【第 2 步】工具定义 —— 复制进 server.py 的工具区
# ─────────────────────────────────────────────────────────────────────


@mcp.tool(
    name="solidworks_topology_create_study",
    title="Create SolidWorks Topology Study",
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def solidworks_topology_create_study(
    params: SolidworksTopologyCreateStudyInput,
) -> str:
    """Create a topology optimization study (type 13) on the active single-body part.

    Topology optimization works on **one single-body part at a time** (official CHM).
    A study with the same name is deleted first, matching the official example.
    """

    def op():
        from scripts.sw_topology import create_topology_study

        return create_topology_study(
            params.system,  # 见下方【接入注意】：需按既有工具的取法传 ISldWorks
            params.study_name,
            mesh_type=params.mesh_type,
        )

    return _run_locked(op, params.response_format)


@mcp.tool(
    name="solidworks_topology_set_goal",
    title="Set SolidWorks Topology Goal and Constraints",
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
def solidworks_topology_set_goal(params: SolidworksTopologySetGoalInput) -> str:
    """Set the topology goal plus mass / factor-of-safety constraints on the active study.

    Reuses the mass constraint that goals 0 and 1 create automatically; creating a
    second one makes ``EndEdit`` return error 7 (OnlyOneMassConstraintCanBeDefined).
    """

    def op():
        from scripts.sw_topology import set_topology_goal

        study = _resolve_topology_study(params.study_name)  # 见下方【接入注意】
        return set_topology_goal(
            study,
            goal_type=params.goal_type,
            mass_reduce_percent=params.mass_reduce_percent,
            factor_of_safety=params.factor_of_safety,
        )

    return _run_locked(op, params.response_format)


@mcp.tool(
    name="solidworks_topology_evidence",
    title="Collect SolidWorks Topology Evidence",
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
def solidworks_topology_evidence() -> str:
    """Read back the topology studies and their constraints on the active document.

    Read-only: returns study names, analysis types, and which constraints/controls exist.
    """

    def op():
        from scripts.sw_topology import collect_topology_evidence

        return collect_topology_evidence(_active_sw_app())  # 见下方【接入注意】

    return _run_locked(op, ResponseFormat.JSON)


# ─────────────────────────────────────────────────────────────────────
# 【接入注意】三处需要顺着 server.py 的既有取法补齐（本草稿不臆造）
# ─────────────────────────────────────────────────────────────────────
#
# 1. `params.system` —— 本草稿**没有**这个字段。server.py 里既有的 SolidWorks 工具
#    是怎么拿 `ISldWorks` 实例的（是 `_run_locked` 里注入，还是工具内 `sw_connect.connect_solidworks()`），
#    **照那个写法改**。本草稿不预设，避免写错。
#
# 2. `_resolve_topology_study(study_name)` —— 需要「按名取研究 / 取活动研究」。
#    ⚠ 已核实：`scripts/sw_topology.py` **没有** `get_study_manager`（原文误引，已删）。
#    它有的是 `get_topology_study_manager(study)`（**从已有 study 取管理器**，不是反向）。
#    取研究的入口在 `scripts/sw_simulation.py`（`iter_studies` / `get_study_by_name`）
#    —— 接入时**复用那两个**，不要在本文件新写一份。
#
# 3. `_active_sw_app()` —— 同上，照 server.py 既有取法。
#
# **为什么本草稿不把这些写死**：写死一份猜的取法，接入时若与现有机制不符，
# 会得到一份「看起来完整、实际跑不通」的代码 —— 那比留 TODO 更坏。
# 三处的正确写法在 `server.py` 与 `sw_simulation.py` 里已有先例，接入时照抄即可。
