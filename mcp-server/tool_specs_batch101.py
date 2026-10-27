"""★ 批次 101：规格 213 · B3（前半）—— B 类 5 项里的 `weld_symbol` 与 `forming_tool`。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   `specs/213-hook-up-tools/plan.md` 的 **B3**；★ 本批先落 5 项里的前两项
# 定位:   ★★ **B 类 = 只在探针里验过、`scripts/` 里没有模块函数**的那五项之一二 ✓ ——
#   本批的**第一步已完成**（B2）：★ 把探针里**已证实**的调用序**缝进模块** ✓
#     · `scripts/sw_weldment.py` 的 `insert_weld_symbol_report`（★ 来自
#       `tools/probe_spec211_weldsymbol_real.py` ✓）
#     · `scripts/sw_sheet_metal.py` 的 `insert_form_tool_report`（★ 来自
#       `tools/probe_spec211_formtool.py` ✓）
#   第二步即本文件：★ **把模块函数挂成 ToolSpec** ✓
# 官方依据: ★ 两处都在模块函数的来源块里逐字写了（`swapi` 签名 + `## Remarks` 前置）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **2 个工具** ⇒ 工具数 454 → **456**
# ★★ 为什么这两项值得先挂（★ 逐项带读数）：
#   · ★★ **`weld_symbol`（焊接符号）是「真入口是另一条 API」的实证** ✓ —— ★ 我原先走
#     `IDrawingDoc::InsertWeldSymbol`（10 参、**静默无效、12 组 0→0**）✗；★ 而官方示例走
#     **`IModelDoc2::InsertWeldSymbol3()`（零参）** ✓ ⇒ ★ **建成** ✓
#   · ★★ **`forming_tool`（成形工具）**：★ 官方 `## Remarks` 逐字要求**先选一个面** ✗ ——
# ★ 我第一版没选 ⇒ 回 `None` ⇒ ★ **那与「建不出来」长得一模一样** ✓ ⇒ ★ 建成 `circular e
# mboss1` ✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH101"]


SPECS_BATCH101 = [
    #: ── ① 焊接符号（★ 规格 211 B3-2 · ★ `verified` · ★ 真入口是另一条 API）────────
    ToolSpec(
        name="solidworks_insert_weld_symbol",
        title="Insert Weld Symbol (IModelDoc2::InsertWeldSymbol3)",
        module="sw_weldment",
        function="insert_weld_symbol_report",
        inject="model",
        params=[
            Param(
                "face_index",
                int,
                default=0,
                description=(
                    "Index of the face to select as the attachment point, which is the precondition of the insert. Defa"
                    "ults to 0."
                ),
            ),
            Param(
                "top",
                bool,
                default=False,
                description="Whether to draw the symbol above the line instead of below it. Defaults to false.",
            ),
            Param(
                "left",
                str,
                default="Left",
                description=(
                    "Left-side text; the default is a placeholder rather than a real annotation. Defaults to 'Left'."
                ),
            ),
            Param(
                "symbol",
                str,
                default="BUTT",
                description=(
                    "Symbol short name from the gtol.sym list, for example BUTT, FILL or PLUG; the first few names may "
                    "raise, so retry with another one. Defaults to 'BUTT'."
                ),
            ),
            Param(
                "right",
                str,
                default="Right",
                description="Right-side text; the default is a placeholder. Defaults to 'Right'.",
            ),
            Param(
                "stagger",
                str,
                default="Stagger",
                description="Stagger text; the default is a placeholder. Defaults to 'Stagger'.",
            ),
            Param(
                "contour",
                int,
                default=0,
                description="Weld contour option code, an enum with no unit. Defaults to 0.",
            ),
        ],
        evidence=(
            "焊接符号：在零件上按面插入焊接符号并设文字。★ **焊接符号**（官方 `IModelDoc2::InsertWeldSymbol3`，★ **零参"
            "**）—— ★★★ **本能力是「真入口是另一条 API」的实证**：★ 我原先走 `IDrawingDoc::InsertWeldSymbol`（**10 参、"
            "静默无效** —— ★ 12 组试完读数全 **0→0**）✗；★★ 而**官方示例**走的是 **`InsertWeldSymbol3()`（零参）** + `I"
            "WeldSymbol::SetText(Top, Left, Symbol, Right, Stagger, Contour)` ✓ ⇒ ★ **建成** ✓ ★★ **判据 = 回读**（★ 不"
            "看 `SetText` 的 bool —— 事实 8）：★ `GetLineCount` / `GetTextCount` / `IsAttached` 三项 ✓ ★★★ **前置是硬性"
            "的**：★ 官方 Preconditions 逐字「select a face, edge, or sketch segment」—— ★ 没选时 `InsertWeldSymbol3()`"
            " **静默回 `None`** ⇒ ★ 本工具**把前置是否有效单独回报**（`selection_count`），★ 免得把「前置没上」记成「符"
            "号建不出来」 ✓"
        ),
        doc=(
            "Insert a weld symbol on a face of a part and set its text. It creates the symbol annotation; an attachable"
            " entity has to be available to select, and a missing selection makes the insert return nothing rather than"
            " fail loudly."
        ),
    ),
    #: ── ② 成形工具（★ 规格 211 B1-1 批 · ★ `verified`）────────────────────────
    ToolSpec(
        name="solidworks_insert_form_tool",
        title="Insert Form Tool (InsertFormToolFeature)",
        module="sw_sheet_metal",
        function="insert_form_tool_report",
        inject="model",
        params=[
            Param(
                "tool_path",
                str,
                description=(
                    "Path of the forming tool file on disk; the reference takes a file path and not a tool name."
                ),
            ),
            Param(
                "face_index",
                int,
                default=0,
                description=(
                    "Index of the face to press the tool on, which is one of the two preconditions. Defaults to 0."
                ),
            ),
            Param("flip", bool, default=False, description="Whether to flip the tool. Defaults to false."),
            Param(
                "rot_angle_deg",
                float,
                default=0.0,
                description="Rotation angle in degrees, converted once at the boundary. Defaults to 0.0.",
            ),
            Param("config", str, default="", description=(
                                                 "Configuration name; empty means the default configuration. Defaults t"
                                                 "o empty."
                                             )),
            Param(
                "override_doc", bool, default=False, description=(
                                                         "Override-document option as the reference takes it. Defaults "
                                                         "to false."
                                                     )
            ),
            Param("show_punch", bool, default=True, description=(
                                                        "Show-punch option as the reference takes it. Defaults to true."
                                                    )),
            Param("show_profile", bool, default=True, description=(
                                                          "Show-profile option as the reference takes it. Defaults to t"
                                                          "rue."
                                                      )),
            Param("show_center", bool, default=True, description=(
                                                         "Show-centre option as the reference takes it. Defaults to tru"
                                                         "e."
                                                     )),
            Param("link_to_part", bool, default=True, description=(
                                                          "Link-to-part option as the reference takes it. Defaults to t"
                                                          "rue."
                                                      )),
        ],
        evidence=(
            "成形工具：在钣金面上压出成形特征（需先选面）。★ **成形工具**（官方 `IFeatureManager::InsertFormToolFeature"
            "`，★ **9 参**）—— ★★ **会新建特征**（非只读）✓ ★★★ **前置有两处，★ 而它们都会「静默失败」**（★ 本仓栽过的"
            "形态）：★ **① 官方 `## Remarks` 逐字要求先选一个面** —— ★ 我第一版没选 ⇒ 回 `None` ✗，★ **而「没选」与「建"
            "不出来」长得一模一样** ✓；★ **② 前置是钣金件** —— ★ 而建钣金件的契约是 `create_base_flange(model, sketch_r"
            "ef, spec: BaseFlangeSpec)` ✗，★ **不是** `(model, sketch, thickness, …)`，★ 且它**不抛、只回 `None`** ✓ ★★"
            " **判据 = 回读**：★ 特征树增量（★ 不看返回值 —— 事实 8）✓；★ 且**两处前置各自单列布尔**（`tool_file_exists"
            "` / `selection_count`）—— ★★ 因为「读数无效」与「真的不建」长得一样 ✓ ★ 真机建成读数：★ `circular emboss1`"
            " ✓"
        ),
        doc=(
            "Press a forming tool into a sheet-metal face and create the form feature. It creates a feature in the acti"
            "ve part; it needs a sheet-metal part and a face to select, and either precondition failing returns nothing"
            " instead of an error, so check both readings before concluding the feature cannot be built."
        ),
    ),
]
