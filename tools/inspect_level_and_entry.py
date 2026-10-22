"""★ 看 `capabilities.yaml` 的 level 取值分布 + 某条目的 limitations（★ 供 A-assembly F1 处置）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tools/inspect_level_and_entry.py
# 定位:   ★ 阶段 1 的 **A-assembly F1**（★ 裁判 [`JUDGE-A_B.md`] 判为"🔴 立刻要改"）：
#   ★ 条目 `assembly_and_mates` 的证据顶层是 `verdict: fail`，★ 而条目是 `verified` ⇒
#   ★★ 要改 level ⇒ ★ **先看清本仓的 level 枚举与同域别的条目怎么写** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    d = json.loads((REPO / "capabilities.yaml").read_text(encoding="utf-8"))
    caps = d.get("capabilities") or []
    print("★ level 取值分布:", dict(collections.Counter(c.get("level") for c in caps)))
    print()
    c = next((x for x in caps if x.get("id") == "assembly_and_mates"), None)
    if not c:
        print("★ 找不到 assembly_and_mates")
        return 1
    print("★ id:", c["id"], "· level:", c["level"])
    print("★ label:", c["label"][:110])
    print("★ limitations:")
    for x in c.get("limitations") or []:
        print("   ·", x[:200])
    print()
    print("★ 同域别的条目的 level（★ 看惯例）：")
    for x in caps:
        i = str(x.get("id") or "")
        if "assembly" in i or "mate" in i:
            print("   %-34s %s" % (i[:33], x.get("level")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
