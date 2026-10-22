# ── 200 轮计划 v3 · 段 1：**B 组第一条**（刚性连接件）─────────────────────────────────
# ─
# ★★★★ 2026-10-03（轮 425）★ 来源：**事实 336 / 337 / 338 / 339** —— 而这是那条链的**终
# 点**。
#
# ★★ **它为什么以前建不成**（★ 五次尝试、两个真因，★ 逐条都留了证据）：
#   ```
#   ① ★ **读选区只拿得到第一个实体**（事实 336/337）：
#      ★ `ISelectionMgr` 上"按序号取对象"那一族**只回得到第 1 个**
#        （`GetSelectedObject6`/`4`/`5`/`GetSelectedObjectsFace` **五个入口都试过**），
#      而 `GetSelectedObjectCount2(-1)` **如实报 2** ⇒ ★★ 传**不完整的数组**
#        ⇒ SW 内部越界 ⇒ **RPC 服务器不可用**（`0x800706BA`/`BE`）。
#   ② ★ **它要在两个体上才建得出来**（事实 338）：
#      ★ 单体零件上它**成功返回却不建**（★ 计数 `0→0`、★ 无错误）—— ★ 而那是**应然的**：
#      同族形参名写着 `DispArrayComp1`/`DispArrayComp2` ⇒ ★ **连接件连的是两个东西** ✓
#   ```
# ★★ **正解**：★ **不读选区** —— 用 `entities_as_array`（由**序号**取对象）自己装两组；
#   ★ 而**体号两侧可分别指定** ⇒ ★ 双体零件上能连 ✓
#   ★★ 真机（`tools/prove_rigid_twobody.py`，★ 无弹窗）：`count = **[0, 1]**` ✓
#
# ★★★★ **2026-10-03（轮 432）本文件的一处修正**（★ 由 pytest 的收集期门禁抓到）：
#   ★ 原先它复用 `tool_specs_batch29._spec`，★ 而那个骨架**写死了**
#     `param_alias=_consumed("study_name", "selection")` **且**挂了 `pre_call=_select_face`
#     （★ 即"先选一个面"）。
#   ⇒ ★★ 而**本工具两样都不该有**：★ 它**不读选区**（自己按序号装数组）⇒
#     - `param_alias` 只该声明 `study_name`（★ 不含 `selection`）
#     - **不该有 `pre_call`**（★ 那会去读一个本工具没有的 `selection` 参数）
#   ⇒ ★ **故本文件改为直接声明 `ToolSpec`**（★ 而不再借 batch29 的骨架）✓
# ⚠ 那条违反是 `tool_registry` 的门禁报的：★「param_alias 指向未声明的参数 `selection`」
# ——
# ★★ 而**它在 pytest 收集期就报**，★ 故**只跑 `release_check` 抓不到它**（★ 见事实 346）
# 。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch61.py —— 本文件
# 定位:   把 `apply_rigid_connector_by_objects_report` 挂成 MCP 工具。
# 官方依据: 出厂类型库（`SolidWorks.Interop.cosworks.dll` **34.4.1.1011**）反射出的形参
#           名
#   `AddRigidConnector(PersistIDFaceArray, PersistIDTargetArray, ByRef ErrorCode)` ·
#   `IBody2.GetFaces` · `swsAnalysisStudyTypeStatic = 0`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec

#: ★★ 复用 batch29 的**两个**助手（★ 而**不用**它的 `_spec` 骨架 —— ★ 那个骨架带 `select
#: ion` 契约）
from tool_specs_batch29 import _STUDY, _consumed, _derive_model

SPECS_BATCH61 = [
    # 签名: apply_rigid_connector_by_objects_report(manager, model, source_indices, targ
    # et_indices,
    #                                                *, kind="FACE", source_body_index=0, target_body_index=0)
    ToolSpec(
        name="solidworks_simulation_apply_rigid_connector",
        title="Apply a Rigid Connector",
        module="sw_simulation_loads",
        function="apply_rigid_connector_by_objects_report",
        inject="manager",
        #: ★★ 只声明 `study_name` 被消费 —— ★ **不含 `selection`**（★ 本工具不读选区）
        param_alias=_consumed("study_name"),
        #: ★★ **没有 `pre_call`** —— ★ 本工具**不读选区**，★ 它自己按序号把两组实体装好
        derived_args=_derive_model,
        params=[
            Param("study_name", str, default="", description=_STUDY),
            Param(
                "source_indices",
                list,
                description="源侧要取的实体**序号**（★ **0 基**，★ 一个列表）",
            ),
            Param(
                "target_indices",
                list,
                description="目标侧要取的实体**序号**（★ **0 基**，★ 一个列表）",
            ),
            Param(
                "kind",
                str,
                default="FACE",
                description="实体种类：`FACE` / `EDGE` / `VERTEX`（★ 两侧同一类）",
            ),
            Param(
                "source_body_index",
                int,
                default=0,
                description="源侧取第几个**体**（★ 0 基）—— ★ **要与目标侧不同**",
            ),
            Param(
                "target_body_index",
                int,
                default=0,
                description="目标侧取第几个**体**（★ 0 基）",
            ),
        ],
        doc=(
            "Add a **RIGID CONNECTOR** between two bodies and return a READ-BACK report. "
            "★★ **本工具不读选区** —— 它自己按**序号**把两组实体装好（`entities_as_array`）。"
            "⚠★ **它要在「两个体」上才建得出来**："
            "★ 在**单体零件**上会**成功返回但不建**（计数不涨、也不报错）—— ★ 那是**应然的**"
            "（同族形参名写着 `Comp1`/`Comp2` ⇒ **连接件连的是两个东西**）。"
            "★ 所以请**两侧体号指向不同的体**（多体零件即用；装配体属另一条链）。"
            "★ `ok` 的判据是**回读**：载荷计数**恰好 +1**，★ **不是**返回值。"
        ),
    ),
]
