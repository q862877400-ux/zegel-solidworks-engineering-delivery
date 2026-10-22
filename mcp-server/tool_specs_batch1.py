"""第一批 MCP 工具声明（护城河域 + 模具域 + 只读证据）—— T-011 的开工批次。

## 本批状态（**全部声明式**，不再用 `extra_op`）
2026-10-01：`tool_registry` 加了 `inject`（注入语义建模）⇒ 本批 8 条**全部走
`module`/`function` + `inject`**，没有一条需要 `extra_op`。
**⇒ 这才是评估里说的「~10 行一个工具」。**

## ⚠⚠ 本批暴露出的**真实冲突**（记录在案，供后续批次照办）
`scripts/sw_simulation.py::select_face_at(model, x, y, z, …)` ——
**入参是裸坐标 `x/y/z`，违反「并入六条规则」的规则 3**（「选择用声明式 `selection`，
不写裸坐标」），而规则 3 的门禁就在 `tool_registry.check_spec` 里，**注册时会直接拒掉**。

**⇒ 这不是 bug，而是「内部实现」与「对外表面」的合法差异**：
- **内部**：`SelectByID2("", "FACE", x, y, z, …)` **必须**给一个**面上的点** —— 官方 API 的形状
- **对外**：工具的入参必须是**声明式选择**（「哪个面」），由**工具内部**解析成坐标

**⇒ 判据**：**能直接暴露的只有「入参本身就是声明式」的函数**；
凡内部用坐标/裸索引的函数，暴露时**必须加一层「声明式 → 坐标」的解析**，
且**解析规则要显式写出来**（不能藏在默认值里）。
`select_face_at` 之类**留到有解析层再做**（登记在 T-011 评估的「已发现的阻碍」段）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植）
# 文件:   mcp-server/tool_specs_batch1.py
# 定位:   `docs/T-011-expose-capabilities-assessment.md` 第一批的实现。
#         每条声明的 `module`/`function` 指向 `scripts/` 里**已存在**的函数；
#         参数**逐条照真实签名抄**（守卫测试用 `inspect.signature` 核）。
# 官方签名依据: 不适用（本文件只做参数搬运，不做 COM 调用；
#         被搬运的函数各自的官方依据在其源码的来源块里）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ **尚未接入 `mcp-server/server.py`**（单源原则，已知事实 24）。
#   接入 = `register(mcp, SPECS_BATCH1, …, resolvers=SIM_RESOLVERS)` 一行。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH1", "SIM_RESOLVERS"]

#: ⚠ 参数**逐条照真实签名抄**，签名出处：
#:   `Select-String scripts/sw_topology.py   -Pattern '^def create_topology_study'`
#:   `Select-String scripts/sw_mold.py       -Pattern '^def insert_parting_line'`
#:   `Select-String scripts/sw_simulation.py -Pattern '^def set_material'`
SPECS_BATCH1: list[ToolSpec] = [
    # ── 拓扑（护城河）────────────────────────────────────────────────
    # 签名: def create_topology_study(sw_app, name: str, *, mesh_type: int = 0,
    #                                 delete_existing: bool = True)
    #: ★★★★★★ 2026-10-04（轮 117）**补 `delete_existing`** —— ★ 处置这条**存量失败** ✓
    #:   ★ **真机读数**（★ `tests/test_tool_specs_batch1.py` 逐字）：
    #: 「工具 `solidworks_topology_create_study` 折算后的目标参数 `['mesh_type', 'name']
    #: `
    #:       与 `sw_topology.create_topology_study` 的真实形参
    #:       `['delete_existing', 'mesh_type', 'name']` 不一致」✓
    #:   ★★ **真因**：★ 实现**加了**带默认值的关键字参数 `delete_existing: bool = True`、
    #:     而 **ToolSpec 没跟上** ⇒ ★★★ **⇒ 与「mock 落后」「登记表落后」
    #:     **同一个病**（★ "改了实现、★ 配套的没跟上"）** ✓
    #:   ★★★★ **⇒ 已补**（★ 默认值与实现一致 = `True`）✓
    ToolSpec(
        name="solidworks_topology_create_study",
        title="Create SOLIDWORKS Topology Study",
        module="sw_topology", function="create_topology_study",
        inject="sw_app",
        # ⚠ MCP 表面用 `study_name` 比 `name` 清楚；目标函数形参叫 `name`
        #   ⇒ 用 `param_alias` 显式映射（**别名也是显式的**，不靠猜）。
        param_alias={"study_name": "name"},
        params=[
            Param("study_name", str, default="Topology Study 1",
                  description="Study name; a study with the same name is deleted first."),
            Param("mesh_type", int, default=0,
                  description="swsMeshType: 0=solid, 1=midsurface, 2=surfaces, 3=mixed, 4=beam."),
            #: ★ 新增（★ 与实现同步）：★ 同名研究是否先删掉重建 ✓
            Param("delete_existing", bool, default=True,
                  description="Delete an existing study with the same name before creating "
                              "(★ 与实现默认值一致 = True)。"),
        ],
        doc=("Create a topology optimization study (analysis type 13) on the ACTIVE part. "
             "Topology optimization works on ONE single-body part at a time (official limit). "
             "Returns which entry point was used (CreateNewStudy3, or a fallback)."),
    ),
    # 签名: def collect_topology_evidence(sw_app) -> dict[str, Any]
    ToolSpec(
        name="solidworks_topology_evidence",
        title="Collect SOLIDWORKS Topology Evidence",
        module="sw_topology", function="collect_topology_evidence",
        inject="sw_app",
        params=[],
        read_only=True,
        doc=("Read back the topology studies on the active document: names, analysis types, "
             "and which constraints/controls exist. Read-only."),
    ),
    # 签名: def run_topology_study(study, *, units=0, element_size=0.0, tolerance=0.0)
    # ⚠ element_size / tolerance 单位是**毫米**（真机实测，见 sw_simulation.create_mesh 
    # 来源块）
    ToolSpec(
        name="solidworks_topology_run",
        title="Run SOLIDWORKS Topology Study",
        module="sw_topology", function="run_topology_study",
        inject="study",
        # `study_name` 由**解析器**消费（不进目标函数）⇒ alias 映射到 None 表示「不传」
        param_alias={"study_name": None,
                     "element_size_mm": "element_size",
                     "tolerance_mm": "tolerance"},
        params=[
            Param("study_name", str, default="",
                  description="Target study; omit to use the active study. "
                              "Consumed by the resolver, NOT passed to the function."),
            Param("units", int, default=0,
                  description="swsUnit_e: 0=SI, 1=English, 2=Metric. "
                              "Must be a VALID value (-1 is rejected by the API)."),
            Param("element_size_mm", float, default=0.0,
                  description="Global element size in MILLIMETRES, must be > 0. "
                              "Use solidworks_simulation_default_mesh_size for the official value."),
            Param("tolerance_mm", float, default=0.0,
                  description="Mesh tolerance in MILLIMETRES, must be > 0. "
                              "Official default is 5% of the element size."),
        ],
        doc=("Mesh and solve the topology study and report whether results exist. "
             "A zero RunAnalysis return code does NOT mean success - judge by study results."),
    ),

    # ── 模具（本轮并入的新域）───────────────────────────────────────
    # 签名: def insert_parting_line(model, *, draft_analysis: bool = True)
    ToolSpec(
        name="solidworks_mold_parting_line",
        title="Insert Mold Parting Line",
        module="sw_mold", function="insert_parting_line",
        inject="model",
        params=[
            Param("draft_analysis", bool, default=True,
                  description="The official single parameter. Its exact meaning is UNVERIFIED; "
                              "kept True to match the reference usage."),
        ],
        doc=("Insert a mold parting line. Select the draft-direction reference first "
             "(edge/plane/axis); without it the call inserts nothing."),
    ),
    # 签名: def insert_shut_off_surface(model)
    ToolSpec(
        name="solidworks_mold_shut_off_surface",
        title="Insert Mold Shut-off Surface",
        module="sw_mold", function="insert_shut_off_surface",
        inject="model",
        params=[],
        doc="Auto-create shut-off surfaces over holes for mold separation. Zero parameters.",
    ),
    # 签名: def mold_draft_analysis(model, *, draft_angle_deg, analysis_type=0, colors=N
    # one, option=0)
    ToolSpec(
        name="solidworks_mold_draft_analysis",
        title="Run Mold Draft Analysis",
        module="sw_mold", function="mold_draft_analysis",
        inject="model",
        # ⚠ `colors` 是官方第 3 参（COM `Object`），**故意不暴露** ——
        #   它在 MCP 表面无法表达。**显式声明省略**，否则与「手抄漏了」无法区分。
        omitted_params=("colors",),
        params=[
            Param("draft_angle_deg", float, description="Draft angle in DEGREES."),
            Param("analysis_type", int, default=0,
                  description="Official arg 2 (Int32). Its meaning is UNVERIFIED."),
            Param("option", int, default=0,
                  description="Official arg 4 (Int32). Its meaning is UNVERIFIED."),
        ],
        doc=("Run mold draft analysis. Returns the official return code as-is: that code has "
             "NO published enum, so this tool does NOT judge success from it."),
    ),
    # 签名: def mold_evidence(model) -> dict
    ToolSpec(
        name="solidworks_mold_evidence",
        title="Collect Mold Evidence",
        module="sw_mold", function="mold_evidence",
        inject="model",
        params=[],
        read_only=True,
        doc=("★ **当前这条在真机上**读不到东西**、★ 如实说明** —— "
             "处置 `JUDGE-C_D_E.md` 的 🔴 **#14**（★ `E-1 #9`）："
             "★ 原 doc 逐字写「Read back the mold state of the active part: parting-line/surface "
             "and cavity/core surface counts, parting type, core-cavity split. **Read-only.**」"
             "⇒ ★★ 而**能力层自己的 docstring 逐字**写着"
             "「⚠ **本函数当前仍从旧位置读** ⇒ ★ **它在真机上只会返回全 `None`**」"
             "（★ `scripts/sw_mold.py::mold_evidence`）⇒ ★★★ **两处说法相反** ✓ "
             "★★ **真因（★ 轮 172 真机 + 反射复核）**：★ 那些计数**不在 `IFeatureManager` / "
             "`IModelDoc2` 上**（★ 实测全 `AttributeError: <unknown>.X`），★ 而在 "
             "**`I*FeatureData`** 上（★ `GetPartingLinesCount` ⇒ `IPartingLineFeatureData` · "
             "`PartingType` ⇒ `IPartingSurfaceFeatureData` · `CoreCavitySplit` ⇒ "
             "`IPartingLineFeatureData` —— ★ 事实 36 那一族：**成员在别的接口上**）✓ "
             "★★★ **⇒ 要真读到，必须先拿到对应的 `I*FeatureData`**（★ 从**已存在的**分型线/分型面"
             "特征上取）⇒ ★ **前提是零件上**已经有那些特征**；★ 空零件上**本来就取不到**"
             "（★ **两者表象相同、别混**）✓ "
             "★★★★ **∴ 现在**：★ `read_only=True` 仍然成立（★ 它确实不改模型）· "
             "★★ 但**读到的计数会全是 `None`** ⇒ ★ 请按返回值里的 **`readable`** 字段判"
             "（★ `false` = 本机读不到、★ **不是**「没有分型」）✓"),
    ),

    # ── 仿真：材料（真机修好的那条路）───────────────────────────────
    # 签名: def set_material(model, material_name: str, database: str = SWS_MATERIAL_DAT
    # ABASE) -> str
    # ⚠ 返回的是**回读值**（`MaterialIdName`），空串表示没赋上
    ToolSpec(
        name="solidworks_simulation_set_material",
        title="Set Part Material",
        module="sw_simulation", function="set_material",
        inject="model",
        params=[
            Param("material_name", str,
                  description='Material name inside the library, e.g. "AISI 1020". '
                              '"Plain Carbon Steel" is NOT in that library.'),
            Param("database", str, default="SOLIDWORKS Materials",
                  description="Library DISPLAY name (NOT the .sldmat file name)."),
        ],
        doc=("Assign a material to the active part and RETURN THE READ-BACK MaterialIdName. "
             "An empty string means it did NOT take effect (the API itself returns void)."),
    ),
]


# ── 注入解析器（**由调用方提供** ⇒ `tool_registry` 保持宿主无关）──────
def _sw_app(_params):
    from scripts.sw_connect import connect_solidworks

    sw_app, _model, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    return sw_app


def _active_model(_params):
    from scripts.sw_connect import connect_solidworks

    _sw, model, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    if model is None:
        raise RuntimeError("没有活动文档 —— 请先打开一个零件")
    return model


def _study(params):
    """按 `study_name` 解析研究；为空则取第一个。"""
    from scripts.sw_simulation import get_study_by_name, iter_studies

    sw_app = _sw_app(params)
    name = getattr(params, "study_name", "") or ""
    study = get_study_by_name(sw_app, name) if name else next(iter(iter_studies(sw_app)), None)
    if study is None:
        raise RuntimeError("没找到研究（study_name=%r）" % name)
    return study


#: 注入名 → 解析器。接入 `server.py` 时把它传给 `register(...)`。
SIM_RESOLVERS = {
    "model": _active_model,
    "sw_app": _sw_app,
    "study": _study,
}
