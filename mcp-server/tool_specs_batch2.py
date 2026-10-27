"""第二批 MCP 工具声明（核心建模域里**能干净暴露**的那些）+ 其余函数的**分类**。

## ⚠⚠ 本批最重要的产出不是声明，而是**那个分类**
第一轮枚举说「32 个模块 / 229 个候选动作函数」，评估说「真实工作量 ~120 个」。
**看清签名之后，这个数是乐观的。** 核心建模域的公开函数按「能否干净暴露」分四类：

| 类 | 形状 | 例子 | 缺什么才能暴露 |
|---|---|---|---|
| **A 能直接暴露** | 只收标量/字符串/bool，宿主对象靠注入 | `weldment_evidence(model)` | 无 —— **本批收的就是这些** |
| **B 要「声明式选择解析」** | 收**坐标向量** | `create_planar_surface(sw_app, point, normal)
` | 规则 3 要求声明式选择 ⇒ 需要一层「选择器 → 坐标」（已有雏形：`sw_simulation.select_face_by_selector`，
但那只覆盖**面**，不覆盖**点/方向**） |
| **C 要「spec 展平层」** | 收 **typed spec 对象** | `create_base_flange(model, sketch_ref, spec: BaseFlangeSpec)
` | 要把 `BaseFlangeSpec` 的字段展平成 MCP 入参（**字段多且带默认值** ⇒ 需要**读 dataclass 定义**逐个抄，不能猜） |
| **D 不该暴露** | 纯 getter / 拿中间对象 | `get_sketch_segments(sketch)`、`merge_points(sketch, tol)
` | 它们是**内部读**或**需要「取 sketch」的解析** —— 用户不会直呼；
暴露它们只会把工具的**选择集状态**变成 API（违规则 3 的精神） |

**⇒ 修正后的估计**：能**直接**暴露的（A 类）远少于 120；
B/C 两类**各自需要一层基础设施**，那是**独立的工作项**，不是「多写几条声明」。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植）
# 文件:   mcp-server/tool_specs_batch2.py
# 定位:   `docs/history/T-011-expose-capabilities-assessment.md` 第二批。
#         参数**逐条照真实签名抄**（守卫测试用 `inspect.signature` 核）。
# 官方签名依据: 不适用（只做参数搬运；被搬运函数的依据在其源码来源块里）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ **尚未接入 `mcp-server/server.py`**（单源原则，已知事实 24）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH2", "CLASSIFICATION"]

#: ⚠ 参数逐条照真实签名抄，签名出处：
#: `Select-String scripts/sw_weldment.py    -Pattern '^def (weldment_evidence|ensure_cut
#: _list|update_cut_list|create_sub_weld_folder)'`
#:   `Select-String scripts/sw_sheet_metal.py -Pattern '^def sheet_metal_evidence'`
#:   `Select-String scripts/sw_surface.py     -Pattern '^def collect_surface_evidence'`
SPECS_BATCH2: list[ToolSpec] = [
    # ── 焊件（A 类：只收 model + 标量）─────────────────────────────
    # 签名: def weldment_evidence(model, *, create_missing_cut_list: bool = False,
    #                             update_cut_list_too: bool | None = None) -> dict[str, Any]
    #: ★★★★★★ 2026-10-04（轮 117）**补 `update_cut_list_too`** —— ★ 处置这条**存量失败**
    #:  ✓
    #:   ★ **真机读数**（★ `tests/test_tool_specs_batch2.py` 逐字）：
    #:     「工具 `solidworks_weldment_evidence` 折算后 `['create_missing_cut_list']`
    #:       ≠ `sw_weldment.weldment_evidence` 的真实形参
    #:       `['create_missing_cut_list', 'update_cut_list_too']`」✓
    #: ★★ **真因**：★ 实现**加了**带默认值的关键字参数 `update_cut_list_too: bool | None
    #:  = None`、
    #:     而 **ToolSpec 没跟上** ⇒ ★★★ **⇒ 同一个病**（★ 与 `batch1` 那条同轮同因）✓
    #:   ★★★★ **⇒ 已补**（★ 默认值与实现一致 = `None`）✓
    ToolSpec(
        name="solidworks_weldment_evidence",
        title="Collect Weldment Evidence",
        module="sw_weldment",
        function="weldment_evidence",
        inject="model",
        params=[
            Param(
                "create_missing_cut_list",
                bool,
                default=False,
                description=(
                    "Whether to create a missing cut list before reading, which creates cut-list folders in the model. "
                    "Defaults to false, which keeps the call read-only."
                ),
            ),
            #: ★ 新增（★ 与实现同步）：★ 只读回读时是否**顺带刷新**切割清单 ✓
            Param(
                "update_cut_list_too",
                bool,
                default=None,
                description=(
                    "Whether to refresh the cut list as well, a write operation; unset follows create_missing_cut_list."
                    " Defaults to unset."
                ),
            ),
        ],
        evidence=(
            "Read back the weldment state: structural members, cut-list folders, and their quantity/length/angle/source"
            " properties. Read-only when create_missing_cut_list is False."
        ),
        doc=(
            "Read back the weldment state: features, cut-list folders and their properties. Read-only by default, and i"
            "t writes to the model only when create_missing_cut_list or update_cut_list_too asks for a cut-list update,"
            " which the returned wrote_model flag reports."
        ),
    ),
    # 签名: def ensure_cut_list(model) -> list[Any]
    ToolSpec(
        name="solidworks_weldment_ensure_cut_list",
        title="Ensure Weldment Cut List",
        module="sw_weldment",
        function="ensure_cut_list",
        inject="model",
        params=[],
        evidence=(
            "Create the cut list if it is missing, and return the cut-list folders."
        ),
        doc=(
            "Create native cut-list folders for a weldment that has none, grouping bodies by their longest bounding-box"
            " edge. Creates the folders in the active part; when cut-list folders already exist it returns them unchang"
            "ed instead of recreating them."
        ),
    ),
    # 签名: def update_cut_list(model) -> list[dict[str, Any]]
    ToolSpec(
        name="solidworks_weldment_update_cut_list",
        title="Update Weldment Cut List",
        module="sw_weldment",
        function="update_cut_list",
        inject="model",
        params=[],
        evidence=(
            "Refresh the cut list and return the updated folders."
        ),
        doc=(
            "Refresh every native cut-list folder and return folder-level geometry evidence. Modifies the cut list in t"
            "he active part, because the official call updates the automatically generated list; each returned row carr"
            "ies the update flag and the folder properties."
        ),
    ),
    # 签名: def create_sub_weld_folder(model, folder=None)
    # ⚠ `folder` 是 `Object`（一个已有的切割清单文件夹）⇒ **故意不暴露**
    #   —— MCP 表面无法表达「传一个已存在的对象」。
    ToolSpec(
        name="solidworks_weldment_create_sub_weld_folder",
        title="Create Sub-weldment Folder",
        module="sw_weldment",
        function="create_sub_weld_folder",
        inject="model",
        omitted_params=("folder",),
        params=[],
        evidence=(
            "Create a sub-weldment folder in the active weldment part."
        ),
        doc=(
            "Create a weldment sub-folder in the feature tree of the active document. Modifies that feature tree by ins"
            "erting the folder, and it raises when the insert call returns no feature, so read the tree back to confirm"
            "."
        ),
    ),
    # ── 钣金（A 类：只收 model）────────────────────────────────────
    # 签名: def sheet_metal_evidence(model) -> dict[str, Any]
    ToolSpec(
        name="solidworks_sheet_metal_evidence",
        title="Collect Sheet Metal Evidence",
        module="sw_sheet_metal",
        function="sheet_metal_evidence",
        inject="model",
        params=[],
        read_only=True,
        evidence=(
            "Read back the sheet-metal state of the active part: thickness, bend radius, bend allowance settings, flat-"
            "pattern state. Read-only. VERIFIED ON A REAL MACHINE: run 2026-10-01 on SW 2026 SP4.1 and it read back cor"
            "rectly (thickness_m=0.002, has_base_flange=True, all_solid_bodies_are_sheet_metal=True)."
        ),
        doc=(
            "Read the sheet-metal evidence of the active part: feature list, base flange parameters and per-body flags."
            " Read-only, and the base flange lengths come back in metres; use the all_solid_bodies_are_sheet_metal flag"
            " to check that the part really is a sheet-metal part."
        ),
    ),
    # ── 曲面（A 类：收 sw_app）─────────────────────────────────────
    # 签名: def collect_surface_evidence(sw_app) -> dict[str, Any]
    ToolSpec(
        name="solidworks_surface_evidence",
        title="Collect Surface Evidence",
        module="sw_surface",
        function="collect_surface_evidence",
        inject="sw_app",
        params=[],
        read_only=True,
        evidence=(
            "Read back the surface bodies on the active document: counts and types. Read-only."
        ),
        doc=(
            "Read the surface evidence: whether the Modeler object is reachable and which surface creation methods are "
            "registered. Read-only; it reports reachability and the registered entry points, not surface body counts, a"
            "nd it records that the process-internal pointer variants are unavailable to this binding."
        ),
    ),
]


#: 核心建模域的**函数分类**（供后续批次按类推进；**不是**「没做」，是「各需一层基础设施
#: 」）。
#:
#: ⚠ 这张表是**判断**，不是机器判定的 —— 每一类的**判据**写在下面，可复核。
CLASSIFICATION: dict[str, dict[str, list[str]]] = {
    "A_直接可暴露": {
        "判据": "只收标量/字符串/bool；宿主对象（model/sw_app/study）靠 inject",
        "weldment": [
            "weldment_evidence",
            "ensure_cut_list",
            "update_cut_list",
            "create_sub_weld_folder",
        ],
        "sheet_metal": ["sheet_metal_evidence"],
        "surface": ["collect_surface_evidence"],
        "topology": [
            "create_topology_study",
            "collect_topology_evidence",
            "run_topology_study",
        ],
        "mold": [
            "insert_parting_line",
            "insert_shut_off_surface",
            "mold_draft_analysis",
            "mold_evidence",
        ],
    },
    "B_需声明式选择解析": {
        "判据": "入参含**坐标/向量**（point / normal / axis / origin）⇒ 违规则 3",
        "surface": [
            "create_planar_surface",
            "create_cylindrical_surface",
            "create_spherical_surface",
            "create_conical_surface",
            "create_toroidal_surface",
            "create_offset_surface",
            "create_extrusion_surface",
            "create_revolution_surface",
            "create_ruled_surface",
            "create_swept_surface",
            "create_bspline_surface",
            "create_coons_b_surface",
            "create_sheet_from_surface",
        ],
        "缺的基础设施": (
            "「选择器 → 坐标/向量」解析层。**已有雏形**"
            "（`sw_simulation.select_face_by_selector` 覆盖**面**），"
            "但不覆盖**点**（原点/质心/顶点）与**方向**（法向/轴向）。"
            "⇒ 这是一个**独立工作项**，不是「多写几条声明」。"
        ),
    },
    "C_需spec展平层": {
        "判据": "入参含 **typed spec dataclass**（BaseFlangeSpec / OneBendSpec / …）",
        "sheet_metal": [
            "create_base_flange",
            "create_one_bend",
            "create_edge_flange",
            "create_draft",
            "create_gusset",
            "create_swept_flange",
        ],
        "缺的基础设施": (
            "把 dataclass 字段**逐个抄**成 MCP 入参（含默认值与单位换算）。"
            "⚠ **不能猜字段** —— 要读 `scripts/sw_sheet_metal.py` 里的 dataclass 定义。"
            "另：这类函数多**依赖调用方已选好实体**（`sketch_ref` / `face_ref` / `path_ref`）"
            "⇒ 同时需要 B 类的选择解析。"
        ),
    },
    "D_不该暴露": {
        "判据": "纯内部读（getter）或需要「取中间对象」的解析；用户不会直呼",
        "sketch": [
            "get_sketch_segments",
            "get_lines",
            "get_arcs",
            "get_ellipses",
            "get_parabolas",
            "get_polylines",
            "get_splines",
            "get_sketch_points",
            "get_user_points",
            "get_contour_edges",
            "get_sketch_contours",
            "get_sketch_regions",
            "get_sketch_hatches",
            "get_sketch_slots",
            "get_sketch_pictures",
            "get_sketch_paths",
            "get_sketch_block_instances",
            "get_relation_manager",
            "is_3d_sketch",
            "get_model_to_sketch_transform",
            "merge_points",
            "set_automatic_solve",
            "as_sequence",
        ],
        "理由": (
            "它们是**内部读**或**需要「取 sketch」的解析**。"
            "暴露它们等于把工具的**选择集状态**变成 API（违规则 3 的精神）。"
            "**用户要的是「这个草图完整吗」「改个尺寸」这类动作**，"
            "而那类动作一旦要做，应当**新写**面向意图的工具，而不是把 getter 搬出来。"
        ),
    },
}
