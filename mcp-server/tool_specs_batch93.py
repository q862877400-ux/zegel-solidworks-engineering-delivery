"""★ 批次 93：规格 209 · 钣金展开/折叠/折边（3 个工具）—— ★ 前两个真机过、折边是**负结论**。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   `scripts/sw_sheet_metal.py`（本轮追加段）
# 定位:   ★ 规格 `specs/209-union-adopt-18/`：**B2-1（idx 336 unfold）** · **B4-4（idx
#            155 fold）** ·
#         **B4-2（idx 173 hem）**。★ 三条都落在**已有模块** `sw_sheet_metal.py`（铁律 3）✓
# 官方依据: ★★ 逐页读过 —— 见 `scripts/sw_sheet_metal.py` 本轮追加段的来源块：
#   `IModelDoc2\{InsertSheetMetalUnfold,InsertSheetMetalFold}.md` ·
# `IFeatureManager\{InsertSheetMetalHem2,CreateCustomBendAllowance,GetFlatPatternFolder}
# .md` ·
#   `IFlatPatternFolder\{GetFlatPatternCount,GetFlatPatterns}.md` ·
#   `ISelectionMgr\{SetSelectedObjectMark,GetSelectedObjectMark}.md` ·
# `enums\{swHemTypes_e,swHemPositionTypes_e,swSheetMetalReliefTypes_e,swReliefTearTypes_
# e,
#   swSelectionMarkAction_e}.md` ·
#   ★★ 两份官方示例（**mark 与调用序的唯一出处**）：
#     `examples\Insert_and_Access_Fold_Feature_Example_VB.md` ·
#     `examples\Insert_Sheet_Metal_Hem_Example_VB.md`
# 许可:   本仓库 MIT。★ 无第三方代码引入（全部按官方签名与官方示例自建）。
# 规模:   **3 个工具** ⇒ 工具数 439 → **442**
# ★★ **本批的诚实边界（别把它读成「三个都成了」）**：
# · `create_unfold` / `create_fold` —— ★ **真机建成了**（`展开1` / `折叠1`，marks 逐条 `
# [1, 4]`）✓
#   · `create_hem` —— ★★ **真机回 `None`（五种形态全部失败）** ⇒ 能力标 `stitched`，
# 工具**仍然挂出来**（★ 与既有 4 个失败入口同策：★ 由 `require_verified` 在**调用前**抛*
# *带原因**的错误，
#     而不是让用户吃一个裸 COM 错误）✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH93"]

#: ★ 面序号 = **本仓的声明式选择**（★ 面**不能按名字选** —— 事实 32）⇒ 不是"裸坐标"（规
#: 则 3）✓
_FACE_INDEX = (
    "**固定面**在体上的序号（0 基）—— ★ 本仓的**声明式选择**："
    "★ 事实 32 实测**面不能按名字选** ⇒ 只能按**序号/对象**选；"
    "★★ 序号顺序**官方未承诺稳定**（与体的拓扑生成顺序有关）⇒ **别当持久引用**。"
)

_BENDS = (
    "要展开/折叠的**实体特征名**（逗号分隔）—— ★ 可以留空："
    "★★ **真机实测：留空（只给固定面 mark 1）也能建出 `展开1`** ⇒ "
    "★ 官方示例里那些折弯是「照着做」、**不是必需的** ✓"
)

SPECS_BATCH93 = [
    # ── ① 展开（idx 336）—— ★ 真机建成 ────────────────────────────────────────────────
    ToolSpec(
        name="solidworks_sheet_metal_create_unfold",
        title="Insert an Unfold Feature (sheet metal)",
        module="sw_sheet_metal",
        function="create_unfold",
        inject="model",
        params=[
            Param(
                "bend_feature_names",
                str,
                description=(
                    "Comma separated bend feature names to select with mark 4; a real machine builds the unfold even wh"
                    "en this is empty, but the argument has no default, so pass an empty string to leave it out."
                ),
            ),
            Param("face_index", int, default=0, description=(
                                                    "Zero-based index of the face to keep fixed; face order is not guar"
                                                    "anteed stable across rebuilds. Defaults to 0."
                                                )),
        ],
        evidence=(
            "★ **插入展开特征**（官方 `IModelDoc2::InsertSheetMetalUnfold()`，**零参**）—— ★★ **真机建成 `展开1`**（202"
            "6-10-06 · SW 2026 SP4.1）✓ ★★ **选择契约（照官方示例，不是猜的）**：固定面 **mark 1** + 实体特征 **mark 4*"
            "*；★ 而**面不能按名字选**（事实 32）⇒ 面走 `IEntity.Select4` **再补 mark**（★ `Select4` 没有 mark 形参 ⇒ "
            "用 `ISelectionMgr::SetSelectedObjectMark`）✓ ★★ **一个必须知道的坑**：`SetSelectedObjectMark` 的第 3 参是 "
            "`swSelectionMarkAction_e`，**要传 `swSelectionMarkSet`(0)** —— 传 `-1` 会**静默不生效**（返回 `false`、**"
            "不报错**）⇒ ★ 那正是本仓第一轮「没建出来」的原因 ✓ ★ 判据（规则 6，全回读）：**特征树增量 + 平展型式个数 +"
            " 逐条 mark** —— ★ 它回 `void`，**只能靠回读** ✓"
        ),
        doc=(
            "Insert an unfold feature so the sheet-metal part shows its flat pattern. Writes the feature and does not s"
            "ave; a fixed face is picked by index with selection mark 1, and success is judged by the feature tree and "
            "the flat-pattern count."
        ),
    ),
    # ── ② 折叠（idx 155）—— ★ 真机建成 ────────────────────────────────────────────────
    ToolSpec(
        name="solidworks_sheet_metal_create_fold",
        title="Insert a Fold Feature (sheet metal)",
        module="sw_sheet_metal",
        function="create_fold",
        inject="model",
        params=[
            Param("bend_feature_names", str, default="", description=(
                                                             "Comma separated bend feature names to select with mark 4;"
                                                             " leaving it empty still builds the feature on a real mach"
                                                             "ine. Defaults to empty."
                                                         )),
            Param("face_index", int, default=0, description=(
                                                    "Zero-based index of the face to keep fixed; face order is not guar"
                                                    "anteed stable across rebuilds. Defaults to 0."
                                                )),
            Param(
                "unfold_feature_name",
                str,
                default="",
                description=(
                    "Name of an existing unfold feature to select with mark 0 before folding; empty means none is selec"
                    "ted. Defaults to empty."
                ),
            ),
        ],
        evidence=(
            "★ **插入折叠特征**（官方 `IModelDoc2::InsertSheetMetalFold()`，**零参**）—— ★★ **真机建成 `折叠1`**（`unfo"
            "ld → fold` 一条链，★ 与官方示例同形）✓ ★★ 选 `unfold_feature_name` 的那一步**必须在 `ClearSelection2` 之后"
            "** —— ★ 本仓第一版把它放在调用前 ⇒ 会被选择函数开头的清选区**清掉**（★ 顺序错、静默失效）✓ ★ 其余同 `solid"
            "works_sheet_metal_create_unfold`（mark 表 / 判据 / 坑）✓"
        ),
        doc=(
            "Insert a fold feature to close a flat pattern back into its bent state. Writes the feature and does not sa"
            "ve; the unfold feature is selected with mark 0 after the selection is cleared, and a fixed face is picked "
            "by index with mark 1."
        ),
    ),
    # ── ③ 折边（idx 173）—— ★★ 真机**失败** ⇒ 挂出来但**调用前就抛带原因的错误** ──────
    # ────────
    ToolSpec(
        name="solidworks_sheet_metal_create_hem",
        title="Insert a Hem on Selected Edges (KNOWN UNAVAILABLE on this backend)",
        module="sw_sheet_metal",
        function="create_hem",
        inject="model",
        params=[
            Param(
                "edge_selector",
                str,
                description=(
                    "Declarative edge selector: 'index:<n>' for the n-th edge on the body, or '__current_selection__' t"
                    "o reuse the selection; edges cannot be selected by name."
                ),
            ),
            Param(
                "hem_type",
                str,
                default="open",
                description=(
                    "Hem shape: open (0), closed (1), teardrop (2), rolled (3) or double (4). Defaults to 'open'."
                ),
            ),
            Param(
                "position",
                str,
                default="outside",
                description=(
                    "Hem position, 'inside' or 'outside', where the numeric values 0 and 1 come from the factory type l"
                    "ibrary. Defaults to 'outside'."
                ),
            ),
            Param(
                "reverse", bool, default=False, description="Whether to reverse the direction. Defaults to false."
            ),
            Param(
                "length_mm",
                float,
                default=0.01,
                description="Hem length in millimetres. Defaults to 0.01.",
            ),
            Param(
                "gap_mm",
                float,
                default=0.01,
                description="Gap in millimetres, used only by the open hem. Defaults to 0.01.",
            ),
            Param(
                "angle_deg",
                float,
                default=0.0,
                description="Hem angle in degrees, used only by teardrop and rolled hems. Defaults to 0.",
            ),
            Param(
                "radius_mm",
                float,
                default=0.005,
                description="Hem radius in millimetres, used only by teardrop and rolled hems. Defaults to 0.005.",
            ),
            Param(
                "miter_gap_mm",
                float,
                default=0.0011,
                description="Mitre gap in millimetres. Defaults to 0.0011.",
            ),
            Param(
                "use_default_relief",
                bool,
                default=False,
                description="Whether to use the default relief cut. Defaults to false.",
            ),
            Param(
                "relief",
                str,
                default="obround",
                description=(
                    "Relief shape: rectangular (1), tear (2), obround (3), none (4) or tear_bend (5). Defaults to 'obro"
                    "und'."
                ),
            ),
            Param(
                "relief_tear",
                str,
                default="rip",
                description="Tear relief style: rip (1) or extend (2). Defaults to 'rip'.",
            ),
            Param(
                "use_relief_ratio",
                bool,
                default=True,
                description="Whether the relief is sized by a ratio. Defaults to true.",
            ),
            Param(
                "relief_ratio",
                float,
                default=1.0,
                description="Relief ratio. Defaults to 1.",
            ),
            Param(
                "relief_width_mm",
                float,
                default=0.0,
                description="Relief width in millimetres. Defaults to 0.",
            ),
            Param(
                "relief_depth_mm",
                float,
                default=0.0,
                description="Relief depth in millimetres. Defaults to 0.",
            ),
            Param(
                "k_factor",
                float,
                default=0.5,
                description="K factor of the custom bend allowance. Defaults to 0.5.",
            ),
        ],
        evidence=(
            "★★★ **本工具在本机（SW 2026 SP4.1 + pywin32）建不出折边** —— **五种形态全部回 `None`**：边选择（`index:0` "
            "/ 最长边）× 长度口径（0.01 / 10.0）× 卸料槽（自定义 / 默认）× 板厚（0.002 箔片 / **2.0 真厚度**）⇒ ★ 按事"
            "实 53 **停止**、**不当场继续凑形态** ✓ ★ 而**成员名与 16 参顺序、五个枚举值已逐条核对官方无误**；官方 `## "
            "Remarks` 的四步前置（`CreateCustomBendAllowance` → 初始化 → 赋 `PCBA` → **再**选边）**已照做**，仍 `None` "
            "✓ ★★ **它的价值在别处**（裁决书原话：「dp5 的发现**比实现本身更值**」）：别家调的 `InsertHemFeature2` 在官"
            "方全树**零命中**（真名 `InsertSheetMetalHem2`）、且把 `Open=0`/`Closed=1` **正好互换**、**漏掉 `Double=4`*"
            "* —— ★ 这三处已做成**常量表 + 静态断言**（见 `tests/test_tool_specs_batch93.py`）✓ ⚠ **调用它会抛 `Runtime"
            "Error` 并写明原因**（`require_verified`）—— ★ 那不是缺陷，是**不让用户吃裸 COM 错误**的设计 ✓"
        ),
        doc=(
            "Skip this tool, NOT USABLE on this machine: every hem shape returns nothing, so no hem is created. It woul"
            "d write a hem feature on one selected edge and does not save the document, and calling it raises an error "
            "naming the reason unless the unverified probe path is explicitly allowed."
        ),
    ),
]
