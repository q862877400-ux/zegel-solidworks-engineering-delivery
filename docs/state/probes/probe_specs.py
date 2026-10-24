"""H 维度观测器：`specs/` 规格层现状（只读）。

记录：规格数、有无 spec.md、Status 字段取值、`→ 验收:` 行数、
编号缺口、以及 spec 之间/被文档引用的覆盖情况。

跑法：python docs\\state\\probes\\probe_specs.py --json docs/state/inventory-h.json
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SPECS = ROOT / "specs"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    dirs = sorted(p for p in SPECS.iterdir() if p.is_dir())
    data: dict = {"spec_dirs": len(dirs)}

    nums = []
    with_spec = 0
    status_hist = collections.Counter()
    acceptance_total = 0
    no_spec_md = []
    rows = []
    for d in dirs:
        m = re.match(r"^(\d+)-", d.name)
        if m:
            nums.append(int(m.group(1)))
        spec = d / "spec.md"
        has = spec.exists()
        if has:
            with_spec += 1
            txt = spec.read_text(encoding="utf-8", errors="replace")
            st = re.search(r"^\*\*Status\*\*[:：]\s*(.+)$", txt, re.M)
            status = st.group(1).strip() if st else "<无 Status 行>"
            status_hist[status[:40]] += 1
            acc = len(re.findall(r"→\s*验收", txt))
            acceptance_total += acc
        else:
            no_spec_md.append(d.name)
            acc = 0
            status = "<无 spec.md>"
        rows.append({"name": d.name, "has_spec_md": has, "status": status, "acceptance_lines": acc})

    data["with_spec_md"] = with_spec
    data["without_spec_md"] = no_spec_md
    data["status_histogram"] = dict(status_hist.most_common(12))
    data["acceptance_lines_total"] = acceptance_total
    data["numbering"] = {
        "min": min(nums) if nums else None,
        "max": max(nums) if nums else None,
        "count_numeric": len(nums),
        "missing_in_range": (
            sorted(set(range(min(nums), max(nums) + 1)) - set(nums)) if nums else []
        )[:30],
    }

    # 被 AGENTS/ROADMAP/docs 引用的 spec 目录名出现次数
    corpus = []
    for p in list((ROOT / "docs").rglob("*.md"))[:4000] + [ROOT / "AGENTS.md"]:
        try:
            corpus.append(p.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
    blob = "\n".join(corpus)
    unref = [r["name"] for r in rows if r["name"] not in blob]
    data["specs_not_mentioned_in_docs"] = len(unref)
    data["specs_not_mentioned_sample"] = unref[:12]

    print(f"规格目录 {data['spec_dirs']} 个 · 有 spec.md {with_spec} · 无 spec.md {len(no_spec_md)}")
    print(f"编号 {data['numbering']['min']}~{data['numbering']['max']} · 区间缺口 {len(data['numbering']['missing_in_range'])}（前 30 显示）")
    print(f"`→ 验收:` 行合计 {acceptance_total}")
    print(f"Status 取值 top: {list(data['status_histogram'].items())[:6]}")
    print(f"在 docs/AGENTS 里未被提及的规格 {len(unref)}/{len(rows)}")

    if args.json:
        out = pathlib.Path(args.json)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({**data, "rows": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
        print("已写出:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())