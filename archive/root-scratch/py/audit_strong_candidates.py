"""★ **57 个强候选的逐条核对助手**（2026-10-01 · 轮 313）。

★ 目的：★ 把 `union-gap-v3.json` 的 57 个强候选**逐条**摊开，★ 每条给出：
```
① 在我们的 **183 个工具名**里，有没有**包含该词**的（★ 词级子串，★ 不只是词集交叠）
② 在我们的 **783 个公开函数**里，有没有包含该词的
③ 该词**由哪些四家来源提供**（★ 决定它是不是"只有一家有"⇒ 只能抄它并自己测）
```
⇒ ★★ **然后人工只判"①②都空"的那些** —— ★ 那才是"真缺"的强候选。

★★ 它**不做判断**（★ 事实 191：真缺口不能自动算）—— ★ 它只把**判断所需的材料**摆齐。
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

R = Path(r"C:\swprojects\sw-skill-fork")
W = Path(r"D:\AI\SW")
sys.path[:0] = [str(R), str(R / "mcp-server")]


def main() -> int:
    import ast                                                            # noqa: PLC0415
    import register_capabilities as rc                                    # noqa: PLC0415
    d = json.loads((W / "output" / "union-gap-v3.json").read_text(encoding="utf-8"))
    strong = [x["op"] for x in d["strong"]]
    #: ★ 我们两侧的名字池
    tools = [s.name.replace("solidworks_", "") for s in rc.all_specs()]
    funcs, mods = [], []
    for p in sorted((R / "scripts").glob("sw_*.py")):
        mods.append(p.stem)
        try:
            for n in ast.parse(p.read_text(encoding="utf-8")).body:
                if isinstance(n, ast.FunctionDef) and not n.name.startswith("_"):
                    funcs.append(n.name)
        except Exception:                                                  # noqa: BLE001
            pass
    #: ★ 四家来源（★ 看每个词是谁提供的）
    src = json.loads((R / "tools" / "union-sources.json").read_text(encoding="utf-8"))["sources"]
    by_op = defaultdict(list)
    for s in src:
        for t in (s.get("tools") or []):
            by_op[t].append(s.get("repo", "?").split("/")[0])

    def hits(word, pool):
        w = word.replace("_", "")
        return [x for x in pool if w in x.replace("_", "").lower()]

    rows = []
    for op in strong:
        toks = [t for t in re.split(r"[^A-Za-z0-9]+", op) if len(t) > 2]
        th, fh = [], []
        for t in toks:
            th += hits(t, tools)
            fh += hits(t, funcs)
        rows.append({"op": op, "domain": next((x["domain"] for x in d["strong"] if x["op"] == op), "?"),
                     "tokens": toks, "tool_hits": sorted(set(th))[:5], "func_hits": sorted(set(fh))[:5],
                     "sources": sorted(set(by_op.get(op, []))) or ["（不在各家 tools 里）"]})
    covered = [r for r in rows if r["tool_hits"] or r["func_hits"]]
    naked = [r for r in rows if not r["tool_hits"] and not r["func_hits"]]
    out = {"total": len(rows), "with_any_hit": len(covered), "naked": len(naked),
           "rows": rows,
           "★": "★ 「naked」= 我们两侧都搜不到相关名字 ⇒ ★★ 那才是要人工判「真缺 vs 语义等价」的"}
    (W / "output" / "strong-candidates-audit.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  强候选 %d · 双侧都搜不到相关名字（naked）= **%d** · 有命中 = %d" %
          (len(rows), len(naked), len(covered)))
    print()
    print("  ★★ **naked（要人工判真缺 vs 语义等价）**:")
    for r in naked:
        print("     %-34s [%s] \u6765\u6e90=%s" % (r["op"], r["domain"][:12], ",".join(r["sources"])[:32]))
    print()
    print("  ★ 有命中的（★ 多半已有 —— 列前 14 条供抽查）:")
    for r in covered[:14]:
        print("     %-30s \u5de5\u5177=%s \u51fd\u6570=%s" % (r["op"], ",".join(r["tool_hits"][:2])[:34],
                                                          ",".join(r["func_hits"][:2])[:34]))
    print()
    print("  写出 output/strong-candidates-audit.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
