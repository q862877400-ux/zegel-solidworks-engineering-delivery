"""★ 列出**生产（`scripts/`）**里剩下的废弃成员调用点 —— ★ 逐条核"是不是都已判过"。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（读 `tools/scan_obsolete_safe.py` 的产物）。
# 文件:   tools/list_production_obsolete.py
# 定位:   ★ 阶段 2 的**收口核对**：★ 生产还剩多少条、★ 各在哪、★ 是不是都已判过
#   （★ 判据来自 `tools/scan_obsolete_safe.py`，★ **不改判据**，★ 只读它的产物）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(r"D:\AI\SW")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = REPO / "output" / "obsolete-dotcall-scan.json"


def main() -> int:
    d = json.loads(SRC.read_text(encoding="utf-8", errors="replace"))
    print("★ 产物顶层键:", list(d.keys())[:10])
    #: ★ 找"真命中"那一类
    rows = None
    for k in ("真命中", "真命中（待修）", "hits", "真命中待修"):
        if isinstance(d.get(k), list):
            rows = d[k]
            break
    if rows is None:
        for k, v in d.items():
            if isinstance(v, list) and v and isinstance(v[0], dict) and "member" in str(v[0]):
                rows = v
                print("★ 用键:", k)
                break
    if rows is None:
        print("★★ 找不到真命中列表 ⇒ 键:", {k: type(v).__name__ for k, v in d.items()})
        return 1
    prod = [r for r in rows if "scripts" in str(r.get("file", "")).replace("\\", "/")]
    print("★ 真命中合计 %d ⇒ ★★ **生产 %d**" % (len(rows), len(prod)))
    print()
    print("%-42s %-26s %s" % ("文件", "成员", "行"))
    print("-" * 88)
    for r in sorted(prod, key=lambda x: (str(x.get("file")), x.get("line") or 0)):
        f = str(r.get("file", "")).replace("\\", "/").split("/")[-1]
        print("%-42s %-26s %s" % (f[:41], str(r.get("member"))[:25], r.get("line")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
