"""★ 把分块跑出的若干个 JSON 合并成一份（★ 分块是为了绕开一次未复现的卡顿）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性合并）
# 文件:   tools/merge_chunks.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B3**。★ 起因（真机）：
#   ★★ 全组跑 `nonempty`（135）时**卡了 50 分钟没出来**，★ 而实测速率是 **1.4 秒/条**
#       （★ 全组本应 ~3 分钟）⇒ ★ 说明**某一条卡住**，★ 不是慢 ✓
#   ⇒ ★ 加 `--offset` **分块跑**（★ 每块 ≤ 1 分钟）⇒ ★★ 全组 **187 秒**跑完、
#     ★ **卡顿一次也没复现** ⇒ ★ 如实记为「**一次未能复现的卡顿**」✓
# 判据:   ★ **按 `changed` 合并**（★ 同一条工具在多块里只出现一次，★ 后到的不覆盖先到的）✓
#   ★ 四类计数**重算**（★ 不用各块自报的 —— ★ 那是各块的，★ 合起来要重新数）✓
# 官方依据: 无 —— ★ 我方探针口径
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

#: ★★ 合并后要重算的字段（★ 别信各块自报的计数）✓
RECOUNT = ("conservative", "agree", "missed", "undecided")


def main() -> int:
    ap = argparse.ArgumentParser(description="★ 合并分块结果")
    ap.add_argument("--glob", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    rows: dict = {}
    scanned = []
    for path in sorted(glob.glob(a.glob)):
        try:
            d = json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception:                                               # noqa: BLE001
            continue
        scanned.append(Path(path).name)
        for r in (d.get("rows") or []):
            #: ★ **先到的不被覆盖**（★ 若同一条出现在两块里，★ 说明分块重叠 ⇒ ★ 保留第一次）✓
            rows.setdefault(r.get("tool"), r)

    counts: dict = {}
    for r in rows.values():
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    missed = sorted(n for n, r in rows.items() if r["verdict"] == "missed")
    call_failed = sorted(n for n, r in rows.items() if not r.get("writer_ok"))
    out = {
        "_": "★ B3 存活普查（★ 由分块结果合并 —— ★ 分块是为绕开一次未复现的卡顿）",
        "_merged_from": scanned,
        "_judge": "★ agree=一致 · conservative=声明保守 · ★★ missed=声明漏报（硬红门禁）· undecided=未判定",
        "counts": counts, "missed": missed, "call_failed": call_failed,
        "rows": [rows[k] for k in sorted(rows)],
    }
    p = Path(a.out)
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 合并 %d 份 ⇒ %d 条" % (len(scanned), len(rows)))
    print("★ 四类（★ 重算）：%s" % counts)
    print("★★ 硬红门禁（声明只读却观察到变化）：**%d** 条" % len(missed))
    print("★ 调用没调成：**%d** 条" % len(call_failed))
    print("★ 产物：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
