"""G 维度补充：生成「文档地图」的可观测信号（只读）。

对 `docs/` 与仓库根的 markdown，采集四个**可观测**信号，不做权威/过期的判断：
  ① 最近一次 git 提交日期（是谁在何时动过）
  ② 仓库内被多少份其它 md 引用（按文件名出现次数）
  ③ 是否与另一份文件逐字重复（内容哈希相同）
  ④ 体积

输出：`docs/state/doc-map.md`（人读）+ `docs/state/inventory-g-map.json`（机读）
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]


def last_commit_date(rel: str) -> str:
    proc = subprocess.run(
        ["git", "log", "-1", "--format=%ad", "--date=short", "--", rel],
        cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return (proc.stdout or "").strip() or "<无提交记录>"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="docs/state/inventory-g-map.json")
    ap.add_argument("--md", default="docs/state/doc-map.md")
    args = ap.parse_args()

    targets = [p for p in (ROOT / "docs").rglob("*.md") if p.is_file()]
    targets += [p for p in ROOT.glob("*.md") if p.is_file()]

    # 语料：所有非重型目录的 md 全文（算被引用次数）
    corpus_files = [
        p for p in ROOT.rglob("*.md")
        if not set(p.relative_to(ROOT).parts) & {"AI Solidworks", "archive", "node_modules", ".git", "output"}
    ]
    corpus = []
    for p in corpus_files:
        try:
            corpus.append(p.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
    blob = "\n".join(corpus)

    # 重复检测
    hashes: dict[str, list[str]] = collections.defaultdict(list)
    for p in corpus_files:
        try:
            raw = p.read_bytes()
        except OSError:
            continue
        h = hashlib.sha1(b"\n".join(ln.strip() for ln in raw.splitlines() if ln.strip())).hexdigest()
        hashes[h].append(str(p.relative_to(ROOT)))

    rows = []
    for p in targets:
        rel = str(p.relative_to(ROOT))
        raw = p.read_bytes()
        h = hashlib.sha1(b"\n".join(ln.strip() for ln in raw.splitlines() if ln.strip())).hexdigest()
        twins = [x for x in hashes[h] if x != rel]
        # ★ 按**相对路径**计引用，不按文件名 —— 否则所有 README.md 会得到同一个数（本轮实测踩到）
        rel_fwd = rel.replace("\\", "/")
        n_ref = blob.count(rel_fwd) + blob.count(rel.replace("/", "\\"))
        rows.append(
            {
                "path": rel,
                "bytes": len(raw),
                "last_commit": last_commit_date(rel),
                "referenced_by_docs": n_ref,
                "exact_twin": twins[0] if twins else "",
            }
        )

    rows.sort(key=lambda r: (-r["referenced_by_docs"], r["path"]))

    out_json = pathlib.Path(args.json)
    if not out_json.is_absolute():
        out_json = ROOT / out_json
    out_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# 文档地图（可观测信号）",
        "",
        "> 由 `docs/state/probes/probe_doc_map.py` 生成。**本表不做「权威 / 过期」判断**——",
        "> 只列四个可观测信号（最后提交日、被引用次数、是否逐字重复、体积），判定留给读者。",
        "",
        f"覆盖：`docs/` 下 {len([r for r in rows if r['path'].startswith('docs')])} 份 + 仓库根 "
        f"{len([r for r in rows if '/' not in r['path'] and chr(92) not in r['path']])} 份。",
        "",
        "| 文件 | 最后提交 | 被引用次数 | 逐字重复 | 体积 |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        md.append(
            "| `{p}` | {d} | {n} | {t} | {b:,} B |".format(
                p=r["path"], d=r["last_commit"], n=r["referenced_by_docs"],
                t=(f"↔ `{r['exact_twin']}`" if r["exact_twin"] else "—"), b=r["bytes"],
            )
        )
    out_md = pathlib.Path(args.md)
    if not out_md.is_absolute():
        out_md = ROOT / out_md
    out_md.write_text("\n".join(md) + "\n", encoding="utf-8")

    twins = sum(1 for r in rows if r["exact_twin"])
    print(f"文档地图：{len(rows)} 份 · 其中与别处逐字重复 {twins} 份")
    print(f"被引用次数 top5：{[(r['path'], r['referenced_by_docs']) for r in rows[:5]]}")
    print("已写出:", out_md, "与", out_json)
    return 0


if __name__ == "__main__":
    sys.exit(main())