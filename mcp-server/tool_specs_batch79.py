"""★ 批次 79：**FR-008 的两半** —— 装配爆炸视图 9 个 + 宏/VBA 8 个（★ 规格 204 的 T-1）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其源码里）
# 文件:   `scripts/sw_assembly_doc.py`（★ 本批新增的 9 个爆炸视图包装，官方依据见该段来
# 源块）
#         `scripts/sw_macro.py`（★ 新建：`ISldWorks.RunMacro2` + `swRunMacroOption_e` /
#          `swRunMacroError_e` 两枚举）
#         `scripts/sw_macro_guard.py`（既有：宏文本的生成 / 校验 / 落盘，**不执行**）
# 定位:   ★★★ 规格 `specs/202-user-coverage-gaps/spec.md` **FR-008** 逐字：
#         「装配**爆炸视图**与**宏/VBA 执行** MUST 可用」⇒ ★ 本批就是它的落地。
#         ★ 实测（2026-10-04）：`capabilities.yaml` 里搜 `Explode` / `RunMacro` = **0 命中**
#         ⇒ 两块此前**完全空白** ✓
# 官方依据: `C:\\swapi\\types\\IAssemblyDoc\\{CreateExplodedView,AutoExplode,ViewExplode
#           Assembly,ViewCollapseAssembly,ShowExploded2,GetExplodedViewNames2,GetExplode
#           dViewCount2,GetExplodedViewConfigurationName,EditExplodeParameters}.md`（★
#           逐页读过）· `C:\\swapi\\types\\ISldWorks\\RunMacro2.md` · `C:\\swapi\\enums\
#           \swRunMacro{Option,Error}_e.md`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **17 个工具**（★ 9 + 8）—— 起点 296 ⇒ 本批后 313（SC-001 的第一段）
# ★ 本批与既有工具**不重叠**（SC-004）：既有 296 个里没有一个爆炸视图或宏**执行**工具；
# ★ 唯一的相邻者 `solidworks_macro_*` 类**不存在**（`sw_macro_guard` 的 9 个公开函数此前
# **一个都没挂**）✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH79"]

#: ★ 与既有多批同形：`asm_model` 走 `RESOLVERS["asm_model"]`（★ 解析成活动文档；装配也是
#:  IModelDoc2）
_ASM = "The ACTIVE assembly document (resolved for you; assembly docs are IModelDoc2 as well)."
_CFG = (
    "Configuration name to inspect. ★ Official signature takes the configuration name "
    "(`GetExplodedViewNames2(String ConfigurationName)`), not an index."
)

SPECS_BATCH79 = [
    # ── ① 爆炸视图（9 个 · FR-008 上半）────────────────────────────────────
    ToolSpec(
        name="solidworks_assembly_create_exploded_view",
        title="Create an Exploded View (IAssemblyDoc.CreateExplodedView)",
        module="sw_assembly_doc",
        function="create_exploded_view",
        inject="doc",
        params=[],
        evidence=(
            "Create an explode view of the active assembly configuration (official `System.bool CreateExplodedView()`, "
            "**zero arguments**). ★ Official Remarks: call it MULTIPLE times to add multiple explode views to the same "
            "configuration; and \"Perfect explode views often require user interaction\" — it does its best from the CU"
            "RRENT MATE CONDITIONS. ⚠ Judged by the returned bool, but do NOT trust that alone: read back with `solidwo"
            "rks_assembly_get_exploded_view_count` (this repo's rule: read-back proves it)."
        ),
        doc=(
            "Create an explode view of the active assembly configuration from the current mate conditions. It writes on"
            "e view into the document and does not save it; call it repeatedly to add several views to the same configu"
            "ration. Read solidworks_assembly_get_exploded_view_count back to prove the create happened, because a perf"
            "ect result often needs user interaction."
        ),
    ),
    ToolSpec(
        name="solidworks_assembly_auto_explode",
        title="Automatically Explode the Assembly (IAssemblyDoc.AutoExplode)",
        module="sw_assembly_doc",
        function="auto_explode",
        inject="doc",
        params=[],
        evidence=(
            "Automatically generate an exploded view of the current configuration (official `System.bool AutoExplode()`"
            ", zero arguments). ★ Official Remarks: it creates only ONE exploded view per configuration — for several, "
            "use `solidworks_assembly_create_exploded_view`."
        ),
        doc=(
            "Create one exploded view automatically for the current configuration. It creates only one view per configu"
            "ration, so use solidworks_assembly_create_exploded_view when you need more. It writes the view into the as"
            "sembly and does not save the document."
        ),
    ),
    ToolSpec(
        name="solidworks_assembly_view_explode",
        title="Show the Exploded State (IAssemblyDoc.ViewExplodeAssembly)",
        module="sw_assembly_doc",
        function="view_explode_assembly",
        inject="doc",
        params=[],
        evidence=(
            "Explode the selected exploded view in the display (official `void ViewExplodeAssembly()`, zero arguments)."
            " ★ Official Remarks: pair it with `solidworks_assembly_view_collapse` to TOGGLE the display."
        ),
        doc=(
            "Explode the selected exploded view in the display without changing any geometry. Pair it with solidworks_a"
            "ssembly_view_collapse to toggle the display back; it changes no geometry and does not save the document."
        ),
    ),
    ToolSpec(
        name="solidworks_assembly_view_collapse",
        title="Show the Collapsed State (IAssemblyDoc.ViewCollapseAssembly)",
        module="sw_assembly_doc",
        function="view_collapse_assembly",
        inject="doc",
        params=[],
        evidence=(
            "Collapse the display back (official `void ViewCollapseAssembly()`, zero arguments). ★ The pair of `solidwo"
            "rks_assembly_view_explode` (official Remarks name them together)."
        ),
        doc=(
            "Collapse the displayed exploded view back to its assembled position without changing geometry. Pair it wit"
            "h solidworks_assembly_view_explode to toggle the display; it changes no geometry and does not save the doc"
            "ument."
        ),
    ),
    ToolSpec(
        name="solidworks_assembly_show_exploded",
        title="Show/Hide a Named Exploded View (IAssemblyDoc.ShowExploded2)",
        module="sw_assembly_doc",
        function="show_exploded",
        inject="doc",
        param_alias={"explode_view_name": "explode_view_name"},
        params=[
            Param(
                "show_it",
                bool,
                description="Whether to show the view exploded: true shows it exploded and false shows it collapsed.",
            ),
            Param(
                "explode_view_name",
                str,
                description=(
                    "Name of the exploded view to show, taken from solidworks_assembly_get_exploded_view_names."
                ),
            ),
        ],
        evidence=(
            "Display the named exploded view (official `System.bool ShowExploded2(Boolean ShowIt, String ExplodeViewNam"
            "e)` — **two arguments**, and note the trailing `2`)."
        ),
        doc=(
            "Display one named exploded view in the exploded or collapsed position. It changes only the display, change"
            "s no geometry and does not save the document; take the view name from solidworks_assembly_get_exploded_vie"
            "w_names."
        ),
    ),
    ToolSpec(
        name="solidworks_assembly_get_exploded_view_names",
        title="List the Exploded View Names of a Configuration (GetExplodedViewNames2)",
        module="sw_assembly_doc",
        function="get_exploded_view_names",
        inject="doc",
        params=[Param("configuration_name", str, description=(
                                                     "Configuration name to inspect; this takes a configuration name, n"
                                                     "ot an index."
                                                 ))],
        evidence=(
            "Return the exploded-view NAMES of a configuration as a list of strings (official `System.object GetExplode"
            "dViewNames2(String ConfigurationName)`). ★ `None` comes back as an EMPTY LIST here — never as \"one namele"
            "ss view\"."
        ),
        doc=(
            "List the exploded-view names of one configuration as strings. Read-only; a missing result comes back as an"
            " empty list, never as one nameless view."
        ),
    ),
    ToolSpec(
        name="solidworks_assembly_get_exploded_view_count",
        title="Count the Exploded Views of a Configuration (GetExplodedViewCount2)",
        module="sw_assembly_doc",
        function="get_exploded_view_count",
        inject="doc",
        params=[Param("configuration_name", str, description=(
                                                     "Configuration name to inspect; this takes a configuration name, n"
                                                     "ot an index."
                                                 ))],
        evidence=(
            "Return the number of exploded views in a configuration (official `System.int GetExplodedViewCount2(String "
            "ConfigurationName)`). ★ This is the READ-BACK that proves a create actually happened."
        ),
        doc=(
            "Get the number of exploded views in one configuration as an integer. Read-only; it is the read-back that p"
            "roves a create really happened."
        ),
    ),
    ToolSpec(
        name="solidworks_assembly_exploded_view_configuration",
        title="Read GetExplodedViewConfigurationName (argument semantics UNVERIFIED)",
        module="sw_assembly_doc",
        function="get_exploded_view_configuration_name",
        inject="doc",
        param_alias={"arg": "arg"},
        params=[
            Param(
                "arg",
                str,
                description=(
                    "Passed through unchanged; the official page documents no meaning for it, so do not read it as an i"
                    "ndex or as a name."
                ),
            )
        ],
        evidence=(
            "Thin wrapper over `IAssemblyDoc.GetExplodedViewConfigurationName` (one argument). ⚠ **The meaning of that "
            "argument is not documented** on the official page — passed through as-is, and the returned value is echoed"
            " with no interpretation."
        ),
        doc=(
            "Get the configuration name behind an exploded view by passing the argument through unchanged. Read-only; t"
            "he official parameter has no documented meaning, so supply the value the official page requires and read t"
            "he echoed string without interpreting it."
        ),
    ),
    ToolSpec(
        name="solidworks_assembly_edit_explode_parameters",
        title="Open the Explode Parameter Editor (IAssemblyDoc.EditExplodeParameters)",
        module="sw_assembly_doc",
        function="edit_explode_parameters",
        inject="doc",
        params=[],
        evidence=(
            "Call `IAssemblyDoc.EditExplodeParameters` (zero arguments). ⚠ The official page carries NO Remarks, so whe"
            "ther it opens an INTERACTIVE dialog is NOT determined here — run it through the dialog guard (`python tool"
            "s/sw_guard.py --timeout N -- python <script>`) as the repo requires."
        ),
        doc=(
            "Open the explode-parameter editing step of the active assembly. It takes no arguments and modifies the exp"
            "lode parameters; whether it raises an interactive dialog is not determined, so drive it through the repo d"
            "ialog guard."
        ),
    ),
    # ── ② 宏 / VBA（8 个 · FR-008 下半）──────────────────────────────────
    ToolSpec(
        name="solidworks_macro_run",
        title="Run a Macro File (ISldWorks.RunMacro2)",
        module="sw_macro",
        function="run_macro",
        inject="sw_app",
        params=[
            Param(
                "file_path",
                str,
                description="Absolute path of the macro project file, for example a .swp or .swb file.",
            ),
            Param(
                "module_name",
                str,
                description=(
                    "Module name inside the macro; for a VBA .swp this is the VBA module name, and VSTA .swb semantics "
                    "are not determined."
                ),
            ),
            Param("procedure_name", str, description="Procedure name to run, for example main."),
            Param(
                "options",
                int,
                default=0,
                description="Run-macro option: 0=swRunMacroDefault, 1=swRunMacroUnloadAfterRun. Defaults to 0.",
            ),
        ],
        evidence=(
            "Run a macro from a project file (official `System.bool RunMacro2(String FilePathName, String ModuleName, S"
            "tring ProcedureName, Int32 Options, out Int32 Error)` — **4 in + 1 out**). ★ Returns `{ok, return_value, e"
            "rror_code, error_name, file, file_exists, module, procedure, options}`. ★★ The out-parameter is the useful"
            " part: `error_name` maps the code through `swRunMacroError_e` (all 28 members; official page and factory r"
            "eflection agree member-by-member). ⚠ On failure also check `file_exists` — a bogus path is the commonest c"
            "ause and yields `error_code` 28 (`OpenFileFailed`)."
        ),
        doc=(
            "Run a macro procedure from a project file inside the running SolidWorks session. Returns ok, return_value,"
            " error_code and error_name, where error_name maps the code through the run-macro error enum; whatever the "
            "macro does to the document happens here, and this tool does not save the document. On failure check file_e"
            "xists first, because a bogus path is the commonest cause and reports error_code 28."
        ),
    ),
    ToolSpec(
        name="solidworks_macro_normalize_model_family",
        title="Normalize a Model Name to a Prompt Family",
        module="sw_macro_guard",
        function="normalize_model_family",
        params=[
            Param("model_name", str, description=(
                                         "Model name exactly as written by the caller, for example gpt-4o or claude-3.5"
                                         "-sonnet."
                                     ))
        ],
        evidence=(
            "★ **内部件（模型不必直接调用）**：本工具是 `sw_macro_guard.generate_macro_with_guard` 管线的**一步**。Map "
            "a concrete model name onto one of the prompt families this repo uses (gpt / kimi / claude / generic). ★ Pu"
            "re string function — no SolidWorks, no COM."
        ),
        doc=(
            "Map a concrete model name onto one of the prompt families this repo uses (gpt, kimi, claude, generic). Int"
            "ernal step of the sw_macro_guard generate_macro_with_guard pipeline; pure string function with no SolidWor"
            "ks call and no COM."
        ),
    ),
    ToolSpec(
        name="solidworks_macro_build_prompt",
        title="Build the VBA-Generation Prompt for a Model Family",
        module="sw_macro_guard",
        function="build_prompt",
        params=[
            Param(
                "user_request", str, description="What the user wants the macro to do, in natural language."
            ),
            Param(
                "model_name",
                str,
                default="",
                description=(
                    "Model name mapped onto a prompt family by solidworks_macro_normalize_model_family; empty means the"
                    " generic family. Defaults to empty."
                ),
            ),
            Param(
                "strict",
                bool,
                default=True,
                description="Whether to emit the strict variant of the prompt. Defaults to true.",
            ),
        ],
        evidence=(
            "★ **内部件（模型不必直接调用）**：本工具是 `sw_macro_guard.generate_macro_with_guard` 管线的**一步**。Buil"
            "d the prompt that asks a model to write SolidWorks VBA for `user_request`. ★ Pure string function (no Soli"
            "dWorks call), so it is safe to call anywhere."
        ),
        doc=(
            "Build the prompt that asks a model to write SolidWorks VBA for user_request. Internal step of the sw_macro"
            "_guard generate_macro_with_guard pipeline, not meant to be called on its own; it is a pure string function"
            " and never calls SolidWorks."
        ),
    ),
    ToolSpec(
        name="solidworks_macro_extract_vba_code",
        title="Extract the VBA Code Block from Model Output",
        module="sw_macro_guard",
        function="extract_vba_code",
        params=[
            Param(
                "text",
                str,
                description="Raw model output, which may contain prose and Markdown code fences around the code.",
            )
        ],
        evidence=(
            "★ **内部件（模型不必直接调用）**：本工具是 `sw_macro_guard.generate_macro_with_guard` 管线的**一步**。Pull"
            " the VBA code out of a model's reply (official-free helper: pure text). ★ Returns the extracted code; use "
            "`solidworks_macro_validate_vba_code` next."
        ),
        doc=(
            "Pull the VBA source out of a model reply that mixes prose and code fences. Internal step of the sw_macro_g"
            "uard generate_macro_with_guard pipeline; pure text handling, no SolidWorks call. Feed the result to solidw"
            "orks_macro_validate_vba_code before anything runs."
        ),
    ),
    ToolSpec(
        name="solidworks_macro_validate_vba_code",
        title="Validate VBA Before It Is Handed to SolidWorks",
        module="sw_macro_guard",
        function="validate_vba_macro",
        params=[Param("code", str, description="VBA source to check.")],
        evidence=(
            "Check a VBA macro against the minimum this repo requires before it may be handed to SolidWorks. ★ Pure fun"
            "ction: a static pre-flight, not an execution."
        ),
        doc=(
            "Check a VBA macro against the minimum this repo requires before it is handed to SolidWorks. Pure static pr"
            "e-flight that runs no code and calls no SolidWorks; it reports the issues it finds, so a non-empty issue l"
            "ist means the macro is not ready to run."
        ),
    ),
    ToolSpec(
        name="solidworks_macro_select_template",
        title="Pick a Local VBA Template by Keyword",
        module="sw_macro_guard",
        function="select_template_key",
        params=[Param("user_request", str, description="The user's request text, matched against template keywords.")],
        evidence=(
            "★ **内部件（模型不必直接调用）**：本工具是 `sw_macro_guard.generate_macro_with_guard` 管线的**一步**。Choo"
            "se the local VBA template key whose keywords match `user_request`. ★ Pure function; the template bodies li"
            "ve in this repo (MIT)."
        ),
        doc=(
            "Choose the local VBA template whose keywords match user_request. Internal step of the sw_macro_guard gener"
            "ate_macro_with_guard pipeline; pure function, and the template bodies live in this repo under the MIT lice"
            "nce."
        ),
    ),
    ToolSpec(
        name="solidworks_macro_fallback_template",
        title="Get the Fallback VBA Template for a Request",
        module="sw_macro_guard",
        function="fallback_macro_for_request",
        params=[Param("user_request", str, description="The user's request text, used to pick the closest template.")],
        evidence=(
            "★ **内部件（模型不必直接调用）**：本工具是 `sw_macro_guard.generate_macro_with_guard` 管线的**一步**。Retu"
            "rn the local fallback VBA template for `user_request` — used when generation fails. ★ Pure function; no So"
            "lidWorks call, no network."
        ),
        doc=(
            "Return the local fallback VBA template for user_request, used when model generation fails. Internal step o"
            "f the sw_macro_guard generate_macro_with_guard pipeline; pure function with no SolidWorks call and no netw"
            "ork access."
        ),
    ),
    ToolSpec(
        name="solidworks_macro_write_file",
        title="Write Generated VBA to a File",
        module="sw_macro_guard",
        function="write_macro_file",
        params=[
            Param("code", str, description="VBA source to write."),
            Param(
                "output_path",
                str,
                description="Absolute path to write; a resource path, not a geometry coordinate.",
            ),
        ],
        evidence=(
            "Write VBA source to a file so a human or an agent can load it into SolidWorks. ★ Returns the write report;"
            " it does NOT run the macro (use `solidworks_macro_run`)."
        ),
        doc=(
            "Write VBA source to a local file so a human or an agent can load it into SolidWorks. Writes the file, crea"
            "tes its parent directory when missing and resolves the path; it does not run the macro, so use solidworks_"
            "macro_run to execute it."
        ),
    ),
]
