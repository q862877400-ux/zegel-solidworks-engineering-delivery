"""★ T1-5b：量**联合**（十个别名同时装）下的逐工具增益 —— ★ 平均值不足以决定去留。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
sys.path.insert(0, str(ROOT / "tools"))
import t1_remeasure_sc1 as M                                          # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    n_b, d_b = M.build(strip_alias=True)
    n_a, d_a = M.build(strip_alias=False)
    bm_b, bm_a = M.BM25(n_b, d_b), M.BM25(n_a, d_a)

    cand = json.loads((ROOT / "output" / "t1-alias-candidates.json").read_text(encoding="utf-8"))
    final = json.loads((ROOT / "output" / "t1-alias-final.json").read_text(encoding="utf-8"))
    adopted = {x["tool"] for x in final["same"]}
    alias_of: dict = {}
    for k in cand["kept"]:
        if k["tool"] in adopted:
            a = alias_of.setdefault(k["tool"], {"ops": set(), "keys": set()})
            a["ops"].add(k["op"])
            a["keys"] |= set(k["keys"])

    rows = []
    for tool, a in sorted(alias_of.items()):
        q = " ".join(sorted(a["ops"])) + " " + " ".join(sorted(a["keys"]))
        r0, r1 = bm_b.rank(q, tool), bm_a.rank(q, tool)
        rows.append({"tool": tool, "q": q.strip(), "rank_stripped": r0, "rank_joint": r1,
                     "delta": ((r0 - r1) if (r0 and r1) else None)})
    imp = [r for r in rows if r["delta"] and r["delta"] > 0]
    same = [r for r in rows if r["delta"] == 0]
    worse = [r for r in rows if r["delta"] is not None and r["delta"] < 0]
    print("★ 联合（十个别名同时装）下逐工具排名变化 · n=%d" % len(rows))
    print("   · 提升: **%d** · 不变: %d · 变差: %d" % (len(imp), len(same), len(worse)))
    print()
    for r in rows:
        print("   %-40s %s → %s" % (r["tool"].removeprefix("solidworks_"),
                                    r["rank_stripped"], r["rank_joint"]))
    print()
    if len(imp) <= 2:
        print("★★ 判定：联合增益≈0（提升 ≤2 个）⇒ ★ **按 D-2 自己的判据（别名必须挣到字节）应【回退】** ✓")
    else:
        print("★ 判定：仍有 %d 个提升 ⇒ 可保留这 %d 个的别名、回退其余" % (len(imp), len(imp)))
    (ROOT / "output" / "t1-joint-gain.json").write_text(
        json.dumps({"rows": rows, "n_improved": len(imp), "n_same": len(same),
                    "n_worse": len(worse)}, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
