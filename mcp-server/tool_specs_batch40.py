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
                description="Study name; omitting it keeps the SolidWorks default name. Defaults to no name.",
            ),
            Param(
                "duration",
                float,
                default=4.0,
                description="Study duration in seconds, not a length. Defaults to 4.0.",
            ),
            Param(
                "study_type",
                int,
                default=None,
                description=(
                    "Motion Study type enum value; when omitted the SolidWorks default type is kept. Defaults to no val"
                    "ue."
                ),
            ),
        ],
        evidence=(
            "Create a Motion Study on the active assembly and return it. ★ Needs an ASSEMBLY document — the capability "
            "layer reports it if the active document is not one. ⚠ Does NOT save the document."
        ),
        doc=(
            "Create a Motion Study on the active assembly and return it. Writes a study into the assembly and does not "
            "save the document; the active document must be an assembly, and a non-assembly is reported rather than gue"
            "ssed."
        ),
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
        doc=(
            "Return a JSON-able summary of every motion study in the assembly: type, duration, motor count and result s"
            "tatus. Read-only; it never modifies a study, and results_out_of_date true means the study must be calculat"
            "ed again."
        ),
    ),
    ToolSpec(
        name="solidworks_motion_validate_studies",
        title="Validate the Motion Studies Against Requirements",
        module="sw_motion",
        function="validate_motion_studies_report",
        inject="asm_model",
        params=[
            Param(
                "study_name", str, default=None, description=(
                                                     "Only validate this study; omitting it validates every available s"
                                                     "tudy. Defaults to no filter."
                                                 )
            ),
            Param(
                "expected_study_type",
                int,
                default=None,
                description="Required study type enum value; omitting it accepts any type. Defaults to no requirement.",
            ),
            Param(
                "minimum_duration_seconds",
                float,
                default=None,
                description="Minimum study duration in seconds. Defaults to no requirement.",
            ),
            Param(
                "minimum_motor_count",
                int,
                default=None,
                description="Minimum number of motors. Defaults to no requirement.",
            ),
            Param(
                "require_results",
                bool,
                default=None,
                description="Whether the study must have computed, non-stale results. Defaults to no requirement.",
            ),
        ],
        evidence=(
            "Validate the motion studies against the given requirements and return the result. ★ Read-only (★ it report"
            "s, it does not fix)."
        ),
        doc=(
            "Validate the motion studies against the given requirements and return the result. Read-only: it reports, i"
            "t does not fix, and the returned asked key lists which requirements were actually applied."
        ),
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
                description=(
                    "Whether to load the Motion type library first, which a fresh session needs. Defaults to true."
                ),
            ),
        ],
        evidence=(
            "Return the assembly's motion study manager (★ the entry point for the rest). ★ Read-only."
        ),
        doc=(
            "Return the Motion Study manager object of the active assembly, the entry point for the other motion tools."
            " Read-only; loading the Motion type library first avoids members that behave like properties instead of me"
            "thods."
        ),
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
                description=(
                    "Whether to raise instead of returning false when the library cannot be found or loaded. Defaults t"
                    "o false."
                ),
            ),
        ],
        evidence=(
            "Check (and load) the Motion type library. ★ Zero-argument apart from the flag — use it to find out whether"
            " Motion is usable BEFORE asking for anything else. ★ 动画导出（AVI）在 known-facts 里记为 stitched —— 缺 M"
            "otion 加载项就是那条的原因。"
        ),
        doc=(
            "Check whether the Motion Study type library is loaded, load it if needed, and return its path. Use it befo"
            "re asking anything else from Motion: without swmotionstudy.tlb the manager members misbehave as properties"
            " instead of methods."
        ),
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
                description="Summary dict as returned by solidworks_motion_collect_summary.",
            ),
            Param(
                "study_name", str, default=None, description=(
                                                     "Only validate this study; omitting it validates every available s"
                                                     "tudy. Defaults to no filter."
                                                 )
            ),
            Param(
                "expected_study_type",
                int,
                default=None,
                description="Required study type enum value; omitting it accepts any type. Defaults to no requirement.",
            ),
            Param(
                "minimum_duration_seconds",
                float,
                default=None,
                description="Minimum study duration in seconds. Defaults to no requirement.",
            ),
            Param(
                "minimum_motor_count",
                int,
                default=None,
                description="Minimum number of motors. Defaults to no requirement.",
            ),
            Param(
                "require_results",
                bool,
                default=None,
                description="Whether the study must have computed, non-stale results. Defaults to no requirement.",
            ),
        ],
        evidence=(
            "Validate a motion-study summary dict (★ pure data — no SolidWorks call). ★ Useful to re-check a summary re"
            "corded earlier."
        ),
        doc=(
            "Validate a motion-study summary dict against delivery requirements and return status, checks and issues. R"
            "ead-only, pure data with no SolidWorks call; it re-checks a summary recorded earlier."
        ),
    ),
]
