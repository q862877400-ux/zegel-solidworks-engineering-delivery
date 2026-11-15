"""禁止折线模拟曲线：扫活跃 .py 里的折线指纹，带负例自证。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 依据:   AGENTS.md「十四之五、禁止折线模拟曲线」（业主 2026-11-07 令）
# 判据:   活跃代码不得 import 归档折线模块 sw_gear，不得出现「离散成 N 段」字段
#         （outline_points_m / involute_segments / tip_arc_segments /
#         root_arc_segments）或折线生成器 plan_spur_gear / create_external_spur_gear。
# 边界:   追溯区（archive / docs/history / specs/*/recon / root-scratch /
#         _evidence / output）按铁律 3「只搬不删」不扫；docstring 与注释里
#         解释「为什么折线是错的」不算违规（它们在 AST 里是字符串/注释，不是 Name）。
# 自证:   selftest() 用一段已知折线代码喂同一检测器，必须报出来，否则门禁假绿。
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: 活跃代码目录（不含追溯区）
SCAN_DIRS = (
    "scripts", "tools", "mcp-server", "subskills", "apps", "tests",
    "research/text-to-cad-and-parametric-plugins/proto",
)
#: 路径里出现这些片段即视为追溯区/产物，跳过
SKIP_PARTS = (
    "archive", "docs/history", "/recon/", "\\recon\\", "root-scratch",
    "_evidence", "output", ".git", "__pycache__",
)
#: 归档折线模块名
FORBIDDEN_MODULES = {"sw_gear"}
#: 折线方案的指纹名字（作为 AST Name / Attribute / import 名 / kwarg / def 名）
FORBIDDEN_NAMES = {
    "outline_points_m", "involute_segments", "tip_arc_segments",
    "root_arc_segments", "plan_spur_gear", "calculate_external_spur_gear",
    "create_external_spur_gear", "SpurGearSpec", "polyline_chord_approximation",
}
FORBIDDEN_KWARGS = {"involute_segments", "tip_arc_segments", "root_arc_segments"}
SELF = "check_no_polyline.py"


def scan_source(src: str) -> list[tuple[int, str]]:
    """在一段源码里找折线指纹，返回 [(行号, 命中名)]。AST 天然忽略注释/docstring。"""
    hits: list[tuple[int, str]] = []
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] in FORBIDDEN_MODULES:
                    hits.append((node.lineno, f"import {a.name}"))
        elif isinstance(node, ast.ImportFrom):
            mod = (node.module or "").split(".")[0]
            if mod in FORBIDDEN_MODULES:
                hits.append((node.lineno, f"from {node.module} import"))
            for a in node.names:
                if a.name in FORBIDDEN_NAMES:
                    hits.append((node.lineno, f"from {node.module} import {a.name}"))
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            hits.append((node.lineno, node.id))
        elif isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_NAMES:
            hits.append((node.lineno, f".{node.attr}"))
        elif isinstance(node, ast.keyword) and node.arg in FORBIDDEN_KWARGS:
            hits.append((node.lineno, f"{node.arg}="))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in FORBIDDEN_NAMES:
            hits.append((node.lineno, f"def {node.name}"))
    return sorted(set(hits))


def _is_active(path: Path) -> bool:
    rel = path.as_posix()
    if SELF in rel:
        return False
    return not any(p in rel for p in SKIP_PARTS)


def scan_tree() -> dict:
    """扫全部活跃 .py，返回违规清单与统计。"""
    files = 0
    violations: list[dict] = []
    for d in SCAN_DIRS:
        base = ROOT / d
        if not base.is_dir():
            continue
        for path in base.rglob("*.py"):
            if not _is_active(path):
                continue
            files += 1
            try:
                src = path.read_text(encoding="utf-8")
                hits = scan_source(src)
            except (SyntaxError, UnicodeDecodeError) as exc:
                violations.append({"file": str(path.relative_to(ROOT)),
                                   "error": f"{type(exc).__name__}: {exc}"})
                continue
            if hits:
                violations.append({
                    "file": str(path.relative_to(ROOT)),
                    "hits": [{"line": ln, "name": nm} for ln, nm in hits],
                })
    return {"scanned_files": files, "violations": violations}


def selftest() -> bool:
    """负例自证：一段已知折线代码必须被判违规；一段真曲线代码必须放行。"""
    bad = """
from sw_gear import SpurGearSpec, calculate_external_spur_gear
spec = SpurGearSpec(module_mm=1.0, teeth=20, involute_segments=12)
pts = list(calculate_external_spur_gear(spec).outline_points_m)
def plan_spur_gear(req):
    return pts
"""
    good = """
from scripts import gear_geometry as g
geo = g.calculate_gear_geometry(g.GearSpec(module_mm=1.0, teeth=20, face_width_mm=10.0))
x = g.involute_x_expression(geo.base_diameter_mm / 2.0)
"""
    bad_hits = scan_source(bad)
    good_hits = scan_source(good)
    ok = len(bad_hits) >= 4 and len(good_hits) == 0
    print(f"  [selftest] 折线负例命中 {len(bad_hits)} 处（期望 >=4）：{bad_hits}")
    print(f"  [selftest] 真曲线正例命中 {len(good_hits)} 处（期望 0）：{good_hits}")
    return ok


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

    if "--selftest" in sys.argv:
        print("VERDICT:", "OK" if selftest() else "SELFTEST FAILED")
        return 0 if selftest() else 1

    if not selftest():
        print("VERDICT: SELFTEST FAILED（门禁假绿，拦不住折线）")
        return 1

    result = scan_tree()
    print(json.dumps(result, ensure_ascii=False, indent=1))
    v = result["violations"]
    if v:
        print(f"\n发现 {len(v)} 个活跃文件含折线模拟曲线指纹（禁令见 AGENTS.md 十四之五）：")
        for item in v:
            print(f"  ✗ {item['file']}: {item.get('hits') or item.get('error')}")
        print("VERDICT: FAIL")
        return 1
    print(f"\n扫描 {result['scanned_files']} 个活跃 .py，零折线指纹。")
    print("VERDICT: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
