"""O 维度：文档归并清单生成器（只读；先出计划，再决定动手）。

产出两件事：
  ① **重复组全量**，并把「根 ↔ 内嵌快照（apps/.../resources/skill）」这类**构建镜像**单独标出
     （镜像由 `sync_bundled_skill.py` 生成，删了会让 release_check 的漂移检查变红）
  ② **断链全量**，并对每条尝试按文件名在仓库里找真身，给出可重定向的目标

跑法：python docs\\state\\probes\\probe_doc_consolidate.py --json docs/state/inventory-o.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HEAVY = {"AI Solidworks", "archive", "node_modules", ".git", "output"}
LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+?)\)")


def scan() -> list[pathlib.Path]:
    out = []
    for p in ROOT.rglob("*.md"):
        if set(p.relative_to(ROOT).parts) & HEAVY:
            continue
        out.append(p)
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    files = scan()
    by_hash: dict[str, list[str]] = {}
    for p in files:
        raw = p.read_bytes()
        h = hashlib.sha1(b"\n".join(ln.strip() for ln in raw.splitlines() if ln.strip())).hexdigest()
        by_hash.setdefault(h, []).append(str(p.relative_to(ROOT)))

    dup = {h: v for h, v in by_hash.items() if len(v) > 1}
    mirror, other = [], []
    for h, group in dup.items():
        if all("src-tauri" in g or g in ("README.md", "SKILL.md", "SUBSKILLS.md", "AGENTS.md") for g in group):
            mirror.append(group)
        else:
            other.append(group)

    broken = []
    for p in files:
        txt = p.read_text(encoding="utf-8", errors="replace")
        for m in LINK.finditer(txt):
            tgt = m.group(2)
            if not tgt.endswith(".md") or tgt.startswith(("http", "mailto:")):
                continue
            clean = tgt.split("#")[0]
            if not clean:
                continue
            if (p.parent / clean).resolve().exists():
                continue
            name = pathlib.Path(clean).name
            cands = [q for q in ROOT.rglob(name) if not (set(q.relative_to(ROOT).parts) & HEAVY)][:3]
            broken.append({
                "from": str(p.relative_to(ROOT)),
                "link_text": m.group(1)[:40],
                "target": tgt,
                "found": [str(c.relative_to(ROOT)) for c in cands],
            })

    data = {
        "md_scanned": len(files),
        "duplicate_groups_total": len(dup),
        "duplicate_groups_build_mirror": len(mirror),
        "duplicate_groups_other": len(other),
        "mirror_groups": mirror,
        "other_groups": other,
        "broken_links_total": len(broken),
        "broken_with_redirect": [b for b in broken if b["found"]],
        "broken_unresolvable": [b for b in broken if not b["found"]],
    }

    print(f"md {len(files)} 份 · 重复组 {len(dup)}（构建镜像 {len(mirror)} · 其它 {len(other)}）")
    for g in other[:8]:
        print("   其它重复组:", g)
    print(f"断链 {len(broken)} 条 · 可重定向 {len(data['broken_with_redirect'])} · 无解 {len(data['broken_unresolvable'])}")
    for b in data["broken_with_redirect"][:6]:
        print(f"   {b['from']} -> {b['target'][:50]}  可指向 {b['found'][0]}")
    for b in data["broken_unresolvable"][:6]:
        print(f"   [无解] {b['from']} -> {b['target'][:60]}")

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