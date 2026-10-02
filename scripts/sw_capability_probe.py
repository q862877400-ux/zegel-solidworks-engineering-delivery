"""@brief 探测本机 SolidWorks 类型库与高级机械能力，不修改任何 CAD 文档。"""
# ── 来源 ──
# 仓库:   本项目自身（执行方对上游能力清单的迁移改造，非第三方移植）
# 文件:   scripts/sw_capability_probe.py
# 定位:   docs/capabilities-schema-proposal.md §1.2（`pilot`→五级迁移，裁断走选项 A）
#         与 §五 R11；AGENTS.md 铁律 1「每加一个能力必须能指认出处」。
# 许可:   本仓库 MIT。本文件为原创实现，无第三方代码引入。
# ⚠ 未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）。本次是清单形状与授权判据的迁移，
#   不改变任何 COM 调用；授权等价性由 tests/test_unattended_equivalence.py 对冻结基线守住。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────


from __future__ import annotations

import argparse
import glob
import json
import os
from pathlib import Path

try:
    from .sw_preflight import import_com_dependencies, missing_com_dependencies, solidworks_installed
    from .capabilities import (
        UNATTENDED_MODE,
        backend_route_snapshot,
        capability_index,
        load_capabilities,
        manifest_path,
    )
    from .cad_installation import discover_installations
except ImportError:
    from sw_preflight import import_com_dependencies, missing_com_dependencies, solidworks_installed
    from capabilities import (
        UNATTENDED_MODE,
        backend_route_snapshot,
        capability_index,
        load_capabilities,
        manifest_path,
    )
    from cad_installation import discover_installations


TYPELIB_PATTERNS = {
    "solidworks_core": [
        r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS*\sldworks.tlb",
        r"E:\Solidworks\SOLIDWORKS\sldworks.tlb",
    ],
    "motion_study": [
        r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS*\swmotionstudy.tlb",
        r"E:\Solidworks\SOLIDWORKS\swmotionstudy.tlb",
    ],
    "routing": [
        r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS*\SWRoutingLib.tlb",
        r"E:\Solidworks\SOLIDWORKS\SWRoutingLib.tlb",
    ],
    "simulation_motion": [
        r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS*\cmotionswapi.tlb",
        r"E:\Solidworks\SOLIDWORKS\cmotionswapi.tlb",
    ],
}

CAPABILITY_KEYWORDS = {
    "part_and_features": ("IPartDoc", "IFeatureManager", "ISketchManager"),
    "assembly_and_mates": ("IAssemblyDoc", "IMateFeatureData"),
    "configurations": ("IConfigurationManager", "IConfiguration"),
    "drawings": ("IDrawingDoc", "IView", "ITableAnnotation"),
    "sheet_metal": ("ISheetMetalFeatureData", "IFlatPatternFeatureData"),
    "weldments": ("IStructuralMemberFeatureData", "IWeldmentCutListFeature"),
    "surface_modeling": ("ISurface", "IKnitSurfaceFeatureData"),
    "mold_tools": ("IMold", "ICavityFeatureData"),
    "motion_study": ("IMotionStudyManager", "IMotionStudy", "IMotionStudyResults"),
    "routing": ("IRouteManager", "IRouteProperty", "IAutoRoute"),
}

CAPABILITY_ALIASES = {
    "part_and_features": "part_and_features",
    "assembly_and_mates": "assembly_and_mates",
    "configurations": "configurations_and_design_tables",
    "drawings": "drawings_and_bom",
    "sheet_metal": "sheet_metal",
    "weldments": "weldments",
    "surface_modeling": "surface_modeling",
    "mold_tools": "mold_tools",
    "motion_study": "motion_study",
    "routing": "routing",
}


def _find_typelib(patterns: list[str]) -> Path | None:
    """@brief 从实际安装目录和兼容路径中返回第一个类型库。"""
    target_name = Path(patterns[0]).name if patterns else ""
    if target_name:
        for installation in discover_installations("solidworks"):
            executable = installation.get("executable")
            if not executable:
                continue
            path = Path(executable).parent / target_name
            if path.is_file():
                return path.resolve()
    for pattern in patterns:
        for raw_path in glob.glob(os.path.expandvars(pattern)):
            path = Path(raw_path).resolve()
            if path.is_file():
                return path
    return None


def _type_names(pythoncom, path: Path) -> list[str]:
    """@brief 从类型库读取接口/枚举名称。"""
    library = pythoncom.LoadTypeLib(str(path))
    return sorted(
        {
            str(library.GetDocumentation(index)[0])
            for index in range(library.GetTypeInfoCount())
            if library.GetDocumentation(index)[0]
        }
    )


def probe_capabilities(check_solidworks: bool = True) -> dict:
    """@brief 生成不夸大实现状态的机器可读能力报告。"""
    missing = missing_com_dependencies()
    manifest = load_capabilities()
    manifest_index = capability_index(manifest)
    report = {
        "schema_version": "1.0",
        "manifest_path": str(manifest_path()),
        "capability_manifest_schema": manifest.get("schema_version", "1.0"),
        "verified_versions": manifest.get("verified_versions", {}),
        "language_backend_matrix": backend_route_snapshot(manifest),
        "solidworks_detected": solidworks_installed() if check_solidworks else None,
        "missing_com_dependencies": missing,
        "type_libraries": {},
        "capabilities": {},
        "notes": [
            "type_library_present 只证明本机安装包含接口定义，不证明许可证、当前文档或自动化实现已验证。",
            "implementation_status=reference_only/not_implemented 的能力禁止自动宣称完成。",
            "language_backend_matrix 只定义适用边界；具体运行时仍须由 backend_router.py 按版本、依赖和接口语义选择。",
        ],
    }
    if missing or not check_solidworks:
        return report
    pythoncom, _client, _variant = import_com_dependencies(allow_install=False)
    all_types: set[str] = set()
    for name, patterns in TYPELIB_PATTERNS.items():
        path = _find_typelib(patterns)
        item = {"present": path is not None, "path": str(path) if path else None, "type_count": 0}
        if path:
            try:
                names = _type_names(pythoncom, path)
                item["type_count"] = len(names)
                all_types.update(names)
            except Exception as exc:
                item["error"] = str(exc)
        report["type_libraries"][name] = item

    lowered_types = {name.lower() for name in all_types}
    for capability, interface_names in CAPABILITY_KEYWORDS.items():
        matches = [name for name in interface_names if name.lower() in lowered_types]
        report["capabilities"][capability] = {
            "interfaces_found": matches,
            "interface_coverage": len(matches) / len(interface_names),
            "implementation_status": manifest_index.get(CAPABILITY_ALIASES[capability], {}).get("level", "not_implemented"),
            # 授权判据是 `allowed_modes` 含 `unattended`，不再是 `level == "verified"`。
            # 2026-10-01 的 pilot→五级迁移把「证据强度」与「授权」拆开
            # （docs/capabilities-schema-proposal.md §1.2）：那 13 条由 pilot 升为 verified 的能力
            # 跑过但不许无人值守；此处若仍按 level 判，会给它们**静默发授权**，
            # 与本字段的语义（可直接无人值守）相反。本处是迁移必须同批改的第二条授权路径。
            "ready_for_unattended_use": UNATTENDED_MODE
            in (manifest_index.get(CAPABILITY_ALIASES[capability], {}).get("allowed_modes") or [])
            and len(matches) == len(interface_names),
            "manifest_capability_id": CAPABILITY_ALIASES[capability],
        }
    return report


def main() -> int:
    """@brief 命令行入口。"""
    parser = argparse.ArgumentParser(description="探测 SolidWorks 高级机械能力和本机类型库。")
    parser.add_argument("--output", type=Path, help="可选 JSON 输出路径。")
    parser.add_argument("--no-solidworks-check", action="store_true", help="仅校验能力清单，不访问本机 SolidWorks/类型库。")
    args = parser.parse_args()
    report = probe_capabilities(check_solidworks=not args.no_solidworks_check)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload)
    if args.no_solidworks_check:
        return 0
    return 0 if report["solidworks_detected"] and not report["missing_com_dependencies"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
