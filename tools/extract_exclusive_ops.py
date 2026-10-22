"""★ 抽出四家的「独家操作」（只出现在**一家**的操作名）⇒ 带编号的清单文件。"""

# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/extract_exclusive_ops.py
# 定位:   ★ 为「一个 bunny 一个操作」的调度准备输入。清单权威源是 `tools/union-sources
#           .json`（`sources[].tools` 是四家各自的**真实工具名**，`union_operations` 是
#           去重并集）✓
#         ★★ 「独家」的定义：某个操作名**只出现在四家里的恰好一家** —— ★ 与
#           `docs/union-coverage-matrix.md` §三「每个域的独家来源（只有一家有 ⇒ 只能抄它）」同义 ✓
#         ★★★ 为什么先用**名字**筛：★ 名字级差异**约 59% 是假阳性**（历史分诊结论）——
#           ⇒ ★ **假阳性由 bunny 逐条判**（每个 bunny 一个操作），**不在这一步判** ✓
# 官方依据: 不适用（本仓台账）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: ★ 域 → 该域的操作名（从 `docs/union-coverage-matrix.md` §五 的「缺口操作」行抄来，
#:   只为给 bunny 一个**域线索**；★ 域判错不影响它做真活）
DOMAIN_HINTS = {
    "① 会话/文档/文件": [
        "activate_document",
        "active_document_info",
        "apply_template",
        "close_all",
        "close_document",
        "close_model",
        "compare_templates",
        "convert_file_format",
        "export_document",
        "export_dwg",
        "export_file",
        "export_pdf",
        "export_with_options",
        "extract_template",
        "manage_file_properties",
        "open_documents",
        "open_model",
        "part",
        "rebuild_document",
        "rebuild_model",
        "referenced_documents",
        "save_active_document",
        "save_all",
        "save_as",
    ],
    "② 参考几何": ["ref_axis", "reference_planes"],
    "③ 草图": [
        "3d_sketch",
        "3point_arc",
        "check_sketch_fully_defined",
        "circle",
        "close_sketch",
        "construction_geometry",
        "convert_entities",
        "edit_sketch",
        "ellipse",
        "exit_sketch",
        "hide_all_sketches",
        "polygon",
        "rectangle",
        "show_all_sketches",
        "sketch",
        "sketch_arc",
        "sketch_chamfer",
        "sketch_circle",
        "sketch_constraint",
        "sketch_construction",
        "sketch_dimension",
        "sketch_ellipse",
        "sketch_line",
        "sketch_polygon",
    ],
    "④ 尺寸/约束/参数": [
        "delete_equation",
        "design_table",
        "design_table_create",
        "design_table_refresh",
        "diameter_dimension",
        "equation",
        "global_var",
        "link_dimension_to_equation",
        "manage_design_table",
        "relation",
    ],
    "⑤ 零件特征": [
        "combine_bodies",
        "curve_driven_pattern",
        "delete_body",
        "dome",
        "draft",
        "extrude",
        "fill_pattern",
        "helix",
        "intersect",
        "linear_pattern",
        "loft",
        "mirror",
        "move_body",
        "pattern_circular",
        "pattern_features",
        "revolve",
        "save_body_as_part",
        "scale_body",
        "shell",
        "simple_extrude",
        "split_body",
        "sweep",
        "tutorial_simple_hole",
        "wrap",
    ],
    "⑥ 曲面": [
        "boundary_boss",
        "extend_surface",
        "extruded_surface",
        "filled_surface",
        "knit_surfaces",
        "surface_modeling",
        "thicken_surface",
        "trim_surface",
    ],
    "⑦ 钣金": [
        "base_flange",
        "edge_flange",
        "export_flat_pattern",
        "flat_pattern_info",
        "flatten_sheet_metal",
        "hem",
        "jog",
        "miter_flange",
        "sheet_metal",
        "sketched_bend",
        "unfold",
    ],
    "⑧ 焊件": [
        "end_cap",
        "gusset",
        "structural_member",
        "trim_weldment",
        "weld_symbol",
    ],
    "⑨ 模具": ["parting_line", "shut_off_surface", "tooling_split"],
}
#: ⚠ ⑩⑪⑫⑬⑭⑮⑰ 的§五 清单未在本脚本里抄全（⑥⑦⑧⑨ 之后的行没读）——★ 按铁律 5 **不猜**：
#:   这些域的操作**仍会从 JSON 里被抽到**，只是 `domain_hint` 留空，由 bunny 自己判 ✓


def main() -> int:
    data = json.loads(
        (ROOT / "tools" / "union-sources.json").read_text(encoding="utf-8")
    )
    sources = data.get("sources") or []
    if not sources:
        print("★ `sources` 为空 ⇒ 结构变了，看一眼再改")
        return 1

    #: 每家一个名字集合 + 许可
    per: list[tuple[str, str, set[str]]] = []
    for s in sources:
        repo = (
            "%s/%s" % (s.get("owner"), s.get("repo"))
            if s.get("owner")
            else str(s.get("repo"))
        )
        names = {
            str(t.get("name") if isinstance(t, dict) else t)
            for t in (s.get("tools") or [])
        }
        names = {n for n in names if n and n != "None"}
        per.append((repo, str(s.get("license")), names))
        print("  %-42s %-12s tools=%d" % (repo, s.get("license"), len(names)))

    allnames: set[str] = set()
    for _, _, ns in per:
        allnames |= ns
    print("\n★ 四家名字并集：**%d**" % len(allnames))

    #: ★ 独家 = 恰好出现在一家人里
    exclusive: list[dict] = []
    for name in sorted(allnames):
        owners = [(repo, lic) for repo, lic, ns in per if name in ns]
        if len(owners) == 1:
            exclusive.append(
                {"op": name, "source_repo": owners[0][0], "license": owners[0][1]}
            )
    print("★ **独家操作**（只一家有）：**%d**" % len(exclusive))

    #: 挂域线索（按名字查 DOMAIN_HINTS；查不到就留空 —— ★ 不猜）
    hint = {}
    for d, ops in DOMAIN_HINTS.items():
        for o in ops:
            hint.setdefault(o, d)
    for i, e in enumerate(exclusive, 1):
        e["index"] = i
        e["domain_hint"] = hint.get(e["op"], "")

    out = ROOT / "output" / "exclusive-ops.json"
    out.write_text(
        json.dumps(
            {"count": len(exclusive), "ops": exclusive}, ensure_ascii=False, indent=1
        ),
        encoding="utf-8",
    )
    print("★ 已写：%s" % out)
    print("\n★ 前 12 条样例：")
    for e in exclusive[:12]:
        print(
            "   #%-4d %-28s %-42s %s"
            % (e["index"], e["op"], e["source_repo"], e["license"])
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
