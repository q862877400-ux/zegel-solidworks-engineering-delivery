"""★ 规格 207 · V7-2：假阳性率报告 —— **分类器自述**与**逐条实测**必须并列（SC-2 / SC-4）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/report_false_positive_rate.py
# 定位:   ★ 规格 207 的 SC-2（①档 273 条逐条验证，产出**真实**假阳性率）与
#           SC-4（★★ **两个数必须并列报**：分类器自述 vs 逐条实测；只报一个即不达标）✓
#         ★★★ **为什么设 SC-4**：我在规格 206 的支线里把 `output/union-gap-v3.json` 的
#           **分类器自述**当成"实测结果"引用，写下「假阳性率**实测**是 78%」—— **一条都没核过** ✓✗
#           ⇒ 本工具的存在就是为了让"引用"与"测量"**不可能被混为一谈**（同一行给出两者与差值）✓
#         ★★ 口径（★ 两个数**分母不同，不许相减成"误差"就完事**）：
#           · 分类器自述 = **它给整个 union 打了多少「①已有等价物」的标** → 273 / 349
#           · 逐条实测   = **在①档那 273 条里，标错了几条** → 其实没有 / 已判定条数
#           ⇒ ★ 报告里把**两个口径各写一行**，再给"标错率"，**不把两个百分比相减** ✓
# 官方依据: 不适用（本仓工序）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WORKLOAD = ROOT / "output" / "union-workload-349.json"
RECORDS = ROOT / "output" / "bunny-records-verify"


def main() -> int:
    wl = json.loads(WORKLOAD.read_text(encoding="utf-8"))
    items = {int(x["index"]): x for x in wl["items"]}
    tier1 = [i for i, x in items.items() if x["task"] == "verify"]

    recs: dict[int, dict] = {}
    bad: list[str] = []
    for f in sorted(RECORDS.glob("*.json")):
        try:
            r = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            recs[int(r["index"])] = r
        except Exception as exc:                                    # noqa: BLE001
            bad.append("%s（%s）" % (f.name, type(exc).__name__))

    have = sum(1 for i in tier1 if recs.get(i, {}).get("verdict") == "已有等价物")
    missing = sum(1 for i in tier1 if recs.get(i, {}).get("verdict") == "其实没有")
    unknown = sum(1 for i in tier1 if recs.get(i, {}).get("verdict") == "查不到")
    done = have + missing + unknown
    pending = len(tier1) - done
    decided = have + missing

    print("=" * 74)
    print("★ 规格 207 · 假阳性率报告（SC-2 / SC-4）")
    print("=" * 74)
    print()
    print("【口径一】分类器**自述**（不是实测）：")
    print("   它把整个 union 的 **%d / %d = %.1f%%** 打成「①已有等价物」"
          % (len(tier1), len(items), 100.0 * len(tier1) / len(items)))
    print("   ★ 这个数的来源是 `output/union-gap-v3.json` 的 `best_cov >= 0.5` 词面覆盖率阈值，")
    print("     只带 7 条回归样本 —— ★ **我没有核过任何一条**（规格 206 支线的错，见 spec.md §一）")
    print()
    print("【口径二】逐条**实测**（bunny 一条一读，证据落 output/bunny-records-verify/）：")
    print("   已判定 **%d / %d** 条（未完成 %d 条）" % (done, len(tier1), pending))
    print("     · 确认「已有等价物」  %3d" % have)
    print("     · 实际「其实没有」    %3d   ← ★ 这些是**分类器标错**的" % missing)
    print("     · 「查不到」          %3d" % unknown)
    if decided:
        print("   ⇒ ★★ **分类器「已有」这一标的错判率 = %d / %d = %.1f%%**（分母 = 已判定的条数）"
              % (missing, decided, 100.0 * missing / decided))
        print("      而**在同一批里**它标「已有」的命中率 = %d / %d = %.1f%%"
              % (have, decided, 100.0 * have / decided))
    print()
    print("★★ 两个百分比的分母**不是同一件事** ⇒ 不许相减当成「误差」：")
    print("   口径一算的是「它给多少条打了这个标」；口径二算的是「这个标错了几条」。")
    if pending:
        print()
        print("⚠⚠ **本报告是部分值**（还有 %d 条未完成）⇒ ★ **现在不得当结论引用**；"
              % pending)
        print("   等 6 片全齐后重跑，届时才写进事实与总结。")
    if bad:
        print()
        print("★ 解析失败的记录 %d 份：%s" % (len(bad), bad[:5]))

    #: ★ 分类器错法分布（方向）—— 单向乐观还是双向？
    dirs = Counter(recs[i].get("classifier_was_right", "（空）") for i in tier1 if i in recs)
    print()
    print("【分类器错法分布（方向）】")
    for k, v in dirs.most_common():
        print("   %-24s %3d" % (k, v))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
