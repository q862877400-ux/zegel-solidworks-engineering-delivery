"""★ SC-008：报"某批工具**背后的能力**里有多少条是 `verified`"（★ 规格 205 §7.2 要求）。

★ 为什么（★ 支线那条告诫）：★「工具数」是**代码组织方式的函数**，不是能力指标 ⇒
  ★ 所以每批都要报"能力侧的真实性"，不能只报工具数 ✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/report_batch_capability_levels.py
# 定位:   SC-008：报"某批工具**背后的能力**里有多少条是 `verified`"（★ 规格 205 §7.2 
#           要求）。
# 官方依据: 不适用（本仓工具，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import argparse
import io
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--names", nargs="*", default=[], help="本批工具名；省略则按批次文件数")
    ap.add_argument("--modules", nargs="*", default=[])
    a = ap.parse_args()
    import register_capabilities as rc
    caps = json.loads((ROOT / "capabilities.yaml").read_text(encoding="utf-8"))["capabilities"]
    specs = {s.name: s for s in rc.all_specs()}

    if not a.modules:
        mods = Counter()
        for n in a.names:
            s = specs.get(n)
            if s is not None:
                mods[getattr(s, "module", "")] += 1
        a.modules = [m for m, _ in mods.most_common()]
    print("★ 本批涉及的实现模块:", a.modules)

    #: ★ 把能力条目与模块对上：看它的 `mcp_tools` / `evidence` / `source_evidence` 里有
    #: 没有该模块
    hit: dict = {}
    for c in caps:
        blob = json.dumps(c, ensure_ascii=False)
        for m in a.modules:
            if m and m in blob:
                hit.setdefault(c["id"], {"level": c.get("level"), "modules": set()})
                hit[c["id"]]["modules"].add(m)
    levels = Counter(v["level"] for v in hit.values())
    print("★ 相关能力条目 **%d** 条 · level 分布: %s" % (len(hit), dict(levels)))
    ver = sum(1 for v in hit.values() if v["level"] == "verified")
    print("★★ SC-008：其中 **verified %d 条** / 共 %d 条（%.0f%%）"
          % (ver, len(hit), 100.0 * ver / max(1, len(hit))))
    for cid, v in sorted(hit.items()):
        mark = "★" if v["level"] == "verified" else " "
        print("   %s %-34s %s" % (mark, cid, v["level"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
