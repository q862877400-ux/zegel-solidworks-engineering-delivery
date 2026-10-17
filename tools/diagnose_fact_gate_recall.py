"""★ T5-1 的 recall 诊断：查那 2 例「真复述」为什么没被报出来。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import check_fact_single_home as G                                  # noqa: E402

bodies = G.fact_bodies()
step = max(1, len(bodies) // 10)
picks = [bodies[i] for i in range(0, min(len(bodies), step * 10), step)][:10]
print("★ 家里正文 %d 条 ⇒ 抽 %d 条诊断" % (len(bodies), len(picks)))
print()

missed = []
for n, b in picks:
    nb = G._norm(b)
    probe = nb[20:20 + G.MIN_LEN] if len(nb) > 20 + G.MIN_LEN else nb[:G.MIN_LEN]
    doc = G._norm("# 别的文档\n\n%s\n" % b)
    ok = len(probe) >= G.MIN_LEN and probe in doc
    if not ok:
        missed.append((n, b, nb, probe, doc))

print("★ 漏报 **%d** 例" % len(missed))
for n, b, nb, probe, doc in missed:
    print()
    print("── 事实 %s ──" % n)
    print("   ★ 正文原样长度 : %d 字符" % len(b))
    print("   ★ 归一后长度   : **%d** 字符（★ 判据要求 probe ≥ %d）" % (len(nb), G.MIN_LEN))
    print("   ★ probe 长度   : **%d**" % len(probe))
    print("   ★ probe 是否在归一后的 doc 里: **%s**" % (probe in doc))
    print("   ★★ 真因: %s"
          % ("★ **归一后正文太短** ⇒ probe 不足 %d 字符 ⇒ 判据直接放过" % G.MIN_LEN
             if len(nb) < 20 + G.MIN_LEN else
             "★ probe 取的是 [20:20+80] ⇒ 该段在原文里**跨行/含被归一掉的字符** ⇒ 对不上"))
    print("   ★ 正文前 90 字: %s" % b[:90].replace("\n", " "))
