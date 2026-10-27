# ── 200 轮计划 v3 · 段 2：**焊件族的第一条**（结构构件）───────────────────────────────
# ─
# ★★★★ 2026-10-03（轮 428）★ 来源：★ 本轮的**侦察推翻了**一条既有结论。
#
# ★★ **为什么它以前没挂**（★ 而原因**早就写在能力表里**）：
#   ```
#   capabilities.yaml 的 weldment_cut_list 条目（轮 364）：
#   「真因查明：**本机没装「焊件轮廓库」（Weldment Profiles）** ⇒ 所以报
#     「没有可写入切割清单的结构构件实体」**不是代码问题**，而是**建不出结构构件**」
#   ```
# ★★★ **而本轮按 AGENTS.md 的顺序查第一现场时，发现那条不成立了**：
#   ```
#   ✓ 在：C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\weldment profiles
#   ⇒ **111 个** `.sldlfp`（ansi / **GB** / iso / DIN / JIS / BSI / CISC / AS …）
#   ```
#   ⇒ ★★ **即：★ 前置现在是**齐的**** —— ★ 而轮 364 那条结论**已在本轮更新** ✓
#
# ★★ **真机**（`tools/prove_structural_member.py`，★ 走 `sw_guard`，★ 无弹窗）：
#   ```
#   path_sketch        ok=True  草图1
#   entry_check        ok=True  segment_count = 1
#   structural_member  ok=True  feature = **"square-rods (1)"**（★ GB 方管轮廓）
#                               new_type_names = **["WeldMemberFeat", "WeldmentFeature"]** ✓
#   ```
#   ⇒ ★★★ **而判据是**特征树**（★ 与段 1 的 `Count` **完全不同**的一条判据家族）✓
#     ★ 证据 `output/structural-member-evidence.json` 的 `verdict: pass`
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch62.py —— 本文件（新）
# 定位:   把 `create_structural_member_from_sketch` 挂成 MCP 工具。
# 官方依据: `IFeatureManager.InsertStructuralWeldment5` · `ISketch.GetSketchSegments()`
#           （★ 0 参）·
#   `IFeature.GetSpecificFeature2`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec

SPECS_BATCH62 = [
    # 签名: def create_structural_member_from_sketch(model, sketch_name, profile_path, *
    # *kwargs)
    ToolSpec(
        name="solidworks_weldment_create_structural_member",
        title="Create a Structural Member",
        module="sw_weldment",
        function="create_structural_member_from_sketch",
        inject="model",
        params=[
            Param(
                "sketch_name",
                str,
                description=(
                    "Name of the path sketch that the member is swept along, exactly as it appears in the feature tree."
                ),
            ),
            Param(
                "profile_path",
                str,
                description=(
                    "Absolute path of a .sldlfp weldment profile; this machine keeps 111 profiles under the SOLIDWORKS "
                    "weldment profiles folder."
                ),
            ),
        ],
        evidence=(
            "Create a **STRUCTURAL MEMBER** (weldment) along a path sketch with a weldment profile, and return a READ-B"
            "ACK report. ★★ **判据是特征树**（★ 不是计数）：`new_type_names` 应含 `WeldmentFeature` 与 `WeldMemberFeat`"
            "。⚠ 本机需要装「焊件轮廓库」—— ★ 本机**有**（111 个 `.sldlfp`）。"
        ),
        doc=(
            "Create a structural member along a path sketch with a weldment profile, then read the feature tree back. I"
            "t writes a weldment feature into the active part; the profile is an absolute .sldlfp path, and this machin"
            "e has the weldment profile library installed."
        ),
    ),
]
