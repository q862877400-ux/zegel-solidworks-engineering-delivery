"""★ 合并三裁判的发现（★ 同一条缺陷被多路报出 ⇒ 置信度更高）。"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = Path(Path(__file__).resolve().parents[1] / "output" / "t0-judge")
rows = []
for f in sorted(D.glob("judge-out-*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    for x in d.get("findings") or []:
        x["_judge"] = d.get("judge_index")
        rows.append(x)
print("★ 三裁判共报 %d 条发现" % len(rows))
print()
by = defaultdict(list)
for r in rows:
    by[r.get("claim_id", "?")].append(r)
for cid in sorted(by):
    rs = by[cid]
    sev = sorted({r.get("severity", "?") for r in rs})
    judges = sorted({r.get("_judge") for r in rs})
    kinds = sorted({r.get("kind", "?") for r in rs})
    print("★ %s（%d 路报出 · 严重度 %s · 类 %s）" % (cid, len(rs), "/".join(sev), "/".join(kinds)))
    for r in rs:
        print("     [J%s %s] %s" % (r.get("_judge"), r.get("severity"),
                                    (r.get("why") or "").strip()))
        if r.get("fix"):
            print("        修法: %s" % r["fix"].strip())
    print()
print("★ 各路 overall:")
for f in sorted(D.glob("judge-out-*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    print("   J%s: %s" % (d.get("judge_index"), (d.get("overall") or "").strip()))
    if d.get("clean_claims"):
        print("       判为干净的: %s" % ", ".join(d["clean_claims"]))
