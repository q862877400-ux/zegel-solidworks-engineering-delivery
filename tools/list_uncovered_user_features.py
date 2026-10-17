"""★ 从 145 项用户功能清单里抽出「本仓库未覆盖」的那些（★ 只读，不改产物）。"""
from __future__ import annotations

import collections
import pathlib

DOC = pathlib.Path(pathlib.Path(__file__).resolve().parents[1] / "docs" / "user-feature-coverage.md")
NAMES = ("Solidworks-MCP-Server", "SolidworksMCP-python", "SolidworksMCP-TS", "solidworks-mcp")


def main() -> int:
    text = DOC.read_text(encoding="utf-8")
    i = text.index("## 九 ·")
    rows = []
    for ln in text[i:].splitlines():
        s = ln.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) != 7 or cells[0] == "域" or set(cells[1]) <= set("-"):
            continue
        rows.append(cells)
    print("★ 清单总条数 = %d" % len(rows))
    bad = [r for r in rows if r[2] != "✅"]
    print("★★ 本仓库**未覆盖** = %d 项" % len(bad))
    print()
    by = collections.defaultdict(list)
    for r in bad:
        by[r[0]].append(r)
    for dom in by:
        print("【%s】%d 项" % (dom, len(by[dom])))
        for r in by[dom]:
            who = [n for n, v in zip(NAMES, r[3:]) if v == "✅"]
            print("   · %-18s ★ 四家里有：%s" % (r[1], "、".join(who) or "（★ 四家都没有）"))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
