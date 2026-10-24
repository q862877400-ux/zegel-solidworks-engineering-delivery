"""C 维度观测器：`capabilities.yaml` 台账现状（只读）。

记录：条数、level 分布、字段齐全度、evidence 形态、limitations 覆盖、
以及与「工具声明 / scripts 模块」的交叉引用计数。
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "mcp-server"))
sys.path.insert(0, str(ROOT / "scripts"))

import yaml  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    doc = yaml.safe_load((ROOT / "capabilities.yaml").read_text(encoding="utf-8"))
    caps = doc.get("capabilities", [])
    data: dict = {"schema_version": doc.get("schema_version"), "total": len(caps)}
    data["top_level_keys"] = sorted(doc.keys())

    # level 分布
    data["level_histogram"] = dict(collections.Counter(c.get("level") for c in caps).most_common())

    # 字段齐全度
    field_counts = collections.Counter()
    for c in caps:
        for k, v in c.items():
            if v not in (None, "", [], {}):
                field_counts[k] += 1
    data["field_presence"] = dict(field_counts.most_common())

    # evidence 形态（只对 verified）
    ev_rows = []
    for c in caps:
        if c.get("level") != "verified":
            continue
        ev = c.get("evidence")
        if ev is None:
            kind = "<无>"
            n = 0
        elif isinstance(ev, str):
            kind = "str"
            n = len(ev)
        elif isinstance(ev, list):
            kind = "list[%d]" % len(ev)
            n = sum(len(str(x)) for x in ev)
        elif isinstance(ev, dict):
            kind = "dict{%s}" % ",".join(sorted(ev)[:3])
            n = len(str(ev))
        else:
            kind = type(ev).__name__
            n = 0
        ev_rows.append({"name": c.get("name"), "kind": kind, "chars": n})
    data["verified_evidence"] = {
        "count": len(ev_rows),
        "kind_histogram": dict(collections.Counter(r["kind"] for r in ev_rows).most_common()),
        "missing": [r["name"] for r in ev_rows if r["kind"] == "<无>"],
        "shortest": sorted(ev_rows, key=lambda r: r["chars"])[:5],
    }

    # limitations 覆盖
    data["limitations_present"] = sum(1 for c in caps if c.get("limitations"))
    data["provenance_present"] = sum(1 for c in caps if c.get("provenance"))

    # 交叉引用：能力名 → 是否有同名/近名工具
    import register_capabilities as rc  # noqa: PLC0415

    spec_names = [s.name for s in rc.all_specs()]
    spec_mods = {s.module for s in rc.all_specs() if s.module}
    cap_names = [c.get("name", "") for c in caps]
    hit_tool, hit_mod = [], []
    for c in cap_names:
        slug = re.sub(r"[^a-z0-9]+", "_", c.lower()).strip("_")
        if any(slug and slug in s for s in spec_names):
            hit_tool.append(c)
        if any(c in m or slug in m for m in spec_mods):
            hit_mod.append(c)
    data["name_match_tool"] = {"hit": len(hit_tool), "of": len(cap_names)}
    data["name_match_module"] = {"hit": len(hit_mod), "of": len(cap_names)}
    data["capabilities_without_any_name_hit"] = [
        c for c in cap_names if c not in hit_tool and c not in hit_mod
    ][:20]

    print(f"能力条数 {data['total']} · schema_version {data['schema_version']}")
    print(f"level 分布 {data['level_histogram']}")
    print(f"字段齐全度 {json.dumps(data['field_presence'], ensure_ascii=False)}")
    print(f"verified 的 evidence 形态 {data['verified_evidence']['kind_histogram']}")
    print(f"verified 无 evidence {len(data['verified_evidence']['missing'])} 条")
    print(f"limitations 覆盖 {data['limitations_present']}/{data['total']} · provenance {data['provenance_present']}/{data['total']}")
    print(f"名称能对上工具 {data['name_match_tool']['hit']}/{data['name_match_tool']['of']} · 能对上模块 {data['name_match_module']['hit']}/{data['name_match_module']['of']}")

    if args.json:
        out = pathlib.Path(args.json)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print("已写出:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())