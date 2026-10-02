"""★ **S0 缺口判定 · v3**（2026-10-01 · 轮 312）。

★ v1 的毛病：★ 从零按词法交叠算 ⇒ **假阳性约 5/6**（它**不知道域**、也**不知道我们已有的工具名**）。
★ v2 的改进与残留：★ 域来自 `union-coverage-matrix.md` §五 ⇒ 判出 **176/239 已有等价物**；
  然而 v2 **只吃 §五 的 239 个名字**（★ §五 只列了一部分），★ 而回归样本里 3 条不在其中。

★★★ **v3 = v2 的域约束 + v1 的 349 全集**：
```
★ **输入**：★ `tools/union-sources.json` 的 `union_operations`（**349** 个 —— ★ 全样本）
★ **域信号**：★ 从 §五 建一张 `缺口名 → 域` 的**映射**（★ 239 条有域；★ 其余按"未分类"）
★ **负样本**：★ 我们已有的 **183** 个工具的 `(name, module, function)` 词集
★ **判据三层**：★ ①cov ≥ 0.5 ⇒ **已有等价物** · ★ ②0 < cov < 0.5 ⇒ **需人工核** · ★ ③cov = 0 ⇒ **强候选**
★ **回归**：★ 7 条已知答案（★ 用**当前**真相）：★ bbox/shell/export_to_step/pack_and_go/run_review
  ⇒ **已有**（★ 5 条假缺口）· ★ measure/measure_distance ⇒ **已有**（★ 我在轮 311 已补上它们）
  ⇒ ★★ **即：7 条**全部**应判"已有"** —— ★ 而 v1 会把其中 6 条误判为缺。
```

★ 用法：`python D:\\AI\\SW\\compute_union_gap_v3.py` ⇒ 写 `output/union-gap-v3.json`，并跑 **7 条回归**。
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

R = Path(r"C:\swprojects\sw-skill-fork")
W = Path(r"D:\AI\SW")
sys.path[:0] = [str(R), str(R / "mcp-server")]

SYN = [
    {"get", "read", "list", "query", "info", "show", "fetch", "collect", "summary", "evidence", "report"},
    {"create", "add", "make", "new", "insert", "generate", "build", "apply", "set"},
    {"delete", "remove", "erase", "clear", "destroy", "suppress"},
    {"set", "update", "modify", "change", "edit", "configure", "activate"},
    {"check", "verify", "validate", "inspect", "analyze", "analyse", "audit", "review", "diagnose"},
    {"export", "save", "write", "output", "deliver", "download"},
    {"import", "load", "open", "read"},
    {"count", "number", "size", "length", "quantity"},
    {"box", "bbox", "bounding", "extent", "bounds"},
    {"shell", "thicken", "hollow", "offset"},
    {"mate", "mates", "constraint", "constraints"},
    {"distance", "length", "measure", "dimension", "gap"},
    {"area", "surface", "face"},
    {"close", "quit", "exit", "end"},
    {"macro", "vba", "script", "automation", "batch", "execute"},
    {"hole", "holes"}, {"feature", "features"}, {"component", "components"},
    {"view", "views"}, {"sheet", "sheets"}, {"sketch", "sketches"}, {"body", "bodies"},
    {"dimension", "dimensions"}, {"property", "properties", "custom"},
    {"study", "studies"}, {"config", "configuration", "configurations"},
    {"assembly", "assemblies"}, {"drawing", "drawings"}, {"part", "parts"},
    {"material", "materials"}, {"select", "selection", "pick", "selector"},
    {"move", "translate", "shift"}, {"hide", "show", "visible", "visibility"},
    {"name", "names", "title"}, {"note", "notes", "annotation", "annotations"},
    {"table", "tables"}, {"bom", "bill"}, {"evidence", "readback"},
    {"pattern", "mirror"}, {"plane", "planes", "axis", "axes", "point", "points"},
    {"spline", "arc", "circle", "line", "ellipse", "polygon"},
    {"thickness", "radius", "diameter", "angle"},
]
STOP = {"sw", "solidworks", "mcp", "tool", "the", "a", "an", "of", "to", "and", "by",
        "with", "at", "in", "on", "for", "all", "document", "doc", "model", "part", "s"}

#: ★ 回归：★ **用"当前真相"** —— ★★ 而**名字必须取自 `union-sources.json` 的并集**（★ 不是我记忆里的常见名）：
#: ★ 2026-10-01（轮 312）踩过这一处：★ 我原先写 `export_to_step` / `pack_and_go` / `run_review`，
#:   而并集里的真名是 **`export_step`** / **`pack_and_go_assembly`**，★ **`review` 压根不在并集里**
#:   ⇒ ★★ 三条 `tier=None` 的"FAIL"**全是样本错**，不是判据错。
KNOWN = {"bbox": False, "shell": False, "export_step": False, "pack_and_go_assembly": False,
         "measure": False, "measure_distance": False}


def _words(name: str) -> set:
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", str(name or ""))
    parts = [p.lower() for p in re.split(r"[^A-Za-z0-9]+", s) if p]
    return {p for p in parts if p not in STOP and len(p) > 1}


def _expand(words: set) -> set:
    out = set(words)
    for w in words:
        for grp in SYN:
            if w in grp:
                out |= grp
    return out


def parse_gap_domain_map() -> dict:
    """★ `缺口名 → 域` 映射（★ 从 §五 建；★ 不在表里的记为「未分类」）。"""
    t = (R / "docs" / "union-coverage-matrix.md").read_text(encoding="utf-8").splitlines()
    _s = next((k for k, l in enumerate(t) if l.startswith("## 五")), 0)
    _e = next((k for k, l in enumerate(t[_s + 1:], start=_s + 1) if l.startswith("## ")), len(t))
    m, cur = {}, None
    for l in t[_s:_e]:
        if l.startswith("### ") and "（缺" in l:
            mm = re.search(r"###\s*(\S+)\s*(.*?)（缺\s*(\d+)）", l)
            cur = (mm.group(2) or "").strip() if mm else l[4:].strip()
        elif cur and "缺口操作：" in l:
            for nm in re.findall(r"`([^`]+)`", l.split("：", 1)[-1]):
                m[nm] = cur
    return m


def main() -> int:
    import register_capabilities as rc                                      # noqa: E402
    ours = [{"tool": s.name,
             "words": _expand(_words(s.name.replace("solidworks_", "")) | _words(s.function))}
            for s in rc.all_specs()]
    dom_of = parse_gap_domain_map()
    ops = json.loads((R / "tools" / "union-sources.json").read_text(encoding="utf-8"))["union_operations"]
    rows = []
    for op in ops:
        ow = _expand(_words(op))
        best, hit = 0.0, []
        for o in ours:
            inter = ow & o["words"]
            if not inter:
                continue
            cov = len(inter) / max(1, len(ow))
            if cov > best:
                best = cov
            hit.append((round(cov, 3), o["tool"]))
        hit.sort(key=lambda x: (-x[0], x[1]))
        tier = "①已有等价物" if best >= 0.5 else ("②需人工核" if best > 0.0 else "③强候选")
        rows.append({"operation": op, "domain": dom_of.get(op, "未分类"), "best_cov": round(best, 3),
                     "tier": tier, "top": [h[1] for h in hit[:3]]})
    c = Counter(r["tier"] for r in rows)
    reg = {}
    for nm, is_gap in KNOWN.items():
        r = next((x for x in rows if x["operation"] == nm), None)
        if r is None:
            reg[nm] = {"found": False, "ok": False}
            continue
        got_gap = (r["tier"] != "①已有等价物")
        reg[nm] = {"expected_gap": is_gap, "got_gap": got_gap, "tier": r["tier"],
                   "cov": r["best_cov"], "ok": (got_gap == is_gap)}
    ok_n = sum(1 for v in reg.values() if v.get("ok"))
    strong = [r for r in rows if r["tier"] == "③强候选"]
    by_dom = Counter(r["domain"] for r in strong)
    out = {"union_size": len(ops), "ours": len(ours), "tiers": dict(c),
           "regression_pass": "%d/%d" % (ok_n, len(KNOWN)), "regression": reg,
           "strong_count": len(strong), "strong_by_domain": dict(by_dom),
           "strong": [{"op": r["operation"], "domain": r["domain"]} for r in strong],
           "rows": rows,
           "★": "v3：349 全集 × 域映射(§五) × 183 个已有工具当负样本 · 三层判据 · 7 条回归"}
    (W / "output" / "union-gap-v3.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  输入: 四家并集 %d · 我们 %d" % (len(ops), len(ours)))
    print("  三层: %s" % dict(c))
    print()
    print("  ★★ 回归 **%s**（★ 判据：7 条已知答案全应判「已有」）" % out["regression_pass"])
    for nm, v in reg.items():
        print("     %-18s tier=%-12s cov=%.2f  %s" % (nm, v.get("tier"), v.get("cov", 0),
                                                       "OK" if v.get("ok") else "**FAIL**"))
    print()
    print("  ③强候选 **%d** 个，按域：" % len(strong))
    for d, n in by_dom.most_common():
        print("     %-22s %d" % (d, n))
    return 0 if ok_n == len(KNOWN) else 1


if __name__ == "__main__":
    raise SystemExit(main())
