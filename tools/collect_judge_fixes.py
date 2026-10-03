"""★ 从 3 份裁判稿里抽「🔴 立刻要改」清单 —— ★ 汇总成一张可执行的工作表。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tools/collect_judge_fixes.py
# 定位:   ★ 阶段 1：`workflow-16` 的 **3 路裁判**（`JUDGE-A_B` · `JUDGE-C_D_E` ·
#   `JUDGE-F_G_H_I_J`）产出的"立刻要改"清单 ⇒ ★ **汇总成一张表**（★ 供逐条施工）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(r"D:\AI\SW")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
Q = REPO / "specs" / "202-user-coverage-gaps" / "recon" / "verify50"

#: ★ 找"立刻要改"那一节的标题（★ 三份稿的写法可能不同）
HEAD = re.compile(r"^#{2,4}\s*.*(立刻要改|立刻改|要立刻改)")


def main() -> int:
    total = 0
    for f in sorted(Q.glob("JUDGE-*.md")):
        lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        print("=" * 24, f.name)
        #: ★ 打印"计数"与"成立率"两节的要点 + 立刻要改那一节
        for i, l in enumerate(lines):
            if HEAD.match(l):
                print("★ 节：", l.strip()[:110])
                n = 0
                for k in range(i + 1, min(len(lines), i + 40)):
                    s = lines[k].strip()
                    if s.startswith("#") and k > i + 1:
                        break
                    if s.startswith("|") and not re.match(r"^\|[\s\-:|]+\|$", s):
                        #: ★ 只打印不是表头的行
                        if "条目" in s and "一句话" in s:
                            continue
                        if "|---|---" in s:
                            continue
                        print("   ", s[:170])
                        n += 1
                total += n
                print("   ★ 本节行数:", n)
                break
        #: ★ 顺带抓成立率
        for l in lines:
            if "成立率" in l and "|" in l:
                print("★", l.strip()[:130])
        print()
    print("★ 三份稿的『立刻要改』条目合计（粗计）:", total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
