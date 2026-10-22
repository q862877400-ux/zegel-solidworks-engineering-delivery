"""★ 最终结算：**「模型挑出来的第一个工具，到底对不对」**（★ 不是"有没有命中我标的那个"）。

★ 数据链：
  挑工具（48 路真模型，各自看得见本仓 478 个工具的清单）
    → 盲判（20 路独立裁判，2 个/组，★ 不给期望、顺序打乱）
    → 本脚本按【工具名】对齐，出四类数：
       ① ★★ **首选的判定分布**（yes / partial / no / cannot_tell）← ★ 这是业主问的那个百分比
       ② ★ **前二里至少一个 yes** 的比例（★ 衡量"备选兜住了吗"）
       ③ ★★ **裁判判 yes 但我标的期望工具不是它** 的清单（★ 说明我的标签错了，
          或这件事本来就有多个正确工具 —— 两种都值得看）
       ④ ★ 两个裁判的**分歧率**（A vs B）—— 衡量这个「对不对」的判定有多主观
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/tally_pick_test.py
# 定位:   最终结算：**「模型挑出来的第一个工具，到底对不对」**（★ 不是"有没有命中我标
#           的那个"）。
# 官方依据: 不适用（本仓工具，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = Path(Path(__file__).resolve().parents[1] / "output" / "pick-test")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import metric_scope as ms   # ★ 口径注册表（事实 517：口径必须落成代码）

idx = json.loads((D / "_judge_index.json").read_text(encoding="utf-8"))
by_i = {p["index"]: p for p in idx}

#: ★ 收裁判结论：{index: {judge: {tool: verdict}}}
verdicts: dict = {}
for f in sorted(D.glob("judge-out-*.json")):
    jt = "B" if f.stem.endswith("-B") else "A"
    for row in json.loads(f.read_text(encoding="utf-8")):
        i = int(row.get("index", -1))
        if i not in by_i:
            continue
        verdicts.setdefault(i, {})
        verdicts[i][jt] = {v["tool"]: v.get("verdict", "?") for v in (row.get("verdicts") or [])}

print("★ 挑工具结果 %d 组 · 收到裁判结论的 %d 组" % (len(by_i), len(verdicts)))
print()
print(ms.block_for('model_pick_correct'))
print()

rows = []
for i, p in by_i.items():
    vs = verdicts.get(i, {})
    first = p["candidates"][0] if p["candidates"] else None
    a = vs.get("A", {})
    b = vs.get("B", {})
    rows.append({
        "index": i, "task": p["task"], "stratum": p["stratum"],
        "expected": p["expected_tool"], "first": first,
        "cands": p["candidates"], "none": p["none"],
        "vA_first": a.get(first, "no_verdict") if first else None,
        "vB_first": b.get(first, "no_verdict") if first else None,
        "any_yes_A": any(v == "yes" for v in a.values()),
        "any_yes_B": any(v == "yes" for v in b.values()),
        "yes_tools_A": [t for t, v in a.items() if v == "yes"],
        "yes_tools_B": [t for t, v in b.items() if v == "yes"],
    })

#: ★ ① 首选的判定分布（★ 业主问的那个百分比）
for jt, key in (("A（主判）", "vA_first"), ("B（复核）", "vB_first")):
    valid = [r for r in rows if r[key] is not None]
    c = Counter(r[key] for r in valid)
    n = len(valid)
    print("★ ①【%s】模型**首选**工具「到底对不对」的分布（n=%d）:" % (jt, n))
    for k in ("yes", "partial", "no", "cannot_tell", "no_verdict"):
        if c.get(k):
            print("     %-12s %2d / %d = **%.0f%%**" % (k, c[k], n, 100.0 * c[k] / n))
    print()

#: ★ ② 前二里至少一个 yes
for jt, key in (("A", "any_yes_A"), ("B", "any_yes_B")):
    v = [r for r in rows if r["cands"]]
    k = sum(1 for r in v if r[key])
    print("★ ②【%s】首选+备选里**至少有一个被判 yes** 的: %d / %d = **%.0f%%**"
          % (jt, k, len(v), 100.0 * k / len(v)))
print()

#: ★ ③ 判 yes 但与我标的期望不同的
print("★★ ③ 裁判判 yes、但**不是我标的那个工具**的（★ 要么我标错了，要么这件事有多个正解）:")
n_diff = 0
for r in rows:
    yes = set(r["yes_tools_A"]) | set(r["yes_tools_B"])
    if yes and r["expected"] not in yes:
        n_diff += 1
        print("     [%s] 任务「%s」" % (r["stratum"].split("_")[0], r["task"][:26]))
        print("          我标的: %s" % r["expected"].removeprefix("solidworks_"))
        print("          ★ 裁判认可的: %s" % ", ".join(t.removeprefix("solidworks_")
                                                       for t in sorted(yes)))
print("     ⇒ 共 **%d** 组" % n_diff)
print()

#: ★ ④ 两裁判分歧
both = [r for r in rows if r["vA_first"] and r["vB_first"] and r["vA_first"] != "no_verdict"
        and r["vB_first"] != "no_verdict"]
dis = [r for r in both if r["vA_first"] != r["vB_first"]]
print("★ ④ 两个裁判对**首选**的判定不一致: %d / %d = **%.0f%%**（★ 越大说明「对不对」越主观）"
      % (len(dis), len(both), 100.0 * len(dis) / max(1, len(both))))
for r in dis[:8]:
    print("     %s: A=%s B=%s" % (r["first"].removeprefix("solidworks_")[:34],
                                  r["vA_first"], r["vB_first"]))
print()

#: 分层
print("★ 分层（以 A 判为准）: yes / 有效")
for st in ("C1_cold_no_cn_doc_small_domain", "C2_cold_thin_doc",
           "C3_non_api_selfmade", "H_hot_baseline"):
    s = [r for r in rows if r["stratum"] == st and r["vA_first"] and r["vA_first"] != "no_verdict"]
    if s:
        y = sum(1 for r in s if r["vA_first"] == "yes")
        print("     %-34s %d / %d = %.0f%%" % (st.split("_")[0], y, len(s), 100.0 * y / len(s)))

(D / "_final.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
print()
print("★ 明细: output/pick-test/_final.json")
