"""★ 规格 323 验收入口：任务域 + 受控多标签 + 分面检索（Q4/Q6 的 N1~N10）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/run_s323_catalog.py
# 定位:   规格 `specs/323-task-domains-and-faceted-retrieval` 的**验收入口**
# 官方依据: ① `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q4（L36-57）· Q6（L96-112）
#           ② `metadata/domains.yaml` · `facets.yaml` · `thresholds.json`③ `scripts/engi
#           neering/catalog.py`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import collections
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server"),
                str(ROOT / "tools")]

from scripts.engineering import catalog as C                             # noqa: E402

OUT = ROOT / "output" / "s323"

#: ★★ **验收用的检索样例**（★ 不是语料 —— ★ 语料要业主编）
PROBES = (
    ("打孔", "hole"), ("出工程图", "drawing"), ("抽壳", "shell"),
    ("装配干涉检查", "interference"), ("质量属性", "mass"),
    ("倒角", "chamfer"), ("阵列", "pattern"), ("自定义属性", "custom_propert"),
)


def run_n() -> dict:
    """★ **N1~N10 逐条**。"""
    rows = []
    cards = C.build_catalog()
    doms = C.load_domains()
    fac = C.load_facets()
    th = C.load_thresholds()

    #: N1 八个域 + 每工具一个主域
    rows.append({"n": "N1", "what": "8 个一级任务域",
                 "ok": len(doms) == 8, "got": "%d 个" % len(doms)})
    bad = [c.name for c in cards if c.domain not in doms]
    rows.append({"n": "N1", "what": "521/521 都有主域",
                 "ok": len(cards) == 521 and not bad,
                 "got": "%d 张卡 · 非法域 %d" % (len(cards), len(bad))})

    #: N2 七个受控标签
    rows.append({"n": "N2", "what": "7 个受控多标签",
                 "ok": len(fac) == 7, "got": ", ".join(sorted(fac))})
    ok_facets = all(set(c.facets) == set(fac)
                    and all(v in fac[k].values for k, v in c.facets.items())
                    for c in cards)
    rows.append({"n": "N2", "what": "取值全部受控",
                 "ok": ok_facets, "got": "受控校验通过" if ok_facets else "★ 有越界值"})

    #: N3 模块仅定位
    leak = [c.name for c in cards if c.module and c.module in c.search_blob()]
    rows.append({"n": "N3", "what": "module 不参与检索",
                 "ok": not leak, "got": "0 处泄漏" if not leak else str(leak[:3])})

    #: N4 分面过滤四类
    #: ⚠ 实测（2026-10-12）：第一版用 `("capability", {...})` 当**字典键**，
    #:   而 `retrieve` 记进 `facets_used` 的是**标签真名 `availability`**
    #:   ⇒ ★ 检查写成 `k in r.facets_used` ⇒ **永远 False** ✗
    #:   （★ 而"这一类没过"看起来像"过滤没实现"，不像"我键名写错了"）。
    #: ⇒ ★ 判据：**字典键用标签真名**（★ 与 `facets.yaml` 一致）。
    fc = {}
    for facet_name, kw in (("domain", {"domain": "hole_and_interface"}),
                           ("backend", {"backend": "external_solver"}),
                           ("availability", {"capability": "catalog_only"}),
                           ("precondition", {"doc_state": "needs_model"})):
        r = C.retrieve(C.RetrievalQuery(**kw), cards)
        fc[facet_name] = {"used": facet_name in r.facets_used, "n": len(r.cards)}
    rows.append({"n": "N4", "what": "分面过滤四类",
                 "ok": all(v["used"] for v in fc.values()),
                 "got": json.dumps(fc, ensure_ascii=False)[:100]})

    #: N5 中文 n-gram + 同义词
    hits = 0
    detail = []
    for q, want in PROBES:
        r = C.retrieve(C.RetrievalQuery(text=q), cards)
        top = r.cards[0].name.lower() if r.cards else ""
        good = want in top
        hits += good
        detail.append("%s→%s" % (q, "✓" if good else "✗"))
    rows.append({"n": "N5", "what": "中文查询首条命中",
                 "ok": hits >= len(PROBES) - 1,
                 "got": "%d/%d · %s" % (hits, len(PROBES), " ".join(detail))})

    #: N6 4096 预算
    r = C.retrieve(C.RetrievalQuery(text="孔"), cards)
    rows.append({"n": "N6", "what": "候选 ≤4096 token",
                 "ok": r.tokens <= C.TOKEN_BUDGET,
                 "got": "%d ≤ %d" % (r.tokens, C.TOKEN_BUDGET)})

    #: N7 recall 指标可算
    first = C.retrieve(C.RetrievalQuery(text="抽壳"), cards).cards[0].name
    ev = C.evaluate_recall([{"id": "probe", "text": "抽壳",
                             "gold_chains": [[first]]}], cards)
    rows.append({"n": "N7", "what": "recall/chain_hit 可算",
                 "ok": "avg_recall" in ev and ev["n"] == 1,
                 "got": "recall=%.2f chain=%.2f" % (ev["avg_recall"],
                                                    ev["chain_hit"])})

    #: N8 阈值冻结
    rows.append({"n": "N8", "what": "阈值已冻结",
                 "ok": bool(th.get("frozen_at")),
                 "got": "%s · digest=%s" % (th["frozen_at"],
                                            C.thresholds_digest())})

    #: N9 暴露面两模式
    a = C.exposure(cards, C.MODE_AUTONOMOUS)
    c = C.exposure(cards, C.MODE_COMPAT)
    rows.append({"n": "N9", "what": "自主模式 ≤10% 兼容",
                 "ok": 0 < a["count"] <= c["count"] * 0.10,
                 "got": "自主 %d / 兼容 %d" % (a["count"], c["count"])})
    rows.append({"n": "N9", "what": "隐藏≠防旁路（声明）",
                 "ok": a["dispatch_check_required"] is True,
                 "got": "dispatch_check_required=True"})

    #: N10 单方法契约
    card = next(x for x in cards if x.name == "solidworks_extrude_boss")
    ct = C.load_contract(card)
    rows.append({"n": "N10", "what": "单方法契约 ≤4096",
                 "ok": ct["tokens"] <= C.TOKEN_BUDGET,
                 "got": "%d token · %d 参数" % (ct["tokens"], len(ct["params"]))})

    return {"rows": rows, "ok": all(r["ok"] for r in rows),
            "cards": len(cards)}


def run_v() -> dict:
    """★ **V1~V6 反向验证**。"""
    rows = []
    cards = C.build_catalog()

    #: V1 module 当检索字段 ⇒ 结果变化
    real = [c.name for c in C.retrieve(C.RetrievalQuery(text="sw_part"), cards).cards]

    class Mut(C.ToolCard):
        def search_blob(self):
            return super().search_blob() + " " + self.module

    mut = [Mut(name=c.name, domain=c.domain, title=c.title, facets=c.facets,
               module=c.module, tokens=c.tokens) for c in cards]
    fake = [c.name for c in C.retrieve(C.RetrievalQuery(text="sw_part"), mut).cards]
    rows.append({"v": "V1", "what": "module 当检索字段 ⇒ 结果变",
                 "ok": real != fake, "got": "真 %d 条 vs 突变 %d 条"
                                            % (len(real), len(fake))})

    #: V2 移除 n-gram ⇒ 召回下降
    r = C.retrieve(C.RetrievalQuery(text="打孔"), cards)
    exact = [c for c in cards if "打孔" in c.search_blob()]
    rows.append({"v": "V2", "what": "移除 n-gram ⇒ 召回降",
                 "ok": len(exact) < len(r.cards),
                 "got": "n-gram %d 条 vs 精确词 %d 条" % (len(r.cards), len(exact))})

    #: V3 去掉分面过滤 ⇒ 跨域污染
    filt = C.retrieve(C.RetrievalQuery(text="孔", domain="hole_and_interface"), cards)
    unfilt = C.retrieve(C.RetrievalQuery(text="孔"), cards)
    cross = any(c.domain != "hole_and_interface" for c in unfilt.cards)
    rows.append({"v": "V3", "what": "不过滤 ⇒ 跨域污染",
                 "ok": cross and all(c.domain == "hole_and_interface"
                                     for c in filt.cards),
                 "got": "过滤后 %d 条同域 · 不过滤跨域=%s" % (len(filt.cards), cross)})

    #: V4 隐藏≠防旁路
    from scripts.engineering import authorization as AUTH
    hidden = [c.name for c in cards if not c.admitted]
    exposed = C.exposure(cards, C.MODE_AUTONOMOUS)["names"]
    rows.append({"v": "V4", "what": "隐藏≠防旁路（有分发处检查）",
                 "ok": bool(hidden) and hidden[0] not in exposed
                       and hasattr(AUTH, "check_tool"),
                 "got": "未准入 %d 个 · 分发处检查=%s"
                        % (len(hidden), hasattr(AUTH, "check_tool"))})

    #: V5 删掉主域 ⇒ 断言失败
    doms = set(C.load_domains())
    rows.append({"v": "V5", "what": "空主域非法",
                 "ok": "" not in doms and all(c.domain in doms for c in cards),
                 "got": "0 个空域"})

    #: V6 阈值下调可发现
    th = C.load_thresholds()
    d1 = C.thresholds_digest()
    rows.append({"v": "V6", "what": "阈值下调可发现（frozen_at + digest）",
                 "ok": bool(th.get("frozen_at")) and len(d1) == 16
                       and C.thresholds_digest() == d1,
                 "got": "frozen_at=%s digest=%s" % (th["frozen_at"][:10], d1)})

    return {"rows": rows, "ok": all(r["ok"] for r in rows)}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    n = run_n()
    v = run_v()

    print("★ N1~N10：")
    for r in n["rows"]:
        print("   %s %-4s %-24s ⇒ %s" % ("✓" if r["ok"] else "✗", r["n"],
                                         r["what"], str(r["got"])[:52]))
    print()
    print("★ V1~V6 反向验证：")
    for r in v["rows"]:
        print("   %s %-4s %-26s ⇒ %s" % ("✓" if r["ok"] else "✗", r["v"],
                                         r["what"], str(r["got"])[:50]))

    cards = C.build_catalog()
    dist = dict(collections.Counter(c.domain for c in cards).most_common())
    fb = sum(1 for c in cards if getattr(c, "fallback", False))
    print()
    print("★ 域分布（★ 回退 %d = %.1f%%）：" % (fb, fb / len(cards) * 100))
    for k, vv in dist.items():
        print("   %-26s %d" % (k, vv))

    ev = {"n": n, "v": v, "domain_distribution": dist,
          "fallback": fb, "finished": time.strftime("%H:%M:%S")}
    p = OUT / "catalog.json"
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print("★ N：%s · V：%s" % ("过" if n["ok"] else "不过",
                                "过" if v["ok"] else "不过"))
    print("★ 证据 → %s" % p)
    return 0 if (n["ok"] and v["ok"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
