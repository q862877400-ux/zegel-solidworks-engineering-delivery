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
_CFG = ("Configuration name to inspect. ★ Official signature takes the configuration name "
        "(`GetExplodedViewNames2(String ConfigurationName)`), not an index.")

SPECS_BATCH79 = [
    # ── ① 爆炸视图（9 个 · FR-008 上半）────────────────────────────────────
    ToolSpec(
        name="solidworks_assembly_create_exploded_view",
        title="Create an Exploded View (IAssemblyDoc.CreateExplodedView)",
        module="sw_assembly_doc", function="create_exploded_view",
        inject="doc",
        params=[],
        doc="Create an explode view of the active assembly configuration (official "
            "`System.bool CreateExplodedView()`, **zero arguments**). "
            "★ Official Remarks: call it MULTIPLE times to add multiple explode views to the same "
            "configuration; and \"Perfect explode views often require user interaction\" — it does "
            "its best from the CURRENT MATE CONDITIONS. "
            "⚠ Judged by the returned bool, but do NOT trust that alone: read back with "
            "`solidworks_assembly_get_exploded_view_count` (this repo's rule: read-back proves it).",
    ),
    ToolSpec(
        name="solidworks_assembly_auto_explode",
        title="Automatically Explode the Assembly (IAssemblyDoc.AutoExplode)",
        module="sw_assembly_doc", function="auto_explode",
        inject="doc",
        params=[],
        doc="Automatically generate an exploded view of the current configuration (official "
            "`System.bool AutoExplode()`, zero arguments). "
            "★ Official Remarks: it creates only ONE exploded view per configuration — for several, "
            "use `solidworks_assembly_create_exploded_view`.",
    ),
    ToolSpec(
        name="solidworks_assembly_view_explode",
        title="Show the Exploded State (IAssemblyDoc.ViewExplodeAssembly)",
        module="sw_assembly_doc", function="view_explode_assembly",
        inject="doc",
        params=[],
        doc="Explode the selected exploded view in the display (official `void "
            "ViewExplodeAssembly()`, zero arguments). ★ Official Remarks: pair it with "
            "`solidworks_assembly_view_collapse` to TOGGLE the display.",
    ),
    ToolSpec(
        name="solidworks_assembly_view_collapse",
        title="Show the Collapsed State (IAssemblyDoc.ViewCollapseAssembly)",
        module="sw_assembly_doc", function="view_collapse_assembly",
        inject="doc",
        params=[],
        doc="Collapse the display back (official `void ViewCollapseAssembly()`, zero arguments). "
            "★ The pair of `solidworks_assembly_view_explode` (official Remarks name them together).",
    ),
    ToolSpec(
        name="solidworks_assembly_show_exploded",
        title="Show/Hide a Named Exploded View (IAssemblyDoc.ShowExploded2)",
        module="sw_assembly_doc", function="show_exploded",
        inject="doc",
        param_alias={"explode_view_name": "explode_view_name"},
        params=[
            Param("show_it", bool, description="True = show it exploded; False = show it collapsed "
                                               "(official parameter semantics, verbatim)."),
            Param("explode_view_name", str, description="Name of the exploded view to show "
                                                        "(★ take it from "
                                                        "`solidworks_assembly_get_exploded_view_names`)."),
        ],
        doc="Display the named exploded view (official `System.bool ShowExploded2(Boolean ShowIt, "
            "String ExplodeViewName)` — **two arguments**, and note the trailing `2`).",
    ),
    ToolSpec(
        name="solidworks_assembly_get_exploded_view_names",
        title="List the Exploded View Names of a Configuration (GetExplodedViewNames2)",
        module="sw_assembly_doc", function="get_exploded_view_names",
        inject="doc",
        params=[Param("configuration_name", str, description=_CFG)],
        doc="Return the exploded-view NAMES of a configuration as a list of strings (official "
            "`System.object GetExplodedViewNames2(String ConfigurationName)`). "
            "★ `None` comes back as an EMPTY LIST here — never as \"one nameless view\".",
    ),
    ToolSpec(
        name="solidworks_assembly_get_exploded_view_count",
        title="Count the Exploded Views of a Configuration (GetExplodedViewCount2)",
        module="sw_assembly_doc", function="get_exploded_view_count",
        inject="doc",
        params=[Param("configuration_name", str, description=_CFG)],
        doc="Return the number of exploded views in a configuration (official `System.int "
            "GetExplodedViewCount2(String ConfigurationName)`). ★ This is the READ-BACK that proves "
            "a create actually happened.",
    ),
    ToolSpec(
        name="solidworks_assembly_exploded_view_configuration",
        title="Read GetExplodedViewConfigurationName (argument semantics UNVERIFIED)",
        module="sw_assembly_doc", function="get_exploded_view_configuration_name",
        inject="doc",
        param_alias={"arg": "arg"},
        params=[Param("arg", str, description="★ Passed through UNCHANGED. The official page gives "
                                              "only a Parameters section and NO description of this "
                                              "argument, so this tool does not guess whether it is "
                                              "an index or a name (repo rule: say 'not determined').")],
        doc="Thin wrapper over `IAssemblyDoc.GetExplodedViewConfigurationName` (one argument). "
            "⚠ **The meaning of that argument is not documented** on the official page — passed "
            "through as-is, and the returned value is echoed with no interpretation.",
    ),
    ToolSpec(
        name="solidworks_assembly_edit_explode_parameters",
        title="Open the Explode Parameter Editor (IAssemblyDoc.EditExplodeParameters)",
        module="sw_assembly_doc", function="edit_explode_parameters",
        inject="doc",
        params=[],
        doc="Call `IAssemblyDoc.EditExplodeParameters` (zero arguments). "
            "⚠ The official page carries NO Remarks, so whether it opens an INTERACTIVE dialog is "
            "NOT determined here — run it through the dialog guard "
            "(`python tools/sw_guard.py --timeout N -- python <script>`) as the repo requires.",
    ),
    # ── ② 宏 / VBA（8 个 · FR-008 下半）──────────────────────────────────
    ToolSpec(
        name="solidworks_macro_run",
        title="Run a Macro File (ISldWorks.RunMacro2)",
        module="sw_macro", function="run_macro",
        inject="sw_app",
        params=[
            Param("file_path", str, description="Absolute path of the macro project file "
                                                "(`.swp` / `.swb` …)."),
            Param("module_name", str, description="Module name inside the macro. ⚠ For VBA `.swp` "
                                                  "that is the VBA module name; the official page's "
                                                  "Remarks are EMPTY, so VSTA/`.swb` semantics are "
                                                  "NOT determined here."),
            Param("procedure_name", str, description="Procedure name (e.g. `main`)."),
            Param("options", int, default=0, description="`swRunMacroOption_e`: 0=swRunMacroDefault, "
                                                         "1=swRunMacroUnloadAfterRun (both official "
                                                         "page and factory reflection agree)."),
        ],
        doc="Run a macro from a project file (official `System.bool RunMacro2(String FilePathName, "
            "String ModuleName, String ProcedureName, Int32 Options, out Int32 Error)` — **4 in + 1 "
            "out**). ★ Returns `{ok, return_value, error_code, error_name, file, file_exists, module, "
            "procedure, options}`. ★★ The out-parameter is the useful part: `error_name` maps the "
            "code through `swRunMacroError_e` (all 28 members; official page and factory reflection "
            "agree member-by-member). ⚠ On failure also check `file_exists` — a bogus path is the "
            "commonest cause and yields `error_code` 28 (`OpenFileFailed`).",
    ),
    ToolSpec(
        name="solidworks_macro_normalize_model_family",
        title="Normalize a Model Name to a Prompt Family",
        module="sw_macro_guard", function="normalize_model_family",
        params=[Param("model_name", str, description="Model name as written by the caller.")],
        doc="★ **内部件（模型不必直接调用）**：本工具是 `sw_macro_guard.generate_macro_with_guard` 管线的**一步**。"
            "Map a concrete model name onto one of the prompt families this repo uses "
            "(gpt / kimi / claude / generic). ★ Pure string function — no SolidWorks, no COM.",
    ),
    ToolSpec(
        name="solidworks_macro_build_prompt",
        title="Build the VBA-Generation Prompt for a Model Family",
        module="sw_macro_guard", function="build_prompt",
        params=[
            Param("user_request", str, description="What the user wants the macro to do."),
            Param("model_name", str, default="", description="Model name (normalized internally)."),
            Param("strict", bool, default=True, description="Emit the strict variant of the prompt."),
        ],
        doc="★ **内部件（模型不必直接调用）**：本工具是 `sw_macro_guard.generate_macro_with_guard` 管线的**一步**。"
            "Build the prompt that asks a model to write SolidWorks VBA for `user_request`. "
            "★ Pure string function (no SolidWorks call), so it is safe to call anywhere.",
    ),
    ToolSpec(
        name="solidworks_macro_extract_vba_code",
        title="Extract the VBA Code Block from Model Output",
        module="sw_macro_guard", function="extract_vba_code",
        params=[Param("text", str, description="Raw model output (may contain prose + fences).")],
        doc="★ **内部件（模型不必直接调用）**：本工具是 `sw_macro_guard.generate_macro_with_guard` 管线的**一步**。"
            "Pull the VBA code out of a model's reply (official-free helper: pure text). "
            "★ Returns the extracted code; use `solidworks_macro_validate_vba_code` next.",
    ),
    ToolSpec(
        name="solidworks_macro_validate_vba_code",
        title="Validate VBA Before It Is Handed to SolidWorks",
        module="sw_macro_guard", function="validate_vba_macro",
        params=[Param("code", str, description="VBA source to check.")],
        doc="Check a VBA macro against the minimum this repo requires before it may be handed to "
            "SolidWorks. ★ Pure function: a static pre-flight, not an execution.",
    ),
    ToolSpec(
        name="solidworks_macro_select_template",
        title="Pick a Local VBA Template by Keyword",
        module="sw_macro_guard", function="select_template_key",
        params=[Param("user_request", str, description="The user's request text.")],
        doc="★ **内部件（模型不必直接调用）**：本工具是 `sw_macro_guard.generate_macro_with_guard` 管线的**一步**。"
            "Choose the local VBA template key whose keywords match `user_request`. "
            "★ Pure function; the template bodies live in this repo (MIT).",
    ),
    ToolSpec(
        name="solidworks_macro_fallback_template",
        title="Get the Fallback VBA Template for a Request",
        module="sw_macro_guard", function="fallback_macro_for_request",
        params=[Param("user_request", str, description="The user's request text.")],
        doc="★ **内部件（模型不必直接调用）**：本工具是 `sw_macro_guard.generate_macro_with_guard` 管线的**一步**。"
            "Return the local fallback VBA template for `user_request` — used when generation fails. "
            "★ Pure function; no SolidWorks call, no network.",
    ),
    ToolSpec(
        name="solidworks_macro_write_file",
        title="Write Generated VBA to a File",
        module="sw_macro_guard", function="write_macro_file",
        params=[
            Param("code", str, description="VBA source to write."),
            Param("output_path", str, description="Absolute path to write (★ a resource path, not a "
                                                  "coordinate — repo rule 3 only forbids bare "
                                                  "geometry coordinates)."),
        ],
        doc="Write VBA source to a file so a human or an agent can load it into SolidWorks. "
            "★ Returns the write report; it does NOT run the macro (use `solidworks_macro_run`).",
    ),
]
