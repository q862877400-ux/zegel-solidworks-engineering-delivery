"""★ 批次 84：由 Bunny 扇出产出、**经门禁**（`tools/check_bunny_toolspec_rows.py`）过滤后的 ToolSpec 声明。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   sw_gui_focus · sw_gui_modal · sw_part · sw_ref_geometry · sw_sketch_edit_ops ·
#  sw_surface_features · sw_weldment
# 定位:   ★ 规格 `specs/204-tool-ramp/spec.md` 的批 84；
#         ★★ **本文件由 `tools/build_toolspec_batch_from_rows.py` 生成** ——
#         行来自 Bunny 子代理（**只读官方源与仓库**），而**判据、门禁、真机、提交归主线** ✓
# 官方依据: 逐行的 `official_file` / `official_signature` 见下表（★ 每条都是官方页的逐字
#           签名）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **7 个工具**
# ⚠ 生成器**只收 `exposable=True` 且门禁 0 问题的行**（★ 被门禁挡下的 0 行见 `output/`）
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH84"]

SPECS_BATCH84 = [
    ToolSpec(
        name="solidworks_gui_get_foreground_window",
        title="读当前前台窗口句柄（GUI 焦点前置关卡，非 SolidWorks API）",
        module="sw_gui_focus",
        function="foreground",
        inject="",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 sw_gui_focus.py）：`查不到（非 SolidWorks API 成员）—— ★ 底层真源是 **pywin32 的 `w"
            "in32gui.GetForegroundWindow()`**，即 Win32 API `GetForegroundWindow()`（无参、返回 HWND），**不是** `ISldW"
            "orks` / 任何 `I*` 接口的成员 ⇒ 没有可逐字抄的 `**Signature**:` 行。★ 本仓这一`。★ 真源是**本仓** `scripts/"
            "sw_gui_focus.py` 的 `foreground`（★ 它不是 SolidWorks API 成员，故无官方页）—— 查不到（无官方页）。★ 改用"
            "仓库来源块 + 源码注释逐字：D:\\AI\\SW\\scripts\\sw_gui_focus.py:3-29 的 `# ── 来源 ──` 块写着「定位: 嘉立"
            "创 FA 插件 GUI 自动化的**前置关卡**，与 sw_gui_modal 配套」「⚠ 本模块只管焦点，不操作 SolidWorks 模型」⇒ "
            "三条焦点长效规则（:15-20）：① 每次动作**前**断言前台窗口 == 期望窗口，不是就修复"
        ),
        doc=(
            "Get the window handle of whatever currently holds foreground focus. Read-only and model-free; call it befo"
            "re driving the GUI so the next keys or clicks land in the intended window instead of in whichever one had "
            "focus."
        ),
    ),
    ToolSpec(
        name="solidworks_gui_screen_png",
        title="Capture a Full-Screen PNG (Modal-Dialog Forensics)",
        module="sw_gui_modal",
        function="screen_png",
        inject="",
        params=[
            Param(
                "path",
                str,
                default="",
                description=(
                    "Absolute path of the PNG file to write; the source has no usable default, so always pass a real pa"
                    "th. Defaults to an empty string."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_gui_modal.py）：`查不到 —— 本函数是本仓自研的 PIL 整屏截图助手，**不对应任何 Sol"
            "idWorks 官方成员**，两套官方源里都没有同名/同语义成员。`。★ 真源是**本仓** `scripts/sw_gui_modal.py` 的 `s"
            "creen_png`（★ 它不是 SolidWorks API 成员，故无官方页）—— 查不到（无官方页，故无官方 Remarks）。★ 仓库内替"
            "代依据：scripts/sw_gui_modal.py:1-35 的模块来源块给出的是**判据**而非官方语义 —— 判据 = cls `#32770`（标准"
            " Win32 对话框类）+ title 为空 + owner != 0 + 同进程独立顶层 + 尺寸≥60×40；实测命中 hwnd=4983664 cls=#32770"
            " title='' owner=65564"
        ),
        doc=(
            "Write a full-screen PNG capture to path as evidence of what the SolidWorks window showed. Writes the image"
            " file and never touches SolidWorks itself, so it still works while a modal dialog blocks the COM session; "
            "it grabs the whole screen because a window-only capture loses the floating windows outside the client area"
            "."
        ),
    ),
    ToolSpec(
        name="solidworks_revolve_cut",
        title="Create Revolve Cut",
        module="sw_part",
        function="revolve_cut",
        inject="model",
        param_alias={"angle_deg": "angle_rad"},
        params=[
            Param(
                "sketch_name",
                str,
                default="",
                description="Name of the profile sketch exactly as it appears in the feature tree. Defaults to empty.",
            ),
            Param(
                "angle_deg",
                float,
                default=0.0,
                description=(
                    "Revolve angle in degrees, converted once to the radians the official call takes. Defaults to 0.0."
                ),
            ),
            Param(
                "axis_sketch_name",
                str,
                default="",
                description=(
                    "Name of the axis sketch to revolve about, selected before the profile; empty selects no axis and u"
                    "ses the centreline in the profile sketch. Defaults to empty."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 FeatureRevolve2.md）：`Feature FeatureRevolve2( System.bool SingleDir, System.bool "
            "IsSolid, System.bool IsThin, System.bool IsCut, System.bool ReverseDir, System.bool BothDirectionUpToSameE"
            "ntity, System.int Dir1Type, System`。★ 调用前按 `IModelDocExtension::SelectByID2` 选中：**轮廓草图 mark = "
            "0**；**旋转轴 mark = 4 或 16**；**上至面 / 上至顶点 / 等距面 mark = 32**；受影响体或组件 **mark = 1**（仅"
            "当 `UseFeatScope=true` 且 `UseAutoSelect=false`）—— ★ 其中 **mark=32 与 mark=1 本仓从未用过**。★ 逐字 NOTE"
            "：本成员 'provides more functionality … than the now obsolete FeatureRevolve"
        ),
        doc=(
            "Revolve a profile sketch into a cut feature around an axis, removing material from the part. Creates a cut"
            " feature and does not save the document; the axis has to enter the selection set before the profile, and a"
            "n omitted axis name means the sketch centreline is used."
        ),
    ),
    ToolSpec(
        name="solidworks_ref_geometry_create_3d_bounding_box",
        title="创建焊件切割清单项的 3D 边界框",
        module="sw_ref_geometry",
        function="create_3d_bounding_box",
        inject="model",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 Create3DBoundingBox.md）：`**Signature**: `void Create3DBoundingBox()``。官方摘要逐"
            "字「Creates a 3D bounding box for a **cut list item in a weldment part**.」⇒ ★ 只对『焊件零件的切割清单项"
            "』有意义，普通零件上不成是应然的。Remarks：调用后 ISelectionMgr::GetSelectedObjectType3 返回 swSelSKETCHES"
            "，而 GetSelectedObject6 返回的是 IFeature（不是 ISketch）。★ 官方回 void ⇒ 成败判据只有特征树增量。"
        ),
        doc=(
            "Create a 3D bounding box for a cut list item of a weldment part. Creates a sketch that becomes the box and"
            " does not save the document; on an ordinary part, or on a part without a selected cut list item, nothing i"
            "s created and the feature tree not growing is the expected result."
        ),
    ),
    ToolSpec(
        name="solidworks_sketch_select_segment",
        title="Select Sketch Segment By Index",
        module="sw_sketch_edit_ops",
        function="select_sketch_segment",
        inject="model",
        params=[
            Param(
                "index",
                int,
                default=0,
                description=(
                    "Zero-based position of the segment in the active sketch; the order is not promised to stay stable "
                    "across a rebuild. Defaults to 0."
                ),
            ),
            Param(
                "append",
                bool,
                default=False,
                description=(
                    "True appends the segment to the existing selection, false replaces the selection with it; a runnin"
                    "g PropertyManager command ignores this and always appends. Defaults to false."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 sw_sketch_edit_ops.py）：`查不到（本函数无同名官方成员 —— 官方 ISketchManager/ISket"
            "ch/IEntity 里都没有叫 select_sketch_segment 的东西；★ 它是本仓自研的**编排**函数）。真源 = 仓库 scripts/sw"
            "_sketch_edit_ops.py:86-102（`def select_sketch_segment(model, index: int, *, app`。★ 真源是**本仓** `scrip"
            "ts/sw_sketch_edit_ops.py` 的 `select_sketch_segment`（★ 它不是 SolidWorks API 成员，故无官方页）—— IEntity"
            ".Select4 官方 Remarks 要点：只能用**从活动文档直接取到**的 IEntity（不能从底层零件文档取）；当 SOLIDWORKS "
            "正在跑带 PropertyManager 选择框的命令（如 Insert Fillet）时，**Append 形参被忽略**，总是追加；「选中已选中"
            "的实体」会取消选中。ISelectionMgr.GetSelectedObjectC"
        ),
        doc=(
            "Select one sketch segment by its position in the active sketch so later sketch commands act on it. Modifie"
            "s the selection list and returns the read-back selection count rather than the call's own success flag; se"
            "lecting the segment that is already selected deselects it."
        ),
    ),
    ToolSpec(
        name="solidworks_surface_cut",
        title="Insert Surface-Cut Feature",
        module="sw_surface_features",
        function="cut_surface_report",
        inject="model",
        params=[
            Param(
                "flip",
                bool,
                default=False,
                description="True reverses the side the cut is taken from, false keeps it; defaults to false.",
            ),
            Param(
                "keep_piece_index",
                int,
                default=0,
                description=(
                    "Which resulting piece to keep when the cut is ambiguous, as a zero-based result index; -1 means th"
                    "e result is unambiguous. Defaults to 0."
                ),
            ),
            Param(
                "use_feat_scope",
                bool,
                default=False,
                description=(
                    "True cuts only the bodies in this feature's scope that the surface intersects, false cuts every in"
                    "tersecting body; defaults to false."
                ),
            ),
            Param(
                "use_auto_select",
                bool,
                default=True,
                description=(
                    "True cuts every body the surface intersects, false cuts only the bodies given explicitly; defaults"
                    " to true."
                ),
            ),
        ],
        evidence=(
            "★ 官方签名（逐字，来自 InsertCutSurface.md）：``Feature InsertCutSurface( System.bool Flip, System.int Kee"
            "pPieceIndex, System.bool UseFeatScope, System.bool UseAutoSelect, System.object Bodies, out System.int Err"
            "or )``。逐字：「When there is ambiguity in the result of a cut, KeepPieceIndex is used to resolve which of"
            " the possible results is used. **This can be set to -1 if there is no ambiguity**; otherwise, it should be"
            " the index of the result, starting from 0 (up to one less than the possible number of outcomes).」★★ "
        ),
        doc=(
            "Create a surface-cut feature that cuts solids with a preselected surface or plane. Writes a feature into t"
            "he active part and does not save the document; select the cutting surface or plane first, and keep_piece_i"
            "ndex chooses which piece survives when the cut is ambiguous."
        ),
    ),
    ToolSpec(
        name="solidworks_weldment_iter_features",
        title="Recursively List Weldment Feature Tree",
        module="sw_weldment",
        function="iter_features_recursive",
        inject="model",
        params=[],
        evidence=(
            "★ 官方签名（逐字，来自 sw_weldment.py）：`查不到（本函数不是 API 成员，无官方签名可抄）。★ 真源是本仓 scri"
            "pts/sw_weldment.py 第 294-306 行（`def iter_features_recursive(model)` → 内部 `walk()` 递归 + `_iter_featu"
            "re_chain(first_feature, next_member)` 逐字：`_iter_feature_chain` `。★ 调用序（docs/recon/member-to-exampl"
            "e-index.md 第 4144 行 `Get_Mates_and_Mate_Entities_Example_VBNET.md` 摘句，逐字）：「each mate is a subfea"
            "ture of MateGroup; walk with GetFirstSubFeature / ...」—— ★ 即「先顶层 FirstFeature/GetNextFeature 循环，"
            "再对每个节点用 GetFirstSubFeature/GetNextSubFeature 下钻」，与本函数 walk() 的写法一致。★ 同索引第 7"
        ),
        doc=(
            "Walk the weldment feature folders and list the cut list folders with their sub-features. Read-only; it rec"
            "urses through sub-features instead of reporting only top-level nodes, so the result is the whole tree belo"
            "w the weldment folder."
        ),
    ),
]
