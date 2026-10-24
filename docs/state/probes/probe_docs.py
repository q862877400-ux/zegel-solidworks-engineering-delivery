"""G 维度观测器：文档层（markdown）现状（只读）。

记录：md 文件分布、体积、**逐字重复**（内容哈希相同）、内部 md 链接可达性、
以及被 AGENTS/ROADMAP 引用但磁盘上不存在的文档。

跑法：python docs\\state\\probes\\probe_docs.py --json docs/state/inventory-g.json
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
#: 这些目录体积大且是外部素材/历史归档，单独统计，不参与重复与链接判定
HEAVY = ("AI Solidworks", "archive", "node_modules", ".git", "output")

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+?)\)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    all_md = []
    for p in ROOT.rglob("*.md"):
        rel = p.relative_to(ROOT)
        top = rel.parts[0]
        if top in HEAVY:
            continue
        all_md.append(p)

    data: dict = {"md_files_scanned": len(all_md)}
    data["per_dir"] = dict(
        collections.Counter(
            ("<root>" if len(p.relative_to(ROOT).parts) == 1 else p.relative_to(ROOT).parts[0])
            for p in all_md
        ).most_common(15)
    )

    # 逐字重复
    by_hash: dict[str, list[str]] = collections.defaultdict(list)
    sizes = []
    for p in all_md:
        raw = p.read_bytes()
        sizes.append(len(raw))
        norm = hashlib.sha1(b"\n".join(
            ln.strip() for ln in raw.splitlines() if ln.strip()
        )).hexdigest()
        by_hash[norm].append(str(p.relative_to(ROOT)))
    dup = {h: v for h, v in by_hash.items() if len(v) > 1}
    data["exact_duplicate_groups"] = len(dup)
    data["exact_duplicate_sample"] = list(dup.values())[:6]
    data["size_bytes"] = {
        "min": min(sizes) if sizes else 0,
        "max": max(sizes) if sizes else 0,
        "total_mb": round(sum(sizes) / 1048576, 1),
    }

    # 空文档 / 极短文档
    data["empty_or_tiny"] = [
        [str(p.relative_to(ROOT)), len(p.read_text(encoding="utf-8", errors="replace").strip())]
        for p in all_md
        if len(p.read_text(encoding="utf-8", errors="replace").strip()) < 40
    ][:12]

    # 内部链接可达性（只查 .md 目标）
    broken: list[dict] = []
    checked = 0
    for p in all_md:
        txt = p.read_text(encoding="utf-8", errors="replace")
        for m in LINK.finditer(txt):
            tgt = m.group(1)
            if not tgt.endswith(".md") or tgt.startswith(("http://", "https://", "mailto:")):
                continue
            checked += 1
            tgt_clean = tgt.split("#")[0]
            if not tgt_clean:
                continue
            resolved = (p.parent / tgt_clean).resolve()
            if not resolved.exists():
                broken.append({"from": str(p.relative_to(ROOT)), "to": tgt})
    data["md_links_checked"] = checked
    data["md_links_broken"] = len(broken)
    data["md_links_broken_sample"] = broken[:10]

    # 被 AGENTS.md / ROADMAP.md 引用的 md 是否存在
    ref_missing = []
    for src_name in ("AGENTS.md", "docs/ROADMAP.md", "RESTART-HANDOFF.md"):
        src = ROOT / src_name
        if not src.exists():
            continue
        txt = src.read_text(encoding="utf-8", errors="replace")
        for m in LINK.finditer(txt):
            tgt = m.group(1)
            if not tgt.endswith(".md") or tgt.startswith(("http", "mailto")):
                continue
            if not (src.parent / tgt.split("#")[0]).resolve().exists():
                ref_missing.append({"from": src_name, "to": tgt})
    data["core_docs_broken_links"] = len(ref_missing)
    data["core_docs_broken_sample"] = ref_missing[:10]

    print(f"扫描 md {data['md_files_scanned']} 个（已排除 {HEAVY}）")
    print(f"目录分布 top: {data['per_dir']}")
    print(f"总体积 {data['size_bytes']['total_mb']} MB · 单文件 {data['size_bytes']['min']}~{data['size_bytes']['max']} B")
    print(f"逐字重复组 {data['exact_duplicate_groups']} 组")
    print(f"内部 .md 链接 {data['md_links_checked']} 条 · 断链 {data['md_links_broken']}")
    print(f"核心文档（AGENTS/ROADMAP/HANDOFF）断链 {data['core_docs_broken_links']}")

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