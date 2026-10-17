"""★ 第 0 步实测的**组题**：把 Bunny 写的中文查询当作任务文本（★ 不让我再写），
   分层抽一批，写成"让真模型挑工具"的输入文件。

★ 为什么这样组题：
  · 业主的更正：★★ 我之前的指标是「**我标的那个工具在不在 top-k**」——
    标签是我选的 ⇒ ★ 标签错了整个测量就错 ⇒ 现在改成**让独立裁判判"挑出来的能不能做这件事"**
  · ★ 任务文本复用 Bunny 那批**中文用户说法**（独立产出者）⇒ 少一处我自己的偏倚 ✓
  · ★★ 挑工具的是**真模型**（子代理）——它手上就有本仓**真实的工具清单**
    ⇒ 这正是「当前形态下模型挑得准不准」的忠实测法 ✓
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(Path(__file__).resolve().parents[1])
SEED = 20261004
TARGET = 48                      #: ★ 48 个任务 ⇒ 48 条挑工具路（★ 与业主"60 路"同量级）

sample = json.loads((ROOT / "output" / "rag-sample.json").read_text(encoding="utf-8"))
recs, strata = sample["records"], sample["strata"]
stratum_of = {t: k for k, v in strata.items() for t in v}

#: ★ 收集 Bunny 写的中文查询
tasks = []
qdir = ROOT / "output" / "rag-queries"
for f in sorted(qdir.glob("out-*.json")):
    for row in json.loads(f.read_text(encoding="utf-8")):
        t = row["tool"]
        if t in recs and row.get("cn_query"):
            tasks.append({"tool": t, "task_cn": row["cn_query"],
                          "stratum": stratum_of.get(t, "?"),
                          "title": recs[t]["title"], "doc": recs[t]["doc"][:400]})
print("★ 可用任务（有中文查询的）: %d" % len(tasks))

#: ★ 分层抽样：保证冷门/自研层/热门都有
by: dict = {}
for t in tasks:
    by.setdefault(t["stratum"], []).append(t)
rng = random.Random(SEED)
picked = []
for st, pool in by.items():
    pool = sorted(pool, key=lambda x: x["tool"])
    rng.shuffle(pool)
    n = max(6, round(TARGET * len(pool) / len(tasks)))       #: ★ 按层大小配额，每层至少 6
    picked += pool[:n]
picked = picked[:TARGET]
print("★ 抽样 %d 个 · 分层: %s" % (len(picked), {k: sum(1 for p in picked if p["stratum"] == k)
                                                 for k in by}))

OUT = ROOT / "output" / "pick-test"
OUT.mkdir(parents=True, exist_ok=True)
for i, p in enumerate(picked):
    (OUT / ("task-%02d.json" % i)).write_text(json.dumps({
        "index": i,
        "task": p["task_cn"],                 #: ★ 只给任务文本与"我预期的工具"（★ 挑工具路看不到后者）
        #: ★★ 期望工具**不放进挑工具路的输入** —— 只放在答案表里，供事后对账
    }, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "_answers.json").write_text(json.dumps(
    [{"index": i, "task": p["task_cn"], "expected_tool": p["tool"],
      "stratum": p["stratum"], "title": p["title"], "doc": p["doc"]}
     for i, p in enumerate(picked)], ensure_ascii=False, indent=1), encoding="utf-8")
print("★ 写出 %d 个 task-XX.json（★ **不含**期望工具）+ 一份 _answers.json（含，供对账）" % len(picked))
print("★ 目录: %s" % OUT)
