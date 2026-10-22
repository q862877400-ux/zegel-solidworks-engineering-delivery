"""第二十九批 MCP 工具声明：**仿真载荷族（四类常用载荷）** 4 个（24h 段 2.1 / Spec Kit `143`）。

## ★★★ 本批补的是**广度**：W7 只挂了两个（夹具 + 法向力），这里把**其余常用载荷**补齐
```
★ 能力层早已有（`scripts/sw_simulation_loads.py`，来源是 `ICWLoadsAndRestraintsManager` 的官方成员）：
    · `AddPressure`            ⇒ `add_pressure`
    · `AddForce(swsForceTypeTorque, …)` ⇒ `add_torque`
    · `AddGravity`             ⇒ `add_gravity`
    · `AddCentriFugalForce`    ⇒ `add_centrifugal_force`
  ⇒ ★ **但四个都回 COM 对象** ⇒ MCP 回不了 ⇒ 本批给每个补一个**回读报告**包装（能力层已加）：
      `apply_pressure_report` / `apply_torque_report` /
      `apply_gravity_report`  / `apply_centrifugal_force_report`
```

## ★★★★ 判据（★ 按 `AGENTS.md` §5.0：**先在自家仓库找**，找到就照用）
```
★ 来源：`tools/capture_simulation_loads_evidence.py` 的判据表（**本项目自己写的**）：
    「夹具 / 载荷 | **选区计数 = 1** 且 `LoadsAndRestraintsManager.Count == 2`」
⇒ ★ 包装函数据此**回读 `Count` 的前后差**：`ok = (count_after == count_before + 1)`
  ⇒ ★★ **不看返回对象**（本项目铁律：**COM 返回值凡不能自证，一律以回读为判据**）。
★ 四家开源项目的**测试里没有**载荷判据（W7 已核实）⇒ ★ **找过了，没有** ⇒ 自己搓（★ 已说明）。
```

## ★ 包装形状（**第六种**：`inject` 用**新加的解析键** `manager`）
```
★ 这批函数的首参叫 **`manager`**（`ICWLoadsAndRestraintsManager`），**不是** `study`
  ⇒ ★ 而**注入名只能是 `RESOLVERS` 的键**（known-facts 169 的机制）
⇒ ★ 正解 = **给 `RESOLVERS` 加一行 `"manager": resolve_manager`** —— ★ **那张表就是为这件事设计的**
  （W6 给 `asm_model` 加一行的同一个手法）。
★ 三件套仍然并用（W7 的既有组合）：
    `inject="manager"`（载荷管理器）+ `pre_call`（**先把 `selection` 选成真实选区**）
    + `derived_args`（**补 `model`** —— 能力层靠它把选区装成官方 `DispArray`）
★ ⚠ `derived_args` **不得覆盖已直传的参数名** ⇒ 本批补的 `model` 没被任何 `Param` 直传 ✓
```

## ⚠ 本批**不调** `RunAnalysis` ⇒ ★ **没有模态框挂起风险**
```
★ 这批只**建载荷**（`CreateMesh` / `RunAnalysis` 才是会弹框的两步，见 known-facts 174/177）。
⇒ ★ 所以本批可以对**普通进程**跑真机证据，不需要 `sw_isolate`。
```

## ★ 参数命名（规则 2）
```
★ `study_name` / `selection` —— 两者都由解析器消费（`param_alias` 标 `None`），与既有
  simulation 工具同一约定。
★ `pressure_type` —— 官方 `swsPressureType_e` 的取值（★ 能力层 `SWS_PRESSURE_TYPES` 有对照表）。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch29.py
# 定位:   24h 计划 段 2.1（Spec Kit `143`）—— 载荷族广度 4 个工具。
# 官方依据: `ICWLoadsAndRestraintsManager.AddPressure` / `AddForce` / `AddGravity` /
#          `AddCentriFugalForce`（`scripts/sw_simulation_loads.py` 的来源块）
# 许可:   本仓库 MIT。
# ⚠ 需要 Simulation 加载项；首次调用会自动 `LoadAddIn`。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH29"]

_STUDY = (
    'Name of an EXISTING simulation study (e.g. "Study 1" / "算例 1"). '
    "⚠ Leave empty to use the FIRST study in the document."
)
_SEL = (
    "Declarative face/entity selection the load applies to: '__current_selection__' "
    "or 'index:<n>' (the n-th face on the body, 0-based). ★ The faces are assembled into "
    "the official DispArray by the capability layer, so the selection is made before the call."
)
_PTYPE = (
    "Pressure type: swsPressureType_e (0 = normal to each face, 1 = use reference "
    "geometry). ★ The result is judged by read-back, not by a return object."
)


def _consumed(*names: str) -> dict:
    """这些入参由解析器消费，**不传给目标函数**（与既有 simulation 工具同一约定）。"""
    return {n: None for n in names}


def _model():
    """取活动文档（照 `tool_specs_batch26.py::_model` 的既有模式）。"""
    from scripts.sw_connect import connect_solidworks

    _sw, model, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    if model is None:
        raise RuntimeError("没有活动文档 —— 请先打开一个零件")
    return model


def _select_face(params):
    """★ **调用目标函数之前**：把 `selection`（声明式）解析成真实选区（`kind="FACE"`）。"""
    from scripts.sw_selection_spec import resolve_selection

    return resolve_selection(_model(), params.selection, "FACE")


def _derive_model(params):  # noqa: ARG001
    """★ 把活动文档作为 `model=` 补进实参（能力层靠它把选区装成官方 `DispArray`）。"""
    return {"model": _model()}


def _spec(name: str, title: str, function: str, doc: str, params: list) -> ToolSpec:
    """★ 四个载荷的**共同骨架**（★ 抽出来是为了让四处差异只剩 `name` / `function` / `doc`）。"""
    return ToolSpec(
        name=name,
        title=title,
        module="sw_simulation_loads",
        function=function,
        inject="manager",
        param_alias=_consumed("study_name", "selection"),
        pre_call=_select_face,
        derived_args=_derive_model,
        params=params,
        doc=doc,
    )


SPECS_BATCH29 = [
    _spec(
        "solidworks_simulation_apply_pressure",
        "Apply a Pressure Load to the Selected Faces",
        "apply_pressure_report",
        "Apply a PRESSURE load to the selected face(s) of a static study and return a "
        "READ-BACK report (`count_before` / `count_after`), not a COM object. "
        "★ `ok` means the load/restraint count went up by exactly one — the criterion is "
        "read-back, never the return value. "
        "⚠ Requires the Simulation add-in; the first call loads it automatically.",
        [
            Param("study_name", str, default="", description=_STUDY),
            Param("selection", str, description=_SEL),
            Param("pressure_type", int, default=0, description=_PTYPE),
        ],
    ),
    _spec(
        "solidworks_simulation_apply_torque",
        "Apply a Torque Load to the Selected Faces",
        "apply_torque_report",
        "Apply a TORQUE load (`AddForce` with swsForceTypeTorque) to the selected face(s) of a "
        "static study and return a READ-BACK report (`count_before` / `count_after`). "
        "★ The result is judged by read-back, not by a return object. "
        "⚠ Requires the Simulation add-in.",
        [
            Param("study_name", str, default="", description=_STUDY),
            Param("selection", str, description=_SEL),
        ],
    ),
    _spec(
        "solidworks_simulation_apply_gravity",
        "Apply a Gravity Load to the Selected Entity",
        "apply_gravity_report",
        "Apply a GRAVITY load to the selected entity of a static study and return a READ-BACK "
        "report. ⚠ The official parameter is a SINGLE entity (DispEntity), so only the FIRST "
        "entity of the selection is used. ★ Judged by read-back, not by a return object.",
        [
            Param("study_name", str, default="", description=_STUDY),
            Param("selection", str, description=_SEL),
        ],
    ),
    _spec(
        "solidworks_simulation_apply_centrifugal_force",
        "Apply a Centrifugal Force to the Selected Entity",
        "apply_centrifugal_force_report",
        "Apply a CENTRIFUGAL FORCE to the selected entity of a static study and return a "
        "READ-BACK report. ⚠ The official parameter is a SINGLE entity, so only the FIRST "
        "entity of the selection is used. ★ Judged by read-back, not by a return object.",
        [
            Param("study_name", str, default="", description=_STUDY),
            Param("selection", str, description=_SEL),
        ],
    ),
]
