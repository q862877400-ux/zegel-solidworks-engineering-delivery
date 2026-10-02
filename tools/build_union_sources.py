r"""扫描外部 MCP 项目，产出去重后的「并集来源清单」。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本工具为原创（扫描对象见下方 SOURCES）
# 文件:   tools/build_union_sources.py —— 本文件自身
# 定位:   docs/union-conventions.md 规则 5「每条并入的条目必须带 provenance」
#         的**数据采集端** —— 从各家仓库抽出工具名 + 许可 + 各自声明的验证状态。
# 官方依据: 无（本工具不涉及 SolidWorks API）
# 许可:   本仓库 MIT。扫描对象的许可逐一记录在输出 JSON 里。
# ⚠ 本工具只做**静态文本抽取**，不运行任何被扫描项目的代码，未在本机实测
#   （见 AGENTS.md 铁律 2）。
# 覆盖:   后续同级定义
# ────────────────────────────────────────────────────────────────────

# ⚑ 为什么需要归一（2026-09-30 实测）：
#   同一个操作，四家四个名字 ——
#       Eduardof0nt     sw_add_annotation
#       andrewbartels1  add_annotation
#       Slacker-LLC     add_note
#       vespo92         add_annotations
#   不归一会得出「并集 515 个工具、每家独有 ~90 个」的假象（其实大量是同一件事）。
#   归一后：381 个不同操作，其中约 100 个 ≥2 家有（真重叠）、~281 个只有一家有。
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tools" / "union-sources.json"

#: 扫描对象。**路径是采集时的本机克隆位置**，不是运行时依赖。
SOURCES = [
    {
        "repo": "Eduardof0nt/Solidworks-MCP-Server",
        "path": r"C:\swprojects\Eduardof0nt",
        "license": "MIT",
        "prefix": "sw_",
        "verified": "",  # ⚠ README 自称已验，但仓库内 0 个测试文件
        "note": "README 称 '✅ Verified on SolidWorks 2024'，但仓库内测试文件数为 0",
    },
    {
        "repo": "andrewbartels1/SolidworksMCP-python",
        "path": r"C:\swprojects\andrewbartels1",
        "license": "MIT",
        "prefix": "",
        "verified": "",
        "note": "README 自述 'under active construction'；mock 适配器输出为模拟值",
    },
    {
        "repo": "vespo92/SolidworksMCP-TS",
        "path": r"C:\swprojects\SolidworksMCP-TS",
        "license": "MIT",
        "prefix": "",
        "verified": "",
        "note": "TypeScript；103 个工具里 27 个是 vba_* 宏生成器，不是直接操作",
    },
    {
        "repo": "Slacker-LLC/solidworks-mcp",
        "path": r"C:\swprojects\Slacker-LLC",
        "license": "Apache-2.0",
        "prefix": "",
        "verified": "SW 2026 SP3.2 简体中文",
        "note": "README 称每个工具都在 SolidWorks 2026 SP3.2 上跑过；含 tools/tlb_probe.py 直读类型库",
    },
]

#: 工具注册的四种写法（按项目而异，全都要认）
PATTERNS = (
    r'@mcp\.tool\([^)]*?name\s*=\s*["\']([a-z][\w]*)["\']',
    r'@mcp\.tool\([^)]*\)\s*\n\s*(?:async\s+)?def\s+([a-z]\w+)',
    r'@tool\(\s*["\']([a-z][\w]*)["\']',
    r'\{\s*name:\s*["\']([a-z][\w]*)["\']',
)

#: 语义归一同义词表（避免把同一操作数成两个）
SYNONYMS = {
    "note": "annotation", "annotations": "annotation", "text_note": "annotation",
    "round": "fillet", "corner_round": "fillet",
    "hole_wizard": "hole", "simple_hole": "hole",
    "boss_extrude": "extrude", "extrusion": "extrude", "cut_extrude": "extrude_cut",
    "screenshot": "screenshot", "capture": "screenshot",
    "suppress_feature": "suppress", "set_feature_suppression": "suppress",
    "reference_plane": "ref_plane", "create_plane": "ref_plane",
    "reference_axis": "ref_axis", "create_axis": "ref_axis",
    "centerlines": "centerline", "center_marks": "center_mark",
    "bom_table": "bom", "flatten": "flat_pattern",
    "structural_member": "structural_member", "weldment": "structural_member",
    "mass_properties": "mass_props", "material_properties": "mass_props",
    "bounding_box": "bbox",
    "custom_properties": "custom_prop", "custom_property": "custom_prop",
    "global_variables": "global_var", "global_variable": "global_var",
    "equations": "equation", "dimensions": "dimension",
    "geometric_tolerance": "gdt", "datum_feature": "gdt", "surface_finish": "gdt",
    "check_interference": "interference", "exploded_view": "explode",
}

#: 域分类（正则，**按序首个命中者生效**）
#: ⚑ 顺序有讲究：**具体域必须排在笼统域之前**。
#:   实测教训：原先 `feature` 在 `mold` 之前，`tooling_split` 被 `feature` 的
#:   `split` 抢走；`surface` 在 `mold` 之前，`shut_off_surface` 被抢走
#:   ⇒ 结果「模具」域显示 0 个，而来源明明有 3 个。
DOMAINS = (
    # ── ① 最具体：专属名词，先抢 ──────────────────────────────
    ("advanced",  r"topolog|dfm|machinab|costing|_cost\b|\bpdm\b|vault|routing|\bpipe\b|harness|electrical|toolbox|dimxpert|toleranc|_gdt_|datum|surface_finish"),
    ("mold",      r"mold|parting|shut_off|tooling_split|core_cavity"),
    ("weldment",  r"weld|structural_member|gusset|end_cap"),
    ("sheetmetal", r"sheet_?metal|flange|unfold|_fold\b|jog|hem\b|flat_pattern|bend"),
    ("simulation", r"simulat|_study|thermal|buckling|fatigue|_drop\b|static_study|motion|cosworks|\bfea\b"),
    ("surface",   r"surface|knit|thicken|delete_face|filled|_loft\b|boundary_boss"),
    ("macro",     r"macro|vba|record|_script|batch|_run_code"),
    ("appearance", r"material|appearance|_color|config|display_state|background|render|photoview"),
    ("drawing",   r"drawing|_view\b|views|annot|balloon|\bbom\b|centerline|center_mark|revision_table|hole_table|section_view|_sheet\b|sheets"),
    ("assembly",  r"component|_mate|assembl|interference|explode|assembly_tree"),
    ("sketch",    r"sketch|_line\b|circle|_arc\b|rectang|polygon|spline|ellipse|slot|trim|offset|convert_ent|construction|3d_sketch|_spline"),
    ("param",     r"dimension|relation|constraint|equation|global_var|design_table|driving|link_|_scale\b"),
    ("refgeom",   r"ref_plane|ref_axis|reference_plane|reference_axis|_plane\b|_axis\b|refgeom|reference_point"),
    # ── ② 笼统域放后面 ────────────────────────────────────────
    ("inspect",   r"screenshot|mass_prop|bbox|bounding|measure|check_|analyze|inspect|geometry|view_orient|zoom|display_mode|sensor|\bstatus\b"),
    ("feature",   r"extrude|revolve|fillet|chamfer|shell|draft|_rib\b|dome|wrap|intersect|pattern|mirror|hole|sweep|loft|combine|split|_scale|helix|body"),
    ("session",   r"document|_file|open|close|save|new_|export|import|connect|rebuild|template|\bpart\b|\bmodel\b"),
)


def _normalize(tool: str) -> str:
    """把工具的**名字**归一成**操作名**（去掉各家前缀与动词前缀，再查同义词）。"""
    s = tool.lower()
    s = re.sub(r"^(sw_|solidworks_|cadstudio_|automation_|vba_|macro_)", "", s)
    if s in SYNONYMS:
        return SYNONYMS[s]
    s2 = re.sub(r"^(create_|add_|insert_|set_|get_|list_|draw_|start_|make_|build_)", "", s)
    return SYNONYMS.get(s2, s2 or s)


def _domain(op: str) -> str:
    for name, rx in DOMAINS:
        if re.search(rx, op, re.I):
            return name
    return "other"


def scan(path: str) -> list[str]:
    """从一个项目目录抽出所有工具名。**只读文本，不执行其代码**。"""
    root = Path(path)
    if not root.is_dir():
        return []
    found: set[str] = set()
    for f in root.rglob("*"):
        if not f.is_file() or f.suffix not in (".py", ".ts", ".cs"):
            continue
        if any(x in str(f) for x in (".venv", "node_modules", "site-packages",
                                     ".git", "__pycache__", "dist", "build", ".ci")):
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for rx in PATTERNS:
            found |= set(re.findall(rx, text))
    return sorted(found)


def _license_of(src: dict) -> str:
    """读**真实 LICENSE 文件**判定许可。

    ⚠ 不采信 README 徽章 —— 实测有项目徽章写 MIT 而仓库无 LICENSE 文件。
    """
    root = Path(src["path"])
    if not root.is_dir():
        return src["license"] + "（未核，本机无克隆）"
    for f in list(root.glob("LICENSE*")) + list(root.glob("COPYING*")):
        head = f.read_text(encoding="utf-8", errors="ignore")[:600]
        if "Apache License" in head:
            return "Apache-2.0"
        if "MIT License" in head or "Permission is hereby granted, free of charge" in head:
            return "MIT"
        if "GNU General Public" in head:
            return "GPL" + ("-3.0" if "Version 3" in head else "")
    return "无 LICENSE 文件"


def main() -> int:
    payload = {"schema_version": "1.0", "sources": []}
    for src in SOURCES:
        tools = scan(src["path"])
        ops = sorted({_normalize(t) for t in tools})
        by_domain: dict[str, list[str]] = {}
        for op in ops:
            by_domain.setdefault(_domain(op), []).append(op)
        payload["sources"].append({
            "repo": src["repo"],
            "license": _license_of(src),
            "declared_verified": src["verified"],
            "note": src["note"],
            "tool_count": len(tools),
            "operation_count": len(ops),
            "tools": tools,
            "operations": ops,
            "domains": {k: sorted(v) for k, v in sorted(by_domain.items())},
        })
        print("  %-38s 工具 %3d → 操作 %3d" % (src["repo"], len(tools), len(ops)))

    union: set[str] = set()
    for s in payload["sources"]:
        union |= set(s["operations"])
    payload["union_operations"] = sorted(union)
    payload["union_size"] = len(union)

    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print("  并集操作 %d 个" % len(union))
    print("  已写入 %s" % OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
