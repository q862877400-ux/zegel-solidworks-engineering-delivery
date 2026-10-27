"""★ 批次 100：规格 213 · B1 —— A 类 6 项「实现已有、只差 ToolSpec」。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）
# 文件:   `specs/213-hook-up-tools/spec.md` + `plan.md` + `tasks.md`
# 定位:   ★ 规格 213 的 **B1**。★ 起因：★★ `docs/user-feature-coverage.md` 只量三列里的
# **第一列「有入口」**，★ 而它的来源是 `register_capabilities.all_specs()` 的**工具名集
# 合** ✓
#   ★★★ 实测：★ 规格 211 做成 `verified` 的能力**没有任何 ToolSpec 引用它们** ✗ ⇒
#     ★★ 从「用户可发现、可调用」口径看它们**等于不存在** ✓
#     （★ 装配域做了爆炸直线 + SpeedPak 两个 verified ⇒ 覆盖率**仍 5/10** ✓）
# 本批:   ★★ **A 类 6 项 —— `scripts/` 里已有可复用实现，本批只加声明** ✓：
#     `section_properties`(sw_mass_property.py:237) · `scale_feature`(sw_part.py:732) ·
# `untrim_surface`(sw_surface_features.py:1084) · `sweep_surface`(sw_surface_features.py
# :1195) ·
#     `weldment_trim`(sw_weldment.py:146) · `flat_pattern_dxf`(sw_export.py:250) ✓
#   ★★ 形状照 `tool_specs_batch99.py`；★ 基线工具数 **448** ⇒ 本批应到 **454** ✓
# 官方依据: 各能力的官方页三样已在规格 211 逐条读过（★ 见 `capabilities.yaml` 各条的
#   `source_evidence` 与 `evidence`）✓ —— ★ 本文件**只做声明**、不重读官方页 ✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **6 个工具** ⇒ 工具数 448 → **454**
# ★★ **参数命名要过的两道既有门禁**（★ 规格 212 的产出）：
# ★ 规则 2：★ 长度 `_mm` · ★ 角度 `_deg`；★ 且 `_BARE_COORD_NAMES = {x,y,z,point,coordin
# ate}`
#     ⇒ ★★ `scale_feature` 的 `x`/`y`/`z` 是**无量纲缩放比例**（★ 不是坐标 ✗）——
#        本批**照原样声明**，★ 由 `check_spec` 裁定；★ 若被拦 ⇒ ★ 改用 `param_alias` 改名 ✓
#   ★ 规则 2b：★ 名字带单位后缀 ⇒ 描述必须有单位词；★ 无量纲 ⇒ 名字不许带单位后缀 ✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH100"]


SPECS_BATCH100 = [
    #: ── ① 截面属性（★ 规格 211 B1-1 · **⚠ 原标"只读"是错的，2026-10-07 订正**）──────
    ToolSpec(
        name="solidworks_section_properties",
        title="Section Properties (mass-property readback)",
        module="sw_mass_property",
        function="section_properties",
        inject="model",
        #: ★★★ 2026-10-07（接手轮 · 规格 216）**`read_only` 由 `True` 改成 `False`** ——
        #: ★★ 依据是**台账明文裁定**（`capabilities.yaml` 的 `section_properties` 条目逐
        #: 字）：
        #:     「★★ **有副作用**：★ 官方写「**This method clears the selection set**」＋
        #: 「objects in the `Sections` parameter **are added to** the current selection
        #: set」
        #:       ⇒ ★★ **它清空并重写选择集** ⇒ ★ 按**规格 210** 的效应声明体系，
        #:       ★ **它不许被标 `read_only`** ✓」
        #:   ★★ 实测复核（2026-10-07）：★ 这里原先**显式**写的是 `read_only=True` ✗ ——
        #:     而 `tool_registry.effective_read_only` 的**判序第一是「显式声明优先」**
        #: （`explicit = getattr(spec, "read_only", None); if explicit is not None: retu
        #: rn bool(explicit)`）
        #:     ⇒ ★★ 那句显式声明**直接覆盖了派生** ⇒ ★ 于是台账的裁定**被架空**
        #:     （★ 而**没有任何门禁**在守它 —— 已实测确认）✗
        #:   ⚠ 为什么不能靠改效应表解决：★ 它是**生成物**（表头逐字 `★ 不要手改`），
        #:     而它的静态判据**只用「动词这一路」**（其 `_limitations` 自述）⇒
        #: ★★ **看不见只写在官方 `## Remarks` 里的副作用**（"clears the selection set"
        #: 不是动词写）
        #:     ⇒ ★ 故效应表里那条 `writes: []` 是**欠近似**（★ 但**它是生成物、不改**）✓
        #: ★★ 正解：★ **人判（有官方 Remarks 引文的那一判）显式覆盖** ⇒ 写 `read_only=Fa
        #: lse` ✓
        #: ⚠ `state_classes` **本来就含 `selection`** ⇒ ★ 这条副作用**在体系的语义之内**
        #: ，
        #:     只是**静态判据抓不到** ⇒ ★ 不是"体系没设计"，是"这一路看不见" ✓
        read_only=False,
        params=[],
        evidence=(
            "★★ **⚠ 不是只读**：★ 官方 Remarks 逐字「**This method clears the selection set**」⇒ ★ 它会**清空并重写当前"
            "选择集**（★ 按规格 210 的效应体系，`selection` 也是状态类之一）。★ **截面属性**（官方 `IModelDocExtension:"
            ":GetSectionProperties2`，★ 以**当前选择集**求值）—— ★★★ **单位那件事已查实并登记在册**：官方 `## Returns` "
            "说 `square meters`，★ 而**真机读数相反** —— 20×20×20 正方体端面读 **400**（= 20×20 的 **mm²**）、★ 侧面读 "
            "**0.4**（差 1000 倍）⇒ ★★ **不是面积换算** ✓ ★ 本工具因此**把单位未确证这件事如实带在返回里**（`units_veri"
            "fied` / `unit_caveat`），★★ 与 `docs/history/unit-conflicts.md` 第 1 条、第 3 条同源 ✓ ★ 用法：★ 先选面（"
            "或让它在整件上求值）⇒ ★ 读回截面属性 ✓"
        ),
        doc=(
            "Read the section properties of the current selection. Not read-only: the official member clears and rewrit"
            "es the selection set, and the returned area unit is unverified, so treat it as a number without a unit."
        ),
    ),
    #: ── ② 缩放 / 变形（★ 规格 211 B1-2 · 写）────────────────────────────────
    ToolSpec(
        name="solidworks_scale_feature",
        title="Scale Feature (InsertScale)",
        module="sw_part",
        function="insert_scale",
        inject="model",
        #: ★★★ 2026-10-07（本批真机门禁的裁定）：★ 原名 `x`/`y`/`z` **被规则 3 拦下** ✗
        #: ——
        #: ★ 逐字：「规则 3 违反：工具 `solidworks_scale_feature` 的入参 `x` 是**裸坐标*
        #: *
        #:   —— 必须改用具名实体 + 声明式 selection」✓
        #:   ★★ 而它们**其实是无量纲缩放比例**、★ **不是坐标** ✗ ⇒
        #: ★ **改名成 `*_factor`**（★ 语义更准 ✓）+ ★ **用 `param_alias` 把它们映射回函
        #: 数形参**
        #: （★ `make_tool_function` 逐字：`target = spec.param_alias.get(p.name, p.name)
        #: ` ✓）✓
        param_alias={"x_factor": "x", "y_factor": "y", "z_factor": "z"},
        params=[
            Param(
                "scale_type",
                int,
                default=1,
                description=(
                    "Scale type passed to the official call; 0, 1 and 2 are the values this repository has verified. De"
                    "faults to 1."
                ),
            ),
            Param(
                "uniform",
                bool,
                default=True,
                description="Whether the three directions share one factor; true uses only x_factor. Defaults to true.",
            ),
            Param(
                "x_factor",
                float,
                default=2.0,
                description="Scale ratio along X, dimensionless, where 2.0 doubles the body. Defaults to 2.0.",
            ),
            Param(
                "y_factor",
                float,
                default=2.0,
                description="Scale ratio along Y, dimensionless. Defaults to 2.0.",
            ),
            Param(
                "z_factor",
                float,
                default=2.0,
                description="Scale ratio along Z, dimensionless. Defaults to 2.0.",
            ),
        ],
        evidence=(
            "缩放/变形：按比例缩放实体，新建一个缩放特征。★ **缩放 / 变形**（官方 `IFeatureManager::InsertScale`，**参"
            "数式、无 ACL**）—— ★★ **会新建一个缩放特征**（非只读）✓ ★★★ **判据用体积比、★ 不是查返回值**：★ 因子 3.0 ⇒"
            " 真机回读 **`volume_ratio = 27.0`**、★ `volume_ok = True` ✓ —— ★★ 比值**无量纲** ⇒ ★ **不受单位影响**，★ "
            "那是设计选择被实证的结果 ✓ ★ 默认特征名 **`缩放比例1`**（★ 官方/UI 惯例）✓ ⚠ ★ **三个 `_factor` 语义的参数"
            "**：★ 它们是**无量纲比例**、★ 不是坐标 ⇒ ★ 别按毫米传（★ 传 1000 得 1000 倍）✓"
        ),
        doc=(
            "Create a scale feature that scales the body by the given factors. It writes a new feature into the active "
            "part; the factors are dimensionless ratios, so 2.0 doubles the body and 0.5 halves it."
        ),
    ),
    #: ── ③ 取消剪裁（★ 规格 211 B2-1 · 写）──────────────────────────────────
    ToolSpec(
        name="solidworks_untrim_surface",
        title="Untrim Surface (reverse of trim)",
        module="sw_surface_features",
        function="untrim_surface_report",
        inject="model",
        params=[
            Param(
                "face_untrim_type",
                int,
                default=0,
                description=(
                    "Face untrim option from the official enum, listed in the returned face_untrim_types table; default"
                    "s to 0."
                ),
            ),
            Param(
                "edge_untrim_type",
                int,
                default=0,
                description=(
                    "Edge untrim option from the official enum, listed in the returned edge_untrim_types table; default"
                    "s to 0."
                ),
            ),
            Param(
                "distance_mm",
                float,
                default=0.0,
                description=(
                    "Extension distance in millimetres; the official parameter gives no unit, so the millimetre reading"
                    " is an assumption reported back. Defaults to 0.0."
                ),
            ),
            Param("merge", bool, default=True, description="Whether to merge the resulting surfaces; defaults to true."),
            Param(
                "trim_opposite_side",
                bool,
                default=False,
                description="Whether to untrim the opposite side as well; defaults to false.",
            ),
        ],
        evidence=(
            "取消剪裁：把被剪裁的曲面还原回原始范围，新建特征。★ **取消剪裁**（官方 `IFeatureManager::InsertUntrimSurfa"
            "ce`）—— ★★ **会新建特征**（非只读）✓ ★★ **它是「剪裁曲面」的另一半**：★ 剪裁曲面判「不做（后端受限，事实 4"
            "19）」，★ 而取消剪裁**补了包装**并有真机读数 ⇒ ★ 登记 **`stitched`** ✓ ★ 判据：★ **返回体里带 `unt_type` "
            "两个枚举表 + 特征树增量** ✓ ⚠ ★ 本工具的**正例（真的建出被取消剪裁的曲面）尚未做** —— ★ 需要先有一条「造出"
            "被剪裁的曲面」的链 ✓ ⇒ ★★ 如实标 `stitched`、★ 不许写成 `verified` ✓"
        ),
        doc=(
            "Untrim a surface so a trimmed face or edge grows back, adding that as a new feature. It writes a feature i"
            "nto the active part, works only on surface parts with the face or edges preselected, and its positive case"
            " has not been built on this machine yet."
        ),
    ),
    #: ── ④ 扫描曲面（★ 规格 211 B2-2 · 写 · 本规格里唯一 verified 的曲面项）──
    ToolSpec(
        name="solidworks_sweep_surface",
        title="Sweep Surface (InsertSweepSurface2, path B)",
        module="sw_surface_features",
        function="sweep_surface_report",
        inject="model",
        params=[
            Param("propagate", bool, default=True, description="Official propagate flag; defaults to true."),
            Param(
                "twist_ctrl", int, default=0, description="Official twist control option value; defaults to 0."
            ),
            Param(
                "keep_tangency",
                bool,
                default=True,
                description="Official keep-tangency flag; defaults to true.",
            ),
            Param(
                "advanced_smoothing",
                bool,
                default=False,
                description="Official advanced-smoothing flag; defaults to false.",
            ),
            Param(
                "start_matching",
                int,
                default=0,
                description="Official start matching type value; defaults to 0.",
            ),
            Param(
                "end_matching",
                int,
                default=0,
                description="Official end matching type value; defaults to 0.",
            ),
            Param(
                "path_align",
                int,
                default=0,
                description=(
                    "Official path alignment value, meaningful only with certain twist control options; defaults to 0."
                ),
            ),
            Param(
                "use_feat_scope",
                bool,
                default=False,
                description="Official feature scope flag; defaults to false.",
            ),
            Param(
                "use_auto_select",
                bool,
                default=True,
                description=(
                    "Official auto-select flag; false means the caller must select the bodies. Defaults to true."
                ),
            ),
            Param(
                "twist_angle_deg",
                float,
                default=0.0,
                description="Twist angle in degrees, meaningful only with a twist option; defaults to 0.0.",
            ),
            Param(
                "merge_smooth_faces",
                bool,
                default=False,
                description="Official merge-smooth-faces flag; defaults to false.",
            ),
        ],
        evidence=(
            "扫描曲面：按轮廓 + 路径生成一张曲面（参数式，不需 ACL）。★★★ **扫描曲面**（官方 `IFeatureManager::InsertSw"
            "eepSurface2`，**参数式 11 参、不要求 `AccessSelections`**）—— ★★ **会新建曲面体**（非只读）✓ ★★★★ **本能力"
            "是实证「事实 237」的那一条**：★「**不做曲面族**」那条结论**只覆盖半条路** —— 官方有**两条**建曲面的入口，★"
            " 而**第二条从没试过** ✓ ⇒ ★★ **路 A**（`CreateDefinition` + `CreateFeature`）★ 静默回 `None` ✗；★ **路 B（"
            "本工具）真机建成 `曲面-扫描1`** ✓✓ ★★★ **前置是硬性的、★ 且只有官方 `## Remarks` 说得清**：★ 调之前**必须*"
            "*用 `SelectByID2` 按 mark 选 —— ★ **1 = Profile** · ★ 2 = Guide（有才给）· ★ **4 = Sweep path** ✓；★ **没"
            "选时静默回 `None`**（★ 不抛、★ 特征树不变）⇒ ★ 调用方拿到 `None` 时**先查 mark** ✓ ★★ **已试形态的边界**（"
            "★ 逐条带读数、★ 不许推广）：★ **可做** —— 直线路径（无引导线）✓ · **带引导线（mark 2）**✓；★ **试死** —— *"
            "*闭合路径**（圆作路径，前置已完全对上仍静默回 `None`）✗ ★ 仍未试：`twist_ctrl` 各档 · `path_align` 各档 · "
            "多引导线 · 开放轮廓 · `propagate` 档 ✓"
        ),
        doc=(
            "Create a swept surface from a profile and a path, and report the new feature. It writes a surface feature "
            "into the active part; the profile must be selected with mark 1 and the path with mark 4, a closed path is "
            "known to fail, and a missing selection returns nothing without raising."
        ),
    ),
    #: ── ⑤ 裁剪 / 延伸焊件（★ 规格 211 B3-1 · 写）────────────────────────────
    ToolSpec(
        name="solidworks_weldment_trim",
        title="Weldment Trim/Extend (InsertWeldmentTrimFeature2)",
        module="sw_weldment",
        function="insert_weldment_trim_report",
        inject="model",
        params=[
            Param(
                "end_cond",
                int,
                default=0,
                description=(
                    "End condition from the weldment end-condition enum: 0=none, 1=miter, 2=butt1, 3=butt2, 4=trim, 5=u"
                    "se default. Defaults to 0."
                ),
            ),
            Param(
                "options",
                int,
                default=0,
                description="Option bits combined as a logical sum: 1, 2, 4 and 8. Defaults to 0.",
            ),
            Param(
                "gap_mm",
                float,
                default=0.0,
                description=(
                    "Trim gap in millimetres; the official parameter gives no unit, so the millimetre reading is an ass"
                    "umption reported back. Defaults to 0.0."
                ),
            ),
        ],
        evidence=(
            "裁剪/延伸焊件：按 mark 选体与边界，修整焊件体。★ **裁剪/延伸焊件**（官方 `IFeatureManager::InsertWeldmentT"
            "rimFeature2`，**参数式 5 参**）—— ★ **会改/新建焊件体**（非只读）✓ ★★ **前置只有官方 `## Remarks` 说得清**"
            "：★ `SelectByID2` 按 mark 选 —— ★ **1 = Body or bodies to trim** · ★ **2 = Trimming boundaries (body **or "
            "face**)** ✓ ★★★ **真机读数（★ 三处成因逐条追过）**：★ ① 前置 ✓（焊件特征建了 · 两个相交体在）· ★ ② mark ✓"
            "（1 = 体[按生成体的特征名] · 2 = 面，两条都 `True`）· ★ ③ 档位 ✓（`end_cond` 四档 × `options` 两档 = **8 "
            "组全试**）⇒ ★★ **而特征树一次都没变** ✗ ⇒ ★ **判「在后端到不了建成」** ✓ ★★★★ **本批最值钱的教训就在这条里"
            "**：★ 第三步**第一次跑**的八组读数**全部无效** ✗ —— 因为 `select_entity_by_index` 的 `append` **默认 `Fals"
            "e`**，★ **它清空了 mark 1 的体** ✗；★★ **而「读数无效」的样子与「真的不建」一模一样** ✗ ⇒ ★ **若没为每处前"
            "置单独落布尔字段，就会把无效读数当结论写进登记表** ✓"
        ),
        doc=(
            "Skip this tool, NOT USABLE on this machine: trimming or extending weldment bodies adds no feature. It woul"
            "d write a weldment trim feature after you select the bodies with mark 1 and the boundaries with mark 2, bu"
            "t eight measured option combinations left the feature tree unchanged."
        ),
    ),
    #: ── ⑥ 展开图导出 DXF（★ 规格 211 D 项 · 用户授权 · 写文件）──────────────
    ToolSpec(
        name="solidworks_export_flat_pattern_dxf",
        title="Export Flat Pattern DXF (with authorized temporary save)",
        module="sw_export",
        function="export_flat_pattern_dxf",
        inject="model",
        writes=[("file", "dxf")],
        params=[
            Param("output_path", str, description="Absolute target DXF path."),
            Param(
                "include_bend_lines", bool, default=True, description=(
                                                              "Whether to write the bend lines. Defaults to true."
                                                          )
            ),
            Param(
                "include_sketches", bool, default=False, description=(
                                                             "Whether to write the sketches. Defaults to false."
                                                         )
            ),
            Param(
                "include_hidden_edges",
                bool,
                default=False,
                description="Whether to write hidden edges. Defaults to false.",
            ),
            Param(
                "include_bounding_box",
                bool,
                default=False,
                description="Whether to write the bounding box. Defaults to false.",
            ),
            Param(
                "merge_coplanar_faces",
                bool,
                default=False,
                description="Whether to merge coplanar faces. Defaults to false.",
            ),
            Param(
                "allow_temporary_save",
                bool,
                default=False,
                description=(
                    "Whether to save the unsaved part into temporary_save_dir first so the official precondition holds."
                    " Defaults to false, which keeps the previous behaviour."
                ),
            ),
            Param(
                "temporary_save_dir",
                str,
                default=None,
                description=(
                    "Directory for that temporary save; must stay inside this repository. Defaults to output/_temp_save"
                    "."
                ),
            ),
        ],
        evidence=(
            "导出钣金展开图 DXF（可临时另存以补齐官方前置）。★ **钣金展开图导出 DXF**（官方 `IModelDoc2::ExportToDWG2` "
            "+ `swExportToDWG_SHEET_METAL`）—— ★★ **会写文件**；★ 在 `allow_temporary_save=True` 且零件未保存时**还会临"
            "时另存一个零件** ✓ ★★★ **判据 = 一正两负**（★ 事实 62：★ 门禁只靠负例证明 ✓）：★ **负例①** 默认 ⇒ **抛 `Va"
            "lueError`**、★ 且**错误里点名那个开关** ✓；★★ **负例②** 授权了、★ 但目录**在仓库外** ⇒ **抛 `ValueError`**"
            "、★ **且拒绝发生在另存之前**（`_save_as` 一次都没被调）✓ · ★ 且**没在用户目录建任何东西** ✓；★★★ **正例** "
            "授权 + 仓库内目录 ⇒ 临时另存 + 导出成功，★ **回读 DXF 存在且 20219 字节** ✓ ★ 临时零件**不删** —— ★ 删数据"
            "是红线；★ 用完的去留由人决定 ✓"
        ),
        doc=(
            "Export the sheet-metal flat pattern of the active part to a DXF file for cutting. Writes the file, and ref"
            "uses to run unless the part is already saved or allow_temporary_save is true."
        ),
    ),
]
