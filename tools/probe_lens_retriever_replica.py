"""★ 复刻 `dsh-mcp-lens` 的检索器，并在**我们的目录**上跑 —— ★ 用来核「1000 个工具都能精准找回」。

★ 为什么能复刻：先前调研从 `src/catalog.ts` 把算法**逐项抽出**，且用他们真实 trace 的
  `score: 0.122753` 反算校验过（字段词数 ≈ 29，与文档一致）✓ 本脚本**照抄那份口径**：

    field贡献 = weight × 1/(1 + b×log2(1 + max(0, 该字段去重词数 − 1)))
    total     = Σ_词( 最佳字段贡献 × IDF )
    score     = total × (1 + 0.12×命中词数/查询词数) / sqrt(查询词数)
    IDF       = log(1 + (N − df + 0.5)/(df + 0.5))      N = 工具数（非字段数）
    权重      = name 3.2 · title 2.4 · server 1.9 · schema 1.15 · description 0.9
    b         = name 0.08 · title 0.15 · server 0.05 · schema 0.55 · description 0.72
    ★ 无 tf/k1（布尔命中）· 中文=整块 Han+相邻二元组（2 字词只出自己）
    ★ df/N > 0.72 的查询词被丢弃 · 同分按 name 码点升序

★ 与我的 BM25 探针对比 ⇒ 回答「换了他们的算法，我们的中文查询能不能找回」。
"""
from __future__ import annotations

import json
import math
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import metric_scope as ms   # ★ 口径注册表（★ 事实 517：口径必须落成代码）
import register_capabilities as rc                                    # noqa: E402

W = {"name": 3.2, "title": 2.4, "server": 1.9, "schema": 1.15, "description": 0.9}
B = {"name": 0.08, "title": 0.15, "server": 0.05, "schema": 0.55, "description": 0.72}
HAN = re.compile(r"[\u3400-\u9fff\u3040-\u30ff\uac00-\ud7af]+")


def stem(w: str) -> str:
    """★ 照抄他们那 3 条玩具级规则。"""
    if w.endswith("ies") and len(w) > 3:
        return w[:-3] + "y"
    if re.search(r"(s|x|z|ch|sh)es$", w) and len(w) > 3:
        return re.sub(r"es$", "", w)
    if w.endswith("s") and not w.endswith("ss") and len(w) > 2:
        return w[:-1]
    return w


def tok(text: str) -> list:
    """★ 照抄：NFKC → 驼峰切 → 小写 → [\\p{L}\\p{N}]+（★ `_`/`-` 天然是分隔符）
    ★ 中文：整块 Han 串 + **相邻二元组**（★ 仅当该串 > 2 字；2 字词只产出它自己）。"""
    t = unicodedata.normalize("NFKC", text or "")
    t = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", t)          #: 驼峰切
    #: ★ 先把 Han 段抠出来单独处理
    out: list = []
    for m in HAN.finditer(t):
        run = m.group(0)
        if len(run) > 2:
            out.append(run)
            out += [run[i:i + 2] for i in range(len(run) - 1)]
        else:
            out.append(run)                                 #: ★ 2 字（或 1 字）只出自己
    t2 = HAN.sub(" ", t)
    for w in re.findall(r"[^\W_]+", t2, flags=re.UNICODE):    #: ★ `_` 排除掉 ⇒ 等价 \p{L}\p{N}
        if len(w) >= 2:
            out.append(stem(w.lower()))
    return out


def build_fields():
    """★ 5 个字段各自的词集（去重）—— ★ 长度归一化用的是**该字段的去重词数**。"""
    rows = []
    for s in rc.all_specs():
        schema = " ".join(p.name for p in (getattr(s, "params", None) or []))
        fields = {
            "name": set(tok(s.name.removeprefix("solidworks_"))),      #: ★ 名字去掉统一前缀
            "title": set(tok(getattr(s, "title", "") or "")),
            "server": {"solidworks"},
            "schema": set(tok(schema)),
            "description": set(tok(getattr(s, "doc", "") or "")),
        }
        rows.append({"tool": s.name, "fields": fields})
    return rows


def main() -> int:
    rows = build_fields()
    N = len(rows)
    #: ★ df：一个词出现在**多少个工具**里（任一字段）—— ★ 官方口径 N = 工具数
    df: dict = {}
    for r in rows:
        allw = set().union(*r["fields"].values())
        for w in allw:
            df[w] = df.get(w, 0) + 1
    idf = {w: math.log(1 + (N - d + 0.5) / (d + 0.5)) for w, d in df.items()}
    #: ★ 每工具每字段的「贡献」(不含 IDF)
    contrib = []
    for r in rows:
        c = {}
        for f, ws in r["fields"].items():
            c[f] = W[f] / (1 + B[f] * math.log2(1 + max(0, len(ws) - 1)))
        contrib.append(c)

    def score(q: str):
        qt = [w for w in dict.fromkeys(tok(q))]
        #: ★ 高频闸门：df/N > 0.72 的查询词整体丢弃（df==0 或 N<=2 例外）
        qt = [w for w in qt if (df.get(w, 0) == 0 or N <= 2
                                or df.get(w, 0) / N <= 0.72)]
        out = []
        for i, r in enumerate(rows):
            tot, hit = 0.0, 0
            for w in qt:
                best = 0.0
                for f, ws in r["fields"].items():
                    if w in ws:
                        best = max(best, contrib[i][f])
                if best > 0:
                    tot += best * idf.get(w, 0.0)
                    hit += 1
            s = tot * (1 + 0.12 * (hit / max(1, len(qt)))) / math.sqrt(max(1, len(qt)))
            out.append((s, r["tool"]))
        #: ★ 同分按 name 码点升序
        out.sort(key=lambda x: (-x[0], x[1]))
        return out

    #: ★ 用与前面探针**同一批任务**（48 题，来自 Bunny 的中文查询）
    D = ROOT / "output" / "pick-test"
    answers = {a["index"]: a for a in json.loads((D / "_answers.json").read_text(encoding="utf-8"))}
    qs = {}
    for f in sorted((ROOT / "output" / "rag-queries").glob("out-*.json")):
        for row in json.loads(f.read_text(encoding="utf-8")):
            qs[row["tool"]] = row
    tasks = [{"i": i, "task": a["task"], "expected": a["expected_tool"],
              "cn": (qs.get(a["expected_tool"]) or {}).get("cn_query"),
              "en": (qs.get(a["expected_tool"]) or {}).get("en_query")}
             for i, a in answers.items()]
    print("★ 复刻 dsh-mcp-lens 的检索器 · 目录 **%d** 个工具 · 任务 %d 个" % (N, len(tasks)))
    print()
    print(ms.block_for('lens_replica_topk'))
    print()
    ks = (1, 3, 5, 10)
    for label, key in (("CN（中文用户说法）", "cn"), ("EN-nat（自然英文）", "en")):
        hit = {k: 0 for k in ks}
        n = 0
        for t in tasks:
            q = t[key]
            if not q:
                continue
            n += 1
            ranked = score(q)
            names = [nm for _s, nm in ranked]
            idx = names.index(t["expected"]) if t["expected"] in names else None
            rank = (idx + 1) if idx is not None else None
            for k in ks:
                if rank and rank <= k:
                    hit[k] += 1
        print("★ **%s**（n=%d）: %s" % (label, n,
              " · ".join("top-%d **%d/%d = %.0f%%**" % (k, hit[k], n, 100.0 * hit[k] / n)
                         for k in ks)))
    print()
    print("★ 对照（本会话已测）:")
    print("   · 我的 BM25（同目录、同题）: CN top-5 约 33% / EN-nat 约 88%")
    print("   · ★★ 真模型自己挑（同一批 48 题、双盲判）: **正确率 87–91%，前二 96%**")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
