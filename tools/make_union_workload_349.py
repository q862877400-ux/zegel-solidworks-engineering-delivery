"""★ 编全 349 条的工作量清单（tier-aware）：①档只验证，②③档深调。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/make_union_workload_349.py
# 定位:   ★ 规格 207 的 V0-2：把 `output/union-gap-v3.json` 的 **349 条全集**编成带编号的清单，
#           每条带 `task`（①档 = `verify` 只判「是不是已有等价物」；②③档 = `deep` 学透 + 起草）✓
#         ★★ **取代** `tools/make_bunny_workload.py` —— 那个按**未验证的 cov 阈值**砍成 76 条，
#           方向与业主指令相反（原话：「**让 bunny 判断是不是假阳性**」）✓
# 官方依据: 不适用（本仓台账）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: ★ 分类器的三档 → 本轮的任务类型。★ **只有 ① 档变成本轮的「验证」对象**（spec.md D-2）
VERIFY_TIER = "①已有等价物"


def main() -> int:
    gap = json.loads((ROOT / "output" / "union-gap-v3.json").read_text(encoding="utf-8"))
    rows = gap.get("rows") or []
    if len(rows) != 349:
        print("★ rows 不是 349（实为 %d）⇒ 先看一眼再改" % len(rows))
        return 1

    #: 操作名 → 来源（四家）与许可。★ 多家的都列出，bunny 自己挑最相关的读
    src = json.loads((ROOT / "tools" / "union-sources.json").read_text(encoding="utf-8"))
    owners: dict[str, list[dict]] = {}
    for s in src.get("sources") or []:
        repo = "%s/%s" % (s.get("owner"), s.get("repo")) if s.get("owner") else str(s.get("repo"))
        for t in (s.get("tools") or []):
            nm = str(t.get("name") if isinstance(t, dict) else t)
            owners.setdefault(nm, []).append({"repo": repo, "license": str(s.get("license"))})

    items = []
    for i, r in enumerate(rows, 1):
        tier = str(r.get("tier") or "")
        op = str(r.get("operation"))
        items.append({
            "index": i,
            "op": op,
            "domain": r.get("domain"),
            "task": "verify" if tier == VERIFY_TIER else "deep",
            "classifier_tier": tier,
            "classifier_best_cov": r.get("best_cov"),
            "classifier_top3": r.get("top"),
            "sources": owners.get(op, []),
        })

    out = ROOT / "output" / "union-workload-349.json"
    out.write_text(json.dumps({"count": len(items),
                               "note": "一个 bunny 一条；①档 task=verify，②③档 task=deep",
                               "items": items}, ensure_ascii=False, indent=1), encoding="utf-8")

    #: ★ V0-3 自检：条数 + **op 集合与 v3 完全一致**（SC-1 的前半）
    a = [x["op"] for x in items]
    b = [str(r.get("operation")) for r in rows]
    ok_count = len(items) == 349
    ok_set = sorted(a) == sorted(b)
    n_verify = sum(1 for x in items if x["task"] == "verify")
    n_deep = sum(1 for x in items if x["task"] == "deep")
    print("★ 条数 == 349 ? %s（实为 %d）" % (ok_count, len(items)))
    print("★ op 集合与 union-gap-v3 完全一致 ? %s" % ok_set)
    print("★ 任务分布：verify（①档）= **%d** · deep（②③档）= **%d**" % (n_verify, n_deep))
    print("★ 批次：每批 ≤60 ⇒ **%d 批**" % ((len(items) + 59) // 60))
    print("★ 已写：%s" % out)
    return 0 if (ok_count and ok_set) else 2


if __name__ == "__main__":
    raise SystemExit(main())
