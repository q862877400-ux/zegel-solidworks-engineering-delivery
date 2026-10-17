"""★ 组装**盲判**输入：把 48 路挑出来的工具，配上它**真实的 title/描述**，给独立裁判判「能不能做这件事」。

★★ 盲判的三条设计（为什么这样才对得上业主的要求）：
  ① ★ **不告诉裁判我期望哪个工具**（★ 否则它只会顺着我标）
  ② ★ **不告诉它哪个是首选/备选**（★ 去掉位置偏倚）
  ③ ★★ **给它候选工具【真实的描述】** —— 裁判要判的是「这个工具真能做那件事吗」，
     而它只能靠读工具自己的说明来判 ⇒ ★ 这也顺带把「描述写得清不清楚」暴露出来 ✓

★ 输出：`output/pick-test/judge-in-XX.json`（每个裁判 5 组）+ `_judge_index.json`（对账用）
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import register_capabilities as rc                                    # noqa: E402

SEED = 20261004
PER_JUDGE = 5
D = ROOT / "output" / "pick-test"
answers = {a["index"]: a for a in json.loads((D / "_answers.json").read_text(encoding="utf-8"))}

#: ★ 工具名 → 真实说明（★ 裁判要看的就是它）
by_name = {s.name: s for s in rc.all_specs()}
#: ★ 上游 server.py 的工具（★ 不在 all_specs 里 ⇒ 说明取不到，要如实标出来）
upstream_known = {"mcp__solidworks__"}          # 前缀而已

def mcp_to_plain(n: str) -> str:
    """★ 子代理报的是 `mcp__solidworks__solidworks_xxx`（★ DSH 的命名是
    `mcp__<server>__<toolName>`，而 toolName 本身已带 `solidworks_` 前缀）
    ⇒ ★★ 要把 `mcp__solidworks__` **整段去掉**，不是换成 `solidworks_`
    （★ 我第一版换成 `solidworks_` ⇒ 得到 `solidworks_solidworks_…` **双前缀** ⇒ 全查不到 ✓）
    2026-10-04 修（★ 由本脚本自己的"不在工具里"统计抓出来的）。"""
    return n.removeprefix("mcp__solidworks__") if n.startswith("mcp__") else n


picks = []
for f in sorted(D.glob("pick-*.json")):
    rows = json.loads(f.read_text(encoding="utf-8"))
    rows = rows if isinstance(rows, list) else [rows]
    for r in rows:
        i = int(r.get("index", -1))
        if i not in answers:
            continue
        cands = []
        for key in ("first_choice", "second_choice"):
            v = (r.get(key) or "").strip()
            if v and v.upper() != "NONE":
                cands.append(mcp_to_plain(v))
        seen, uniq = set(), []
        for c in cands:
            if c not in seen:
                seen.add(c)
                uniq.append(c)
        picks.append({"index": i, "task": answers[i]["task"], "stratum": answers[i]["stratum"],
                      "expected_tool": answers[i]["expected_tool"],
                      "sees": r.get("sees_solidworks_tools"),
                      "visible_sample": r.get("visible_sample") or [],
                      "none": bool(r.get("none_possible")) or not uniq,
                      "candidates": uniq})

print("★ 收到 %d 组挑工具结果" % len(picks))
print("   · ★ 自报看不见清单的: %d" % sum(1 for p in picks if p["sees"] is False))
print("   · ★ 自报清单可见但报的名字**不在本仓工具里**的: %d"
      % sum(1 for p in picks if p["sees"] and p["candidates"]
            and all(c not in by_name for c in p["candidates"])))
print("   · ★ 选了 NONE（认为没有工具能做）的: %d" % sum(1 for p in picks if p["none"]))

rng = random.Random(SEED)
groups = [picks[i:i + PER_JUDGE] for i in range(0, len(picks), PER_JUDGE)]
made = 0
for gi, g in enumerate(groups):
    payload = []
    for p in g:
        #: ★ 给裁判的候选：只给名字 + **真实说明**，★ 不排序提示、不给期望
        items = []
        for c in p["candidates"]:
            s = by_name.get(c)
            items.append({"tool": c,
                          "title": (getattr(s, "title", "") or "") if s else "(上游工具，说明取不到)",
                          "description": (getattr(s, "doc", "") or "")[:500] if s else "(上游工具，说明取不到)"})
        rng.shuffle(items)                                  #: ★ 随机序 ⇒ 去位置偏倚
        payload.append({"index": p["index"], "task": p["task"],
                        "candidates_are_none": p["none"], "candidates": items})
    (D / ("judge-in-%02d.json" % gi)).write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    made += 1
(D / "_judge_index.json").write_text(json.dumps(picks, ensure_ascii=False, indent=1), encoding="utf-8")
print("★ 写出 %d 个裁判输入（每个 %d 组）" % (made, PER_JUDGE))
print("★ 对账表: _judge_index.json")
