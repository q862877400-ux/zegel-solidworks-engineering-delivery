"""第二十六批 MCP 工具声明：**仿真载荷包装层** 2 个（砌墙 W7 / Spec Kit `140` · ★★ 护城河）。

## ★★★★ 为什么这是"护城河"—— 而且是**核实过**的
```
★ 四家的**工具名**里跟仿真有关的合计只有 **4 个**，且**全是"建研究 / 跑"**：
    `Eduardof0nt` 3 个（create_motion_study / create_simulation_study / run_simulation）·
    `vespo92` 1 个（vba_simulation_setup）· `Slacker-LLC` **0 个**
    （`andrewbartels1` 那 2 个是**误命中** —— 它的 "load" 指 `load_part` / `load_assembly`）
  ⇒ ★ **没有任何一家挂"载荷 / 约束"** —— 护城河成立。
★ 四家的**测试**里也**没有**仿真载荷的判据（三家用"无"）
  ⇒ ★ 按 `AGENTS.md` §5.0（用户指令）：**找过了，没有 ⇒ 自己搓**。
```

## ★★★★ 而能力层**早就包装好了**（目标里那句「有就直接挂」正是答案）
```
★ `sw_simulation.apply_fixed_restraint(study, *, model=None, restraint_type=0)`
★ `sw_simulation.apply_normal_force(study, magnitude, *, model=None, force_type=1, unit=0)`
  ⇒ ★ **首参是 `study`（不是 raw COM 对象）** ⇒ **已经是包装层** ✓
★ 而且真机**整链已跑通过**（能力清单 `simulation_and_fea` 的文字证据）：
    「赋材料 → 按面坐标选面 → 夹具 → 载荷（**Count == 2**）→ CreateMesh（**7,310 单元**）
      → RunAnalysis（1 秒）→ study.Results 非空、GetPlotCount == 4」
★ 并且**已有可复跑的证据脚本**：`tools/capture_simulation_evidence.py`（205 行，判据三条）
  ⇒ ★★ 本批**不必新写探针/证据** —— 挂上工具、跑那个脚本即可。
```

## ⚠ 「插件不在」这个**假象**（本批差点据此误判，值得记）
```
★ 我用 `win32com.client.Dispatch("SldWorks.Simulation")` 去测"插件在不在" ⇒ 报「找不到指定的模块」
★ 而本项目**早就查清**（事实 141/142）：真因是「**加载项没启用**」，**不是许可** ——
    `LoadAddIn` 的参数是「**Fully qualified file name**」，传 ProgID 当然"找不到"（返回 3 = swFileNotFound）；
    ★ 而**许可错是 7 = swLicenseError**。
⇒ 用**注册表里的真路径** `LoadAddIn("…\\SOLIDWORKS\\Simulation\\cosworks.dll")` ⇒ **0 = swSuccess**。
⇒ ★★ 本批实测：`ensure_simulation_addin(sw_app)` ⇒ **CDispatch** ✓ · `get_cosmosworks(sw_app)` ⇒ **CDispatch** ✓
⇒ ★★★ **教训（与用户纪律同源）：判断"某个东西在不在"之前，先查项目里有没有查过它** ——
   我当时**没先查**，直接搓了个探针，**得出错误结论**。
```

## ★ 包装形状（**第五种**：三种机制**组合**）
```
`apply_fixed_restraint(study, *, model=None, …)` 需要**两个**宿主对象 ⇒ 而 `inject` 只能注一个。
读 `tool_registry` 的组装顺序（L399–432）后确定可以**三者并用**：
    L408-416  `inject`       ⇒ `kwargs[inj] = resolver(params)`
    L419-422  `pre_call`     ⇒ 选择类副作用（**不动 kwargs**）
    L423-432  `derived_args` ⇒ **在 pre_call 之后**往 kwargs 里补（★ 不得覆盖已直传名）
⇒ ★ 所以：
    `inject="study"`（研究）+ `pre_call`（**先选好面**）+ `derived_args`（**补 `model`**）
★ 既有 **8 个**先例已用 `inject` + `derived_args` 组合 ⇒ 这是**既有机制的组合，不新造**。
```

## ★ 参数命名（规则 2）
```
★ `study_name` / `selection` —— 二者都**由解析器消费**（`param_alias` 里标 `None`），
  与既有三个 simulation 工具（`generate_report` / `create_mesh_for_control` /
  `default_element_size_and_tolerance`）**同一写法**。
★ `magnitude_n`：力的大小，★ **单位后缀写进名字**（牛顿）——
  力不是长度、不是角度，规则 2 没规定后缀，但**明确单位**与规则 2 的精神一致。
  ⚠ 能力层的 `unit=0` 对应 `SWS_FORCE_UNITS["n_or_nm"]` ⇒ ★ 说明里写清「牛顿」。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch26.py
# 定位:   「孤立能力暴露」第二十六批 / 砌墙 W7（Spec Kit `140`）· ★★ **护城河域**。
# 官方签名依据: 不适用（只做参数搬运）；被搬运函数的官方依据见 `scripts/sw_simulation.py`
#          与 `scripts/sw_simulation_loads.py` 的来源块（`ICWLoadsAndRestraintsManager.AddRestraint`
#          / `AddForce` 等）。
# 许可:   本仓库 MIT。无第三方代码引入（★ 四家**没有**这一域）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH26"]

_STUDY = (
    'Name of an EXISTING simulation study (e.g. "Study 1" / "算例 1"). '
    "⚠ Leave empty to use the FIRST study in the document — ★ **建算例请用 "
    "`solidworks_simulation_create_study`**（★ 它早就有了）。"
    "⚠★ 2026-10-03（轮 438）**更正**：本行原先写着「solidworks_* has no create-study tool yet」"
    "—— ★★ **那是假的**，而那句假信息**会误导用户以为得手动建算例**。"
)
_SEL = (
    "Declarative FACE selection for the entities the load/restraint applies to: "
    "'__current_selection__' or 'index:<n>' (the n-th face on the body, 0-based). "
    "★ The capability layer writes these into the official DispArray, so the selection "
    "MUST be made before the call — that is what this argument drives."
)


def _consumed(*names: str) -> dict:
    """这些入参由解析器消费，**不传给目标函数**（既有 3 个 simulation 工具同一约定）。"""
    return {n: None for n in names}


def _model():
    """取活动文档（照 `tool_specs_batch4/23.py::_model` 的既有模式）。"""
    from scripts.sw_connect import connect_solidworks

    _sw, model, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    if model is None:
        raise RuntimeError("没有活动文档 —— 请先打开一个零件")
    return model


def _select_face(params):
    """★ **调用目标函数之前**：把 `selection`（声明式）解析成真实选区（`kind="FACE"`）。

    ★ 复用 `sw_selection_spec.resolve_selection` —— 与 `batch4`/`batch23` 同一行逻辑。
    ★ 返回选区计数；选不中时它自己会抛错（不静默）。
    """
    from scripts.sw_selection_spec import resolve_selection

    return resolve_selection(_model(), params.selection, "FACE")


def _derive_model(params):  # noqa: ARG001
    """★ 把活动文档作为 `model=` 补进实参。

    ⚠ 能力层的 docstring 明写：「**给了它才会把选区实体装成官方要求的 `DispArray`**；
      不给则退回旧行为（传 `None`），此时**必然建不出来**」
    ⇒ ★ 所以 `model` **必须**补 —— 这是这两个工具能工作的前提。
    ⚠ `derived_args` **不得覆盖已直传的参数名**（`tool_registry` L424-431 会 `GateError`）；
      而 `model` 没有被任何 `Param` 直传（`study_name`/`selection` 都被 `param_alias` 消费）
      ⇒ ★ 不会冲突。
    """
    return {"model": _model()}


SPECS_BATCH26 = [
    ToolSpec(
        name="solidworks_simulation_apply_fixed_restraint",
        title="Apply a Fixed Restraint (Fixture) to the Selected Faces",
        module="sw_simulation",
        function="apply_fixed_restraint",
        inject="study",
        param_alias=_consumed("study_name", "selection"),
        pre_call=_select_face,
        derived_args=_derive_model,
        params=[
            Param("study_name", str, default="", description=_STUDY),
            Param("selection", str, description=_SEL),
        ],
        evidence=(
            "Apply a FIXED restraint (fixture) to the selected face(s) of a static study and return the ICWRestraint. ★"
            " The faces come from `selection` (declarative) because the capability layer assembles them into the offici"
            "al DispArray. ⚠ Requires the Simulation add-in; the first call loads it automatically."
        ),
        doc="Apply a FIXED restraint (fixture) to the selected face(s) of a static study and "
        "return the ICWRestraint. ★ The faces come from `selection` (declarative) because the "
        "capability layer assembles them into the official DispArray. "
        "⚠ Requires the Simulation add-in; the first call loads it automatically.",
    ),
    ToolSpec(
        name="solidworks_simulation_apply_normal_force",
        title="Apply a Normal Force to the Selected Faces",
        module="sw_simulation",
        function="apply_normal_force",
        inject="study",
        #: ★★ `magnitude_n` → `magnitude`：能力层形参叫 `magnitude`（不带 `_n`），对外名
        #: 带单位后缀
        #:   ⇒ **必须靠 `param_alias` 改名**（W4 的定则）。
        #:   ⚠ 第一版**漏了这一条**，被"走工具路径"的证据脚本当场抓住
        #: （`TypeError: apply_normal_force() got an unexpected keyword argument 'magnit
        #: ude_n'`）
        #:   —— ★ 若证据只直调能力层，这个 bug **永远不会暴露**（能力层本身是对的）。
        param_alias={
            **_consumed("study_name", "selection"),
            "magnitude_n": "magnitude",
        },
        pre_call=_select_face,
        derived_args=_derive_model,
        params=[
            Param("study_name", str, default="", description=_STUDY),
            Param("selection", str, description=_SEL),
            Param(
                "magnitude_n",
                float,
                description="Force magnitude in NEWTONS (the capability "
                "layer uses force unit 0 = n_or_nm).",
            ),
        ],
        evidence=(
            "Apply a NORMAL force to the selected face(s) of a static study and return the ICWForce. ★ The faces come f"
            "rom `selection` (declarative). ⚠ The magnitude is in NEWTONS — it is not converted."
        ),
        doc="Apply a NORMAL force to the selected face(s) of a static study and return the "
        "ICWForce. ★ The faces come from `selection` (declarative). "
        "⚠ The magnitude is in NEWTONS — it is not converted.",
    ),
]
