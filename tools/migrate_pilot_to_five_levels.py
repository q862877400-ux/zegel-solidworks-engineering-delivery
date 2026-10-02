"""@brief `pilot` → 五级迁移（`docs/capabilities-schema-proposal.md` §1.2，裁断走选项 A）。

一次做完，缺一即数据与门禁不自洽：

1. 13 条 `pilot` 且有 `verified_versions` → `verified` + 补 `evidence`
   （跑过，这是事实；`evidence` 是真实测试文件，已逐个实跑确认）
2. 6 条 `pilot` 且 `verified_versions` 为空 → `stitched`
3. `allowed_modes` 值域扩为 interactive / reviewed / unattended；
   **原 8 条 `verified` 补 `unattended`，原 19 条 `pilot` 不补**
4. `schema_version` 1.0 → 2.0

**等价性**：迁移前 `unattended_allowed()` 为真的是原 8 条 `verified`；
迁移后带 `unattended` 的仍是那 8 条 ⇒ 集合逐条相同（由
`tests/test_unattended_equivalence.py` 守）。

用法：`python tools/migrate_pilot_to_five_levels.py [--apply]`（默认 dry-run）。
"""
# ── 来源 ──
# 仓库:   本项目自身（执行方对上游能力清单的迁移改造，非第三方移植）
# 文件:   tools/migrate_pilot_to_five_levels.py
# 定位:   docs/capabilities-schema-proposal.md §1.2（`pilot`→五级迁移，裁断走选项 A）
#         与 §五 R11；AGENTS.md 铁律 1「每加一个能力必须能指认出处」。
# 许可:   本仓库 MIT。本文件为原创实现，无第三方代码引入。
# ⚠ 未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）。本次是清单形状与授权判据的迁移，
#   不改变任何 COM 调用；授权等价性由 tests/test_unattended_equivalence.py 对冻结基线守住。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────


from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "capabilities.yaml"

# 13 条有运行证据的 pilot：capability_id → evidence 条目（真实测试文件，已实跑确认全绿）
MIGRATE_TO_VERIFIED: dict[str, list[str]] = {
    "external_spur_gear_geometry": ["pytest tests/test_cad_reliability.py（外部直齿锥齿轮几何）"],
    "parameter_updates": ["pytest tests/test_cad_reliability.py（参数更新回读）"],
    "custom_properties_and_bom": ["pytest tests/test_cad_reliability.py（自定义属性与 BOM）"],
    "pack_and_go": [
        "pytest tests/test_sw_delivery.py",
        "pytest tests/solidworks_week3_delivery_regression.py（Pack and Go 交付）",
    ],
    "motion_study": ["pytest tests/test_sw_motion_audit.py（旋转马达创建与结果审计）"],
    "drawings_and_bom": [
        "pytest tests/test_delivery_compare.py",
        "pytest tests/test_drawing_subskill.py（工程图与 BOM）",
    ],
    "headless_open_format_writing": [
        "pytest tests/test_headless_cad_writer.py",
        "pytest tests/test_mcp_headless_open_format.py（OCP 无头写出）",
    ],
    "configurations_and_design_tables": ["pytest tests/test_cad_reliability.py（配置与设计表）"],
    "sheet_metal": [
        "pytest tests/test_sw_sheet_metal.py",
        "pytest tests/solidworks_sheet_metal_regression.py（钣金）",
    ],
    "weldments": ["pytest tests/test_cad_reliability.py（焊件）"],
    "simulation_and_fea": ["pytest tests/test_fea_analysis.py（CalculiX / Elmer 求解链）"],
    "autocad_script_backend": ["pytest tests/test_acad_script_backend.py（AutoCAD 脚本后端）"],
    "autocad_dotnet_backend": ["pytest tests/test_acad_dotnet_preflight.py（AutoCAD .NET 预检）"],
}

# 6 条无运行证据的 pilot → stitched
MIGRATE_TO_STITCHED: tuple[str, ...] = (
    "dfm_checks",
    "surface_modeling",
    "mold_tools",
    "autocad_headless_preview",
    "dxf_preview_scene",
    "routing",
)

# 原 8 条 verified 的 evidence（B4 要求每条 verified 都有）
EXISTING_VERIFIED_EVIDENCE: dict[str, list[str]] = {
    "requirements_planning": ["pytest tests/test_engineering_orchestrator.py（需求阶段与阶段编目）"],
    "solidworks_addin_host": ["pytest tests/test_cad_reliability.py（加载项宿主状态）"],
    "part_and_features": ["pytest tests/test_cad_reliability.py（零件与特征）"],
    "holes_and_finishing": ["pytest tests/test_sw_hole_features.py（孔特征与修饰）"],
    "assembly_and_mates": [
        "pytest tests/test_sw_assembly_doc_contract.py",
        "pytest tests/test_sw_assembly_aliases.py（装配与配合）",
    ],
    "drawing_dimension_insertion": ["pytest tests/test_cad_reliability.py（工程图尺寸插入回读）"],
    "export_delivery": ["pytest tests/test_delivery_compare.py（导出交付）"],
    "geometry_and_delivery_review": ["pytest tests/test_delivery_compare.py（几何与交付复核）"],
}

UNATTENDED = "unattended"


def migrate(payload: dict) -> tuple[dict, list[str]]:
    """就地迁移并返回 (payload, 变更日志)。"""
    log: list[str] = []
    caps = payload["capabilities"]

    for item in caps:
        cid = item["id"]
        level = item.get("level")
        modes = list(item.get("allowed_modes") or [])
        vv = item.get("verified_versions") or []

        if level == "pilot" and cid in MIGRATE_TO_VERIFIED:
            item["level"] = "verified"
            item["evidence"] = list(MIGRATE_TO_VERIFIED[cid])
            log.append("pilot→verified  %-34s（有 vv=%s）" % (cid, vv))

        elif level == "pilot" and cid in MIGRATE_TO_STITCHED:
            item["level"] = "stitched"
            log.append("pilot→stitched  %-34s（vv 为空）" % cid)

        elif level == "verified":
            # 原 8 条：补 evidence，并补 unattended 授权
            if cid in EXISTING_VERIFIED_EVIDENCE:
                item["evidence"] = list(EXISTING_VERIFIED_EVIDENCE[cid])
            if UNATTENDED not in modes:
                modes.append(UNATTENDED)
                log.append("verified+unattended  %-30s" % cid)

        # 迁移过来的 13 条与 6 条 stitched / not_implemented 一律**不补** unattended
        if modes != (item.get("allowed_modes") or []):
            item["allowed_modes"] = modes

    # 只有原 8 条 verified 该带 unattended —— 逐条核对这条不变量
    original_verified = set(EXISTING_VERIFIED_EVIDENCE)
    for item in caps:
        has = UNATTENDED in (item.get("allowed_modes") or [])
        should = item["id"] in original_verified
        assert has == should, (
            "不变量破了：%s 的 unattended=%s，应为 %s" % (item["id"], has, should)
        )

    payload["schema_version"] = "2.0"
    log.append("schema_version 1.0 → 2.0")
    return payload, log


def main() -> int:
    apply = "--apply" in sys.argv
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))

    # ⚠ 迁移「前」的授权要按**旧判据**算：那时的 unattended_allowed() 是 `level == "verified"`。
    #   按 allowed_modes 算会得到 0 条（旧数据里根本没有 unattended 这个模式），
    #   那样比出来的是「0 → 8」，不是等价性。
    before_unattended = sorted(
        i["id"] for i in payload["capabilities"] if i.get("level") == "verified"
    )

    migrated, log = migrate(payload)

    # 迁移「后」按**新判据**算：allowed_modes 含 unattended。
    after_unattended = sorted(
        i["id"] for i in migrated["capabilities"] if "unattended" in (i.get("allowed_modes") or [])
    )

    print("变更（%d 条）：" % len(log))
    for line in log:
        print("   %s" % line)
    print()
    print("无人值守授权集合：")
    print("   迁移前 %d 条  %s" % (len(before_unattended), before_unattended))
    print("   迁移后 %d 条  %s" % (len(after_unattended), after_unattended))
    print("   ⇒ %s" % ("逐条相同 ✓" if before_unattended == after_unattended else "**不同 ✗**"))
    print()

    if not apply:
        print("[dry-run] 未写盘。加 --apply 落地。")
        return 0

    MANIFEST.write_text(
        json.dumps(migrated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("已写 %s" % MANIFEST)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
