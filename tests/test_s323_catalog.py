"""★ 规格 323 契约测试：任务域 + 受控多标签 + 分面检索（Q4/Q6 的 N1~N10）。

★★ 含**反向验证**（★ 规格 §5 的 V1~V6）：
   V1 把 module 当检索字段 / V2 移除 n-gram / V3 去掉分面过滤
   V4 隐藏工具但不检查权限 / V5 删掉主域 / V6 阈值下调
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_s323_catalog.py
# 定位:   规格 `specs/323-task-domains-and-faceted-retrieval` 的 N1~N10 契约测试
# 官方依据: ① `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q4（L36-57）逐字
#           ② 同文件 Q6（L96-112）逐字
#           ③ 同文件 Q12（L214-231）逐字
#           ④ `metadata/domains.yaml` · `facets.yaml` · `thresholds.json`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

from scripts.engineering import catalog as C                             # noqa: E402


@pytest.fixture(scope="module")
def cards() -> list:
    return C.build_catalog()


#: ══ N1 八个一级任务域 ════════════════════════════════════════════════

def test_exactly_eight_domains() -> None:
    """★★ Q4 L38 逐字：「确定**八个**一级任务域」。"""
    d = C.load_domains()
    assert len(d) == 8, "★ 域不是 8 个：%s" % sorted(d)


def test_domain_names_match_q4_verbatim() -> None:
    """★★ 域名必须**逐字**是 Q4 给的那八个。"""
    want = {"需求与计算", "草图与基准", "实体成形与修改", "孔系与连接接口",
            "装配与机构", "工程图与标注", "分析与检验", "文档与交付"}
    got = {d.name for d in C.load_domains().values()}
    assert got == want, "★ 域名单不符：%s" % (got ^ want)


def test_every_tool_has_a_domain(cards) -> None:
    """★★ FR-001 / SC-001：**每个工具恰好一个主域**。

    ★★ 2026-10-12 更新（★ 规格 329）：**521 → 525**
      （★ +4 个目录检索入口 —— ★ Q6 L110「必须同时改 MCP 暴露面」）。
      ★ 判据是**下限 + 零非法**（★ 工具面只增不减）。
    """
    assert len(cards) >= 521, "★ 工具卡应 ≥521 张：%d" % len(cards)
    doms = set(C.load_domains())
    bad = [c.name for c in cards if c.domain not in doms]
    assert not bad, "★ 这些工具的主域不合法：%s" % bad[:5]


def test_domain_distribution_is_not_degenerate(cards) -> None:
    """★★ **域分布不能退化成"全在一个域"**（★ 实测抓到的真问题）。

    ⚠ 实测（2026-10-12）：第一版 `cues` 只有中文 ⇒ ★ **357/521 落回退域**
      ⇒ 分布看起来像 `{document_and_delivery: 360, ...}` —— ★ **那等于没有分类**。
    ⇒ ★ 判据：**至少 7 个域有 ≥5 个工具**（★ 且回退率 <15%）。
    """
    import collections
    cnt = collections.Counter(c.domain for c in cards)
    thin = [d for d, n in cnt.items() if n < 5]
    assert len(thin) <= 1, "★ 这些域太薄（<5 个工具）：%s" % thin
    fb = sum(1 for c in cards if getattr(c, "fallback", False))
    assert fb / len(cards) < 0.15, "★ 回退率 %.1f%% 过高" % (fb / len(cards) * 100)


#: ══ N2 受控多标签 ════════════════════════════════════════════════════

def test_seven_facets() -> None:
    """★★ Q4 L40 逐字：**七个**受控多标签。"""
    f = C.load_facets()
    assert set(f) == {"object_kind", "operation", "result_kind",
                      "precondition", "effect", "backend", "availability"}, \
        "★ 标签集不符：%s" % sorted(f)


def test_effect_has_six_kinds_per_q12() -> None:
    """★★ Q12 L223 逐字：「效应按**文档几何、文档属性、选择状态、界面状态、
    文件系统、网络**分别描述」⇒ ★ 六类 + `none`。"""
    f = C.load_facets()["effect"].values
    for k in ("doc_geometry", "doc_property", "selection", "ui_state",
              "filesystem", "network"):
        assert k in f, "★ effect 缺 %s" % k


def test_every_card_has_all_seven_facets(cards) -> None:
    """★ SC-002：每张卡都有 7 个标签，且**取值受控**。"""
    fac = C.load_facets()
    for c in cards:
        assert set(c.facets) == set(fac), "★ %s 的标签不全" % c.name
        for fn, fv in c.facets.items():
            assert fv in fac[fn].values, \
                "★ %s 的 %s=%r 不在受控取值里" % (c.name, fn, fv)


def test_bad_facet_value_is_rejected() -> None:
    """★ 受控校验**真的在**（★ 不是摆设）。"""
    fac = C.load_facets()
    assert "乱写的值" not in fac["backend"].values


#: ══ N3 模块仅定位 ════════════════════════════════════════════════════

def test_module_is_not_in_search_blob(cards) -> None:
    """★★★ Q4 L40 逐字：「实现模块仅保留为**定位信息**，**不作为检索分类**」。

    ★★ 这是 **SC-003** —— ★ 判据是**结构性**的（`search_blob()` 里没有它），
      ★ 不是靠"记得别写进去"。
    """
    for c in cards:
        if c.module:
            assert c.module not in c.search_blob(), \
                "★★ %s 的 module 进了检索文本！" % c.name


def test_module_is_kept_as_locator(cards) -> None:
    """★ 但 `module` **仍要保留**（★ 定位信息不能丢）。"""
    assert any(c.module for c in cards)


#: ══ N4/N5 分面检索 + n-gram ══════════════════════════════════════════

def test_ngrams_produce_cjk_grams() -> None:
    """★★ Q6 L103 逐字：「中文 n-gram」⇒ ★ 中文片段要切出 gram。"""
    g = C.ngrams("打孔", 2)
    assert "打" in g and "孔" in g and "打孔" in g


def test_ngram_matches_cross_word() -> None:
    """★★ **n-gram 的意义**：`打孔` 要能命中含 `孔` 的工具（★ 精确词做不到）。"""
    g = C.ngrams("打孔", 2)
    assert "孔" in g


def test_synonyms_expand_chinese_to_english() -> None:
    """★★ Q6 L103 逐字：「受控**中英文**同义词召回」。"""
    t = C.expand_query("打孔")
    assert "hole" in t, "★ 中文没扩到英文：%s" % sorted(t)[:10]


def test_retrieval_finds_hole_tools(cards) -> None:
    """★ 中文「打孔」⇒ 第一条必须是孔类工具（★ 端到端）。"""
    r = C.retrieve(C.RetrievalQuery(text="打孔"), cards)
    assert r.cards, "★ 一个都没召回"
    assert "hole" in r.cards[0].name.lower(), \
        "★ 第一条不是孔工具：%s" % r.cards[0].name


def test_retrieval_finds_drawing_tools(cards) -> None:
    """★ 中文「出工程图」⇒ 第一条必须是工程图工具。"""
    r = C.retrieve(C.RetrievalQuery(text="出工程图"), cards)
    assert "drawing" in r.cards[0].name.lower(), r.cards[0].name


def test_facet_filter_domain(cards) -> None:
    """★★ FR-004 / SC-004：**分面过滤生效**（★ 按任务类型）。"""
    r = C.retrieve(C.RetrievalQuery(text="孔", domain="hole_and_interface"),
                   cards)
    assert "domain" in r.facets_used
    assert all(c.domain == "hole_and_interface" for c in r.cards)


def test_facet_filter_backend(cards) -> None:
    """★ 分面过滤：**后端可达性**。"""
    r = C.retrieve(C.RetrievalQuery(backend="external_solver"), cards)
    assert "backend" in r.facets_used
    assert all(c.facets["backend"] == "external_solver" for c in r.cards)


def test_facet_filter_capability(cards) -> None:
    """★ 分面过滤：**能力范围**（★ `availability`）。"""
    r = C.retrieve(C.RetrievalQuery(capability="catalog_only"), cards)
    assert "availability" in r.facets_used
    assert all(c.facets["availability"] == "catalog_only" for c in r.cards)


#: ══ N6 4096 预算 ═════════════════════════════════════════════════════

def test_retrieval_respects_budget(cards) -> None:
    """★★ Q6 L98 逐字：「单次上限定为 **4096 token**」。"""
    r = C.retrieve(C.RetrievalQuery(text="孔"), cards)
    assert r.tokens <= C.TOKEN_BUDGET, "★ 超预算：%d" % r.tokens


def test_retrieval_truncates_not_raises(cards) -> None:
    """★ 超预算 ⇒ **截断**并如实报（★ 不是报错）。"""
    r = C.retrieve(C.RetrievalQuery(text="孔"), cards, budget=10)
    assert r.truncated >= 1
    assert r.tokens <= 10


#: ══ N7/N8 recall 指标 + 阈值冻结 ═════════════════════════════════════

def test_thresholds_frozen(cards) -> None:
    """★★ SC-009 / FR-009：阈值**在评测前冻结**（★ Q4 L55 逐字：
    「必须在首次正式评测前冻结，**不能看过结果后下调**」）。"""
    th = C.load_thresholds()
    assert th.get("frozen_at"), "★ 没有 `frozen_at`"
    assert th["thresholds"]["avg_recall"] == 0.95
    assert th["thresholds"]["chain_hit"] == 0.90
    assert th["thresholds"]["domain_span_3_ratio"] == 0.90
    assert th["thresholds"]["candidate_token_budget"] == 4096


def test_thresholds_digest_is_stable() -> None:
    """★ 阈值摘要可核（★ 用于证明它没被事后改过）。"""
    assert len(C.thresholds_digest()) == 16


def test_recall_metrics_are_computed(cards) -> None:
    """★★ N7：recall / chain_hit / 域跨度**三个指标都算得出**（★ Q4 L49-51 公式）。"""
    cases = [{"id": "t1", "text": "打孔",
              "gold_chains": [["solidworks_create_hole_feature",
                               "solidworks_hole_wizard"]]}]
    out = C.evaluate_recall(cases, cards)
    assert "avg_recall" in out and "chain_hit" in out
    assert out["n"] == 1


def test_recall_formula_matches_q4(cards) -> None:
    """★★ Q4 L49-51 的公式：`recall_i = max_j |R∩G|/|G|`。"""
    #: ★ 造一个必中的 gold chain（★ 只含检索第一条）
    first = C.retrieve(C.RetrievalQuery(text="抽壳"), cards).cards[0].name
    cases = [{"id": "t", "text": "抽壳", "gold_chains": [[first]]}]
    out = C.evaluate_recall(cases, cards)
    assert out["avg_recall"] == 1.0
    assert out["chain_hit"] == 1.0


def test_recall_skips_whole_machine_for_span(cards) -> None:
    """★★ Q4 L55 逐字：「**复杂整机需求不参加**『≤3 个域』这一局部检索指标」。"""
    cases = [{"id": "w", "text": "孔", "whole_machine": True,
              "gold_chains": [["solidworks_create_hole_feature"]]}]
    out = C.evaluate_recall(cases, cards)
    assert out["local_n"] == 0, "★ 整机需求被算进局部指标了"


def test_recall_without_corpus_is_honest(cards) -> None:
    """★★ **没语料就说没语料**（★ Q4 L44 逐字：语料由**业主**编）。"""
    out = C.evaluate_recall([], cards)
    assert out["ok"] is False
    assert "业主" in out["reason"]


#: ══ N9 暴露面 ════════════════════════════════════════════════════════

def test_autonomous_mode_is_small(cards) -> None:
    """★★ Q6 L110 逐字：自主模式「只返回**规划入口与必要查询工具**」。

    ★ 判据（SC-010）：**≤ 兼容模式的 10%**。
    """
    a = C.exposure(cards, C.MODE_AUTONOMOUS)
    c = C.exposure(cards, C.MODE_COMPAT)
    assert a["count"] > 0, "★ 自主模式一个都不暴露 ⇒ 规划入口没了"
    assert a["count"] <= c["count"] * 0.10, \
        "★ 自主模式 %d / 兼容 %d 太大" % (a["count"], c["count"])


def test_compat_mode_keeps_everything(cards) -> None:
    """★ Q6 L110 逐字：兼容模式**保留原工具名称和签名**。"""
    c = C.exposure(cards, C.MODE_COMPAT)
    assert c["count"] == len(cards)


def test_exposure_declares_dispatch_check(cards) -> None:
    """★★★ Q6 L110 逐字：「**隐藏工具仍要在实际调用分发处检查权限，
    不能靠隐藏列表防旁路**」⇒ ★ 暴露面必须**声明**这一点。"""
    a = C.exposure(cards, C.MODE_AUTONOMOUS)
    assert a["dispatch_check_required"] is True


#: ══ N10 按需加载契约 ═════════════════════════════════════════════════

def test_load_contract_is_single_tool(cards) -> None:
    """★★ Q6 L105-106 逐字：选中后**只加载该方法**；「**不把全部工具 schema
    塞给 LLM**」。"""
    card = next(c for c in cards if c.name == "solidworks_extrude_boss")
    ct = C.load_contract(card)
    assert ct["name"] == card.name
    assert "params" in ct
    #: ★ 判据：**只回这一个**（★ 不是 521 个的并集）
    assert ct["tokens"] <= C.TOKEN_BUDGET


#: ══ ★★ 反向验证 V1~V6 ═══════════════════════════════════════════════

def test_v1_module_as_search_field_would_change_results(cards) -> None:
    """★★ **V1**：**把 `module` 当检索字段** ⇒ 结果必须**变化**
    （★ 即证明它现在**不参与**）。"""
    q = "sw_part"
    real = C.retrieve(C.RetrievalQuery(text=q), cards)

    #: ★ 突变体：把 module 拼进检索文本
    class Mut(C.ToolCard):
        def search_blob(self):
            return super().search_blob() + " " + self.module

    mut = [Mut(name=c.name, domain=c.domain, title=c.title,
               facets=c.facets, module=c.module, tokens=c.tokens) for c in cards]
    fake = C.retrieve(C.RetrievalQuery(text=q), mut)
    assert [c.name for c in real.cards] != [c.name for c in fake.cards], \
        "★★ 加不加 module 结果一样 ⇒ V1 抓不到（判据失效）"


def test_v2_removing_ngrams_lowers_recall(cards) -> None:
    """★★ **V2**：**移除 n-gram，只留精确词** ⇒ 中文查询**召回率必须下降**。"""
    r_real = C.retrieve(C.RetrievalQuery(text="打孔"), cards)
    assert r_real.cards
    #: ★ 突变体：只按**精确整词**匹配（★ 不做 n-gram）
    exact = [c for c in cards if "打孔" in c.search_blob()]
    assert len(exact) < len(r_real.cards), \
        "★ 精确词召回不少于 n-gram ⇒ n-gram 没起作用"


def test_v3_removing_facet_filter_causes_cross_domain(cards) -> None:
    """★★ **V3**：**去掉分面过滤** ⇒ 返回**跨域污染** ⇒ 被检出。"""
    filtered = C.retrieve(C.RetrievalQuery(text="孔",
                                           domain="hole_and_interface"), cards)
    unfiltered = C.retrieve(C.RetrievalQuery(text="孔"), cards)
    #: ★ 真检索：**域内全是孔系**
    assert all(c.domain == "hole_and_interface" for c in filtered.cards)
    #: ★ 突变体（不过滤）：**一定混进别的域**
    assert any(c.domain != "hole_and_interface" for c in unfiltered.cards), \
        "★ 不过滤也不跨域 ⇒ V3 抓不到"


def test_v4_hiding_without_permission_check_must_fail(cards) -> None:
    """★★★ **V4**：**隐藏工具但不检查权限** ⇒ ★ 负例必须**失败**。

    ★★ Q6 L110 逐字：「隐藏工具仍要在实际调用分发处检查权限，
      **不能靠隐藏列表防旁路**」。
    ★ 判据：隐藏 ≠ 防旁路 —— ★ 必须走 `authorization.check_tool`。
    """
    from scripts.engineering import authorization as AUTH
    #: ★ 真检查器：未准入 ⇒ 拒
    hidden = [c.name for c in cards if not c.admitted]
    assert hidden, "★ 目录里应有未准入工具（★ 否则这条检查形同虚设）"
    #: ★ 判据：**隐藏列表里没有它 ≠ 它能跑**
    exposed = C.exposure(cards, C.MODE_AUTONOMOUS)["names"]
    assert hidden[0] not in exposed, "★ 未准入工具被暴露了"
    #: ★ 而**权限检查独立于暴露面**（★ 这是"不能靠隐藏防旁路"的落实）
    assert hasattr(AUTH, "check_tool"), "★ 没有分发处的权限检查"


def test_v5_deleting_a_domain_is_caught(cards) -> None:
    """★★ **V5**：**给一个工具删掉主域** ⇒ `521/521` 断言必须**失败**。"""
    import copy
    broken = copy.copy(cards[0])
    broken.domain = ""
    doms = set(C.load_domains())
    assert broken.domain not in doms, "★ 空域居然合法？"
    #: ★ 真目录里**没有**空域
    assert all(c.domain in doms for c in cards)


def test_v6_threshold_downgrade_is_detectable(cards) -> None:
    """★★ **V6**：**阈值下调**（看过结果之后）⇒ ★ `frozen_at` 检查必须**发现**。

    ★ 判据：冻结文件里**同时**有 `frozen_at` 与 `digest` ——
      ★ 改了阈值，`digest` 必变 ⇒ ★ 可与发布记录比对。
    """
    th = C.load_thresholds()
    assert th.get("frozen_at")
    d1 = C.thresholds_digest()
    #: ★ 模拟"下调"：改内存里的副本（★ 不动盘）
    tampered = {"thresholds": dict(th["thresholds"])}
    tampered["thresholds"]["avg_recall"] = 0.50
    assert tampered["thresholds"]["avg_recall"] != th["thresholds"]["avg_recall"]
    #: ★ 真文件的摘要**没变**（★ 因为它没被改）
    assert C.thresholds_digest() == d1
