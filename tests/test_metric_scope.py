"""★ 口径注册表的契约测试（★ 含负例 —— 负例是门禁有效的唯一证明，事实 62）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tests/test_metric_scope.py
# 定位:   规格 206 的 T0 验收（SC-5）：口径必须结构化、必须有「不算什么」、顺序必须可复现。
# 依据:   `tools/metric_scope.py` · `docs/known-facts.md` 事实 517（三条定则）。
# 官方依据: 不适用（本项目内部工具）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import metric_scope as ms                                              # noqa: E402


def test_every_scope_declares_what_is_not_counted():
    """★ 每条口径都必须写明「不算什么」（★ 事实 517 定则二）。"""
    for s in ms.SCOPES:
        assert s.not_counted, "口径 %s 没写「不算什么」" % s.key
        assert all(str(x).strip() for x in s.not_counted)
        assert s.ordering.strip(), "口径 %s 没写顺序声明" % s.key
        assert s.denominator.strip(), "口径 %s 没写分母" % s.key


def test_scope_keys_are_unique():
    keys = [s.key for s in ms.SCOPES]
    assert len(keys) == len(set(keys)), "口径 key 重复: %s" % keys


def test_scopes_declare_incomparability():
    """★★ 每条口径至少声明一个「不可比」对象 —— 并排报数正是我犯过的错。"""
    for s in ms.SCOPES:
        assert s.not_comparable_with, "口径 %s 没声明与什么不可比" % s.key


# ── ★ 负例：缺关键字段的口径必须【构造期就抛】────────────────────────────
def _kwargs(**over):
    base = dict(key="k", question="q", unit="任务", denominator="d",
                normalization="n", counts_as_hit="h", not_counted=("x",),
                ordering="按 (-score, name)", corpus="c")
    base.update(over)
    return base


def test_negative_empty_not_counted_is_rejected():
    """★ 负例 1：`not_counted` 为空 ⇒ 必须抛（★ 否则「不算什么」就成了可选项）。"""
    with pytest.raises(ValueError, match="不算什么"):
        ms.MetricScope(**_kwargs(not_counted=()))


def test_negative_blank_ordering_is_rejected():
    """★ 负例 2：`ordering` 为空白 ⇒ 必须抛（★ 事实 517 定则三）。"""
    with pytest.raises(ValueError, match="顺序声明"):
        ms.MetricScope(**_kwargs(ordering="   "))


def test_negative_blank_denominator_is_rejected():
    """★ 负例 3：`denominator` 为空 ⇒ 必须抛（★ 分母不明则百分比无意义）。"""
    with pytest.raises(ValueError, match="分母"):
        ms.MetricScope(**_kwargs(denominator=""))


def test_negative_blank_entry_inside_not_counted_is_rejected():
    """★ 负例 4：`not_counted` 里有空条目 ⇒ 必须抛（★ 占位不算声明）。"""
    with pytest.raises(ValueError, match="空条目"):
        ms.MetricScope(**_kwargs(not_counted=("合法的一条", "  ")))


def test_positive_minimal_scope_is_accepted():
    """★ 正例：字段齐备（哪怕很简）⇒ 必须通过（★ 证明上面的负例是判据，不是永远失败）。"""
    s = ms.MetricScope(**_kwargs())
    assert s.key == "k" and s.block().count("不算") >= 1


def test_stable_topk_is_deterministic_on_ties():
    """★★ 同分时必须按名字码点升序钉死（★ 支线 C5 的事故形态：从 set 里取元素）。"""
    rows = [(1.0, "b"), (1.0, "a"), (1.0, "c"), (0.5, "z")]
    got = [n for _s, n in ms.stable_topk(rows, k=3)]
    assert got == ["a", "b", "c"], got
    #: ★ 与输入顺序无关 —— 打乱后结果相同
    import random
    shuffled = rows[:]
    random.Random(7).shuffle(shuffled)
    assert [n for _s, n in ms.stable_topk(shuffled, k=3)] == got


def test_block_for_unknown_key_raises():
    """★ 未登记的口径取块必须抛（★ 不许凭记忆报数）。"""
    with pytest.raises(KeyError):
        ms.block_for("不存在的口径")


def test_dump_shape():
    d = ms.dump()
    assert d["n_scopes"] == len(ms.SCOPES)
    assert all("not_counted" in s and s["not_counted"] for s in d["scopes"])
