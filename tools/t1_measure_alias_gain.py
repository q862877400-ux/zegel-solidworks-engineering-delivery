"""★ T1-2：别名候选的**增益测量** —— 别名必须「挣到它的字节」。"""
from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import register_capabilities as rc                                    # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CJK = re.compile(r"[\u4e00-\u9fff]")


def tok(text: str) -> list:
    t = (text or "").lower()
    t = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", t)
    out = re.findall(r"[a-z0-9]{2,}", t)
    cjk = "".join(ch for ch in t if CJK.match(ch))
    out += [cjk[i:i + 2] for i in range(len(cjk) - 1)]
    return out


def build(alias_map: dict) -> tuple:
    """★ 造检索面（`alias_map` 只在内存里追加，不碰 ToolSpec）。"""
    names, docs = [], []
    for s in rc.all_specs():
        params = " ".join(p.name for p in (getattr(s, "params", None) or []))
        names.append(s.name)
        docs.append(tok(" ".join([s.name, getattr(s, "title", "") or "", params,
                                  getattr(s, "doc", "") or "", alias_map.get(s.name, "")])))
    return names, docs


class BM25:
    def __init__(self, names, docs, k1=1.5, b=0.75):
        self.names, self.docs, self.k1, self.b = names, docs, k1, b
        N = len(docs)
        self.avg = sum(len(d) for d in docs) / max(1, N)
        df = Counter()
        for d in docs:
            df.update(set(d))
        self.idf = {t: math.log(1 + (N - n + 0.5) / (n + 0.5)) for t, n in df.items()}
        self.tfs = [Counter(d) for d in docs]

    def rank(self, query: str, target: str):
        qt, out = tok(query), []
        for i, tf in enumerate(self.tfs):
            dl = len(self.docs[i])
            s = 0.0
            for t in qt:
                f = tf.get(t, 0)
                if f:
                    s += self.idf.get(t, 0.0) * f * (self.k1 + 1) / (
                        f + self.k1 * (1 - self.b + self.b * dl / self.avg))
            out.append((s, self.names[i]))
        out.sort(key=lambda x: (-x[0], x[1]))          #: ★ 同分按名字钉死
        for r, (_s, nm) in enumerate(out, 1):
            if nm == target:
                return r
        return None


def main() -> int:
    cand = json.loads((ROOT / "output" / "t1-alias-candidates.json").read_text(encoding="utf-8"))
    by_tool: dict = {}
    for k in cand["kept"]:
        a = by_tool.setdefault(k["tool"], {"ops": set(), "keys": set()})
        a["ops"].add(k["op"])
        a["keys"] |= set(k["keys"])

    n0, d0 = build({})
    base = BM25(n0, d0)
    print("★ 别名候选：%d 对 → 涉及 **%d** 个工具" % (len(cand["kept"]), len(by_tool)))
    print("★ 查询 = 该工具的 op + keys（★ 对方词表，不是我编的）")
    print()
    summ = []
    for tool, a in sorted(by_tool.items()):
        alias_text = " ".join(sorted(a["ops"] | a["keys"]))
        query = " ".join(sorted(a["ops"])) + " " + " ".join(sorted(a["keys"]))
        n1, d1 = build({tool: alias_text})
        with_alias = BM25(n1, d1)
        r0, r1 = base.rank(query, tool), with_alias.rank(query, tool)
        summ.append({"tool": tool, "ops": sorted(a["ops"]), "keys": sorted(a["keys"]),
                     "query": query.strip(), "rank0": r0, "rank1": r1,
                     "gain": (r0 - r1) if (r0 and r1) else None})

    improved = [r for r in summ if r["gain"] and r["gain"] > 0]
    newly = [r for r in summ if r["rank0"] is None and r["rank1"] is not None]
    worse = [r for r in summ if r["gain"] is not None and r["gain"] < 0]
    print("★ 结果（n=%d 个工具）:" % len(summ))
    print("   · 排名**提升**    : %d" % len(improved))
    print("   · **新进榜**（原查不到）: %d" % len(newly))
    print("   · 无变化          : %d" % (len(summ) - len(improved) - len(newly) - len(worse)))
    print("   · **变差**        : %d  ★ 变差的一律不采纳" % len(worse))
    print()
    print("★★ 提升最大的 12（★ 这些才值得接进 doc）:")
    for r in sorted(improved, key=lambda x: -x["gain"])[:12]:
        print("   %-42s %s → %s（+%d）" % (r["tool"].removeprefix("solidworks_"),
                                          r["rank0"], r["rank1"], r["gain"]))
    if newly:
        print()
        print("★ 新进榜的:")
        for r in newly[:10]:
            print("   %-42s None → %s" % (r["tool"].removeprefix("solidworks_"), r["rank1"]))
    out = ROOT / "output" / "t1-alias-gain.json"
    out.write_text(json.dumps({"summary": summ}, ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print("★ 写出: %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
