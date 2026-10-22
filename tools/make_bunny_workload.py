"""★ 生成 bunny 工作量清单：一条一个操作（③强候选 + ②需人工核）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/make_bunny_workload.py
# 定位:   ★ 业主的派活形状：**一个 bunny 只负责一个操作**、每批 ≤60 ⇒ 本脚本产出一份带
#           编号的工作量清单，bunny 按编号读自己那一条 ✓
# ★★ **分母的来路**（★ 重要，别用错数）：`docs/union-coverage-matrix.md` §三 的「238 个
# 独家」
#           是**较早、较窄**的口径；而仓库自己的三档分诊（`output/union-gap-v3.json`，
# `regression_pass: 6/6`）给出的是：**union 349 = ①已有等价物 273 + ②需人工核 19 + ③强候
# 选 57** ✓
# ⇒ ★★★ **分类器自述**假阳性 **273/349 = 78%（不是 59%）** —— ★★ 而**我没逐条核过任何一
# 条**，
#             那是 `best_cov ≥ 0.5` 的**词面覆盖率阈值**判的，只带 7 条回归样本 ✓
#             ⇒ ★ 本脚本按它**只派 ②③ 共 76 条**，是**拿一个未验证的过滤器缩工作量** ——
# ★★ 这一步**已被裁定为错**（业主原话：「238 条一条一个 bunny，**让 bunny 判断是不是假阳
# 性**」）
#             ⇒ **规格 207 就是来把这个数真正测出来的**：见 `specs/207-union-gap-verify/`，
#             取代脚本是 `tools/make_union_workload_349.py`（覆盖全 349、①档只验证）✓
# ★ 每条带上分类器给的 `best_cov` 与 top-3 候选 —— ★ **不是结论**，是给 bunny **去核/推
# 翻**的线索 ✓
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


def main() -> int:
    gap = json.loads((ROOT / "output" / "union-gap-v3.json").read_text(encoding="utf-8"))
    rows = gap.get("rows") or []

    #: ★ 操作名 → (来源库, 许可)。★ 四家都有的取全部（bunny 自己挑最相关的那家读）
    src = json.loads((ROOT / "tools" / "union-sources.json").read_text(encoding="utf-8"))
    owners: dict[str, list[dict]] = {}
    for s in src.get("sources") or []:
        repo = "%s/%s" % (s.get("owner"), s.get("repo")) if s.get("owner") else str(s.get("repo"))
        for t in (s.get("tools") or []):
            nm = str(t.get("name") if isinstance(t, dict) else t)
            owners.setdefault(nm, []).append({"repo": repo, "license": str(s.get("license"))})

    #: ★ 只取 ②③（①「已有等价物」不派 —— 那 273 条要核的话是**另一条更便宜的验证链**）
    work = []
    for r in rows:
        tier = str(r.get("tier") or "")
        if "已有等价物" in tier:
            continue
        op = str(r.get("operation"))
        work.append({
            "index": len(work) + 1,
            "op": op,
            "domain": r.get("domain"),
            "classifier_tier": tier,
            "classifier_best_cov": r.get("best_cov"),
            "classifier_top3": r.get("top"),
            "sources": owners.get(op, []),
        })

    out = ROOT / "output" / "bunny-workload.json"
    out.write_text(json.dumps({"count": len(work), "note": "一个 bunny 一条；②③ 档",
                               "items": work}, ensure_ascii=False, indent=1), encoding="utf-8")

    print("★ union 总数: %s" % gap.get("union_size"))
    print("★ 三档: %s" % json.dumps(gap.get("tiers"), ensure_ascii=False))
    print("★ **本清单（②③）= %d 条**" % len(work))
    print("★ 已写: %s" % out)
    print("\n★ 前 8 条：")
    for w in work[:8]:
        srcs = ",".join(x["repo"].split("/")[-1] for x in w["sources"][:2]) or "（未在四家名单里）"
        print("   #%-3d %-26s %-22s cov=%-6s %s" % (w["index"], w["op"], w["domain"],
                                                    w["classifier_best_cov"], srcs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
