"""S16：空白 3 —— 100 条 `verified` 的 evidence 是否**真支撑**该能力（只读）。

不判「对错」，只做三类**可数**的检查（记录员口径）：
 ① 证据里出现**否定/受限**字样（失败 / 不支持 / 无法 / 不可用 / None / 未实现 / 报错）的条数
 ② 证据里点名**测试文件**（`tests/*.py`）的条数
 ③ 证据里点名**运行产物**（`output/*.json` 等）的条数
并把结果与仓库里既有的 `docs/recon/verified-evidence-audit-2.md`（规格 203 B1）的结论并排。

跑法：python docs\\state\\probes\\probe_evidence_substance.py --json docs/state/inventory-q3.json
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
import yaml  # noqa: E402

NEG = re.compile(r"失败|不支持|无法|不可用|未实现|报错|None|❌|✗|limitation|not\s+supported", re.I)
TEST = re.compile(r"tests?[/\\][A-Za-z0-9_]+\.py")
OUTPUT = re.compile(r"output[/\\][A-Za-z0-9_./\\-]+")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    doc = yaml.safe_load((ROOT / "capabilities.yaml").read_text(encoding="utf-8"))
    caps = [c for c in doc.get("capabilities", []) if c.get("level") == "verified"]

    neg_caps, test_caps, out_caps = [], [], []
    neg_hits = collections.Counter()
    for c in caps:
        ev = c.get("evidence") or []
        items = [str(x) for x in (ev if isinstance(ev, list) else [ev])]
        blob = " ".join(items)
        m = NEG.findall(blob)
        if m:
            neg_caps.append({"id": c.get("id"), "hits": sorted(set(m))[:4],
                             "sample": blob[:160]})
            for x in set(m):
                neg_hits[x.lower()] += 1
        if any(TEST.search(i) for i in items):
            test_caps.append(c.get("id"))
        if any(OUTPUT.search(i) for i in items):
            out_caps.append(c.get("id"))

    # 既有审计文档的结论行（只取带数字与关键词的行）
    audit = ROOT / "docs" / "recon" / "verified-evidence-audit-2.md"
    audit_lines = []
    if audit.exists():
        for ln in audit.read_text(encoding="utf-8", errors="replace").splitlines():
            if re.search(r"(否定|失败|不一致|结论|verified|条)", ln) and len(ln.strip()) > 12:
                audit_lines.append(ln.strip()[:150])

    data = {
        "verified_total": len(caps),
        "evidence_with_negation": len(neg_caps),
        "negation_word_histogram": dict(neg_hits.most_common(10)),
        "evidence_naming_a_test_file": len(test_caps),
        "evidence_naming_an_output_artifact": len(out_caps),
        "negation_samples": neg_caps[:8],
        "audit_doc": str(audit.relative_to(ROOT)) if audit.exists() else "",
        "audit_doc_bytes": audit.stat().st_size if audit.exists() else 0,
        "audit_doc_headline_lines": audit_lines[:10],
    }

    print(f"verified {len(caps)} 条")
    print(f"证据里含否定/受限字样：{len(neg_caps)} 条 · 词频 {data['negation_word_histogram']}")
    print(f"证据点名测试文件：{len(test_caps)} 条 · 点名运行产物：{len(out_caps)} 条")
    for s in data["negation_samples"][:5]:
        print(f"   {s['id']}: {s['sample'][:110]}")
    print(f"既有审计文档 {data['audit_doc']}（{data['audit_doc_bytes']} B）结论行：")
    for ln in data["audit_doc_headline_lines"][:6]:
        print("   ", ln)

    if args.json:
        out = pathlib.Path(args.json)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print("已写出:", out)
    return 0


sys.exit(main())