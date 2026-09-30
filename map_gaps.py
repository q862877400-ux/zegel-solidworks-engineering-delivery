"""@brief 从广度地图 §五 抽出各域的「缺口数」与各来源的「该域有数」。

用途：核 ROADMAP 的 P4–P6 表 —— 那张表填错过一次（把「四家域操作总数」
当成了「我们的缺口数」，草图 77 vs 真实缺口 42）。

# ── 来源 ──
# 仓库:   本项目自身（草稿工具）
# 文件:   map_gaps.py
# 定位:   AGENTS.md「报告计数要附枚举命令」—— 数字必须能重跑出来。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 纯文本解析，未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MAP = Path(r"C:\swprojects\sw-skill-fork\docs\union-coverage-matrix.md")

text = MAP.read_text(encoding="utf-8")
blocks = re.split(r"\n### ", text)

print("域                      缺口   来源(该域有)")
print("-" * 72)
total = 0
for block in blocks[1:]:
    head = block.split("\n", 1)[0]
    m = re.search(r"缺\s*(\d+)", head)
    if not m:
        continue
    gap = int(m.group(1))
    total += gap
    name = re.sub(r"[（(]缺.*$", "", head).strip()
    srcs = re.findall(r"\|\s*`([^`]+)`\s*\|\s*(\d+)\s*\|", block)
    desc = "  ".join("%s=%s" % (a.split("/")[-1][:18], b) for a, b in srcs[:4])
    print("%-22s %4d   %s" % (name[:22], gap, desc))
print("-" * 72)
print("%-22s %4d" % ("合计", total))
