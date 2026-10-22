"""第三十批 MCP 工具声明：**拓扑柜台的读数与参数** 6 个（24h 段 2.2 / Spec Kit `144`）。

## ★★★ 本批补的是**拓扑域剩下的那一半柜台**
```
★ 已有 **10 个**拓扑工具（`create_study` / `run` / `evidence` / 六类 `create_*` 约束控件）
  ⇒ ★ 而**读数与参数**这一组从未上柜：
      · `collect_topology_numbers`               ⇒ ★ 已是 dict ⇒ **直挂**
      · `list_topology_constraints_and_controls`  ⇒ ⚠ 回 **COM 对象** ⇒ 要包装
      · `get_topology_study_manager`             ⇒ ⚠ 回 **COM 对象** ⇒ 要包装
      · `get_topology_study_options`             ⇒ ⚠ 回 **COM 对象** ⇒ 要包装
      · `set_topology_goal`                      ⇒ ⚠ 回 COM 对象，**而它是"设置"** ⇒ 要**回读确认**
      · `set_topology_iteration_options`          ⇒ ⚠ 同上
  ⇒ ★ 本批用的包装函数（已加进 `scripts/sw_topology.py`）：
      `topology_constraints_report` / `topology_manager_report` / `topology_options_report` /
      `set_topology_goal_report` / `set_topology_iteration_options_report`
```

## ★★ 判据（★ 按 `AGENTS.md` §5.0：**先在自家仓库找**）
```
★ `collect_topology_numbers` 的 **`material_mass_plot`** 是**既有证据脚本**的核心判据
  （`tools/capture_topology_evidence.py` 的判据表：「`GetPlotNames` 里出现 `材料质量*`」）
  ⇒ ★ 本批**不重复造**，直接复用那个函数。
★ 「设置生效了吗」的判据 = **前后对照「取到了几个 kind」**
  ⇒ ★ 用本模块**自己的读取入口** `list_topology_constraints_and_controls`（★ 它注释里记着
    一条教训：曾因裸传 `0` 当出参而**永远返回全 None（假通过）**，改用 `out_i4()` 后才是真的）
  ⇒ ★★ 所以本组一律只回**布尔 + 计数**（可 JSON 化，**且"取到了"这件事可断言**）。
```

## ⚠ 本批**不跑求解** ⇒ ★ **没有模态框挂起风险**
```
★ 会弹框的是 `run_topology_study` / `RunAnalysis` 那类（known-facts 174/177）；
  本批全是**读数**与**设参数** ⇒ 可在普通进程跑真机证据。
```

## ★ 参数命名（规则 2）
```
★ `study_name` —— 由解析器消费（`param_alias` 标 `None`），与既有拓扑工具同一约定。
★ `mass_reduce_percent` / `iteration_count` —— ★ 计数与百分比不是长度也不是角度，
  规则 2 没规定后缀；★ 但**名字里带单位/量纲**与规则 2 的精神一致。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch30.py
# 定位:   24h 计划 段 2.2（Spec Kit `144`）—— 拓扑读数与参数 6 个工具。
# 官方依据: `ICWTopologyStudyManager` / `ICWTopologyStudyOptions` 的官方成员
#          （见 `scripts/sw_topology.py` 的来源块）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本批的"设置"类工具**只设参数、不跑求解**。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH30"]

_STUDY = (
    "Name of an EXISTING topology study. ⚠ Leave empty to use the FIRST study in the "
    "document — create one first (solidworks_topology_create_study)."
)
_GOAL = (
    "Topology goal type (swsTopologyGoalType_e). ★ The result is judged by READ-BACK "
    "(how many constraints/controls are still retrievable), not by a return object."
)


def _consumed(*names: str) -> dict:
    """这些入参由解析器消费，**不传给目标函数**（与既有拓扑工具同一约定）。"""
    return {n: None for n in names}


def _spec(name: str, title: str, function: str, doc: str, params: list) -> ToolSpec:
    """★ 本批的共同骨架（★ 六个工具的宿主对象都是 `study` ⇒ 抽出来只留三处差异）。"""
    return ToolSpec(
        name=name,
        title=title,
        module="sw_topology",
        function=function,
        inject="study",
        param_alias=_consumed("study_name"),
        params=params,
        doc=doc,
    )


SPECS_BATCH30 = [
    _spec(
        "solidworks_topology_collect_numbers",
        "Read Topology Study Numbers (Results, Plots, Material-Mass Plot)",
        "collect_topology_numbers",
        "Read the topology study's numbers as a JSON-able dict: results presence, plot count, "
        "plot names, max available steps, and ★ `material_mass_plot` — the CORE criterion of "
        "this capability (the material-mass plot appearing in GetPlotNames). ★ Read-only.",
        [Param("study_name", str, default="", description=_STUDY)],
    ),
    _spec(
        "solidworks_topology_list_constraints",
        "List Which Topology Constraints/Controls Already Exist",
        "topology_constraints_report",
        "Report which constraints and controls already exist on the topology study as "
        "BOOLEANS plus a count (never COM objects). ⚠ This is the READ-BACK the set_* tools "
        "use — a kind is `true` only when it was actually retrieved. ★ Read-only.",
        [Param("study_name", str, default="", description=_STUDY)],
    ),
    _spec(
        "solidworks_topology_manager_report",
        "Read the Topology Study Manager (as a JSON report)",
        "topology_manager_report",
        "Return a JSON-able report about the topology study manager: whether it exists, its "
        "object type, and which constraint/control kinds are retrievable. "
        "★ The COM object itself is never returned.",
        [Param("study_name", str, default="", description=_STUDY)],
    ),
    _spec(
        "solidworks_topology_options_report",
        "Read the Topology Study Options (as a JSON report)",
        "topology_options_report",
        "Return a JSON-able report about the topology study options: whether the options "
        "object exists and its type. ★ The COM object itself is never returned.",
        [Param("study_name", str, default="", description=_STUDY)],
    ),
    _spec(
        "solidworks_topology_set_goal",
        "Set the Topology Study Goal (read-back confirmed)",
        "set_topology_goal_report",
        "Set the topology study goal and return a READ-BACK report comparing the number of "
        "retrievable constraints/controls before and after. "
        "★ `ok` means no exception AND the count did not decrease — never the return object. "
        "⚠ Sets parameters only; it does NOT run the solver.",
        [
            Param("study_name", str, default="", description=_STUDY),
            Param("goal_type", int, default=0, description=_GOAL),
            Param(
                "mass_reduce_percent",
                float,
                default=0.0,
                description="Target mass reduction in percent (e.g. 75 means -75%). "
                "★ 0.0 is a legitimate value (keep the document default).",
            ),
        ],
    ),
    _spec(
        "solidworks_topology_set_iteration_options",
        "Set the Topology Iteration Options (read-back confirmed)",
        "set_topology_iteration_options_report",
        "Set the topology iteration options and return a READ-BACK report comparing the "
        "retrievable constraint/control count before and after. "
        "★ `ok` means no exception AND the count did not decrease. "
        "⚠ Sets parameters only; it does NOT run the solver. "
        "⚠⚠ The option VALUES are intentionally NOT exposed: their enums "
        "(swsTopologyIterationOption_e and the count's valid range) are not verified in this "
        "repo — the capability layer itself says to look them up in the reflection dump. "
        "★ Exposing an invented sentinel would be worse than not exposing the argument, so the "
        "tool only carries `study_name` and reproduces the capability layer's own defaults.",
        [Param("study_name", str, default="", description=_STUDY)],
    ),
]
