"""★ 批量扫：**我们仓里用了多少官方废弃成员**（★ 拿官方索引去比，不靠人读）。

★ 这是"批量推进"的第一台**消费者**：`tools/build_obsolete_index.py` 建了官方名单（1671 个、
  ★ 其中 1586 个官方点名了后继），★ 本脚本拿那份名单去扫全仓，★ 一次列全。
★ 判据（★ 只报**能指认**的）：
  · ★ **字符串字面量**里出现该成员名（★ 例：`get_com_member(fm, "Select2", …)`）；
  · ★ **属性访问**里出现（★ 例：`obj.Select2(...)`）。
  ★ 两者都要求**该名字真的在官方废弃名单里** ⇒ ★ 不靠猜。
★ 只读；★ 产出 `output/obsolete-usage-in-repo.json` + 屏幕上的分组表。
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(r"D:\AI\SW")
IDX = REPO / "specs" / "202-user-coverage-gaps" / "recon" / "official-obsolete-index.json"
OUT = REPO / "output" / "obsolete-usage-in-repo.json"


def main() -> int:
    started = time.time()
    idx = json.loads(IDX.read_text(encoding="utf-8", errors="replace"))
    entries = idx["entries"]
    print("★ 官方废弃名单：**%d** 个成员（★ 其中 **%d** 个官方点名了后继）"
          % (len(entries), sum(1 for e in entries if e["successor"])))
    #: ★ 成员名 → 后继（★ 同名可能属不同接口 ⇒ 全收，报告里带上接口）
    by_member: dict = defaultdict(list)
    for e in entries:
        by_member[e["member"]].append(e)
    names = set(by_member)

    hits = []
    scanned = 0
    files = sorted((REPO / "scripts").glob("*.py")) + sorted((REPO / "mcp-server").glob("*.py")) \
        + sorted((REPO / "tools").glob("*.py"))
    for f in files:
        if f.name.startswith("_"):
            continue
        scanned += 1
        try:
            txt = f.read_text(encoding="utf-8", errors="replace")
        except Exception:                                                 # noqa: BLE001
            continue
        for i, line in enumerate(txt.splitlines(), 1):
            s = line.strip()
            if s.startswith("#") or s.startswith('"""'):
                continue
            #: ★ ① 字符串字面量里的成员名
            for m in re.finditer(r'"([A-Za-z_][A-Za-z0-9_]{2,})"', line):
                nm = m.group(1)
                if nm in names:
                    hits.append({"file": str(f.relative_to(REPO)), "member": nm,
                                 "how": "字符串字面量", "line_text": s[:150],
                                 "successors": sorted({e["successor"] for e in by_member[nm]
                                                       if e["successor"]})[:3],
                                 "interfaces": sorted({e["interface"] for e in by_member[nm]})[:3]})
            #: ★ ② 属性访问里的成员名
            for m in re.finditer(r"\.([A-Za-z_][A-Za-z0-9_]{2,})\s*\(", line):
                nm = m.group(1)
                if nm in names:
                    hits.append({"file": str(f.relative_to(REPO)), "member": nm,
                                 "how": "属性访问", "line_text": s[:150],
                                 "successors": sorted({e["successor"] for e in by_member[nm]
                                                       if e["successor"]})[:3],
                                 "interfaces": sorted({e["interface"] for e in by_member[nm]})[:3]})
    #: ★ 去重（同文件同成员同方式只留一条，★ 但记次数）
    agg: dict = {}
    for h in hits:
        k = (h["file"], h["member"], h["how"])
        agg.setdefault(k, {**h, "count": 0})
        agg[k]["count"] += 1
    rows = sorted(agg.values(), key=lambda r: (-r["count"], r["file"], r["member"]))

    OUT.write_text(json.dumps({"at": time.strftime("%Y-%m-%d %H:%M:%S"),
                               "official_obsolete_members": len(names),
                               "scanned_files": scanned,
                               "hit_rows": len(rows),
                               "hit_occurrences": len(hits),
                               "rows": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("★ 扫了 **%d** 个文件 ⇒ ★★ **%d 处**（去重后 **%d** 行）用到官方废弃成员"
          % (scanned, len(hits), len(rows)))
    cnt = Counter(r["member"] for r in rows)
    print()
    print("★ 按成员排（前 20）：")
    print("%-34s %-8s %-34s %s" % ("官方废弃成员", "出现文件数", "官方点名的后继", "接口"))
    print("-" * 118)
    for nm, n in cnt.most_common(20):
        e0 = by_member[nm][0]
        succ = sorted({e["successor"] for e in by_member[nm] if e["successor"]})
        print("%-34s %-8d %-34s %s" % (nm[:33], n, (succ[0] if succ else "（官方没写）")[:33],
                                       e0["interface"][:22]))
    print()
    print("★ 按文件排（前 14）：")
    fcnt = Counter(r["file"] for r in rows)
    for fn, n in fcnt.most_common(14):
        print("   %-44s %d" % (fn[:43], n))
    print()
    print("★ 产出:", OUT, "（耗时 %.1f s）" % (time.time() - started))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
