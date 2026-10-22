"""第三十七批 MCP 工具声明：**求解器设置 5 个**（24h 段 1 续 / Spec Kit `154`）。

## ★★★★ 为什么**不加新的注入键**（★ 而是包一层）
```
★ 底层 `configure_static_solver(options, …)` / `set_option(options, …)` 要一个 `options` **宿主对象**；
  ★★ 而那个对象**从 study 取**：`study_options_of(study, family)`
  ⇒ ★★★ **而 `inject="study"` 早就存在**（`resolve_study`）
  ⇒ ★★★★ **所以正解 = 注入 `study` + 包装内部先取 options** —— ★ **不需要动 `RESOLVERS`**。
★ 与孔族（`*_at_selection`，轮 268）**同一手法**：★ 用**已有 resolver + 包装**表达新工具。
```

## ★ 参数命名（规则 2 / 3）
```
★ 长度参数带 `_mm`（★ 本批的求解器选项里没有长度）；★ **无裸坐标** ✓
★ `family` / `name` 是**登记表里的族名与选项名**（★ 不是长度、不是角度）⇒ 不带后缀。
★ ⚠ `configure_*_solver_report` 用 `**kwargs` ⇒ ★ **选项名由登记表定**（★ 见
  `solidworks_simulation_list_setter_summary` 的族清单 —— ★ 那正是"会列合法值"的入口）。
```

## 判据
```
★ 三层：① **取 options 成功**（★ 失败则如实报，含 `family`）；② **底层返回值如实回传**；
③ ★ **把"用了哪个族 / 改了什么"记在返回里**（★ 便于下一步回读核对）。
★ `set_option` 对**未登记的族名/选项名**抛 `KeyError`（★ 不静默忽略）⇒ 包装如实回传。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch37.py
# 定位:   24h 计划 段 1 续（Spec Kit `154`）—— 求解器设置 5 个。
# 官方依据: `ICWStaticStudyOptions` / `ICWFrequencyStudyOptions` / `ICWBucklingStudyOpti
#           ons`
#          （★ 见 `scripts/sw_simulation_study_options.py` 的 `STUDY_OPTIONS_ACCESSORS`）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本批**不保存文档**（红线）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH37"]

_FAM = (
    "Study-options family name (★ discover valid families/names with "
    "solidworks_simulation_list_setter_summary)."
)


SPECS_BATCH37 = [
    ToolSpec(
        name="solidworks_simulation_configure_static_solver",
        title="Configure the Static Solver Options",
        module="sw_simulation_study_options",
        function="configure_static_solver_report",
        inject="study",
        params=[
            Param("family", str, default="ICWStaticStudyOptions", description=_FAM),
            Param(
                "free_body_force",
                bool,
                default=None,
                description="Use the free-body-force approach (omit = leave unchanged).",
            ),
            Param(
                "contact_penalty",
                float,
                default=None,
                description="Contact penalty stiffness (omit = leave unchanged).",
            ),
            Param(
                "reference_pressure",
                float,
                default=None,
                description="Reference pressure (omit = leave unchanged).",
            ),
        ],
        doc="Configure the static solver options of the injected study and return a report. "
        "⚠ Only the non-None options are applied. Does NOT save the document.",
    ),
    ToolSpec(
        name="solidworks_simulation_configure_frequency_solver",
        title="Configure the Frequency Solver Options",
        module="sw_simulation_study_options",
        function="configure_frequency_solver_report",
        inject="study",
        params=[
            Param("family", str, default="ICWFrequencyStudyOptions", description=_FAM),
            Param(
                "decouple",
                bool,
                default=None,
                description="Decouple (omit = unchanged).",
            ),
            Param(
                "reference_pressure",
                float,
                default=None,
                description="Reference pressure (omit = unchanged).",
            ),
        ],
        doc="Configure the frequency solver options of the injected study. "
        "⚠ Only the non-None options are applied.",
    ),
    ToolSpec(
        name="solidworks_simulation_configure_buckling_solver",
        title="Configure the Buckling Solver Options",
        module="sw_simulation_study_options",
        function="configure_buckling_solver_report",
        inject="study",
        params=[
            Param("family", str, default="ICWBucklingStudyOptions", description=_FAM),
            Param(
                "modes",
                int,
                default=None,
                description="Number of modes (omit = unchanged).",
            ),
            Param(
                "positive_only",
                bool,
                default=None,
                description="Only positive eigenvalues (omit = unchanged).",
            ),
        ],
        doc="Configure the buckling solver options of the injected study. "
        "⚠ Only the non-None options are applied.",
    ),
    ToolSpec(
        name="solidworks_simulation_set_study_option",
        title="Set One Registered Study Option",
        module="sw_simulation_study_options",
        function="set_study_option_report",
        inject="study",
        params=[
            Param("family", str, description=_FAM),
            Param(
                "name",
                str,
                description="The setter name (★ must exist in the registry).",
            ),
            Param(
                "value",
                str,
                description="The value as TEXT (★ the registry decides the type).",
            ),
        ],
        doc="Set one study option by its registered family/name and return a report. "
        '★★ **未知的 family/name 会返回 `{"ok": false, "error": …}` —— 不抛异常**'
        "（2026-10-04 更正，★ 处置 JUDGE-C_D_E 🔴 #3 · E-3 #6）。"
        "★ 旧描述（已作废）：「Unknown family/name **raises** instead of being silently ignored.」——"
        "★ 那半句「**不静默忽略**」成立、「**raises**」不成立：包装层用 `except Exception` 把 "
        "`KeyError` 捕获并回成结构化失败（★ 那是**更好**的行为 —— 失败可见且带原因，"
        "而 MCP 层不该把异常当正常返回）。"
        "⇒ ★ 判据：★ **`ok` 为假且有 `error` 字段** ⇒ 未登记的名字**一定看得见**，只是**以返回值而非异常的形式**。",
    ),
    ToolSpec(
        name="solidworks_simulation_set_study_options",
        title="Set Several Registered Study Options at Once",
        module="sw_simulation_study_options",
        function="set_study_options_report",
        inject="study",
        params=[
            Param("family", str, description=_FAM),
            Param(
                "values",
                dict,
                description="Mapping of setter name → value (★ each must be registered).",
            ),
        ],
        doc="Set several study options and return the read-back dict. "
        '★★ **未知的 family/name 会返回 `{"ok": false, "error": …}` —— 不抛异常**'
        "（2026-10-04 更正，★ 处置 JUDGE-C_D_E 🔴 #3 · E-3 #6）。"
        "★ 旧描述（已作废）：「Unknown family/name **raises** instead of being silently ignored.」——"
        "★ 同上：★「**不静默忽略**」成立、「**raises**」不成立（★ 异常被包装成结构化失败）✓",
    ),
]
