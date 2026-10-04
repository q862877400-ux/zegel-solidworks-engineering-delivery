"""★ T1-5：带口径的复测（SC-1）—— ★ 两面都测，避免只报有利的那一面。

★ 面 A（★ 我预判：几乎不动）：48 题的**中文**查询 —— 别名是英文 ⇒ 词元不重叠 ⇒ 不该提升
★ 面 B（★ 别名的**本来用途**）：用别名自己的词当查询 ⇒ 展示别名到底做了什么
★ 两面的「现状」都把 `★ 别名: …` 行**剥掉**再建面 ⇒ 精确 A/B（不是与历史数比）
"""
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
sys.path.insert(0, str(ROOT / "tools"))
import metric_scope as ms                                             # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CJK = re.compile(r"[\u4e00-\u9fff]")
ALIAS_MARK = "★ 别名:"


def tok(text: str) -> list:
    t = (text or "").lower()
    t = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", t)
    out = re.findall(r"[a-z0-9]{2,}", t)
    cjk = "".join(ch for ch in t if CJK.match(ch))
    out += [cjk[i:i + 2] for i in range(len(cjk) - 1)]
    return out


def build(strip_alias: bool) -> tuple:
    names, docs = [], []
    for s in rc.all_specs():
        params = " ".join(p.name for p in (getattr(s, "params", None) or []))
        doc = getattr(s, "doc", "") or ""
        if strip_alias and ALIAS_MARK in doc:
            doc = doc.split(ALIAS_MARK)[0].rstrip()        #: ★ 剥掉别名行 ⇒ 得到"现状"面
        names.append(s.name)
        docs.append(tok(" ".join([s.name, getattr(s, "title", "") or "", params, doc])))
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

    def rank(self, q: str, target: str):
        qt, out = tok(q), []
        for i, tf in enumerate(self.tfs):
            dl = len(self.docs[i])
            s = 0.0
            for t in qt:
                f = tf.get(t, 0)
                if f:
                    s += self.idf.get(t, 0.0) * f * (self.k1 + 1) / (
                        f + self.k1 * (1 - self.b + self.b * dl / self.avg))
            out.append((s, self.names[i]))
        out.sort(key=lambda x: (-x[0], x[1]))
        for r, (_s, nm) in enumerate(out, 1):
            if nm == target:
                return r
        return None


def main() -> int:
    print(ms.block_for("alias_gain"))
    print()
    n_before, d_before = build(strip_alias=True)
    n_after, d_after = build(strip_alias=False)
    bm_before, bm_after = BM25(n_before, d_before), BM25(n_after, d_after)

    #: ── 面 A：48 题的中文查询（★ 预判：几乎不动） ──
    D = ROOT / "output" / "pick-test"
    answers = json.loads((D / "_answers.json").read_text(encoding="utf-8"))
    qs = {}
    for f in sorted((ROOT / "output" / "rag-queries").glob("out-*.json")):
        for row in json.loads(f.read_text(encoding="utf-8")):
            qs[row["tool"]] = row
    ks = (1, 3, 5, 10)
    print("★ 面 A · 48 题的【中文】查询（★ 别名是英文 ⇒ 预判不提升）")
    for label, bm, nms in (("现状（剥掉别名）", bm_before, n_before), ("加别名后", bm_after, n_after)):
        hit = {k: 0 for k in ks}
        n = 0
        for a in answers:
            q = (qs.get(a["expected_tool"]) or {}).get("cn_query")
            if not q:
                continue
            n += 1
            r = bm.rank(q, a["expected_tool"])
            for k in ks:
                if r and r <= k:
                    hit[k] += 1
        if n:
            print("   %-16s n=%d · %s" % (label, n,
                  " · ".join("top-%d **%d/%d = %.0f%%**" % (k, hit[k], n, 100.0 * hit[k] / n)
                             for k in ks)))

    #: ── 面 B：别名自己的词当查询（★ 别名本来要解决的那件事） ──
    final = json.loads((ROOT / "output" / "t1-alias-final.json").read_text(encoding="utf-8"))
    cand = json.loads((ROOT / "output" / "t1-alias-candidates.json").read_text(encoding="utf-8"))
    alias_of: dict = {}
    for k in cand["kept"]:
        a = alias_of.setdefault(k["tool"], {"ops": set(), "keys": set()})
        a["ops"].add(k["op"])
        a["keys"] |= set(k["keys"])
    print()
    print("★ 面 B · 用别名自己的词当查询（★ 这才是别名本来要解决的事）")
    for name, bm, nms in (("现状（剥掉别名）", bm_before, n_before), ("加别名后", bm_after, n_after)):
        rows = []
        for tool, a in alias_of.items():
            q = " ".join(sorted(a["ops"])) + " " + " ".join(sorted(a["keys"]))
            rows.append((bm.rank(q, tool), tool))
        ok = sum(1 for r, _t in rows if r and r <= 5)
        r1 = sum(1 for r, _t in rows if r == 1)
        print("   %-16s n=%d · top-1 **%d** · top-5 **%d/%d = %.0f%%**"
              % (name, len(rows), r1, ok, len(rows), 100.0 * ok / len(rows)))

    print()
    print("★★ 结论（★ 两面一起读）:")
    print("   · 面 A 若「不动」⇒ ★ **英文别名对中文查询无效**（词元不重叠）—— 这是**预期**，不是失败")
    print("   · 面 B 若「大幅提升」⇒ ★ 别名机制**对它本来的用途有效**")
    print("   ★★ 两面合起来的含义：**别名只对「用英文说那些词」的用户有用**；")
    print("      中文用户的检索要另想办法（★ 那需要真实中文语料，本仓目前没有）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
