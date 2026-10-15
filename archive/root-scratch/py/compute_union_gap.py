"""★ **算「四家有我们没有」的功能级缺口**（2026-10-01 · 轮 311）。

★ 用户目标：★ **下一批先补"别人有我们没有"的** ⇒ 终局 = **四家都没有我们齐全**。

★★ **为什么不能按名字算**（硬约束④「核功能不核名字」）—— 已实测的假缺口：
```
★ `export_to_step`   —— 我们**已有** `solidworks_export_step`（名字只差前缀）
★ `shell`            —— 我们**已有** `solidworks_part_shell`
★ `run_review`       —— 我们**已有** `solidworks_build_review_report`
★ `pack_and_go`      —— 我们**已有** `solidworks_pack_and_go_tool`
★ `create_external_spur_gear` —— 我们**已有** `solidworks_gear_create_spur`
⇒ ★★ **凭名字判，这 5 条都会被算成"缺"** —— ★ 而它们一个都不缺。
```

★ 本脚本做**词法级**匹配（★ 动作词 + 对象词 + 同义词表），★ 产出**待人工确认的强候选**
  —— ★★ **它给的是"嫌疑名单"，不是判据**（★ 事实 191：★ "真缺口"做不到自动算）。
★ 判据分层：★ **交叠度 0 ⇒ 强候选**（★ 我们要看）；★ **交叠度 ≥2 ⇒ 大概率已覆盖**（★ 抽样核对即可）。

★ 用法：`python D:\\AI\\SW\\compute_union_gap.py` ⇒ 写 `output/union-gap.json` 并打印分域统计。
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

R = Path(r"C:\swprojects\sw-skill-fork")
sys.path[:0] = [str(R), str(R / "mcp-server")]

#: ★ 同义词表（★ 小而准 —— ★ 只收**我们两边都实际出现**的词对）
SYN = [
    {"get", "read", "list", "query", "info", "show", "fetch"},
    {"create", "add", "make", "new", "insert", "generate", "build"},
    {"delete", "remove", "erase", "clear", "destroy"},
    {"set", "update", "modify", "change", "edit", "configure"},
    {"check", "verify", "validate", "inspect", "analyze", "analyse", "audit"},
    {"hole", "holes"}, {"surface", "surfaces"}, {"feature", "features"},
    {"component", "components"}, {"mate", "mates"}, {"view", "views"},
    {"sheet", "sheets"}, {"sketch", "sketches"}, {"body", "bodies"},
    {"dimension", "dimensions"}, {"property", "properties"}, {"study", "studies"},
    {"export", "save", "write", "output"}, {"import", "load", "open"},
    {"count", "number", "size", "length"}, {"name", "names", "title"},
    {"material", "materials"}, {"config", "configuration", "configurations"},
    {"assembly", "assemblies"}, {"drawing", "drawings"}, {"part", "parts"},
    {"select", "selection", "pick"}, {"move", "translate", "shift"},
    {"rotate", "spin", "turn"}, {"hide", "show", "visible", "visibility"},
]


def _words(name: str) -> set:
    """★ 把动作名拆成词集（★ 去分隔符 + 拆驼峰 + 去停用词）。"""
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", str(name or ""))
    parts = [p.lower() for p in re.split(r"[^A-Za-z0-9]+", s) if p]
    stop = {"sw", "solidworks", "mcp", "tool", "the", "a", "of", "to", "and", "by", "with", "at", "in", "on", "for"}
    return {p for p in parts if p not in stop and len(p) > 1}


def _expand(words: set) -> set:
    """★ 按同义词表扩张（★ 让 `get` 与 `read` 视为同一族）。"""
    out = set(words)
    for w in words:
        for group in SYN:
            if w in group:
                out |= group
    return out


def main() -> int:
    d = json.loads((R / "tools" / "union-sources.json").read_text(encoding="utf-8"))
    union = list(d.get("union_operations") or [])
    import register_capabilities as rc                                    # noqa: E402
    ours = []
    for s in rc.all_specs():
        ours.append({"tool": s.name, "module": s.module, "function": s.function,
                     "words": _expand(_words(s.name.replace("solidworks_", "")) | _words(s.function))})
    #: ★ 逐条算交叠度（★ Jaccard 的变体：★ 用"四家词的命中比例"—— ★ 因为四家名短、我们的长）
    rows = []
    for op in union:
        ow = _expand(_words(op))
        best = []
        for o in ours:
            inter = ow & o["words"]
            if not inter:
                continue
            #: ★ 命中比例：★ 四家那侧被覆盖了多少（★ 那才是"功能对上"的意思）
            cov = len(inter) / max(1, len(ow))
            best.append((round(cov, 3), len(inter), o["tool"]))
        best.sort(key=lambda x: (-x[0], -x[1]))
        rows.append({"operation": op, "words": sorted(ow),
                     "top": best[:3], "best_cov": (best[0][0] if best else 0.0)})
    strong = [r for r in rows if r["best_cov"] == 0.0]
    weak = [r for r in rows if 0.0 < r["best_cov"] < 0.67]
    likely = [r for r in rows if r["best_cov"] >= 0.67]
    out = {"union_size": len(union), "ours": len(ours),
           "strong_gap_count": len(strong), "weak_count": len(weak), "likely_covered": len(likely),
           "strong_gap": [r["operation"] for r in strong],
           "weak": [{"op": r["operation"], "best_cov": r["best_cov"],
                     "top": [t[2] for t in r["top"]]} for r in weak],
           "★": "★ 交叠度 0 = 强候选（要看）· ≥0.67 = 大概率已覆盖 · 中间 = 人工抽查（★ 事实 191：真缺口不能自动算）"}
    p = Path(r"D:\AI\SW\output\union-gap.json")
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  四家并集 %d · 我们工具 %d" % (len(union), len(ours)))
    print("  ★ 交叠度 0（强候选）  %d" % len(strong))
    print("  ★ 0 < 交叠度 < 0.67   %d" % len(weak))
    print("  ★ 交叠度 >= 0.67（大概率已覆盖）%d" % len(likely))
    print()
    print("  ★★ 强候选（前 40 个）:")
    for r in strong[:40]:
        print("     %s" % r["operation"])
    print()
    print("  ★ 中间档样例（前 12，★ 带我们的最近工具）:")
    for r in weak[:12]:
        print("     %-34s cov=%.2f  \u2192 %s" % (r["operation"], r["best_cov"], ", ".join(r["top"][:2])[:52]))
    print()
    print("  写出 %s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
