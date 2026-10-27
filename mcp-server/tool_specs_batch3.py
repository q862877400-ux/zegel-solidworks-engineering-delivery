"""第三批 MCP 工具声明（**C 类里能干净暴露的那两个**）+ C 类的**精确分类**。

## ⚠⚠ 本批的核心发现：C 类不止「spec 展平」一件事，还有**三种互不相同的 ref 约定**
逐一读 `scripts/sw_sheet_metal.py` 的函数体后（**不是猜**）：

| 函数 | ref 参数 | 约定 | 能否现在暴露 |
|---|---|---|---|
| `create_base_flange` | `sketch_ref` | **草图名**（转给 `sw_part._ensure_sketch_selected`） | ✅ |
| `create_one_bend` | `sketch_ref` | **草图名**（同上） | ✅ |
| `create_edge_flange` | 无 | 文档串：「调用前必须先用 `_select_by_id` 把目标边入选区」⇒ **要求调用方先选好** | ⛔ 需「选择」入参 + 选择步 |
| `create_gusset` | 无 | 同上（吃当前选区） | ⛔ 同上 |
| `create_draft` | `face_ref` | **对象** | ⛔ 需「选择 → 对象」桥 |
| `create_swept_flange` | `path_ref` / `profile_ref` | **对象**（文档串明写「官方示例用 `SelectByRay` 选边后 `GetSelectedObject6(1,-1)` 取得」） | ⛔ 同上 |

**⇒ 修正后的判据：C 类不是「展平 spec 就完了」，还要按 ref 约定再分三小类。**
**⇒ 6 个里只有 2 个能现在暴露。** 另 4 个需要的「selection」概念**正是规则 3 要求的形态**，
  但那需要一个**能按名字/类型选边、选面**的解析层 —— 与本档 §8.3 记的 B 类**同源**，
  且 `_ensure_sketch_selected` 已示范了它的样子（**按名字选，且支持 `__current_selection__`**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植）
# 文件:   mcp-server/tool_specs_batch3.py
# 定位:   `docs/history/T-011-expose-capabilities-assessment.md` §9.2 分类表里 C 类的落地（能
#           做的部分）。
#         参数**逐条照真实签名与 dataclass 定义抄**（守卫测试用 `inspect.signature` + `dataclasses.fields` 核）。
# 官方签名依据: 不适用（只做参数搬运；被搬运函数的依据在其源码来源块里）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ **尚未接入 `mcp-server/server.py`**（单源原则，已知事实 24）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH3", "SHEET_METAL_SPEC_MAP"]


def _consumed(*names: str) -> dict:
    """构造 `param_alias`：**这些入参由 `derived_args` 消费，不传给目标函数**。

    ⚠ 为什么必须显式：注册器会把每个声明参数当 kwarg 传给目标函数，
    而 spec 字段（如 `thickness_mm`）目标函数**并不接受** ⇒ 不标记就 `TypeError`。
    **⇒ 显式，不靠猜**（本项目一贯纪律）。
    """
    return {n: None for n in names}


#: 长度字段 → 米（spec 的 docstring 明写「长度单位为米」，而 MCP 表面按规则 2 用 `_mm`）
_MM = 0.001


def _base_flange_spec(p):
    """把展平后的标量入参装回 `BaseFlangeSpec`（**长度 mm→m，只做一次**）。"""
    from scripts.sw_sheet_metal import BaseFlangeSpec

    return BaseFlangeSpec(
        thickness=float(p.thickness_mm) * _MM,
        bend_radius=float(p.bend_radius_mm) * _MM,
        depth=float(p.depth_mm) * _MM,
        k_factor=float(p.k_factor),
        relief_ratio=float(p.relief_ratio),
        reverse_direction=bool(p.reverse_direction),
        reverse_thickness=bool(p.reverse_thickness),
    )


def _one_bend_spec(p):
    """把展平后的标量入参装回 `OneBendSpec`（**长度 mm→m、角度已是度**）。"""
    from scripts.sw_sheet_metal import OneBendSpec

    return OneBendSpec(
        bend_radius=float(p.bend_radius_mm) * _MM,
        angle=float(p.angle_deg),
        reverse_direction=bool(p.reverse_direction),
        use_default_radius=bool(p.use_default_radius),
    )


#: ⚠ 参数逐条照**真实签名 + dataclass 字段**抄，出处：
#: `Select-String scripts/sw_sheet_metal.py -Pattern '^def create_(base_flange|one_bend)
#: '`
#: `Select-String scripts/sw_sheet_metal.py -Pattern '^class (BaseFlangeSpec|OneBendSpec
#: )'`
SPECS_BATCH3: list[ToolSpec] = [
    # 签名: def create_base_flange(model, sketch_ref, spec: BaseFlangeSpec)
    #     BaseFlangeSpec: thickness, bend_radius, depth, k_factor=0.42,
    #                     relief_ratio=0.5, reverse_direction=False, reverse_thickness=False
    ToolSpec(
        name="solidworks_sheet_metal_create_base_flange",
        title="Create Sheet Metal Base Flange",
        module="sw_sheet_metal",
        function="create_base_flange",
        inject="model",
        # `spec` 是 dataclass ⇒ 由 `derived_args` 从展平入参装回；
        # `sketch_ref` 在实现里收**草图名**（转给 `sw_part._ensure_sketch_selected`）
        # ⚠ `spec` **不写进 param_alias** —— 它根本不是声明参数（由 derived_args 提供）
        # 。
        #   第一版写了 `{"spec": None}` ⇒ 门禁红：「param_alias 指向未声明的参数」。
        # `sketch_name` 是实现里的 `sketch_ref`（显式别名）。
        param_alias=dict(
            {"sketch_name": "sketch_ref"},
            **_consumed(
                "thickness_mm",
                "bend_radius_mm",
                "depth_mm",
                "k_factor",
                "relief_ratio",
                "reverse_direction",
                "reverse_thickness",
            ),
        ),
        derived_args=lambda p: {"spec": _base_flange_spec(p)},
        params=[
            Param(
                "sketch_name",
                str,
                description="Sketch NAME. The special value '__current_selection__' reuses the "
                "current selection instead of selecting by name.",
            ),
            Param(
                "thickness_mm",
                float,
                description="Sheet thickness in MILLIMETRES (must be > 0).",
            ),
            Param(
                "bend_radius_mm",
                float,
                description="Bend radius in MILLIMETRES (>= 0).",
            ),
            Param(
                "depth_mm",
                float,
                description="Base flange depth in MILLIMETRES (must be > 0).",
            ),
            Param(
                "k_factor",
                float,
                default=0.42,
                description="K-factor for the bend allowance (must be strictly between 0 and 1).",
            ),
            Param(
                "relief_ratio",
                float,
                default=0.5,
                description="Relief ratio (must be > 0).",
            ),
            Param(
                "reverse_direction",
                bool,
                default=False,
                description="Reverse the depth direction.",
            ),
            Param(
                "reverse_thickness",
                bool,
                default=False,
                description="Reverse which side the thickness is added to.",
            ),
        ],
        evidence=(
            "Create a native base flange (swFmBaseFlange) from an open or closed sketch. Returns the real IFeature; fai"
            "lures raise instead of returning empty. ⚠⚠ **正确性边界（2026-10-04 更正，★ 处置 JUDGE-C_D_E 🔴 #2 · E-1 #"
            "4）**：★ **只有闭轮廓**真机跑通（2026-10-01，SW 2026 SP4.1，特征树出现「钣金6 / 基体-法兰1 / 平展型式6」）"
            "；★★ **开放折线（轮廓法兰）真机失败** —— `CreateFeature(IBaseFlangeFeatureData) 创建失败`（2026-10-01 补测"
            "）。★★★ **旧描述（已作废）**：本节此前写「An open polyline path produces a profile flange … VERIFIED ON A "
            "REAL MACHINE … and it WORKED」，那是把**闭轮廓**的成功**外推**到了开放折线上 —— 而状态表明写 **`True` 仅对"
            "闭轮廓成立**。⇒ ★ **以 `scripts/sw_sheet_metal.py::SHEET_METAL_RUNTIME_STATUS` 为准**（★ 它是第一现场）。"
        ),
        doc=(
            "Create a native base flange (swFmBaseFlange) from an open or closed sketch. Returns the real IFeature; failures raise instead of returning empty. "
            "⚠⚠ **正确性边界（2026-10-04 更正，★ 处置 JUDGE-C_D_E 🔴 #2 · E-1 #4）**："
            "★ **只有闭轮廓**真机跑通（2026-10-01，SW 2026 SP4.1，特征树出现「钣金6 / 基体-法兰1 / 平展型式6」）；"
            "★★ **开放折线（轮廓法兰）真机失败** —— `CreateFeature(IBaseFlangeFeatureData) 创建失败`（2026-10-01 补测）。"
            "★★★ **旧描述（已作废）**：本节此前写「An open polyline path produces a profile flange … VERIFIED ON A REAL MACHINE … and it WORKED」，"
            "那是把**闭轮廓**的成功**外推**到了开放折线上 —— 而状态表明写 **`True` 仅对闭轮廓成立**。"
            "⇒ ★ **以 `scripts/sw_sheet_metal.py::SHEET_METAL_RUNTIME_STATUS` 为准**（★ 它是第一现场）。"
        ),
    ),
    # 签名: def create_one_bend(model, sketch_ref, spec: OneBendSpec)
    #     OneBendSpec: bend_radius, angle, reverse_direction=False, use_default_radius=True
    ToolSpec(
        name="solidworks_sheet_metal_create_one_bend",
        title="Create Sheet Metal One Bend",
        module="sw_sheet_metal",
        function="create_one_bend",
        inject="model",
        param_alias=dict(
            {"sketch_name": "sketch_ref"},
            **_consumed(
                "bend_radius_mm", "angle_deg", "reverse_direction", "use_default_radius"
            ),
        ),
        derived_args=lambda p: {"spec": _one_bend_spec(p)},
        params=[
            Param(
                "sketch_name",
                str,
                description="Sketch NAME; '__current_selection__' reuses the current selection.",
            ),
            Param("bend_radius_mm", float, description="Bend radius in MILLIMETRES."),
            Param(
                "angle_deg",
                float,
                description="Bend angle in DEGREES (the spec is already in degrees).",
            ),
            Param(
                "reverse_direction",
                bool,
                default=False,
                description="Reverse the bend direction.",
            ),
            Param(
                "use_default_radius",
                bool,
                default=True,
                description="Use the part default bend radius instead of bend_radius_mm.",
            ),
        ],
        evidence=(
            "Create a single sheet-metal bend on the selected sketch. ⚠ **仍不可用，但原因已具体化**（2026-10-04 更正，"
            "★ 处置 JUDGE-C_D_E 🔴 #2 · E-1 #1）。★★ **旧描述（已作废）**：`CreateDefinition(33) returned None` · 「The"
            " correct call shape has not been determined yet」——★ 那是**旧结论**：状态表把它标为「原记法」。★★★ **现在"
            "的事实**：正确入口**已查明并已改用** —— `swFmSketchBend(35)`（接口 `ISketchedBendFeatureData`），真机已验"
            "证 `CreateDefinition(35)` 返回**非 None**；⚠ 仍缺「选中折弯线 / 固定面」这一步 ⇒ **仍标不可用**，但**卡点"
            "不是「形状未查明」**。⇒ ★ **以 `scripts/sw_sheet_metal.py::SHEET_METAL_RUNTIME_STATUS` 为准**（★ 第一现场"
            "）。★ 本工具保留，是为了让失败**可诊断**，不是因为能用。"
        ),
        doc=(
            "Create a single sheet-metal bend on the selected sketch. ⚠ **仍不可用，但原因已具体化**（2026-10-04 更正，★ 处置 JUDGE-C_D_E 🔴 #2 · E-1 #1）。"
            "★★ **旧描述（已作废）**：`CreateDefinition(33) returned None` · 「The correct call shape has not been determined yet」——"
            "★ 那是**旧结论**：状态表把它标为「原记法」。"
            "★★★ **现在的事实**：正确入口**已查明并已改用** —— `swFmSketchBend(35)`（接口 `ISketchedBendFeatureData`），"
            "真机已验证 `CreateDefinition(35)` 返回**非 None**；"
            "⚠ 仍缺「选中折弯线 / 固定面」这一步 ⇒ **仍标不可用**，但**卡点不是「形状未查明」**。"
            "⇒ ★ **以 `scripts/sw_sheet_metal.py::SHEET_METAL_RUNTIME_STATUS` 为准**（★ 第一现场）。"
            "★ 本工具保留，是为了让失败**可诊断**，不是因为能用。"
        ),
    ),
]


#: C 类的**精确分类**（三小类）—— 供后续批次按类推进；**不是**「没做」，是「各需一层」。
SHEET_METAL_SPEC_MAP: dict[str, dict] = {
    "C1_spec展平即可": {
        "判据": "ref 参数不存在，或 ref 在实现里就是**名字**（字符串）",
        "函数": ["create_base_flange", "create_one_bend"],
        "状态": "**已做**（本文件 SPECS_BATCH3）",
    },
    "C2_需调用方先选好": {
        "判据": "函数**没有 ref 参数**，实现直接吃**当前选区** ⇒ 文档串要求调用前先选",
        "函数": ["create_edge_flange", "create_gusset"],
        "缺的基础设施": "「选择」入参 + 在调用前完成选择的步骤。"
        "★ 好消息：`sw_part._ensure_sketch_selected` 已示范了这个形态"
        "（**按名字选**，且支持特殊的 `__current_selection__`）"
        "⇒ 照它做一个「按名字/类型选边、选面」的解析层即可复用同一套设计。",
    },
    "C3_ref是对象": {
        "判据": "ref 参数在实现里是**已取到的 COM 对象**（文档串明写 GetSelectedObject6 取得）",
        "函数": ["create_draft", "create_swept_flange"],
        "缺的基础设施": "「选择 → 对象」桥：先按声明式规则选中，再 `GetSelectedObject6(1, -1)` 取出。"
        "与 C2 的解析层**同源**，可以一次做成。",
    },
}
