"""I 维度观测器：许可与来源现状（只读）。

记录：`tools/union-sources.json` 的来源数与许可分布、`THIRD-PARTY-NOTICES.md` 覆盖、
仓库 LICENSE、以及代码文件头里出现的许可关键词（SPDX / Copyright / GPL 族）。

跑法：python docs\\state\\probes\\probe_license.py --json docs/state/inventory-i.json
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SCAN_DIRS = ("scripts", "tools", "mcp-server", "tests", "subskills")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()
    data: dict = {}

    # ① 来源清单
    us = ROOT / "tools" / "union-sources.json"
    if us.exists():
        sources = json.loads(us.read_text(encoding="utf-8"))
        if isinstance(sources, dict):
            items = sources.get("sources", sources)
        else:
            items = sources
        if isinstance(items, list):
            data["union_sources"] = {
                "count": len(items),
                "licenses": dict(
                    collections.Counter(
                        (i.get("license") or "<无>") for i in items if isinstance(i, dict)
                    ).most_common()
                ),
                "declared_verified": dict(
                    collections.Counter(
                        str(i.get("declared_verified")) for i in items if isinstance(i, dict)
                    ).most_common()
                ),
                "names": [i.get("repo") or i.get("owner") for i in items if isinstance(i, dict)][:12],
            }
        else:
            data["union_sources"] = {"shape": type(items).__name__}

    # ② NOTICE
    notice = ROOT / "THIRD-PARTY-NOTICES.md"
    if notice.exists():
        txt = notice.read_text(encoding="utf-8", errors="replace")
        data["third_party_notices"] = {
            "lines": len(txt.splitlines()),
            "bytes": len(txt.encode("utf-8")),
            "mentions_jiale": "JIALE" in txt.upper(),
            "mentions_mit": txt.upper().count("MIT"),
            "mentions_apache": txt.upper().count("APACHE"),
        }

    # ③ 仓库 LICENSE
    lic = ROOT / "LICENSE"
    data["repo_license"] = {
        "exists": lic.exists(),
        "first_line": (lic.read_text(encoding="utf-8", errors="replace").splitlines()[0][:80] if lic.exists() else ""),
    }

    # ④ 代码头里的许可关键词
    kw = collections.Counter()
    gpl_files = []
    files_scanned = 0
    for d in SCAN_DIRS:
        for p in (ROOT / d).rglob("*.py"):
            files_scanned += 1
            head = "\n".join(p.read_text(encoding="utf-8", errors="replace").splitlines()[:40])
            for k in ("SPDX", "MIT", "Apache", "Copyright", "GPL", "AGPL", "LGPL", "NON-COMMERCIAL"):
                if k.lower() in head.lower():
                    kw[k] += 1
            if re.search(r"\b(A|L)?GPL", head):
                gpl_files.append(str(p.relative_to(ROOT)))
    data["code_files_scanned"] = files_scanned
    data["license_keywords_in_header"] = dict(kw.most_common())
    data["files_with_gpl_family_header"] = gpl_files[:12]
    data["files_with_gpl_family_count"] = len(gpl_files)

    print(f"union-sources 来源 {data.get('union_sources', {}).get('count')} 条 · 许可分布 {data.get('union_sources', {}).get('licenses')}")
    print(f"THIRD-PARTY-NOTICES {data.get('third_party_notices')}")
    print(f"仓库 LICENSE: {data['repo_license']}")
    print(f"扫描代码文件 {files_scanned} 个 · 头部关键词 {data['license_keywords_in_header']}")
    print(f"头部含 GPL 族的文件 {data['files_with_gpl_family_count']} 个")

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