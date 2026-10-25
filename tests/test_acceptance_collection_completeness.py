"""★ 采集层不得把「没取到」说成「不合格」。

## 本文件钉的两条缺陷（第 33 轮修）

| # | 输入 | 修之前 | 修之后 |
|---|---|---|---|
| ① | `requested` 非空、`measured={}` | **fail**（「B-Rep 里有 0 个孔」） | `unknown` |
| ② | `native_features=-1`（读不出的哨兵） | **fail**（「没有任何原生特征」） | `unknown` |

★ 误判 **fail** 比误判 **pass** 更隐蔽：它看起来像「发现了问题」，于是没人去查采集。
  `ENGINEERING-PATH` 要求「采集器与判定器分开」—— 意思正是
  **采集失败的结论是「没测到」，不是「不合格」**。

## ★★ 两侧都要钉

只测「该 unknown 的变 unknown」还不够 —— 那可能是靠「一律 unknown」蒙对的。
必须同时证明**真的 0 孔 / 真的 0 原生特征仍然判 fail**，
否则这次修复会把判据变钝（那比原缺陷更坏）。
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import pytest  # noqa: E402

from engineering.acceptance.e2_e3_solid import (  # noqa: E402
    collect_feature_tree,
    collect_hole_readback,
    judge_feature_tree,
    judge_hole_readback,
)
from engineering.acceptance.result import Status  # noqa: E402

REQ = "R-E"

_REQUESTED = tuple(
    {"id": "H%d" % i, "kind": "through", "diameter_mm": 6.0,
     "position_mm": [x, y, 0.0]}
    for i, (x, y) in enumerate(
        [(10.0, 10.0), (90.0, 10.0), (10.0, 50.0), (90.0, 50.0)], 1
    )
)


def _hole(measured):
    obs = collect_hole_readback(target="板1", requested=_REQUESTED, measured=measured)
    return obs, judge_hole_readback(obs, requirement_id=REQ)


def _tree(**kw):
    base = dict(
        target="板1",
        feature_count=11,
        native_features=6,
        imported_solids=0,
        dangling_refs=0,
        errors=0,
        warnings=0,
        feature_count_before_edit=11,
    )
    base.update(kw)
    obs = collect_feature_tree(**base)
    return obs, judge_feature_tree(obs, requirement_id=REQ)


# ── ① 孔量测 ─────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "measured",
    [
        {},                                    #: 完全没量
        {"holes": [], "errors": ["面读失败"]},   #: 报了错又没孔
    ],
)
def test_没量过孔时必须unknown(measured) -> None:
    """★★ 修之前这两条都判 fail（「B-Rep 里有 0 个孔」）—— 误判。"""
    obs, res = _hole(measured)
    assert obs.complete is False, "★ 采集应标不完整"
    assert res.status is Status.UNKNOWN, (
        "★ 没量过应判 unknown，修之前是 fail（实得 %s）" % res.status.value
    )


def test_真的没有孔仍必须fail() -> None:
    """★★ 反向：零件真的没孔（无错）⇒ 采集完整 ⇒ 判 fail（需求要 4 个）。

    ★ 这条防「一律 unknown」式的假修复。
    """
    obs, res = _hole({"holes": [], "errors": []})
    assert obs.complete is True, "★ 没报错就是采集完整"
    assert res.status is Status.FAIL, "★ 真 0 孔应判 fail，实得 %s" % res.status.value
    assert "数量不符" in res.reason


def test_量到四个孔仍必须pass() -> None:
    """★ 全绿路径不能被这次改动弄坏。"""
    holes = [
        {"diameter_mm": 6.0, "position_mm": [x, y, 0.0], "axis": [0.0, 0.0, 1.0],
         "kind": "through"}
        for x, y in [(10.0, 10.0), (90.0, 10.0), (10.0, 50.0), (90.0, 50.0)]
    ]
    obs, res = _hole({"holes": holes, "errors": []})
    assert obs.complete is True
    assert res.status is Status.PASS, "★ 四个孔对得上应 pass，实得 %s" % res.status.value


# ── ② 特征树 ─────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "field",
    ["native_features", "imported_solids", "dangling_refs", "feature_count"],
)
def test_计数为负时必须unknown(field: str) -> None:
    """★★ 本仓惯用 `-1` 表示「读不出」（`open_doc_count` / `count_sketch_dimensions`）。

    ★ 修之前 `native_features=-1` 判 fail（「没有任何原生特征」）—— 把读不出说成零。
    """
    kw = {field: -1}
    if field == "feature_count":
        kw = {"feature_count": -1}
    obs, res = _tree(**kw)
    assert obs.complete is False, "★ %s=-1 应标不完整" % field
    assert res.status is Status.UNKNOWN, (
        "★ %s=-1 应判 unknown，实得 %s" % (field, res.status.value)
    )


def test_真的一个原生特征都没有仍必须fail() -> None:
    """★★ 反向：`native_features=0` 是**读得出**的零 ⇒ 采集完整 ⇒ fail。"""
    obs, res = _tree(native_features=0, imported_solids=1)
    assert obs.complete is True
    assert res.status is Status.FAIL, "★ 真 0 原生应判 fail，实得 %s" % res.status.value


def test_特征树全绿仍pass() -> None:
    obs, res = _tree()
    assert obs.complete is True
    assert res.status is Status.PASS


def test_采集不完整时note说清原因() -> None:
    """★ 不完整要能看出是「零」还是「读不出」—— 否则诊断又得猜。"""
    obs_zero, _ = _tree(feature_count=0)
    assert "特征数为 0" in obs_zero.note, "★ 零与读不出必须分开报：%r" % obs_zero.note
    obs_neg, _ = _tree(native_features=-1)
    assert "读不出" in obs_neg.note, "★ 应指出是读不出：%r" % obs_neg.note
