"""★ 定点修 JSON：把我刚写进豁免理由里的 `C:\\swapi` 补上转义（★ 用 json.load 自证）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/fix_exemption_escapes.py
# 定位:   定点修 JSON：把我刚写进豁免理由里的 `C:\swapi` 补上转义（★ 用 json.load 自证
#           ）。
# 官方依据: 不适用（本仓工具，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

P = Path(Path(__file__).resolve().parents[1] / "docs" / "gate-wiring-exemptions.json")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
s = io.open(P, encoding="utf-8").read()

#: ★★ 定点：把**未转义**的 `C:\swapi` 补成 `C:\\swapi`
#:   （★ 只改这一个 token，不做通用反斜杠替换 —— 事实 61：批量盲改会改坏别处）
before = s.count("C:\\swapi")
after = s.count("C:\\\\swapi")
print("★ 修前: 未转义 %d 处 · 已转义 %d 处" % (before, after))
s2 = s.replace("C:\\swapi", "C:\\\\swapi")
io.open(P, "w", encoding="utf-8", newline="").write(s2)
print("★ 修后: 未转义 %d 处 · 已转义 %d 处"
      % (s2.count("C:\\swapi"), s2.count("C:\\\\swapi")))
#: ★ 自证：JSON 必须能加载（★ 这是唯一算数的判据）
d = json.load(io.open(P, encoding="utf-8"))
print("★★ JSON ok · %d 条豁免: %s" % (len(d["exemptions"]), [x["gate"] for x in d["exemptions"]]))
