"""★ B6-b 曲面特征的声明式工具（★ 只登记**真机建成**的那些）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（ToolSpec 声明层）
# 文件:   mcp-server/tool_specs_batch69.py
# 定位:   ★ 2026-10-03（轮 476）★ `specs/201-toolbar-gaps` 的 **B6-b**。
# 实现层在 `scripts/sw_surface_ref_ops.py`；★ 真机证据 `output/b6b-surface-ref-evidence.
# json`。
#
#   ==================  ==========================================  ==================
#   工具栏原文           官方成员                                      真机
#   ==================  ==========================================  ==================
# 放样曲面             `IModelDoc2.InsertLoftRefSurface2`            ✅ **建成**（树 7→8
# ）
# 旋转曲面             `IFeatureManager.InsertRevolvedRefSurface`   ❌ 前置未成 ⇒ **本批
# 不登记**
#   ==================  ==========================================  ==================
#
# ★★★ **为什么旋转曲面不登记**（★ 这是本仓 A4 的口径：`verified` **必须有我们自己的运行
# 证据**）：
#     · 真机试过 **4 种**前置（选草图特征 / 轮廓 mark=0 / 轮廓 mark=1 + 中心线 mark=4 /
#       用本仓 `_select_revolve_axis` + `_ensure_sketch_selected`）—— **都没建成**（树 6→6）。
#     · ★ 最后那次量到 **`轴选中数 = 5`** ⇒ ★ `_select_revolve_axis` 把该草图里**所有段**
#       都按 `mark=4` 选上了（矩形 4 边 + 中心线）⇒ ★ **轴不唯一** ⇒ 这才是没建成的直接原因。
#     · ★ 而实体版 `sw_part.revolve_boss` 用同一句 `_select_revolve_axis` 却**是成的**
#       （★ 它走 `FeatureRevolve2`，★ 与本条的 `InsertRevolvedRefSurface` 是**两条特征路**）
#       ⇒ ★ 差别在哪**还没查清**。
#     ⇒ ★ 按**事实 53**（同一处连续 ≥3 次没稳就停下）**停下**，
#       ★ **不登记成工具**、★ 也不写进 `verified` —— ★ **不假装做到** ✓
#     ★ 下一轮的线索：查 `_select_revolve_axis` 为什么选到 5 段（★ 它按 `EXTSKETCHSEGMENT`
#       类型名判据取段，★ 而中心线**可能也是** `EXTSKETCHSEGMENT`，★ 或矩形边被误纳）。
#
# ★ 判据 = **特征树叶子名增量**（`sw_part.feature_names`）—— ★ 本条官方回 `void`。
# ★ 规则 2（`_mm`/`_deg` 只在边界换算一次）· 规则 3（★ 参数是标志/数量，**不是裸坐标**）
# ·
#   规则 6（★ 实现层回带 `verified_by` 的 dict）。
#
# 官方依据（三源）:
#   · `C:\\swapi\\types\\IModelDoc2\\InsertLoftRefSurface2.md`
#     （6 参 `void`；★ "profile selections should be **1**"）
#   · `C:\\swapi\\types\\IModelDoc2\\InsertLoftRefSurface.md`（★ **Obsolete** 那一行）
# · `C:\\swapi\\types\\IFeatureManager\\InsertRevolvedRefSurface.md`（★ 未登记，仅存依据
# ）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
# ★★ 2026-10-03（轮 476）**我自己在这里栽了一下，值得留一行**：
#   头部 docstring **第 1 行就闭合了**（`"""★ … 声明式工具。"""`），★ 而我又在来源块之后
#   **多写了一个 `"""`** ⇒ 它开了个新字符串、把后面全吞掉
#   ⇒ `SyntaxError: unterminated triple-quoted string literal`。
#   ★ AGENTS.md §「新建 .py 的模板」记的是**忘了闭合**那一形态（"同一处栽了七次"），
#     而这次是**镜像**：**多写了一个闭合符**。⇒ 两种都靠同一个模板形态消掉：
#     **docstring 只一行、来源块紧跟、末尾不要再补三引号**。

from __future__ import annotations

from tool_registry import Param, ToolSpec

_BATCH69: list[ToolSpec] = [
    ToolSpec(
        name="solidworks_insert_lofted_ref_surface",
        title="Insert Lofted Reference Surface",
        module="sw_surface_ref_ops",
        function="insert_lofted_ref_surface",
        inject="model",
        param_alias={
            k: k
            for k in (
                "closed",
                "keep_tangency",
                "force_non_rational",
                "tess_tolerance_factor",
                "start_matching_type",
                "end_matching_type",
            )
        },
        params=[
            Param(
                "closed",
                bool,
                description=(
                    "Whether to close the loft; a closed loft needs at least three profiles. Defaults to false."
                ),
                required=False,
                default=False,
            ),
            Param(
                "keep_tangency",
                bool,
                description="Whether to keep tangency where the section curves are tangent. Defaults to true.",
                required=False,
                default=True,
            ),
            Param(
                "force_non_rational",
                bool,
                description="Whether to force a non-rational surface. Defaults to false.",
                required=False,
                default=False,
            ),
            Param(
                "tess_tolerance_factor",
                float,
                description=(
                    "Tessellation tolerance factor for a centerline loft; 0.0 uses the default. Defaults to 0.0."
                ),
                required=False,
                default=0.0,
            ),
            Param(
                "start_matching_type",
                int,
                description=(
                    "Tangency matching type for the start profile; the official page gives no value table, so it is pas"
                    "sed through as an integer. Defaults to 0."
                ),
                required=False,
                default=0,
            ),
            Param(
                "end_matching_type",
                int,
                description=(
                    "Tangency matching type for the end profile, passed through the same way as start_matching_type. De"
                    "faults to 0."
                ),
                required=False,
                default=0,
            ),
        ],
        evidence=(
            "★ 放样曲面：`IModelDoc2.InsertLoftRefSurface2(…)`（6 参，回 `void`）。⚠ 官方 Remarks 逐字：「The mark for:"
            " **profile selections should be 1**」⇒ ★ **调用前把轮廓按 `mark=1` 选好**（★ 且**按期望的顺序**）。★ 真机"
            "建成：树 7→8，新增 `曲面-放样1`。★ 用的是 `…RefSurface2`（★ `…RefSurface` 官方标 **Obsolete**，铁律 4）。"
        ),
        doc=(
            "Create a lofted reference surface from profiles that are already selected. Writes a surface feature into t"
            "he active part and does not save the document; select the profiles with selection mark 1 and in the order "
            "you want them lofted. The call returns void, so success is judged by the feature tree gaining a feature."
        ),
    ),
]

#: ★★ 注册器按 `SPECS_*` 找
SPECS_BATCH69 = _BATCH69
