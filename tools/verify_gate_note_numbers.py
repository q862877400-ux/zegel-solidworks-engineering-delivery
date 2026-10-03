"""★ 核 B-6 里 C4 / C11 的两组数（★ 改前先核）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tools/verify_gate_note_numbers.py
# 定位:   ★ 阶段 1 的 **B-6**：★ 那四处附注要改，★ 而**改前先核**（★ 本轮刚学的教训：
#   ★★ "改正"这个动作必须可核）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(r"D:\AI\SW")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
IDX = REPO / "specs" / "202-user-coverage-gaps" / "recon" / "official-members-index.json"


def main() -> int:
    d = json.loads(IDX.read_text(encoding="utf-8"))
    pi = d.get("per_interface") or {}
    slots = sum(len(v) for v in pi.values())
    uniq = len({x["member"] for v in pi.values() for x in v})
    head = {k: v for k, v in d.items() if k != "per_interface"}
    print("★ C4 —— 两个口径")
    print("   ★ 接口数            =", len(pi))
    print("   ★ 成员槽合计        =", slots, "  （★ GATE-FINAL 写 11557）")
    print("   ★ 唯一成员名        =", uniq)
    print("   ★ JSON 头部字段     =", head)
    print("   ★★ 11557 + 接口数   =", 11557 + len(pi), " （★ 若 == 12123 ⇒ 差值正是「每接口一个 _overview」）")

    print()
    print("★ C11 —— 「3 处」vs 实测")
    n, files = 0, set()
    for f in REPO.rglob("*"):
        if not f.is_file() or ".git" in str(f):
            continue
        try:
            t = f.read_text(encoding="utf-8", errors="replace")
        except Exception:                                                 # noqa: BLE001
            continue
        if "classify_audit_divergences" in t:
            n += t.count("classify_audit_divergences")
            files.add(str(f.relative_to(REPO)))
    #: ★ 排除"这个报告自己"与 D 自己的报告（★ 与裁判一致的口径）
    skip = ("verify-done/D-gate-anchors.md", "verify-done/VERIFY-DONE-SUMMARY.md",
            "verify50/vd50-D-3.md")
    n2, f2 = 0, set()
    for f in REPO.rglob("*"):
        if not f.is_file() or ".git" in str(f):
            continue
        rel = str(f.relative_to(REPO)) if f.is_relative_to(REPO) else str(f)
        if any(s in rel for s in skip):
            continue
        try:
            t = f.read_text(encoding="utf-8", errors="replace")
        except Exception:                                                 # noqa: BLE001
            continue
        if "classify_audit_divergences" in t:
            n2 += t.count("classify_audit_divergences")
            f2.add(rel)
    print("   ★ 全仓（含报告自己）  = %d 处 / %d 个文件" % (n, len(files)))
    print("   ★★ 排除三份报告后    = %d 处 / %d 个文件" % (n2, len(f2)))
    print("   ★★ 裁判记的实测      = 16 处 / 5 个文件")
    for x in sorted(f2):
        print("      ·", x[:90])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
