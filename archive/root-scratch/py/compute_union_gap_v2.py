"""★ **S0 缺口判定 · v2**（2026-10-01 · 轮 312）。

★★ **v1 的毛病**：★ 从零按词法交叠算 ⇒ **假阳性率约 5/6**（核 6 条有 5 条是假缺口）。根因是
  它**不知道域**、也**不知道我们已有的工具名**，于是把 `shell` / `bbox` / `export_to_step`
  这类"我们早就有了、只是名字不同"的，全算成缺。

★★★ **v2 改用仓库里**已有**的权威输入**（★ 不重新发明 —— ★ 事实 235 的"先看已有门禁"）：
```
★ `docs/union-coverage-matrix.md` §二 的「域 × 来源」表 —— ★ **已经分好 16 个域**，
  并自带三条警告：★「只看缺口列会把已有的域记成零」· ★「判断该实现哪个域看**能力面**列；
  判断该暴露哪个工具才看 **MCP** 列」· ★「`⚠` = 缺口>0 而我们已有 ≥5 个函数 ⇒ **多半不是能力缺口，
  只是没暴露**」。
★ §五 的「可执行的并入清单」—— ★ **逐域名列了缺口名**（★ 所以每个缺口名**自带域**）。
```

★ **v2 的判据（三层，逐层放宽 —— ★ 每一层都记下来，便于人工核）**：
```
① **精确/近义命中**：★ 缺口名 与 我们某个工具的 `(module, function, name)` **同域** 且 词集交叠
   ⇒ ★ "**已有等价物**"（★ 排除出缺口）
② **同域已有 ≥N 个函数**（★ 用 §二 的 `⚠` 逻辑）⇒ ★ "**多半只是没暴露**"（★ 标记，不直接排除）
③ ★ 其余 ⇒ ★ "**强候选**"（★ 要人工看）
★ ★ **负样本回归**：★ 已知 5 假 1 真（v1 的答案）⇒ ★ v2 **必须**把 5 条判成"已有"、把 measure 判成缺。
```

★ 用法：`python D:\\AI\\SW\\compute_union_gap_v2.py` ⇒ 写 `output/union-gap-v2.json`，并**跑回归**。
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

R = Path(r"C:\swprojects\sw-skill-fork")
W = Path(r"D:\AI\SW")
sys.path[:0] = [str(R), str(R / "mcp-server")]

#: ★ 同义词表（★ v1 的表，保留并扩了几组）
SYN = [
    {"get", "read", "list", "query", "info", "show", "fetch", "collect", "summary", "evidence"},
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
    {"macro", "vba", "script", "automation", "batch"},
    {"hole", "holes"}, {"feature", "features"}, {"component", "components"},
    {"view", "views"}, {"sheet", "sheets"}, {"sketch", "sketches"}, {"body", "bodies"},
    {"dimension", "dimensions"}, {"property", "properties"}, {"study", "studies"},
    {"config", "configuration", "configurations"}, {"assembly", "assemblies"},
    {"drawing", "drawings"}, {"part", "parts"}, {"material", "materials"},
    {"select", "selection", "pick"}, {"move", "translate", "shift"},
    {"hide", "show", "visible", "visibility"}, {"name", "names", "title"},
]
STOP = {"sw", "solidworks", "mcp", "tool", "the", "a", "an", "of", "to", "and", "by",
        "with", "at", "in", "on", "for", "all", "document", "doc", "model", "part"}

#: ★ 已知答案（★ v1 核过的 6 条）—— ★ 回归用
KNOWN = {"bbox": False, "shell": False, "export_to_step": False, "pack_and_go": False,
         "run_review": False, "measure": True, "measure_distance": True}


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


def parse_gap_domains() -> dict:
    """★ 从 `union-coverage-matrix.md` §五 **按域**取缺口名（★ 每个名字自带域，★ 那就是 v2 的域信号）。"""
    t = (R / "docs" / "union-coverage-matrix.md").read_text(encoding="utf-8").splitlines()
    #: ★★★ 2026-10-01（轮 312）**必须先定位 `## 五` 的起点** —— 旧写法的坑：
    #:   L60 有一个 `### 缺口按域排序（大 → 小）`（★ **也含「缺」字**）⇒ 它把 `cur` 设成了
    #:   一个**没有缺口的节** ⇒ 碰到 L97 的 `## 三、` 就 `break` ⇒ ★★ **§五 根本没被扫到**
    #:   （★ 第一次跑出"解析出 0 个域"就是这么来的）。
    _start = next((k for k, l in enumerate(t) if l.startswith("## 五")), 0)
    _end = next((k for k, l in enumerate(t[_start + 1:], start=_start + 1) if l.startswith("## ")), len(t))
    dom, cur = {}, None
    for i, l in enumerate(t[_start:_end], start=_start):
        if l.startswith("### ") and "（缺" in l:
            m = re.search(r"###\s*(\S+)\s*(.*?)（缺\s*(\d+)）", l)
            cur = (m.group(1) + " " + m.group(2)).strip() if m else l[4:].strip()
            dom[cur] = []
        elif cur and l.strip() and not l.startswith("|") and not l.startswith("#"):
            if "缺口操作：" in l or "缺口：" in l:
                seg = l.split("：", 1)[-1]
                for nm in re.findall(r"`([^`]+)`", seg):
                    dom[cur].append(nm)
            elif l.strip().startswith("- `"):
                for nm in re.findall(r"`([^`]+)`", l):
                    dom[cur].append(nm)
    return {k: v for k, v in dom.items() if v}


def main() -> int:
    import register_capabilities as rc                                     # noqa: E402
    specs = list(rc.all_specs())
    ours = []
    for s in specs:
        ours.append({"tool": s.name, "module": s.module, "function": s.function,
                     "words": _expand(_words(s.name.replace("solidworks_", "")) | _words(s.function)),
                     "raw": _words(s.name.replace("solidworks_", "")) | _words(s.function)})
    #: ★ 每个域的"我们有多少函数"（★ 用 §二 能力面那一列的口径：`scripts/sw_*.py` 的公开函数）
    import ast as _ast
    mod_pub = {}
    for p in (R / "scripts").glob("sw_*.py"):
        try:
            mod_pub[p.stem] = len([n for n in _ast.parse(p.read_text(encoding="utf-8")).body
                                   if isinstance(n, _ast.FunctionDef) and not n.name.startswith("_")])
        except Exception:                                                  # noqa: BLE001
            pass
    dom_gaps = parse_gap_domains()
    total_gap = sum(len(v) for v in dom_gaps.values())
    print("  §五 解析出 %d 个域 · 缺口名合计 **%d**" % (len(dom_gaps), total_gap))
    #: ★ 逐条三层判
    rows, strong = [], []
    for dom, names in dom_gaps.items():
        for nm in names:
            nw = _expand(_words(nm))
            hit = []
            for o in ours:
                inter = nw & o["words"]
                if not inter:
                    continue
                cov = len(inter) / max(1, len(nw))
                hit.append((round(cov, 3), o["tool"]))
            hit.sort(key=lambda x: (-x[0], x[1]))
            best = hit[0][0] if hit else 0.0
            tier = "①已有等价物" if best >= 0.5 else ("③强候选" if best == 0.0 else "②需人工核")
            rows.append({"domain": dom, "operation": nm, "best_cov": best,
                         "top": [h[1] for h in hit[:3]], "tier": tier})
            if tier == "③强候选":
                strong.append(nm)
    #: ★ ★ 回归（★ 判据：已知 5 假必须判成"已有"、2 真必须判成"强候选/需核"）
    reg = {}
    for nm, is_gap in KNOWN.items():
        r = next((x for x in rows if x["operation"] == nm), None)
        if r is None:
            reg[nm] = {"found": False}
            continue
        got_gap = (r["tier"] != "①已有等价物")
        reg[nm] = {"expected_gap": is_gap, "got_gap": got_gap, "tier": r["tier"],
                   "cov": r["best_cov"], "ok": (got_gap == is_gap)}
    ok_n = sum(1 for v in reg.values() if v.get("ok"))
    c = Counter(x["tier"] for x in rows)
    out = {"domain_count": len(dom_gaps), "gap_names": total_gap, "tiers": dict(c),
           "strong_candidates": strong, "regression": reg,
           "regression_pass": "%d/%d" % (ok_n, len(KNOWN)),
           "rows": rows,
           "★": "v2：域来自 union-coverage-matrix §五（每个缺口名自带域）· 判据三层 · 用已知 6 条做回归"}
    (W / "output" / "union-gap-v2.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  三层判定：%s" % dict(c))
    print()
    print("  ★★ 回归（★ 判据：v1 核过的 6 条）: **%d/%d**" % (ok_n, len(KNOWN)))
    for nm, v in reg.items():
        print("     %-18s 期望%s区 实得%s  tier=%s cov=%.2f  %s"
              % (nm, "缺" if v.get("expected_gap") else "不缺", "缺" if v.get("got_gap") else "不缺",
                 v.get("tier"), v.get("cov", 0), "OK" if v.get("ok") else "**FAIL**"))
    print()
    print("  ③强候选 %d 个（前 30）:" % len(strong))
    for x in strong[:30]:
        print("     %s" % x)
    return 0 if ok_n == len(KNOWN) else 1


if __name__ == "__main__":
    raise SystemExit(main())
