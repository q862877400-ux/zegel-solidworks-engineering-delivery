"""S15：补 docs/state 台账的 7 条空白（只读）。

一次跑完 5 条确定性检查：
  · 空白7：`subskills/` 的 `.pyc` 是否入库（git ls-files vs gitignore）
  · 空白4：`C:\\swprojects` 26 个克隆 ↔ `tools/union-sources.json` 的对应
  · 空白6：`docs/recon/official-source-defects-2.md` 里 72 个 examples 文件名在 `C:\\swapi\\examples` 的存在率
  · 空白5：两份 `verified-evidence-audit` 的内容重叠（4-gram Jaccard）
  · 空白1：`apps/` 与 `subskills/` 的 .py 内容普查（模块数、docstring 首行、子目录）

跑法：python docs\\state\\probes\\probe_gaps.py --json docs/state/inventory-q.json
"""
from __future__ import annotations

import argparse
import ast
import collections
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SWP = pathlib.Path(r"C:\swprojects")
SWAPI_EX = pathlib.Path(r"C:\swapi\examples")


def sh(args: list[str]) -> str:
    try:
        p = subprocess.run(args, cwd=str(ROOT), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120)
        return (p.stdout or "") + (p.stderr or "")
    except Exception as exc:  # noqa: BLE001
        return f"<失败 {type(exc).__name__}>"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()
    data: dict = {}

    # ── 空白7：subskills 的 .pyc
    tracked = sh(["git", "ls-files", "subskills"]).splitlines()
    pyc_tracked = [f for f in tracked if f.endswith(".pyc")]
    pyc_disk = [str(p.relative_to(ROOT)) for p in (ROOT / "subskills").rglob("*.pyc")]
    ignored = sh(["git", "check-ignore", "-v", "subskills"]).strip()
    data["gap7_subskills_pyc"] = {
        "on_disk": len(pyc_disk),
        "tracked": len(pyc_tracked),
        "tracked_sample": pyc_tracked[:5],
        "subskills_ignored": bool(ignored),
        "gitignore_line": ignored[:200],
    }

    # ── 空白4：克隆 ↔ union-sources.json
    us = json.loads((ROOT / "tools" / "union-sources.json").read_text(encoding="utf-8"))
    items = us.get("sources", us) if isinstance(us, dict) else us
    declared = []
    for i in items if isinstance(items, list) else []:
        if isinstance(i, dict):
            declared.append((i.get("repo") or "", i.get("owner") or "", i.get("license") or ""))
    clones = sorted(p.name for p in SWP.iterdir() if p.is_dir()) if SWP.exists() else []
    blob = json.dumps(us, ensure_ascii=False)
    matched = [c for c in clones if c in blob]
    data["gap4_clones_vs_sources"] = {
        "clones": len(clones),
        "declared_sources": len(declared),
        "declared": declared,
        "clones_mentioned_in_union_sources": matched,
        "clones_not_mentioned": [c for c in clones if c not in matched],
    }

    # ── 空白6：examples 在外部源的存在率
    doc = ROOT / "docs" / "recon" / "official-source-defects-2.md"
    names = set()
    if doc.exists():
        txt = doc.read_text(encoding="utf-8", errors="replace")
        names = set(re.findall(r"([A-Za-z0-9_]+_Example_[A-Za-z0-9_]+\.md)", txt))
        names |= set(re.findall(r"([A-Za-z0-9_]+\.md)", txt))
    present, absent = [], []
    for n in sorted(names):
        (present if (SWAPI_EX / n).exists() else absent).append(n)
    data["gap6_examples"] = {
        "doc": str(doc.relative_to(ROOT)),
        "distinct_names": len(names),
        "present_in_swapi_examples": len(present),
        "absent": len(absent),
        "absent_sample": absent[:15],
        "swapi_examples_exists": SWAPI_EX.exists(),
    }

    # ── 空白5：两份 audit 的重叠
    a1 = ROOT / "docs" / "verified-evidence-audit.md"
    a2 = ROOT / "docs" / "recon" / "verified-evidence-audit-2.md"

    def grams(p: pathlib.Path, n: int = 4) -> set[str]:
        t = re.sub(r"\s+", "", p.read_text(encoding="utf-8", errors="replace")) if p.exists() else ""
        return {t[i:i + n] for i in range(0, max(0, len(t) - n))}

    g1, g2 = grams(a1), grams(a2)
    inter = len(g1 & g2)
    data["gap5_audit_overlap"] = {
        "a1": {"path": str(a1.relative_to(ROOT)), "bytes": a1.stat().st_size if a1.exists() else 0},
        "a2": {"path": str(a2.relative_to(ROOT)), "bytes": a2.stat().st_size if a2.exists() else 0},
        "gram4_a1": len(g1), "gram4_a2": len(g2), "intersection": inter,
        "jaccard": round(inter / max(1, len(g1 | g2)), 3),
        "containment_of_a1_in_a2": round(inter / max(1, len(g1)), 3),
    }

    # ── 空白1：apps/ 与 subskills/ 内容普查
    inv: dict = {}
    for d in ("apps", "subskills"):
        base = ROOT / d
        files = sorted(base.rglob("*.py"))
        docstrings = collections.Counter()
        no_doc = 0
        for p in files:
            try:
                t = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            ds = ast.get_docstring(t) or ""
            first = ds.strip().splitlines()[0][:60] if ds.strip() else ""
            if first:
                docstrings[first] += 1
            else:
                no_doc += 1
        subdirs = sorted(x.name for x in base.iterdir() if x.is_dir())[:12]
        inv[d] = {
            "py_files": len(files),
            "no_docstring": no_doc,
            "top_docstring_first_lines": dict(docstrings.most_common(8)),
            "subdirs": subdirs,
        }
    data["gap1_content_survey"] = inv

    print(f"空白7 subskills .pyc：盘上 {len(pyc_disk)} · 入库 {len(pyc_tracked)} · 目录被 ignore={bool(ignored)}")
    print(f"空白4 克隆 {len(clones)} 个 · 声明来源 {len(declared)} 条 · 克隆名出现在清单里的 {len(matched)} 个")
    print(f"      未被提及: {data['gap4_clones_vs_sources']['clones_not_mentioned'][:8]}")
    print(f"空白6 examples 不同文件名 {len(names)} · 在 C:\\swapi\\examples 存在 {len(present)} · 缺 {len(absent)}")
    print(f"空白5 两份 audit 重叠：Jaccard {data['gap5_audit_overlap']['jaccard']} · "
          f"a1 被 a2 覆盖 {data['gap5_audit_overlap']['containment_of_a1_in_a2']}")
    for k, v in inv.items():
        print(f"空白1 {k}: {v['py_files']} 个 .py · 无 docstring {v['no_docstring']} · 子目录 {v['subdirs'][:6]}")

    if args.json:
        out = pathlib.Path(args.json)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print("已写出:", out)
    return 0


sys.exit(main())