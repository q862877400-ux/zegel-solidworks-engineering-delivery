"""★ 批次 81：由 Bunny 扇出产出、**经门禁**（`tools/check_bunny_toolspec_rows.py`）过滤后的 ToolSpec 声明。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   sw_automation_knowledge · sw_com_traps · sw_feature_readback · sw_import_mesh_reference · sw_misumi · sw_preflight · sw_review · sw_sketch_dimensions
# 定位:   ★ 规格 `specs/204-tool-ramp/spec.md` 的批 81；
#         ★★ **本文件由 `tools/build_toolspec_batch_from_rows.py` 生成** ——
#         行来自 Bunny 子代理（**只读官方源与仓库**），而**判据、门禁、真机、提交归主线** ✓
# 官方依据: 逐行的 `official_file` / `official_signature` 见下表（★ 每条都是官方页的逐字
#           签名）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **20 个工具**
# ⚠ 生成器**只收 `exposable=True` 且门禁 0 问题的行**（★ 被门禁挡下的 63 行见 `output/`）
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH81"]

SPECS_BATCH81 = [
    ToolSpec(
        name="solidworks_review_drawing_layout",
        title="Review Drawing Layout Collisions (views / dimensions / notes / title block)",
        module="sw_review", function="review_drawing_layout",
        inject="",
        params=[
            Param("structure", str, description="Structured drawing evidence dict, normally produced by the drawing inspection path. Optional keys read here: `views`, `dimensions`, `notes`, `title_block`; each item may carry `box` ({left,bottom,right,top}, metres), `name`, `view`, `sheet`, `note_kind`, `owner_view`, `type`, `box_source` (native | "),
            Param("padding_m", float, default=0.001, description="Collision tolerance in METRES, applied to every edge comparison in _drawing_boxes_overlap (scripts/sw_review.py:73-85). ★ Keyword-only in the source. ★ It is a scalar margin, NOT a coordinate."),
            Param("preview_evidence", str, default="", description="Optional list of BMP preview evidence dicts (`exists`, `likely_blank`). ★ Keyword-only in the source. Used only to set the `drawing-pixel-preview` check; it never decides pass/fail on its own."),
        ],
        doc="★ 官方签名（逐字，来自 sw_review.py）：`查不到（非 API 成员，无官方 **Signature**: 行；源码签名 `review_drawing_layout(structure, *, padding_m=0.001, preview_evidence=None) -> dict`）`。★ 真源是**本仓** `scripts/sw_review.py` 的 `review_drawing_layout`（★ 它不是 SolidWorks API 成员，故无官方页）—— 查不到（无官方 ## Remarks）。★ 函数 docstring 自述（scripts/sw_review.py:91）：「该规则只能依据 SolidWorks 返回的包围盒筛出风险，不能替代 PDF/PNG 目视复核。」⇒ 返回里 `manual_review_required` / `retryable` 在 status != 'pass' 时为 true（scripts/sw_review.py:",
    ),
    ToolSpec(
        name="solidworks_review_export_previews",
        title="Export Multi-View BMP Previews of a Part (read-back verified)",
        module="sw_review", function="save_review_previews",
        inject="model",
        params=[
            Param("output_dir", str, default="", description="预览图输出目录。源码 sw_review.py:691 展开路径，:693 按 `{basename}_{view}.bmp` 命名。"),
            Param("basename", str, default="review", description="文件名前缀。"),
            Param("views", str, default="", description="要导出的视图名列表（★ 空串 = 用源码回落值 `(\"isometric\", \"front\", \"top\", \"right\")` —— ★ 不要把那句回落说明当成默认值）。元素与 `view_name` 同一套命名（源码 STANDARD_VIEWS）。★ 是**名字**不是坐标 ⇒ 不违反规则 3。"),
        ],
        doc="★ 官方签名（逐字，来自 SaveBMP.md）：`System.bool SaveBMP( System.string FileNameIn, System.int WidthIn, System.int HeightIn )`。★ 本函数**本身不是 SolidWorks API 成员** —— scripts/sw_review.py:677-695 是纯 Python 编排（`[save_preview(model, output_dir / f'{basename}_{view}.bmp', view) for view in views]`），来源是本仓库自身既有模式，不是官方成员、不是第三方项目。所驱动的官方成员是 `IModelDoc2::SaveBMP`，其官方页存在且签名逐字为上面那一行（FileNameIn 须含完整路径 + .bmp；Width/Height <=0 时按窗口大小；True = 成",
    ),
    ToolSpec(
        name="solidworks_review_write_report",
        title="Write Review Report JSON",
        module="sw_review", function="write_review_report",
        inject="",
        params=[
            Param("report", str, default="", description="结构化审查报告 dict（★ 形如 sw_review.build_review_report 的返回值：model / cad_spec / previews / expected_outputs / checks / review_notes / evaluation）。⚠ 纯数据，不是 COM 对象。"),
            Param("output_path", str, default="", description="JSON 报告的写出路径（支持 ~ 展开，函数内会 mkdir -p 父目录）。★ 是**文件路径**，不是裸坐标。"),
        ],
        doc="★ 官方签名（逐字，来自 sw_review.py）：`查不到`。查不到 —— 该函数**不是 SolidWorks API 成员**。它是本仓库 scripts/sw_review.py:1116-1127 的纯 Python 文件写出辅助：`_expand_path` → `mkdir(parents=True, exist_ok=True)` → `json.dump(report, file, ensure_ascii=False, indent=2)` → 返回路径字符串。★ 全程零 COM 调用，故不存在官方文档页；同理 docs/recon/member-to-example-index.md 里查不到该成员（无任何调用序可摘）。模块头只有 D",
    ),
    ToolSpec(
        name="solidworks_review_write_summary",
        title="Write Review Markdown Summary",
        module="sw_review", function="write_markdown_summary",
        inject="",
        params=[
            Param("report", str, default="", description="结构化审查报告 dict（读取 evaluation / checks / previews 键；缺键时按 unknown/0/空列表退化）。★ 不是 COM 对象，故无注入。"),
            Param("output_path", str, default="", description="Markdown 摘要输出路径（内部经 _expand_path 展开并自动建父目录）。"),
        ],
        doc="★ 官方签名（逐字，来自 sw_review.py）：`查不到 —— write_markdown_summary 不是 SolidWorks API 成员：scripts/sw_review.py:1130 是本仓库自写的纯 Python 写文件函数（open() + str.join()），C:\\swapi\\types 下无同名成员页（已用 glob 核过 run_review / write_markdown_summary / write_re`。★ 真源是**本仓** `scripts/sw_review.py` 的 `write_markdown_summary`（★ 它不是 SolidWorks API 成员，故无官方页）—— 不适用 —— 无官方页可引，故无 Remarks。该函数自身不碰 COM；它消费的是 build_review_report（:924）/ evaluate_review_report（:979）产出的纯 dict。",
    ),
    ToolSpec(
        name="solidworks_review_run",
        title="一键自审查：导多视角预览图 + 落盘 JSON 报告与 Markdown 摘要",
        module="sw_review", function="run_review",
        inject="model",
        params=[
            Param("output_dir", str, description="第二个形参（★ **必填**：源码 `run_review(model, output_dir, …)` 无默认值）。预览图与报告的输出目录；函数内先经 _expand_path() 展开环境变量并 resolve()，再 mkdir(parents=True, exist_ok=True)。⚠ 它是**文件系统路径、不是裸坐标** ⇒ 规则 3 不适用（scripts/sw_review.py:1180-1186）。"),
            Param("basename", str, default="review", description="第三个形参。输出文件名前缀；决定 {basename}_review_report.json / {basename}_review_summary.md / {basename}_{view}.bmp 的实际文件名（scripts/sw_review.py:1179,1194-1195）。"),
            Param("views", str, default="", description="第四个形参。要导出的标准视图名列表；为空时回落到 ('isometric','front','top','right')（scripts/sw_review.py:944）。⚠ **先例问题**：mcp-server/tool_specs_batch15.py:20-25 已记录『tool_specs_batch*.py 里没有任何 list 型 Param 的先例』，并据此**故意不暴露** build_review_report 的同名参数 ⇒ 若本工具要暴露它，须先决定 list 怎么过 MCP 边界并留下先例。"),
            Param("expected_outputs", str, default="", description="第五个形参。期望存在的交付文件路径列表（sldprt/step/stl 等），逐个做存在性+体积检查；为 None 时 checks.expected_outputs_exist=None 并记一条 warn（scripts/sw_review.py:947,955,1042-1049）。⚠ 同上的 list 型先例问题（tool_specs_batch15.py:20-25）。"),
        ],
        doc="★ 官方签名（逐字，来自 sw_review.py）：`查不到`。★ 真源是**本仓** `scripts/sw_review.py` 的 `run_review`（★ 它不是 SolidWorks API 成员，故无官方页）—— 查不到 —— ★ 该函数**不是 SolidWorks API 成员**，是本项目自身的纯 Python 编排层（C:\\swapi\\types 下 566 个接口目录里既无 RunReview.md，全量 Select-String 也 0 命中；scripts/sw_review.py:1247-1248 的 `if __name__ == '__main__': raise SystemExit(main())` 也表明它是脚",
    ),
    ToolSpec(
        name="solidworks_preflight_check_com_dependencies",
        title="检查 Python COM 依赖包（comtypes / pywin32）是否缺失",
        module="sw_preflight", function="missing_com_dependencies",
        inject="",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 sw_preflight.py）：`查不到（非 SolidWorks API 成员）`。★ 官方页查不到，且**不该**查到：这是纯 Python 函数，不碰任何 SolidWorks API（无 COM 形参、无 sw_connect 调用），只有 importlib.import_module + 一张三元组检查表。★ 真源是**本仓** scripts/sw_preflight.py:68-79（依赖项常量 PIP_REQUIREMENTS 在 :25，检查项三元组在 :70-74，逐项判定 helper `_module_available` 在 :56-65）。★ 出处可指认（铁律 1）：该文件与上游 MIT 归档 C:\\swprojects\\sw-skill-fork",
    ),
    ToolSpec(
        name="solidworks_mesh_configure_import_preferences",
        title="设置 OBJ/STL/VRML 网格导入偏好（全局系统偏好 + 记旧值）",
        module="sw_import_mesh_reference", function="configure_mesh_import_preferences",
        inject="sw",
        params=[
            Param("units", str, default="m", description="网格文件单位；源码 SW_LENGTH_UNITS 表允许 mm/cm/m/meter/meters/inch/in/ft，其余抛 ValueError"),
            Param("model_type", str, default="graphics", description="导入为哪种体；graphics(0)/surface(1)/solid(2)（源码 SW_MESH_MODEL_TYPES 表），高面数外观参考建议 graphics"),
            Param("import_textures", str, default="true", description="是否尝试导入纹理信息（swImportStlVrmlTextureInformation 开关）"),
            Param("as_ps_mesh", str, default="true", description="是否按图形/细分网格路径导入（swVrmlStlImportAsPSMesh 开关）"),
            Param("segmented", str, default="false", description="是否分段导入网格（swVrmlStlImportSegmented 开关）"),
        ],
        doc="★ 官方签名（逐字，来自 SetUserPreferenceIntegerValue.md）：`System.bool SetUserPreferenceIntegerValue( System.int UserPreferenceValue, System.int Value )`。★ 本仓库函数**不是一个**官方成员，而是对两个 ISldWorks 成员的批量包装：源码 sw_import_mesh_reference.py:133/147 调 SetUserPreferenceIntegerValue（3 次）与 SetUserPreferenceToggle（3 次）。主成员页的 Remarks 逐字两句：「This method is intended for user preferences of type integer.」+「This method is equivalent to interactively setting system options ",
    ),
    ToolSpec(
        name="solidworks_mesh_restore_import_preferences",
        title="还原网格导入偏好（按 report 记下的旧值写回并逐条读回校验）",
        module="sw_import_mesh_reference", function="restore_mesh_import_preferences",
        inject="sw",
        params=[
            Param("report", str, default="required", description="configure_mesh_import_preferences 返回的审计字典（取其 restore 数组：kind/preference/old）；★ 旧值为 null 的条目一律跳过不写回，写完再读一次给 match"),
        ],
        doc="★ 官方签名（逐字，来自 SetUserPreferenceIntegerValue.md）：`System.bool SetUserPreferenceIntegerValue( System.int UserPreferenceValue, System.int Value )`。★ 本仓库函数**不是一个**官方成员，而是对两个 ISldWorks 成员的批量还原包装：源码 sw_import_mesh_reference.py:189/191 按 kind 分别调 SetUserPreferenceIntegerValue(preference, int(old)) 与 SetUserPreferenceToggle(preference, bool(old))，随后用 sw_preference_guard.read_preference 读回并逐条比对。主成员页的 Returns 逐字「True if UserPreferenceValue is set, fa",
    ),
    ToolSpec(
        name="solidworks_sketch_insert_chain_dimensions",
        title="尺寸链（链式标注）",
        module="sw_sketch_dimensions", function="insert_chain_dimensions",
        inject="model",
        params=[
            Param("selection", str, default="__current_selection__", description="草图段声明式选择器，逗号分隔且**顺序即语义**（官方 InsertChainDimensions.md:23「The first element in Entities is the starting entity which is used to dimension the second element」）：合法值 `'__current_selection__'` 或 `'index:0,index:1,index:2'`。★ 不收坐标（规则 3）；源码 scripts/sw_sketch_dimensions.py:98-105 已实现该解析，越界与非 index: 前缀都会抛错。"),
        ],
        doc="★ 官方签名（逐字，来自 InsertChainDimensions.md）：`System.object InsertChainDimensions( System.object Entities )`。官方 Remarks（InsertChainDimensions.md:23-27）：Entities 是边/顶点/圆/中点等实体数组，**第一个元素是起始实体**、依次向后标注；Entities 为 Nothing/null 时改用**预选中的实体**建链；★ 返回的尺寸数组比 Entities **少一个**（N 个实体 ⇒ N-1 个 IDisplayDimension）。调用序见 docs/recon/member-to-example-index.md:3081（2 个示例）；官方 C# 例（Insert_Chain_Dimensions_Example_CSharp.md:54-7",
    ),
    ToolSpec(
        name="solidworks_feature_list_names",
        title="List Feature Tree Names",
        module="sw_feature_readback", function="feature_names",
        inject="model",
        params=[
            Param("limit", int, default=400, description="★ 最多回读多少个特征名（★ **它是个计数、不是长度** ⇒ 按规则 2 **不带 `_mm`**；源码 `scripts/sw_feature_readback.py:78` 默认 400）"),
        ],
        doc="★ 官方签名（逐字，来自 sw_feature_readback.py）：`查不到（本函数不是 API 成员，无签名可抄）。★ 被包装成员的官方 `**Signature**:` 逐字如下：`System.object FirstFeature()`（IModelDoc2/FirstFeature）· `System.object GetNextFeature()`（IFeature/GetNextFeature）· `System.string GetTypeName2`。★ 真源是**本仓** `scripts/sw_feature_readback.py` 的 `feature_names`（★ 它不是 SolidWorks API 成员，故无官方页）—— ★ 官方 `IModelDoc2::FirstFeature` 的 `## Remarks` 逐字：「When traversing the FeatureManager design tree, your application should use [[IFeature::GetTypeName2]] and [[IFeature::GetSpecificFeature2]] to identify ",
    ),
    ToolSpec(
        name="solidworks_feature_present",
        title="Check Feature Present In Feature Tree",
        module="sw_feature_readback", function="feature_present",
        inject="model",
        params=[
            Param("feature_name", str, default="required", description="★ 要在特征树里找的特征名（★ 中文 UI 下形如「抽壳1」/「筋1」/「圆顶1」；★ 源码 `scripts/sw_feature_readback.py:99` 无默认值 ⇒ 必填）。★ **它是一个名字、不是坐标** —— ★ 空串直接回 False（`sw_feature_readback.py:101-102`）"),
        ],
        doc="★ 官方签名（逐字，来自 sw_feature_readback.py）：`查不到（本函数不是 API 成员，无签名可抄）。★ 间接触达的成员官方 `**Signature**:` 逐字：`System.object FirstFeature()`（IModelDoc2/FirstFeature）· `System.object GetNextFeature()`（IFeature/GetNextFeature）· `System.string GetTypeName2(`。★ 真源是**本仓** `scripts/sw_feature_readback.py` 的 `feature_present`（★ 它不是 SolidWorks API 成员，故无官方页）—— ★ 官方 `IFeature::Name` 的 `## Remarks` 逐字：「Feature names can be seen in the FeatureManager design tree of any part or assembly.」以及「Any change to a feature name is **not visible to the user until a rebuild",
    ),
    ToolSpec(
        name="solidworks_feature_whats_wrong",
        title="取活动模型「What's Wrong」的条目数与明细（规则 6 查错判据，取不到如实报错）",
        module="sw_feature_readback", function="whats_wrong",
        inject="model",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 GetWhatsWrongCount.md）：`System.int GetWhatsWrongCount()`。★ 本函数**不是官方成员**，而是本仓库的只读判据助手（来源块 sw_feature_readback.py:29-38）。主成员页 C:\\swapi\\types\\IModelDocExtension\\GetWhatsWrongCount.md 的 Signature 逐字 `System.int GetWhatsWrongCount()`、Returns 逐字「Number of items in the What's Wrong dialog」。明细成员页 C:\\swapi\\types\\IModelDocExtension\\GetWhatsWrong.md 的 Signature 逐字 ",
    ),
    ToolSpec(
        name="solidworks_misumi_suggest_part",
        title="Suggest MISUMI Part Numbers",
        module="sw_misumi", function="suggest_part",
        inject="",
        params=[
            Param("keyword", str, default="", description="型号或关键词（实测 SUS304 可查）。返回每条含 partNumber / brandCode / brandName / innerCode。"),
            Param("count", int, default=10, description="返回条数上限（数量，非长度，故不带 _mm）。"),
        ],
        doc="★ 官方签名（逐字，来自 sw_misumi.py）：`查不到（非 SolidWorks API 成员 —— 本函数是仓库自写的纯 Python HTTP 辅助；C:\\swapi\\types 下无对应页面，glob C:\\swapi\\**\\*suggest* 零命中）`。★ 真源是**本仓** `scripts/sw_misumi.py` 的 `suggest_part`（★ 它不是 SolidWorks API 成员，故无官方页）—— 无官方 Remarks（非 SW API）。实际契约见 sw_misumi.py 源码与 docs/research-misumi-api.md:233：GET https://api.cn.misumi.com.cn/api/v1/partNumber/suggest?keyword=<kw>&count=<n>&field=@default,partNumberList.innerCode&applicationId=77",
    ),
    ToolSpec(
        name="solidworks_review_pdf_text_layout",
        title="读取 SolidWorks PDF 矢量文字边界并筛查文字重叠",
        module="sw_review", function="inspect_pdf_text_layout",
        inject="",
        params=[
            Param("path", str, default="", description="待检查的 PDF 绝对路径（须为 .pdf）。源码会先 _expand_path 归一化，再校验后缀 / 存在性 / 0 < size <= 256 MiB；任一不满足返回 error_code=DRAWING_PDF_INVALID。这是路径字符串，不是坐标。"),
            Param("maximum_spans", str, default="20000", description="安全上限：跨页累计提取的文字 span 数，超过即中止并报 DRAWING_PDF_TEXT_PARSE_FAILED。是计数（无量纲），按规则 2 不加 _mm。"),
            Param("minimum_overlap_area_pt2", float, default=0.5, description="判定两个文字包围盒「相交」的最小交叠面积，单位 pt²（PDF point 平方）。★ 是面积阈值、不是长度也不是角度 ⇒ 规则 2 的 _mm / _deg 都不适用，保留原名（其中的 pt 来自 point 的面积单位，不是 point 坐标）。★ 它是判定阈值而非位置 ⇒ 不构成规则 3 的裸坐标。"),
        ],
        doc="★ 官方签名（逐字，来自 sw_review.py）：`查不到 —— 本函数不是 SolidWorks API 成员，是本仓纯 Python 函数（第三方库 PyMuPDF/fitz），无官方签名可抄。源码逐字（scripts/sw_review.py:355）：def inspect_pdf_text_layout(path, *, maximum_spans=20000, minimum_overlap_area_pt2=0.5):`。★ 真源是**本仓** `scripts/sw_review.py` 的 `inspect_pdf_text_layout`（★ 它不是 SolidWorks API 成员，故无官方页）—— 查不到 —— 非官方成员，无官方 Remarks。源码 docstring 逐字：「@brief 读取 SolidWorks PDF 矢量文字边界并筛查文字重叠。／该证据来自 SolidWorks 官方 PDF 导出的渲染文字，不是 COM 原生尺寸包围盒；扫描 PDF 或被轮廓化的字体可能没有可提取文字，此时必须继续使用 BMP/PNG 目视复核。」函数返回值自带两条 limitations 字段，逐字",
    ),
    ToolSpec(
        name="solidworks_review_inspect_bmp",
        title="Inspect Bmp Preview",
        module="sw_review", function="inspect_bmp_preview",
        inject="",
        params=[
            Param("path", str, default="", description="BMP 预览文件的绝对路径；内部经 _expand_path 展开环境变量与 ~ 后取 resolve()。文件不存在或 size<=0 时直接回读并返回，不抛。"),
            Param("sample_limit", int, default=200000, description="字节采样上限，仅在按像素网格解析失败（无 samples）走文件头尾兜底分支时用来限制读取字节数。是一个计数不是长度，故不带 _mm。"),
        ],
        doc="★ 官方签名（逐字，来自 sw_review.py）：`查不到`。★ 该函数不是 SolidWorks API 成员，是纯 Python 文件检查（open() + int.from_bytes 手工解析 BI_RGB BMP 头与像素网格），不碰 COM ⇒ 官方页无从查起。来源：本仓 D:\\AI\\SW\\scripts\\sw_review.py:465 自身，辅助 _file_info(:326) / _read_bmp_size(:336)；模块最近的「── 来源 ──」块在 :593、只覆盖 set_standard_view 之后，不覆盖本函数。返回值判据：unique_sample_values（<8 判空白）、dark_pixel_ratio（<",
    ),
    ToolSpec(
        name="solidworks_view_zoom_to_fit",
        title="View Zoom To Fit",
        module="sw_review", function="zoom_to_fit",
        inject="model",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 sw_review.py）：`查不到`。★ 铁律 5：C:\\swapi\\types\\IModelDoc2\\ 下无 ViewZoomtofit2.md（Get-ChildItem -Recurse -Filter '*oomtofit' 全 types 零命中；内容检索 ViewZoomtofit 只命中 IModelDocExtension\\ViewZoomToSheet.md 与 IView\\*PolyLine* 的交叉引用；带/不带前导 I 的目录都查了，Test-Path 全 False）⇒ 不编签名。唯一官方证据：① C:\\swapi\\types\\IModelDocExtension\\ViewZoomToSheet.md:4",
    ),
    ToolSpec(
        name="solidworks_review_collect_geometry_measurements",
        title="Collect Part Geometry Measurements",
        module="sw_review", function="collect_geometry_measurements",
        inject="model",
        params=[
        ],
        doc="★ 官方签名（逐字，来自 GetPartBox.md）：`**Signature**: `System.object GetPartBox( System.bool NoConversion )``。★ 重要前提：**本函数本身不是一个官方成员**，它是能力层对多个官方成员的**聚合**（scripts/sw_review.py:835-921）。它自己**没有 `# ── 来源 ──` 块** —— 全文件只有一处来源块（sw_review.py:593），属于 `set_standard_view`；按铁律 5 如实报「该函数无来源块」，不借用邻居的。函数 docstring 自述依据是 'SolidWorks API GetPartBox(True) + B-Rep cylindrical faces'（sw_review.py:846）⇒ 主成员取 `IPartDoc.GetPar",
    ),
    ToolSpec(
        name="solidworks_review_evaluate_report",
        title="Evaluate Review Report",
        module="sw_review", function="evaluate_review_report",
        inject="",
        params=[
            Param("report", str, default="", description="结构化审查报告字典（★ 原样由 solidworks_build_review_report 的返回体或此前写出的 review_report.json 回读而来）。★ 本函数是纯数据规则评分，不碰 SolidWorks。"),
        ],
        doc="★ 官方签名（逐字，来自 sw_review.py）：`查不到`。★ 真源是**本仓** `scripts/sw_review.py` 的 `evaluate_review_report`（★ 它不是 SolidWorks API 成员，故无官方页）—— 查不到 —— ★ **本函数不是 SolidWorks API 成员**，是本项目自写的纯 Python 规则评分器（scripts/sw_review.py:979-1115）。逐行读过函数体：只做 `report.get(...)` 取值、整数加减（`score -= penalty`）、字符串字面量与一个内嵌闭包 `add_issue(code, severity, message, recommen",
    ),
]
