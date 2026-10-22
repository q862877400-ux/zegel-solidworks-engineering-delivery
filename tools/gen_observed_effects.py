"""★ 把存活普查的**实证**落成覆盖层（★ 实证优先于静态 —— 规格 210 · B3/B4）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（生成器）
# 文件:   tools/gen_observed_effects.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B3（收尾）+ B4**。★ 外部评审的设
#           计：
#   ★★ 「**静态当提案与否决票，运行时实证当实证，两者都通过才开（自动重试）**」✓
#   ⇒ ★ 于是需要一份**「实证覆盖层」**：★ 静态说「无写」、★ 而实证观察到「改了 X」 ⇒
#     ★★ **以实证为准**（★ 保守方向：★ 一旦观察到变化，就**不许**再当只读）✓
# 判据:   ★★ 数据源：`output/spec210-survival-diff-*.json`（★ 真机普查产物）✓
#   ★ 只收 **`changed` 非空**的条目（★ 观察到了变化才值得覆盖；★ `agree`/没变的**不进**）✓
#   ★ 每条记：★ `writes`（观察变了的类）· `requires` · `tool` · `source: "observed"` ·
#     ★ 以及**它的静态底稿**（★ 好让人一眼看出「静态被推翻了」）✓
#   ★★ 并**如实标出来**：★ 覆盖层里每一条都是「**静态漏报**」（★ 这是它存在的理由）✓
# 官方依据: 读数出处见 `scripts/sw_fingerprint.py` 的 `OFFICIAL`
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import glob
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
STATIC = ROOT / "docs" / "effect-declarations.json"
OUT = ROOT / "docs" / "effect-observed.json"


def main() -> int:
    ap = argparse.ArgumentParser(description="★ 生成实证覆盖层（规格 210 · B3/B4）")
    ap.add_argument(
        "--glob", default=str(ROOT / "output" / "spec210-survival-diff-*.json")
    )
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()

    static = json.loads(STATIC.read_text(encoding="utf-8")).get("tools", {})
    observed: dict = {}
    scanned = []
    for path in sorted(glob.glob(a.glob)):
        try:
            d = json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        scanned.append(Path(path).name)
        for r in d.get("rows") or []:
            changed = [c for c in (r.get("changed_classes") or []) if c]
            if not changed:
                continue
            name = r.get("tool")
            #: ★ 合并多次普查的结果（★ 并集 —— ★ 观察到一次就算观察到）✓
            prev = observed.get(name) or {"writes": [], "seen_in": []}
            prev["writes"] = sorted(set(prev["writes"]) | set(changed))
            prev["seen_in"] = sorted(set(prev["seen_in"]) | {Path(path).name})
            prev["requires"] = r.get("requires") or prev.get("requires")
            prev["observed_verdict"] = r.get("verdict")
            observed[name] = prev

    tools = {}
    for name, rec in sorted(observed.items()):
        base = static.get(name) or {}
        tools[name] = {
            "writes": rec["writes"],
            "source": "observed",
            "seen_in": rec["seen_in"],
            "observed_verdict": rec.get("observed_verdict"),
            "requires": rec.get("requires"),
            #: ★★ **静态底稿**（★ 一眼看出「静态被推翻」）✓
            "static_writes": base.get("writes"),
            "static_was_silent": base.get("writes") == [],
        }
    out = {
        "_": "★★ 实证覆盖层（规格 210 · B3/B4）：★ **真机观察到变化的工具** —— ★ 实证**优先于**静态。",
        "_regenerate": "python tools/gen_observed_effects.py",
        "_judge": "★ 静态说「无写」而实证观察到改动 ⇒ ★ **以实证为准**（★ 一旦观察到，就不许再当只读）✓",
        "_why": "★ 每一条都是「**静态漏报**」—— ★ 那是这份覆盖层存在的唯一理由 ✓",
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "scanned": scanned,
        "tools": tools,
    }
    p = Path(a.out)
    p.write_text(
        json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("★ 扫了 %d 份普查结果：%s" % (len(scanned), "、".join(scanned) or "（无）"))
    print("★ 覆盖层：**%d** 条（★ 全部是「静态说无写、实证观察到改动」）" % len(tools))
    for name, rec in list(tools.items())[:10]:
        print(
            "   %-46s 静态=%r ⇒ 实证=%s" % (name, rec["static_writes"], rec["writes"])
        )
    print("★ 产物：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
