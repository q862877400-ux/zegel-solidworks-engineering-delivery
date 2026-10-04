"""★ T2-5：产出「哪些能力的前置未覆盖」清单给主线（★ D-5：只出清单，不改 level）。"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
d = json.loads((ROOT / "output" / "t2-preconditions-checkable.json").read_text(encoding="utf-8"))
ck = json.loads((ROOT / "specs" / "204-bunny-moat-batches" / "recon"
                 / "c3-merged.json").read_text(encoding="utf-8"))

per_cap: dict = defaultdict(lambda: {"total": 0, "not_covered": 0, "checkable": 0, "level": ""})
for cap in ck["results"]:
    e = per_cap[cap["name"]]
    e["level"] = cap.get("level", "")
    e["total"] = len(cap.get("preconditions") or [])
    e["not_covered"] = sum(1 for p in (cap.get("preconditions") or [])
                           if p.get("state") == "not_covered")
for r in d["checkable"]:
    per_cap[r["cap"]]["checkable"] += 1

rows = sorted(per_cap.items(), key=lambda kv: -kv[1]["checkable"])
lines = [
    "# 能力前置覆盖缺口清单（★ 给主线的决策输入 · 本文件**不改** `capabilities.yaml`）",
    "",
    "> **生成物** —— 由 `tools/t2_write_precondition_gaps.py` 产出，**不要手改**。",
    "> 输入：`specs/204-bunny-moat-batches/recon/c3-merged.json`（另一个对话的 C3 对账，"
    "**只读复用**，其 `conditional_pass` 状态见该规格的 REPORT.md §七）。",
    "",
    "## 一 · 口径（★ 与数字一起读）",
    "",
    "| 项 | 值 |",
    "|---|---|",
    "| 能力条目 | **98**（另一个对话判完的；`capabilities.yaml` 当期共 112 条能力）|",
    "| 有前置条目的 | 91 |",
    "| 前置条目总数 | **%d** |" % sum(e["total"] for e in per_cap.values()),
    "| —— `not_covered`（未覆盖）| ★ **%d** |" % sum(e["not_covered"] for e in per_cap.values()),
    "| —— 其中 ★ **可机检**（提到会话/文档/选择/保存态）| ★ **%d** |" % len(d["checkable"]),
    "| —— 不可机检 | %d（7 条外部工具链/人工操作 + 213 条没提会话状态）|"
    % len(d["not_checkable"]),
    "",
    "★★ **本清单「不算什么」**：",
    "",
    "- ★ **不等于**「这 %d 条能力是坏的」—— 它只说**运行证据没覆盖官方示例揭示的前置**；" % len(per_cap),
    "- ★★ **不是** `level` 的依据（★ 改 level 是主线的决定，D-5）；",
    "- ★ **不可机检的 220 条不算缺陷** —— 它们是环境/工具链要求（如「先建 VS 工程」），本仓不该为此写断言；",
    "- ★ 来源是**另一个对话的判读**且全程 `conditional_pass`（★ 其 REPORT §七 自陈：C3 的更正**未再被门禁复核**）⇒",
    "  ★ **本清单是候选队列**，采纳前需逐条过闸 ✓",
    "",
    "## 二 · ★ 可机检前置最多的能力（**这 %d 条值得先补断言**）" % sum(
        1 for _n, e in rows if e["checkable"]),
    "",
    "| 能力 | level | 前置总数 | 未覆盖 | ★ 其中可机检 |",
    "|---|---|---:|---:|---:|",
]
for name, e in rows:
    if e["checkable"]:
        lines.append("| `%s` | %s | %d | %d | **%d** |"
                     % (name, e["level"] or "—", e["total"], e["not_covered"], e["checkable"]))
lines += [
    "",
    "## 三 · ★ 可机检的前置逐条（按能力分组 · 前 40 条）",
    "",
    "> ★ 每条都是**官方示例文件里写的前置**，而本仓的运行证据没覆盖它。",
    "> 格式：`[能力] 前置文本` —— ★ 括号里是该前置出自哪个示例文件。",
    "",
]
by_cap: dict = defaultdict(list)
for r in d["checkable"]:
    by_cap[r["cap"]].append(r)
n = 0
for cap, rs in sorted(by_cap.items(), key=lambda kv: -len(kv[1])):
    lines.append("### `%s`（%d 条）" % (cap, len(rs)))
    lines.append("")
    for r in rs:
        if n >= 40:
            break
        lines.append("- %s  <sub>（`%s`）</sub>" % (r["text"], r["from"]))
        n += 1
    lines.append("")
    if n >= 40:
        lines.append("★ 其余见 `output/t2-preconditions-checkable.json` 的 `checkable` 数组。")
        break
out = ROOT / "docs" / "precondition-coverage-gaps.md"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("★ 写出 %s（%d 行）" % (out.name, len(lines)))
print("★ 有可机检前置的能力: %d · 可机检前置 %d 条"
      % (sum(1 for _n, e in rows if e["checkable"]), len(d["checkable"])))
