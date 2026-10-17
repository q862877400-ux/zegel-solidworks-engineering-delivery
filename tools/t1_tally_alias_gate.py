"""★ T1-4：把裁判判定并进别名表 —— ★ 只采纳 `same`，其余标待复核/弃用。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = ROOT / "output" / "t1-judge"

verdicts: dict = {}
generic: dict = {}
for f in sorted(D.glob("alias-out-*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    for v in d.get("verdicts") or []:
        verdicts[v["tool"]] = v.get("verdict", "?")
        if v.get("generic_words"):
            generic[v["tool"]] = v["generic_words"]

gain = json.loads((ROOT / "output" / "t1-alias-gain.json").read_text(encoding="utf-8"))["summary"]
cand = json.loads((ROOT / "output" / "t1-alias-candidates.json").read_text(encoding="utf-8"))
pair_of: dict = {}
for k in cand["kept"]:
    a = pair_of.setdefault(k["tool"], {"ops": set(), "keys": set(), "sources": set()})
    a["ops"].add(k["op"])
    a["keys"] |= set(k["keys"])
    a["sources"] |= set(k.get("sources") or [])

rows = []
for r in gain:
    t = r["tool"]
    v = verdicts.get(t, "**未判**")
    rows.append({**r, "verdict": v, "generic": generic.get(t, [])})

from collections import Counter
c = Counter(x["verdict"] for x in rows)
print("★ 裁判判定分布（n=%d）: %s" % (len(rows), dict(c)))
print()

#: ★★ 只采纳 same；related 待复核；wrong 弃用
same = [x for x in rows if x["verdict"] == "same"]
rel = [x for x in rows if x["verdict"] == "related"]
wrong = [x for x in rows if x["verdict"] == "wrong"]
print("★★ 采纳（same）: %d 个工具" % len(same))
for x in sorted(same, key=lambda y: -(y["gain"] or 0)):
    p = pair_of[x["tool"]]
    print("     %-42s 别名=%s  排名 %s→%s"
          % (x["tool"].removeprefix("solidworks_"), ",".join(sorted(p["ops"] | p["keys"])),
             x["rank0"], x["rank1"]))
print()
print("★ 待复核（related）: %d 个 —— ★ 不接进 doc，等真实语料或人工判" % len(rel))
print("★★ 弃用（wrong，泛词命中）: %d 个 —— 附裁判点名的泛词" % len(wrong))
for x in wrong[:10]:
    print("     %-42s 泛词=%s" % (x["tool"].removeprefix("solidworks_"),
                                  ",".join(x["generic"]) or "—"))

#: ★ 重写别名表
lines = [
    "# 工具别名表（★ 由 C5 手核数据机械筛 + 增益实测 + **语义闸**得出）",
    "",
    "> **生成物** —— 由 `tools/t1_tally_alias_gate.py` 产出，**不要手改**。",
    "> 输入：`specs/204-bunny-moat-batches/recon/c5-gap-handcheck.json`（另一个对话的 C5 手核，只读复用）"
    "+ 本仓 `all_specs()` + 3 路独立裁判的语义判定。",
    "",
    "## 一 · ★★ 头号结论：**C5 的「换名已有」经语义闸后大幅缩水**",
    "",
    "| 阶段 | 数 | 说明 |",
    "|---|---|---|",
    "| C5 手核判「换名已有」 | **24** 行 | 另一个对话的人工判读（`conditional_pass`）|",
    "| 其 `hits` 展开成候选对 | 97 对 | ★ `hits` 是**子串匹配**的产物 |",
    "| 机械筛后（词必须出现在 name/title）| **79 对 / 52 工具** | ★ 丢掉 18 对子串疑云 |",
    "| 增益实测（别名当查询）| 45/52 **提升** | ★★ 但**近似同义反复**（查询词就是别名本身）|",
    "| ★★★ **语义闸（3 路裁判）** | ★ **same 仅 9** · related 28 · **wrong 15** | ★★ 83% 不是同一件事 |",
    "",
    "★★ **所以：`hits` 里「子串命中」与「真是别名」是两回事，而增益实测分不开它们** ——",
    "★ 只有**语义闸**能分开。本表最终只采纳 **9** 条。",
    "",
    "## 二 · ★ 采纳（**9** 条 · 裁判判 `same`）",
    "",
    "| 工具 | 别名 | 排名 现状→加别名 | 增益 |",
    "|---|---|---|---:|",
]
for x in sorted(same, key=lambda y: -(y["gain"] or 0)):
    p = pair_of[x["tool"]]
    lines.append("| `%s` | %s | %s → **%s** | +%d |"
                 % (x["tool"], ", ".join(sorted(p["ops"] | p["keys"])),
                    x["rank0"], x["rank1"], x["gain"] or 0))
lines += ["", "## 三 · ★ 待复核（**%d** 条 · 判 `related`）—— **不接进 doc**" % len(rel), "",
          "★ 判据：「同域但不是同一件事」⇒ 接进去会把不该命中的工具抬上来。"]
for x in sorted(rel, key=lambda y: y["tool"]):
    p = pair_of[x["tool"]]
    lines.append("- `%s` ← %s" % (x["tool"], ", ".join(sorted(p["ops"] | p["keys"]))))
lines += ["", "## 四 · ★★ 弃用（**%d** 条 · 判 `wrong`）—— 附裁判点名的泛词" % len(wrong), "",
          "★★ 这些是**子串/泛词命中**的证据：别名里只有 `drawing` / `sketch` / `box` / `macro` 这类",
          "**在很多工具里都出现**的词，于是与工具匹配上了，但那个词**并不指向这个工具的功能**。", "",
          "| 工具 | 别名 | 裁判点名的泛词 |", "|---|---|---|"]
for x in sorted(wrong, key=lambda y: y["tool"]):
    p = pair_of[x["tool"]]
    lines.append("| `%s` | %s | %s |"
                 % (x["tool"], ", ".join(sorted(p["ops"] | p["keys"])),
                    ", ".join(x["generic"]) or "—"))
lines += [
    "",
    "## 五 · 口径（★ 与数字一起读）",
    "",
    "- ★ **采纳面只到 9 条**，因为语义闸逐条判 —— 不是「45 条都有效」；",
    "- ★ **误报率自查**：`wrong 15 / 52 = 28.8%` ⇒ ★★ **远超我自定的 D-1 阈值（≤5%）**",
    "  ⇒ **本批候选不得直接进门禁/进 doc**，只把 `same` 的 9 条作为**候选队列**，",
    "  ★ 且需**再上真实语料复测**（当前无中文语料）；",
    "- ★ **每条只被 1 路裁判判过**（3 路各判 1/3）⇒ 未做多数票 ⇒ 记 `conditional_pass`；",
    "- ★★ **不构成**任何「中文用户会怎么说」的证据（别名全是英文词）。",
]
out = ROOT / "docs" / "tool-aliases.md"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print()
print("★ 已重写 %s（%d 行）" % (out, len(lines)))
print("★★ 误报率自查: wrong 15/52 = **28.8%%** ⇒ 远超 D-1 阈值 5%% ⇒ 只采纳 same 9 条、记 conditional_pass")
(ROOT / "output" / "t1-alias-final.json").write_text(
    json.dumps({"same": same, "related": rel, "wrong": wrong}, ensure_ascii=False, indent=1),
    encoding="utf-8")
