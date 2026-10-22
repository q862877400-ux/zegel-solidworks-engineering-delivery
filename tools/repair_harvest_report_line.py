"""★ 恢复 docs/harvest-report.md 里被审计输出覆盖的那一行（★ 第二次发生；从 HEAD 取值，不手打）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/repair_harvest_report_line.py
# 定位:   恢复 docs/harvest-report.md 里被审计输出覆盖的那一行（★ 第二次发生；从 HEAD 
#           取值，不手打）。
# 官方依据: 不适用（本仓工具，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = ROOT / "docs" / "harvest-report.md"
rel = "docs/harvest-report.md"

#: ★ 从 HEAD 取"那一行"的原文（★ 不手打 —— 事实 48 定则①：内容从文件里搬，不从脑子里搬）
head = subprocess.run(["git", "show", "HEAD:%s" % rel], cwd=str(ROOT),
                      capture_output=True, encoding="utf-8", errors="replace").stdout
head_line = next((ln for ln in head.splitlines() if "偏离上游：" in ln), None)
print("★ HEAD 里那一行: %r" % (head_line or "")[:130])

cur = io.open(P, encoding="utf-8").read()
lines = cur.splitlines(keepends=True)
#: ★★ 判据用**包含**而不是**开头** —— ★ 坏内容的形态是「审计的输出被**拼在**那一行前面」
#:    （实测：那一行前面被拼了三段重复的审计源码文本）⇒ 用 startswith 会一行都找不到 ✓
#:    ⚠ ★ 本注释**刻意不逐字引用**那段审计源码：`check_negative_input_selfproof` 按子串扫，
#:      引用它会把它自己的触发词带进来 ⇒ 被误报（★ 事实 516 的机制）✓
idx = [i for i, ln in enumerate(lines) if "偏离上游：" in ln]
print("★ 当前文件里含该串的行: %d 行（位置 %s）" % (len(idx), idx[:3]))
if not idx:
    print("★★ 找不到那行 ⇒ 不猜，停手")
    raise SystemExit(1)
if head_line is None:
    print("★★ HEAD 里也没有 ⇒ 停手（不手造）")
    raise SystemExit(1)

lines[idx[0]] = head_line.rstrip("\n") + "\n"
#: ★★★ 只改**那一行**，其余一律不动（★ 那是别人暂存的内容）
io.open(P, "w", encoding="utf-8", newline="").write("".join(lines))
print("★ 已把第 %d 行恢复为 HEAD 的值（★ 其余行未动）" % (idx[0] + 1))
after = io.open(P, encoding="utf-8").read().splitlines()
print("★ 回读第 %d 行: %r" % (idx[0] + 1, after[idx[0]][:120]))
