"""★ 扫 `capabilities.yaml` 里全部 `output/*.json` 引用 —— ★ 报出**死链**（★ 同类问题一次扫清）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tools/scan_evidence_links.py
# 定位:   ★ 阶段 1 的 **B-2**（★ 裁判逐字：「★ 两处**文件名笔误** …
#   ★★ 但它们按判据「逐个 `path.exists`」是**死链**，会污染后续的证据可达性检查」）⇒
#   ★ 所以**修两处之后要扫一遍全部**，★ 看还有没有同类的 ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(r"D:\AI\SW")
sys.stdout.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(errors="replace") if hasattr(sys.stdout, "reconfigure") else None

TEXT = (REPO / "capabilities.yaml").read_text(encoding="utf-8", errors="replace")
#: ★ 抓 `output/<名>.json` 与裸的 `<名>-evidence.json` 两种写法
PAT = re.compile(r"\boutput/([A-Za-z0-9_.\-]+\.json)\b")
PAT2 = re.compile(r"\b([a-z0-9][A-Za-z0-9_\-]*(?:evidence|probe|report|scan)\.json)\b")


def main() -> int:
    seen, dead, alive = {}, [], []
    for m in PAT.finditer(TEXT):
        seen.setdefault(m.group(1), "output/")
    for m in PAT2.finditer(TEXT):
        seen.setdefault(m.group(1), "bare")
    for name, how in sorted(seen.items()):
        f = REPO / "output" / name
        (alive if f.is_file() else dead).append((name, how, f.stat().st_size if f.is_file() else 0))
    print("★ capabilities.yaml 里引到的 `output/*.json` 共 **%d** 个" % len(seen))
    print("★★ 存在的 **%d** 个" % len(alive))
    print("★★★ 死链   **%d** 个" % len(dead))
    if dead:
        print()
        for name, how, _ in dead:
            print("   ✗ %-62s (%s)" % (name, how))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
