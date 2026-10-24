"""E 维度观测器：门禁体系现状（只读）。

对每个 `scripts/check_*.py` 记录：首行 docstring、是否被 `release_check.py` 以 subprocess 引用、
在 `docs/gate-classification.json` 里的 kind、以及是否有 `selftest`。

跑法：python docs\\state\\probes\\probe_gates.py --json docs/state/inventory-e.json
"""
from __future__ import annotations

import argparse
import ast
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
RELEASE = SCRIPTS / "release_check.py"
CLASSIFICATION = ROOT / "docs" / "gate-classification.json"


def first_doc_line(p: pathlib.Path) -> str:
    try:
        tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return "<语法错误>"
    doc = ast.get_docstring(tree) or ""
    return doc.strip().splitlines()[0][:110] if doc.strip() else ""


def has_selftest(p: pathlib.Path) -> bool:
    t = p.read_text(encoding="utf-8", errors="replace")
    return "def selftest(" in t


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    release_src = RELEASE.read_text(encoding="utf-8", errors="replace")
    cls = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
    by_gate = {e["gate"]: e for e in cls.get("classification", [])}

    gates = sorted(SCRIPTS.glob("check_*.py"))
    rows = []
    for g in gates:
        wired = bool(re.search(r'str\(\s*ROOT\s*/\s*"scripts"\s*/\s*"%s"' % re.escape(g.name), release_src))
        meta = by_gate.get(g.name, {})
        rows.append(
            {
                "gate": g.name,
                "lines": len(g.read_text(encoding="utf-8", errors="replace").splitlines()),
                "doc": first_doc_line(g),
                "wired_in_release_check": wired,
                "kind": meta.get("kind", ""),
                "runner": meta.get("runner", ""),
                "has_selftest": has_selftest(g),
            }
        )

    data = {
        "gate_files": len(rows),
        "wired": sum(1 for r in rows if r["wired_in_release_check"]),
        "not_wired": [r["gate"] for r in rows if not r["wired_in_release_check"]],
        "kinds": dict(
            __import__("collections").Counter(r["kind"] or "<未登记>" for r in rows).most_common()
        ),
        "with_selftest": sum(1 for r in rows if r["has_selftest"]),
        "classification_entries": len(by_gate),
        "rows": rows,
    }

    print(f"check_*.py 共 {data['gate_files']} 个 · 接进 release_check {data['wired']} · 未接 {len(data['not_wired'])}")
    print(f"kind 分布：{data['kinds']}")
    print(f"带 selftest：{data['with_selftest']}/{data['gate_files']} · classification 登记 {data['classification_entries']} 条")
    if data["not_wired"]:
        print("未接进 release_check 的：")
        for g in data["not_wired"]:
            print("  -", g)

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