"""★ 冷门样本上的三族检索对照（★ 分层统计）—— 等 49 路的查询落地后跑。

★ 三个查询族：
  · CN        —— Bunny 写的**中文用户说法**（★ 不许含工具名英文词）
  · EN-nat    —— Bunny 写的**工程师自然英文**
  · ★ EN-mech —— **从工具名机械反推**（无作者 ⇒ 无措辞偏倚，但当基准看，别当成绩）
★ 分层：C1 冷门(无中文文档∧长尾域) · C2 薄文档 · C3 自研非官方层 · H 热门基线
★ 判据：分层 × 分族的 top-k；**三族全 miss** 的清单；**同族误选**；**understood=false** 数
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/measure_rag_cold_sample.py
# 定位:   冷门样本上的三族检索对照（★ 分层统计）—— 等 49 路的查询落地后跑。
# 官方依据: 不适用（本仓工具，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import register_capabilities as rc  # noqa: E402

CJK = re.compile(r"[\u4e00-\u9fff]")


def tok(text: str) -> list:
    text = (text or "").lower()
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", text)
    out = re.findall(r"[a-z0-9]{2,}", text)
    cjk = "".join(ch for ch in text if CJK.match(ch))
    out += [cjk[i : i + 2] for i in range(len(cjk) - 1)]
    return out


def surface():
    names, docs = [], []
    for s in rc.all_specs():
        params = " ".join(p.name for p in (getattr(s, "params", None) or []))
        t: list = []
        for f in (
            s.name,
            getattr(s, "title", "") or "",
            params,
            getattr(s, "doc", "") or "",
        ):
            t += tok(f)
        names.append(s.name)
        docs.append(t)
    return names, docs


def bm25(docs, k1=1.5, b=0.75):
    N = len(docs)
    avg = sum(len(d) for d in docs) / max(1, N)
    df = Counter()
    for d in docs:
        df.update(set(d))
    idf = {t: math.log(1 + (N - n + 0.5) / (n + 0.5)) for t, n in df.items()}
    tfs = [Counter(d) for d in docs]

    def score(q: str):
        qt = tok(q)
        out = []
        for i, tf in enumerate(tfs):
            dl = len(docs[i])
            s = 0.0
            for t in qt:
                f = tf.get(t, 0)
                if not f:
                    continue
                s += idf.get(t, 0.0) * f * (k1 + 1) / (f + k1 * (1 - b + b * dl / avg))
            out.append((s, i))
        out.sort(reverse=True)
        return out

    return score


def main() -> int:
    sample = json.loads(
        (ROOT / "output" / "rag-sample.json").read_text(encoding="utf-8")
    )
    recs, strata = sample["records"], sample["strata"]
    stratum_of = {t: k for k, v in strata.items() for t in v}
    qdir = ROOT / "output" / "rag-queries"
    queries: dict = {}
    unclear: list = []
    for f in sorted(qdir.glob("out-*.json")):
        for row in json.loads(f.read_text(encoding="utf-8")):
            queries[row["tool"]] = row
            if row.get("understood") is False:
                unclear.append(row["tool"])
    print(
        "★ 抽样 %d 个工具 · 收到查询 %d 条 · ★ 标「看不懂」的 %d 条"
        % (len(recs), len(queries), len(unclear))
    )
    if not queries:
        print("★ 还没有查询产出 —— 等 49 路回来再跑")
        return 0
    names, docs = surface()
    score = bm25(docs)
    ks = (1, 3, 5, 10)
    #: ★ 逐条算三族排名
    per = []
    for tool, row in queries.items():
        if tool not in names:
            continue
        idx = names.index(tool)
        fam = {}
        for key, q in (
            ("CN", row.get("cn_query")),
            ("EN-nat", row.get("en_query")),
            ("EN-mech", tool.removeprefix("solidworks_").replace("_", " ")),
        ):
            if not q:
                fam[key] = None
                continue
            ranked = score(q)
            fam[key] = next(
                (r + 1 for r, (_s, i) in enumerate(ranked) if i == idx), None
            )
            if key == "CN":
                fam["_top1_cn"] = names[ranked[0][1]] if ranked else ""
        per.append({"tool": tool, "stratum": stratum_of.get(tool, "?"), **fam})
    #: ★ 分层 × 分族
    print()
    print("| 层 | 数 | CN top-5 | EN-nat top-5 | EN-mech top-5 | 三族全 miss |")
    print("|---|---:|---:|---:|---:|---:|")
    for st in (
        "C1_cold_no_cn_doc_small_domain",
        "C2_cold_thin_doc",
        "C3_non_api_selfmade",
        "H_hot_baseline",
    ):
        rows = [r for r in per if r["stratum"] == st]
        if not rows:
            continue

        def h(k, fam):
            return sum(1 for r in rows if r[fam] and r[fam] <= k)

        miss = sum(
            1
            for r in rows
            if all((r[f] is None or r[f] > 10) for f in ("CN", "EN-nat", "EN-mech"))
        )
        print(
            "| %s | %d | %d/%d = %.0f%% | %d/%d = %.0f%% | %d/%d = %.0f%% | **%d** |"
            % (
                st.split("_")[0],
                len(rows),
                h(5, "CN"),
                len(rows),
                100.0 * h(5, "CN") / len(rows),
                h(5, "EN-nat"),
                len(rows),
                100.0 * h(5, "EN-nat") / len(rows),
                h(5, "EN-mech"),
                len(rows),
                100.0 * h(5, "EN-mech") / len(rows),
                miss,
            )
        )
    print()
    allmiss = [
        r
        for r in per
        if all((r[f] is None or r[f] > 10) for f in ("CN", "EN-nat", "EN-mech"))
    ]
    print(
        "★★ **三族全部掉出 top-10** 的共 **%d / %d** ⇒ ★ 这些是「检索救不回来」的:"
        % (len(allmiss), len(per))
    )
    for r in allmiss:
        print("     [%s] %s" % (r["stratum"].split("_")[0], r["tool"]))
    print()
    print(
        "★ 同族误选（CN 的 top-1 是它的兄弟）: %d / %d"
        % (
            sum(
                1
                for r in per
                if r.get("_top1_cn")
                and r["_top1_cn"] != r["tool"]
                and r["_top1_cn"].rsplit("_", 1)[0] == r["tool"].rsplit("_", 1)[0]
            ),
            len(per),
        )
    )
    print(
        "★★ 标「看不懂」的 **%d** 个 ⇒ ★ 这是**描述质量**的直接缺陷（不是检索问题）:"
        % len(unclear)
    )
    for t in unclear[:20]:
        print("     %s" % t)
    (ROOT / "output" / "rag-cold-result.json").write_text(
        json.dumps(
            {
                "n": len(per),
                "per": per,
                "all_miss": [r["tool"] for r in allmiss],
                "unclear": unclear,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print("★ 明细: output/rag-cold-result.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
