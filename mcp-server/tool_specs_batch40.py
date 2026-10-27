"""第四十批 MCP 工具声明：**运动算例 6 个**（24h 段 5 续 / Spec Kit `157`）。

## ★★★★ 为什么这一批是**填真缺口**（★ 事实 210 的处置）
```
★ `motion_study` 是 `verified` 条目 —— ★★ **而它 `mcp_tools` 为空**（★ 那是一条**自相矛盾的账**）。
★ 查下去：`sw_motion` 有 **13 个公开函数**、**0 个工具** ⇒ ★ 而其中 **6 个入参可表达**：
   · `create_motion_study(asm_model, name=None, duration=4.0, study_type=None)`
   · `collect_motion_study_summary(asm_model)`
   · `validate_motion_studies(asm_model, **requirements)`
   · `get_motion_study_manager(asm_model, load_type_library=True)`
   · `ensure_motion_type_library(raise_on_error=False)`（★ **零参**）
   · `validate_motion_study_summary(summary, study_name=None, …)`（★ 吃一个**dict**）
⇒ ★★★ **关键是 `asm_model` 这个 resolver **早就存在**（★ 拓扑那批加的）** ⇒ ★ **直接挂，不用新键** ✓
```

## ⚠ 没挂的 7 个及原因
```
· `add_constant_speed_rotary_motor` / `…_by_cylinders` ⇒ ★ **`solidworks_add_rotary_motor` 工具已存在**
  （★ 那一个覆盖了这条意图）⇒ **不重复挂**
· `calculate_and_play` / `export_motion_study_avi` / `create_avi_parameter` / `configure_avi_parameter`
  ⇒ ★ 要 `motion_study` / `avi_parameter` 宿主对象 ⇒ ★ **需包装** ⇒ 下一批；
  ★★ 且 **动画导出（AVI）在 known-facts 里是 `stitched`**（缺 Motion 加载项）⇒ **不急着挂**
· `motion_member(obj, attr_name, *args)` ⇒ ★ **内部辅助**（不是工具候选，事实 191）
```

## ★ 参数命名（规则 2 / 3）
```
★ `duration` 是**秒**（★ 不是长度、不是角度）⇒ 不带后缀；★ `study_type` 是枚举 ✓
★ `requirements` / `summary` 是**纯 dict** ✓；★ **无裸坐标** ✓
```

## 判据
```
★ `create_motion_study` ⇒ ★ 判"**回一个 study 对象**"（★ 不是"没报错"）；
★ `collect_motion_study_summary` ⇒ 判"回 **dict 且非空**"；
★ `ensure_motion_type_library` ⇒ 判"**不抛异常**"（★ 而它 `raise_on_error=False` 时**只反映能不能**）；
★ `validate_*` ⇒ ★ **它自己就是判据**（回 validation 结果 ⇒ 如实回传）。
★ ⚠ 本批**真机前置**：需要一个**装配体**（★ 运动算例建在装配上）—— 能力层在前置不满足时会报出来。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch40.py
# 定位:   24h 计划 段 5 续（Spec Kit `157`）—— 填 `motion_study` 这条空壳（verified 却
#            0 工具）。
# 官方依据: `IMotionStudyManager` / `IMotionStudy` / `ISimulation` 族
#          （★ 见 `scripts/sw_motion.py` 的来源块）· `swmotionstudy.tlb`（★ Motion 类型库）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本批**不保存文档**（红线）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH40"]


SPECS_BATCH40 = [
    ToolSpec(
        name="solidworks_motion_create_study",
        title="Create a Motion Study on the Active Assembly",
        module="sw_motion",
        function="create_motion_study",
        inject="asm_model",
        params=[
            Param(
                "name",
                str,
                default=None,
                description="Study name (omit for the default).",
            ),
            Param(
                "duration",
                float,
                default=4.0,
                description="Study duration in SECONDS (★ not a length).",
            ),
            Param(
                "study_type",
                int,
                default=None,
                description="Study type enum value (omit for the default).",
            ),
        ],
        evidence=(
            "Create a Motion Study on the active assembly and return it. ★ Needs an ASSEMBLY document — the capability "
            "layer reports it if the active document is not one. ⚠ Does NOT save the document."
        ),
        doc="Create a Motion Study on the active assembly and return it. ★ Needs an ASSEMBLY "
        "document — the capability layer reports it if the active document is not one. "
        "⚠ Does NOT save the document.",
    ),
    ToolSpec(
        name="solidworks_motion_collect_summary",
        title="Collect the Motion Study Summary",
        module="sw_motion",
        function="collect_motion_study_summary",
        inject="asm_model",
        params=[],
        evidence=(
            "Return a JSON-able summary of the assembly's motion studies. ★ Read-only."
        ),
        doc="Return a JSON-able summary of the assembly's motion studies. ★ Read-only.",
    ),
    ToolSpec(
        name="solidworks_motion_validate_studies",
        title="Validate the Motion Studies Against Requirements",
        module="sw_motion",
        function="validate_motion_studies_report",
        inject="asm_model",
        params=[
            Param(
                "study_name", str, default=None, description="Only validate this study."
            ),
            Param(
                "expected_study_type",
                int,
                default=None,
                description="Require this study type.",
            ),
            Param(
                "minimum_duration_seconds",
                float,
                default=None,
                description="Require at least this duration in SECONDS.",
            ),
            Param(
                "minimum_motor_count",
                int,
                default=None,
                description="Require at least this many motors.",
            ),
            Param(
                "require_results",
                bool,
                default=None,
                description="Require computed results.",
            ),
        ],
        evidence=(
            "Validate the motion studies against the given requirements and return the result. ★ Read-only (★ it report"
            "s, it does not fix)."
        ),
        doc="Validate the motion studies against the given requirements and return the result. "
        "★ Read-only (★ it reports, it does not fix).",
    ),
    ToolSpec(
        name="solidworks_motion_study_manager",
        title="Get the Motion Study Manager",
        module="sw_motion",
        function="get_motion_study_manager",
        inject="asm_model",
        params=[
            Param(
                "load_type_library",
                bool,
                default=True,
                description="Load the Motion type library first (★ needed on a fresh session).",
            ),
        ],
        evidence=(
            "Return the assembly's motion study manager (★ the entry point for the rest). ★ Read-only."
        ),
        doc="Return the assembly's motion study manager (★ the entry point for the rest). "
        "★ Read-only.",
    ),
    ToolSpec(
        name="solidworks_motion_ensure_type_library",
        title="Ensure the Motion Type Library Is Loaded",
        module="sw_motion",
        function="ensure_motion_type_library",
        inject=None,
        params=[
            Param(
                "raise_on_error",
                bool,
                default=False,
                description="Raise instead of reporting a boolean when loading fails.",
            ),
        ],
        evidence=(
            "Check (and load) the Motion type library. ★ Zero-argument apart from the flag — use it to find out whether"
            " Motion is usable BEFORE asking for anything else. ★ 动画导出（AVI）在 known-facts 里记为 stitched —— 缺 M"
            "otion 加载项就是那条的原因。"
        ),
        doc="Check (and load) the Motion type library. ★ Zero-argument apart from the flag — "
        "use it to find out whether Motion is usable BEFORE asking for anything else. "
        "★ 动画导出（AVI）在 known-facts 里记为 stitched —— 缺 Motion 加载项就是那条的原因。",
    ),
    ToolSpec(
        name="solidworks_motion_validate_summary",
        title="Validate One Motion Study Summary",
        module="sw_motion",
        function="validate_motion_study_summary",
        inject=None,
        params=[
            Param(
                "summary",
                dict,
                description="A summary dict (★ as returned by solidworks_motion_collect_summary).",
            ),
            Param(
                "study_name", str, default=None, description="Only validate this study."
            ),
            Param(
                "expected_study_type",
                int,
                default=None,
                description="Require this study type.",
            ),
            Param(
                "minimum_duration_seconds",
                float,
                default=None,
                description="Require at least this duration in SECONDS.",
            ),
            Param(
                "minimum_motor_count",
                int,
                default=None,
                description="Require at least this many motors.",
            ),
            Param(
                "require_results",
                bool,
                default=None,
                description="Require computed results.",
            ),
        ],
        evidence=(
            "Validate a motion-study summary dict (★ pure data — no SolidWorks call). ★ Useful to re-check a summary re"
            "corded earlier."
        ),
        doc="Validate a motion-study summary dict (★ pure data — no SolidWorks call). "
        "★ Useful to re-check a summary recorded earlier.",
    ),
]
