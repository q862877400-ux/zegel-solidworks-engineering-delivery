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
                description="要选的面序号（★ **前置** —— ★ 官方 Preconditions 逐字要求"
                "「select a face, edge, or sketch segment」✓）。",
            ),
            Param(
                "top",
                bool,
                default=False,
                description="符号画在横线的上方（True）还是下方（False）。",
            ),
            Param(
                "left",
                str,
                default="Left",
                description="左侧文字（★ 缺省是**占位符** `Left`，★ 不是真实标注 ✓）。",
            ),
            Param(
                "symbol",
                str,
                default="BUTT",
                description="**符号短名** —— ★ 来自 `…\\english\\gtol.sym` 的短名表"
                "（`BUTT` / `FILL` / `PLUG` …）✓；★ 前几个名字**可能抛**（探针实测）"
                "⇒ ★ 换一个重试 ✓。",
            ),
            Param(
                "right",
                str,
                default="Right",
                description="右侧文字（★ 同样缺省是**占位符** ✓）。",
            ),
            Param(
                "stagger",
                str,
                default="Stagger",
                description="交错文字（★ 缺省是**占位符** `Stagger` ✓）。",
            ),
            Param(
                "contour",
                int,
                default=0,
                description="`swWeldContour*` 档位（★ **枚举** ⇒ ★ 无量纲 ✓）。",
            ),
        ],
        doc="焊接符号：在零件上按面插入焊接符号并设文字。"
        "★ **焊接符号**（官方 `IModelDoc2::InsertWeldSymbol3`，★ **零参**）—— "
        "★★★ **本能力是「真入口是另一条 API」的实证**："
        "★ 我原先走 `IDrawingDoc::InsertWeldSymbol`（**10 参、静默无效** —— "
        "★ 12 组试完读数全 **0→0**）✗；"
        "★★ 而**官方示例**走的是 **`InsertWeldSymbol3()`（零参）** + "
        "`IWeldSymbol::SetText(Top, Left, Symbol, Right, Stagger, Contour)` ✓ ⇒ ★ **建成** ✓ "
        "★★ **判据 = 回读**（★ 不看 `SetText` 的 bool —— 事实 8）："
        "★ `GetLineCount` / `GetTextCount` / `IsAttached` 三项 ✓ "
        "★★★ **前置是硬性的**：★ 官方 Preconditions 逐字「select a face, edge, or sketch segment」"
        "—— ★ 没选时 `InsertWeldSymbol3()` **静默回 `None`** ⇒ ★ 本工具**把前置是否有效"
        "单独回报**（`selection_count`），★ 免得把「前置没上」记成「符号建不出来」 ✓",
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
                description="成形工具文件（`*.sldftp`）在**磁盘上的路径** —— ★ 官方 `Path` "
                "参数是**文件路径**、★ 不是名字 ✓（★ 建议落仓库内 `output/`）。",
            ),
            Param(
                "face_index",
                int,
                default=0,
                description="要选的面序号（★ **前置** —— ★ 官方 `## Remarks` 逐字要求"
                "「select either a face or a 2D sketch containing points」✓）。",
            ),
            Param("flip", bool, default=False, description="是否翻转。"),
            Param(
                "rot_angle_deg",
                float,
                default=0.0,
                description="旋转角（**度**）—— ★ 按参数名后缀；★ 换算只在边界一次"
                "（仓里既有的 `sw_connect.deg` ✓）。",
            ),
            Param("config", str, default="", description="配置名（★ 空串即缺省 ✓）。"),
            Param(
                "override_doc", bool, default=False, description="`OverrideDoc` 档。"
            ),
            Param("show_punch", bool, default=True, description="`ShowPunch` 档。"),
            Param("show_profile", bool, default=True, description="`ShowProfile` 档。"),
            Param("show_center", bool, default=True, description="`ShowCenter` 档。"),
            Param("link_to_part", bool, default=True, description="`LinkToPart` 档。"),
        ],
        doc="成形工具：在钣金面上压出成形特征（需先选面）。"
        "★ **成形工具**（官方 `IFeatureManager::InsertFormToolFeature`，★ **9 参**）—— "
        "★★ **会新建特征**（非只读）✓ "
        "★★★ **前置有两处，★ 而它们都会「静默失败」**（★ 本仓栽过的形态）："
        "★ **① 官方 `## Remarks` 逐字要求先选一个面** —— ★ 我第一版没选 ⇒ 回 `None` ✗，"
        "★ **而「没选」与「建不出来」长得一模一样** ✓；"
        "★ **② 前置是钣金件** —— ★ 而建钣金件的契约是 "
        "`create_base_flange(model, sketch_ref, spec: BaseFlangeSpec)` ✗，"
        "★ **不是** `(model, sketch, thickness, …)`，★ 且它**不抛、只回 `None`** ✓ "
        "★★ **判据 = 回读**：★ 特征树增量（★ 不看返回值 —— 事实 8）✓；"
        "★ 且**两处前置各自单列布尔**（`tool_file_exists` / `selection_count`）—— "
        "★★ 因为「读数无效」与「真的不建」长得一样 ✓ "
        "★ 真机建成读数：★ `circular emboss1` ✓",
    ),
]
