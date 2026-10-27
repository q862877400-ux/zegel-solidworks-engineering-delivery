"""★ 批次 81：由 Bunny 扇出产出、**经门禁**（`tools/check_bunny_toolspec_rows.py`）过滤后的 ToolSpec 声明。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   sw_automation_knowledge · sw_com_traps · sw_feature_readback · sw_import_mesh_
# reference · sw_misumi · sw_preflight · sw_review · sw_sketch_dimensions
# 定位:   ★ 规格 `specs/204-tool-ramp/spec.md` 的批 81；
#         ★★ **本文件由 `tools/build_toolspec_batch_from_rows.py` 生成** ——
#         行来自 Bunny 子代理（**只读官方源与仓库**），而**判据、门禁、真机、提交归主线** ✓
# 官方依据: 逐行的 `official_file` / `official_signature` 见下表（★ 每条都是官方页的逐字
#           签名）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **20 个工具**
# ⚠ 生成器**只收 `exposable=True` 且门禁 0 问题的行**（★ 被门禁挡下的 63 行见 `output/`
# ）
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH81"]

SPECS_BATCH81 = [
    ToolSpec(
        name="solidworks_review_drawing_layout",
        title="Review Drawing Layout Collisions (views / dimensions / notes / title block)",
        module="sw_review",
        function="review_drawing_layout",
        inject="",
        params=[
            Param(
                "structure",
                str,
                description=(
                    "Structured drawing evidence dict, normally produced by the drawing inspection path; optional keys "
                    "read here are views, dimensions, notes and title_block, and each item may carry box, name, view, s"
                    "heet, note_kind, owner_view, type and box_source."
                ),
            ),
            Param(
                "padding_m",
                float,
                default=0.001,
                description=(
                    "Collision tolerance in metres applied to every edge comparison; it is a scalar margin, not a coord"
                    "inate. Defaults to 0.001."
                ),
            ),
            Param(
                "preview_evidence",
                str,
                default="",
                description=(
                    "Optional list of BMP preview evidence dicts holding exists and likely_blank; it only sets the draw"
                    "ing-pixel-preview check and never decides pass or fail on its own. Defaults to empty."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_review.py）：`查不到（非 API 成员，无官方 **Signature**: 行；源码签名 `review_dr"
            "awing_layout(structure, *, padding_m=0.001, preview_evidence=None) -> dict`）`。★ 真源是**本仓** `scripts/"
            "sw_review.py` 的 `review_drawing_layout`（★ 它不是 SolidWorks API 成员，故无官方页）—— 查不到（无官方 ## R"
            "emarks）。★ 函数 docstring 自述（scripts/sw_review.py:91）：「该规则只能依据 SolidWorks 返回的包围盒筛出风"
            "险，不能替代 PDF/PNG 目视复核。」⇒ 返回里 `manual_review_required` / `retryable` 在 status != 'pass' 时为 "
            "true（scripts/sw_review.py:"
        ),
        doc=(
            "Check structured drawing evidence for layout collisions between views, dimensions, notes and the title blo"
            "ck. Read-only rule scoring: it can only flag risks from SolidWorks bounding boxes, so it never replaces vi"
            "sual PDF or PNG review. Returns status plus the manual_review_required and retryable flags."
        ),
    ),
    ToolSpec(
        name="solidworks_review_export_previews",
        title="Export Multi-View BMP Previews of a Part (read-back verified)",
        module="sw_review",
        function="save_review_previews",
        inject="model",
        params=[
            Param(
                "output_dir",
                str,
                default="",
                description="Directory that receives the preview images. Defaults to empty.",
            ),
            Param("basename", str, default="review", description=(
                                                         "File name prefix used for every exported image. Defaults to '"
                                                         "review'."
                                                     )),
            Param(
                "views",
                str,
                default="",
                description=(
                    "View names to export; an empty string falls back to isometric, front, top and right. Defaults to e"
                    "mpty."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 SaveBMP.md）：`System.bool SaveBMP( System.string FileNameIn, System.int WidthIn, S"
            "ystem.int HeightIn )`。★ 本函数**本身不是 SolidWorks API 成员** —— scripts/sw_review.py:677-695 是纯 Pytho"
            "n 编排（`[save_preview(model, output_dir / f'{basename}_{view}.bmp', view) for view in views]`），来源是本"
            "仓库自身既有模式，不是官方成员、不是第三方项目。所驱动的官方成员是 `IModelDoc2::SaveBMP`，其官方页存在且签"
            "名逐字为上面那一行（FileNameIn 须含完整路径 + .bmp；Width/Height <=0 时按窗口大小；True = 成"
        ),
        doc=(
            "Export isometric, front, top and right preview BMP images of the active model for later visual review. Wri"
            "tes one image per view into output_dir, named basename_view.bmp, and returns the list of written paths."
        ),
    ),
    ToolSpec(
        name="solidworks_review_write_report",
        title="Write Review Report JSON",
        module="sw_review",
        function="write_review_report",
        inject="",
        params=[
            Param(
                "report",
                str,
                default="",
                description=(
                    "Structured review report dict of the form solidworks_build_review_report returns, holding model, c"
                    "ad_spec, previews, expected_outputs, checks, review_notes and evaluation; it is plain data, not a "
                    "COM object. Defaults to empty."
                ),
            ),
            Param(
                "output_path",
                str,
                default="",
                description=(
                    "JSON output path; the parent directory is created when missing and a leading tilde is expanded. De"
                    "faults to empty."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_review.py）：`查不到`。查不到 —— 该函数**不是 SolidWorks API 成员**。它是本仓库 "
            "scripts/sw_review.py:1116-1127 的纯 Python 文件写出辅助：`_expand_path` → `mkdir(parents=True, exist_ok=Tr"
            "ue)` → `json.dump(report, file, ensure_ascii=False, indent=2)` → 返回路径字符串。★ 全程零 COM 调用，故不存"
            "在官方文档页；同理 docs/recon/member-to-example-index.md 里查不到该成员（无任何调用序可摘）。模块头只有 D"
        ),
        doc=(
            "Write a structured review report dict to a JSON file and return that path. Writes the file after creating "
            "its parent directory; this is pure file handling with no SolidWorks call."
        ),
    ),
    ToolSpec(
        name="solidworks_review_write_summary",
        title="Write Review Markdown Summary",
        module="sw_review",
        function="write_markdown_summary",
        inject="",
        params=[
            Param(
                "report",
                str,
                default="",
                description=(
                    "Review report dict whose evaluation, checks and previews keys are read; missing keys fall back to "
                    "unknown, zero or an empty list. Defaults to empty."
                ),
            ),
            Param(
                "output_path",
                str,
                default="",
                description=(
                    "Markdown summary output path; the parent directory is created when missing. Defaults to empty."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_review.py）：`查不到 —— write_markdown_summary 不是 SolidWorks API 成员：scripts"
            "/sw_review.py:1130 是本仓库自写的纯 Python 写文件函数（open() + str.join()），C:\\swapi\\types 下无同名成"
            "员页（已用 glob 核过 run_review / write_markdown_summary / write_re`。★ 真源是**本仓** `scripts/sw_review."
            "py` 的 `write_markdown_summary`（★ 它不是 SolidWorks API 成员，故无官方页）—— 不适用 —— 无官方页可引，故无"
            " Remarks。该函数自身不碰 COM；它消费的是 build_review_report（:924）/ evaluate_review_report（:979）产出的"
            "纯 dict。"
        ),
        doc=(
            "Write a Markdown summary of a review report and return the summary file path. Writes the file after creati"
            "ng its parent directory; it reads only the evaluation, checks and previews keys, so a missing key degrades"
            " to unknown, zero or an empty list."
        ),
    ),
    ToolSpec(
        name="solidworks_review_run",
        title="一键自审查：导多视角预览图 + 落盘 JSON 报告与 Markdown 摘要",
        module="sw_review",
        function="run_review",
        inject="model",
        params=[
            Param(
                "output_dir",
                str,
                description=(
                    "Output directory for the preview images and the reports; it is expanded and created when missing."
                ),
            ),
            Param(
                "basename",
                str,
                default="review",
                description=(
                    "Output file name prefix, which sets the actual names of the report JSON, the summary Markdown and "
                    "each preview image. Defaults to 'review'."
                ),
            ),
            Param(
                "views",
                str,
                default="",
                description=(
                    "Standard view names to export; an empty string falls back to isometric, front, top and right. Defa"
                    "ults to empty."
                ),
            ),
            Param(
                "expected_outputs",
                str,
                default="",
                description=(
                    "Delivery file paths such as sldprt, step or stl to check for existence and size; when empty the ex"
                    "istence check is skipped and a warning is recorded instead. Defaults to empty."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_review.py）：`查不到`。★ 真源是**本仓** `scripts/sw_review.py` 的 `run_review`（"
            "★ 它不是 SolidWorks API 成员，故无官方页）—— 查不到 —— ★ 该函数**不是 SolidWorks API 成员**，是本项目自身"
            "的纯 Python 编排层（C:\\swapi\\types 下 566 个接口目录里既无 RunReview.md，全量 Select-String 也 0 命中；s"
            "cripts/sw_review.py:1247-1248 的 `if __name__ == '__main__': raise SystemExit(main())` 也表明它是脚"
        ),
        doc=(
            "Run the full self-review on the active model and write the report, summary and preview images. Writes revi"
            "ew_report.json, the Markdown summary and one BMP per view into output_dir and returns the report plus its "
            "path; it is an orchestration layer, not a SolidWorks member."
        ),
    ),
    ToolSpec(
        name="solidworks_preflight_check_com_dependencies",
        title="检查 Python COM 依赖包（comtypes / pywin32）是否缺失",
        module="sw_preflight",
        function="missing_com_dependencies",
        inject="",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 sw_preflight.py）：`查不到（非 SolidWorks API 成员）`。★ 官方页查不到，且**不该**查"
            "到：这是纯 Python 函数，不碰任何 SolidWorks API（无 COM 形参、无 sw_connect 调用），只有 importlib.import_"
            "module + 一张三元组检查表。★ 真源是**本仓** scripts/sw_preflight.py:68-79（依赖项常量 PIP_REQUIREMENTS 在 "
            ":25，检查项三元组在 :70-74，逐项判定 helper `_module_available` 在 :56-65）。★ 出处可指认（铁律 1）：该文"
            "件与上游 MIT 归档 C:\\swprojects\\sw-skill-fork"
        ),
        doc=(
            "Check that the Python COM dependencies this server needs are importable and report the missing package nam"
            "es. Read-only and pure Python: it never touches SolidWorks and needs no open document, so run it first whe"
            "n the server misbehaves."
        ),
    ),
    ToolSpec(
        name="solidworks_mesh_configure_import_preferences",
        title="设置 OBJ/STL/VRML 网格导入偏好（全局系统偏好 + 记旧值）",
        module="sw_import_mesh_reference",
        function="configure_mesh_import_preferences",
        inject="sw",
        params=[
            Param(
                "units",
                str,
                default="m",
                description=(
                    "Mesh file length unit; allowed values are mm, cm, m, meter, meters, inch, in and ft, and any other"
                    " value raises an error. Defaults to 'm'."
                ),
            ),
            Param(
                "model_type",
                str,
                default="graphics",
                description=(
                    "How to import the mesh: graphics (0) as a graphics body for high-face-count visual reference, surf"
                    "ace (1) or solid (2). Defaults to 'graphics'."
                ),
            ),
            Param(
                "import_textures",
                str,
                default="true",
                description=(
                    "Whether to try importing texture information, given as the text 'true' or 'false'. Defaults to 'tr"
                    "ue'."
                ),
            ),
            Param(
                "as_ps_mesh",
                str,
                default="true",
                description=(
                    "Whether to import through the graphics or subdivided mesh path, given as the text 'true' or 'false"
                    "'. Defaults to 'true'."
                ),
            ),
            Param(
                "segmented",
                str,
                default="false",
                description=(
                    "Whether to import the mesh in segments, given as the text 'true' or 'false'. Defaults to 'false'."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 SetUserPreferenceIntegerValue.md）：`System.bool SetUserPreferenceIntegerValue( Sys"
            "tem.int UserPreferenceValue, System.int Value )`。★ 本仓库函数**不是一个**官方成员，而是对两个 ISldWorks "
            "成员的批量包装：源码 sw_import_mesh_reference.py:133/147 调 SetUserPreferenceIntegerValue（3 次）与 SetUse"
            "rPreferenceToggle（3 次）。主成员页的 Remarks 逐字两句：「This method is intended for user preferences of "
            "type integer.」+「This method is equivalent to interactively setting system options "
        ),
        doc=(
            "Set the SolidWorks preferences used when importing OBJ, STL or VRML mesh files. Writes six user preference"
            "s and returns an audit dict whose restore array lets solidworks_mesh_restore_import_preferences put the ol"
            "d values back."
        ),
    ),
    ToolSpec(
        name="solidworks_mesh_restore_import_preferences",
        title="还原网格导入偏好（按 report 记下的旧值写回并逐条读回校验）",
        module="sw_import_mesh_reference",
        function="restore_mesh_import_preferences",
        inject="sw",
        params=[
            Param(
                "report",
                str,
                default="required",
                description=(
                    "Audit dict returned by solidworks_mesh_configure_import_preferences, read for its restore array of"
                    " kind, preference and old; there is no default, so it must be supplied."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 SetUserPreferenceIntegerValue.md）：`System.bool SetUserPreferenceIntegerValue( Sys"
            "tem.int UserPreferenceValue, System.int Value )`。★ 本仓库函数**不是一个**官方成员，而是对两个 ISldWorks "
            "成员的批量还原包装：源码 sw_import_mesh_reference.py:189/191 按 kind 分别调 SetUserPreferenceIntegerValue("
            "preference, int(old)) 与 SetUserPreferenceToggle(preference, bool(old))，随后用 sw_preference_guard.read_p"
            "reference 读回并逐条比对。主成员页的 Returns 逐字「True if UserPreferenceValue is set, fa"
        ),
        doc=(
            "Reset the mesh import preferences changed by the configure tool, then read them back to prove the restore."
            " Writes the old values back and skips entries whose old value is null; each entry is read again so the res"
            "ult carries a match flag."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_insert_chain_dimensions",
        title="尺寸链（链式标注）",
        module="sw_sketch_dimensions",
        function="insert_chain_dimensions",
        inject="model",
        params=[
            Param(
                "selection",
                str,
                default="__current_selection__",
                description=(
                    "Sketch segment selector, comma separated and order sensitive: '__current_selection__' or a list su"
                    "ch as 'index:0,index:1,index:2', where an out-of-range index raises an error. Defaults to '__curre"
                    "nt_selection__'."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 InsertChainDimensions.md）：`System.object InsertChainDimensions( System.object Ent"
            "ities )`。官方 Remarks（InsertChainDimensions.md:23-27）：Entities 是边/顶点/圆/中点等实体数组，**第一个元"
            "素是起始实体**、依次向后标注；Entities 为 Nothing/null 时改用**预选中的实体**建链；★ 返回的尺寸数组比 Enti"
            "ties **少一个**（N 个实体 ⇒ N-1 个 IDisplayDimension）。调用序见 docs/recon/member-to-example-index.md:308"
            "1（2 个示例）；官方 C# 例（Insert_Chain_Dimensions_Example_CSharp.md:54-7"
        ),
        doc=(
            "Insert a chain of dimensions along selected sketch segments, dimensioning each segment from the previous o"
            "ne. Creates display dimensions in the active sketch; order is the semantics, the first selector is the sta"
            "rting segment, and no coordinates are accepted."
        ),
    ),
    ToolSpec(
        name="solidworks_feature_list_names",
        title="List Feature Tree Names",
        module="sw_feature_readback",
        function="feature_names",
        inject="model",
        params=[
            Param(
                "limit",
                int,
                default=400,
                description="Maximum number of feature names to read back. Defaults to 400.",
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_feature_readback.py）：`查不到（本函数不是 API 成员，无签名可抄）。★ 被包装成员"
            "的官方 `**Signature**:` 逐字如下：`System.object FirstFeature()`（IModelDoc2/FirstFeature）· `System.objec"
            "t GetNextFeature()`（IFeature/GetNextFeature）· `System.string GetTypeName2`。★ 真源是**本仓** `scripts/sw"
            "_feature_readback.py` 的 `feature_names`（★ 它不是 SolidWorks API 成员，故无官方页）—— ★ 官方 `IModelDoc2:"
            ":FirstFeature` 的 `## Remarks` 逐字：「When traversing the FeatureManager design tree, your application sh"
            "ould use [[IFeature::GetTypeName2]] and [[IFeature::GetSpecificFeature2]] to identify "
        ),
        doc=(
            "List the ordered feature names of the active document by walking the FeatureManager tree from the first fe"
            "ature. Read-only; container nodes are filtered out so a name lookup does not falsely match a folder, and o"
            "nly nodes with a type name are kept."
        ),
    ),
    ToolSpec(
        name="solidworks_feature_present",
        title="Check Feature Present In Feature Tree",
        module="sw_feature_readback",
        function="feature_present",
        inject="model",
        params=[
            Param(
                "feature_name",
                str,
                default="required",
                description=(
                    "Feature name as it appears in the tree; there is no useful default, so pass the exact name, and an"
                    " empty string returns false."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_feature_readback.py）：`查不到（本函数不是 API 成员，无签名可抄）。★ 间接触达的"
            "成员官方 `**Signature**:` 逐字：`System.object FirstFeature()`（IModelDoc2/FirstFeature）· `System.object "
            "GetNextFeature()`（IFeature/GetNextFeature）· `System.string GetTypeName2(`。★ 真源是**本仓** `scripts/sw_"
            "feature_readback.py` 的 `feature_present`（★ 它不是 SolidWorks API 成员，故无官方页）—— ★ 官方 `IFeature::"
            "Name` 的 `## Remarks` 逐字：「Feature names can be seen in the FeatureManager design tree of any part or a"
            "ssembly.」以及「Any change to a feature name is **not visible to the user until a rebuild"
        ),
        doc=(
            "Check whether a named feature really exists in the FeatureManager tree. Read-only; it walks the tree and c"
            "ompares names instead of trusting a return value, and an empty name gives false."
        ),
    ),
    ToolSpec(
        name="solidworks_feature_whats_wrong",
        title="取活动模型「What's Wrong」的条目数与明细（规则 6 查错判据，取不到如实报错）",
        module="sw_feature_readback",
        function="whats_wrong",
        inject="model",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 GetWhatsWrongCount.md）：`System.int GetWhatsWrongCount()`。★ 本函数**不是官方成员*"
            "*，而是本仓库的只读判据助手（来源块 sw_feature_readback.py:29-38）。主成员页 C:\\swapi\\types\\IModelDocEx"
            "tension\\GetWhatsWrongCount.md 的 Signature 逐字 `System.int GetWhatsWrongCount()`、Returns 逐字「Number o"
            "f items in the What's Wrong dialog」。明细成员页 C:\\swapi\\types\\IModelDocExtension\\GetWhatsWrong.md 的"
            " Signature 逐字 "
        ),
        doc=(
            "Report how many entries the What's Wrong dialog holds for the active document, where zero means no rebuild"
            " problem. Read-only; when the count cannot be read the result says so instead of reporting zero."
        ),
    ),
    ToolSpec(
        name="solidworks_misumi_suggest_part",
        title="Suggest MISUMI Part Numbers",
        module="sw_misumi",
        function="suggest_part",
        inject="",
        params=[
            Param(
                "keyword",
                str,
                default="",
                description="Part number or keyword to search for, for example SUS304. Defaults to empty.",
            ),
            Param(
                "count",
                int,
                default=10,
                description="Maximum number of suggestions to return. Defaults to 10.",
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_misumi.py）：`查不到（非 SolidWorks API 成员 —— 本函数是仓库自写的纯 Python HTTP"
            " 辅助；C:\\swapi\\types 下无对应页面，glob C:\\swapi\\**\\*suggest* 零命中）`。★ 真源是**本仓** `scripts/s"
            "w_misumi.py` 的 `suggest_part`（★ 它不是 SolidWorks API 成员，故无官方页）—— 无官方 Remarks（非 SW API）。"
            "实际契约见 sw_misumi.py 源码与 docs/research-misumi-api.md:233：GET https://api.cn.misumi.com.cn/api/v1/pa"
            "rtNumber/suggest?keyword=<kw>&count=<n>&field=@default,partNumberList.innerCode&applicationId=77"
        ),
        doc=(
            "Search the Misumi part-number suggest service by keyword and return candidate part numbers. Read-only HTTP"
            " call to api.cn.misumi.com.cn with no SolidWorks involvement; each hit carries partNumber, brandCode, bran"
            "dName and innerCode, and innerCode is the internal key for later specification lookups."
        ),
    ),
    ToolSpec(
        name="solidworks_review_pdf_text_layout",
        title="读取 SolidWorks PDF 矢量文字边界并筛查文字重叠",
        module="sw_review",
        function="inspect_pdf_text_layout",
        inject="",
        params=[
            Param(
                "path",
                str,
                default="",
                description=(
                    "Absolute path of the PDF to inspect; it must exist and be at most 256 MiB, otherwise the result ca"
                    "rries the error code DRAWING_PDF_INVALID. Defaults to empty."
                ),
            ),
            Param(
                "maximum_spans",
                str,
                default="20000",
                description=(
                    "Safety cap on the text spans extracted across all pages, after which parsing stops with DRAWING_PD"
                    "F_TEXT_PARSE_FAILED. Defaults to 20000."
                ),
            ),
            Param(
                "minimum_overlap_area_pt2",
                float,
                default=0.5,
                description=(
                    "Smallest overlap area in square PDF points for two text boxes to count as intersecting. Defaults t"
                    "o 0.5."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_review.py）：`查不到 —— 本函数不是 SolidWorks API 成员，是本仓纯 Python 函数（第"
            "三方库 PyMuPDF/fitz），无官方签名可抄。源码逐字（scripts/sw_review.py:355）：def inspect_pdf_text_layout(p"
            "ath, *, maximum_spans=20000, minimum_overlap_area_pt2=0.5):`。★ 真源是**本仓** `scripts/sw_review.py` 的 `"
            "inspect_pdf_text_layout`（★ 它不是 SolidWorks API 成员，故无官方页）—— 查不到 —— 非官方成员，无官方 Remark"
            "s。源码 docstring 逐字：「@brief 读取 SolidWorks PDF 矢量文字边界并筛查文字重叠。／该证据来自 SolidWorks "
            "官方 PDF 导出的渲染文字，不是 COM 原生尺寸包围盒；扫描 PDF 或被轮廓化的字体可能没有可提取文字，此时必须继"
            "续使用 BMP/PNG 目视复核。」函数返回值自带两条 limitations 字段，逐字"
        ),
        doc=(
            "Inspect the vector text of a SolidWorks exported PDF and flag overlapping text boxes. Read-only; it reads "
            "rendered text rather than COM dimension boxes, and a scanned or outlined PDF may hold no extractable text,"
            " so keep BMP or PNG review as well."
        ),
    ),
    ToolSpec(
        name="solidworks_review_inspect_bmp",
        title="Inspect Bmp Preview",
        module="sw_review",
        function="inspect_bmp_preview",
        inject="",
        params=[
            Param(
                "path",
                str,
                default="",
                description=(
                    "Absolute path of the BMP preview; a missing file or a size of zero is reported back without raisin"
                    "g. Defaults to empty."
                ),
            ),
            Param(
                "sample_limit",
                int,
                default=200000,
                description=(
                    "Byte sampling cap used only by the header fallback branch when the pixel grid cannot be parsed. De"
                    "faults to 200000."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_review.py）：`查不到`。★ 该函数不是 SolidWorks API 成员，是纯 Python 文件检查（o"
            "pen() + int.from_bytes 手工解析 BI_RGB BMP 头与像素网格），不碰 COM ⇒ 官方页无从查起。来源：本仓 D:\\AI\\S"
            "W\\scripts\\sw_review.py:465 自身，辅助 _file_info(:326) / _read_bmp_size(:336)；模块最近的「── 来源 ──」"
            "块在 :593、只覆盖 set_standard_view 之后，不覆盖本函数。返回值判据：unique_sample_values（<8 判空白）、dar"
            "k_pixel_ratio（<"
        ),
        doc=(
            "Check one exported BMP preview for blank content, a tiny file or a failed export. Read-only file inspectio"
            "n with no COM call; it is a lightweight check and does not replace human or visual model judgement."
        ),
    ),
    ToolSpec(
        name="solidworks_view_zoom_to_fit",
        title="View Zoom To Fit",
        module="sw_review",
        function="zoom_to_fit",
        inject="model",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 sw_review.py）：`查不到`。★ 铁律 5：C:\\swapi\\types\\IModelDoc2\\ 下无 ViewZoomtof"
            "it2.md（Get-ChildItem -Recurse -Filter '*oomtofit' 全 types 零命中；内容检索 ViewZoomtofit 只命中 IModelDo"
            "cExtension\\ViewZoomToSheet.md 与 IView\\*PolyLine* 的交叉引用；带/不带前导 I 的目录都查了，Test-Path 全 F"
            "alse）⇒ 不编签名。唯一官方证据：① C:\\swapi\\types\\IModelDocExtension\\ViewZoomToSheet.md:4"
        ),
        doc=(
            "Zoom the active view to fit the window and refresh the graphics area. Modifies only the view, not the mode"
            "l, and takes no parameters."
        ),
    ),
    ToolSpec(
        name="solidworks_review_collect_geometry_measurements",
        title="Collect Part Geometry Measurements",
        module="sw_review",
        function="collect_geometry_measurements",
        inject="model",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 GetPartBox.md）：`**Signature**: `System.object GetPartBox( System.bool NoConversio"
            "n )``。★ 重要前提：**本函数本身不是一个官方成员**，它是能力层对多个官方成员的**聚合**（scripts/sw_review.p"
            "y:835-921）。它自己**没有 `# ── 来源 ──` 块** —— 全文件只有一处来源块（sw_review.py:593），属于 `set_stand"
            "ard_view`；按铁律 5 如实报「该函数无来源块」，不借用邻居的。函数 docstring 自述依据是 'SolidWorks API GetP"
            "artBox(True) + B-Rep cylindrical faces'（sw_review.py:846）⇒ 主成员取 `IPartDoc.GetPar"
        ),
        doc=(
            "Collect manufacturing geometry evidence from the part B-Rep: envelope box, hole walls and cylindrical face"
            "s. Read-only; faces whose sense flag is true are recorded as internal hole walls, while outer faces stay i"
            "n cylindrical_faces and are not treated as hole-diameter evidence."
        ),
    ),
    ToolSpec(
        name="solidworks_review_evaluate_report",
        title="Evaluate Review Report",
        module="sw_review",
        function="evaluate_review_report",
        inject="",
        params=[
            Param(
                "report",
                str,
                default="",
                description=(
                    "Structured review report as returned by solidworks_build_review_report or read back from a review_"
                    "report.json; it is scored as plain data. Defaults to empty."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_review.py）：`查不到`。★ 真源是**本仓** `scripts/sw_review.py` 的 `evaluate_revi"
            "ew_report`（★ 它不是 SolidWorks API 成员，故无官方页）—— 查不到 —— ★ **本函数不是 SolidWorks API 成员**，"
            "是本项目自写的纯 Python 规则评分器（scripts/sw_review.py:979-1115）。逐行读过函数体：只做 `report.get(...)"
            "` 取值、整数加减（`score -= penalty`）、字符串字面量与一个内嵌闭包 `add_issue(code, severity, message, rec"
            "ommen"
        ),
        doc=(
            "Validate a structured review report with rule-based penalties and list the issues found. Read-only rule en"
            "gine on plain data with no SolidWorks call; it returns status, score, issues, recommendations and a manual"
            "_review_required flag."
        ),
    ),
]
