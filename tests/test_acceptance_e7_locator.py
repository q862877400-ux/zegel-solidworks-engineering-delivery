"""★ E7 的 `locator` 判据：占位符不算出处，但真出处绝不能误伤。

## 背景

E7 的负例清单第一条是「**假引用**」。而现有判定器只要求引用「非空 + `resolved=True`」，
而 `resolved` 是**调用方自己声明**的 ⇒ 填 `locator="见上"` + `resolved=True` 就能过。

⇒ 补一条：`locator` 必须像真出处（表/图/条/§/标准号/点分条款号 任一形态）。

## ★ 这条判据的边界（必须一起测，否则会变成误伤）

它只能拦「**明显不是出处**」的占位符，**不能**证明条款真实存在。
所以本文件两侧都测：

- **左侧（该拒的）**：占位符必须被拒
- **右侧（不该拒的）**：各种合法定位形态必须通过 —— 误伤比漏拦更容易让人不信判据
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import pytest  # noqa: E402

from engineering.acceptance.e7_provenance import (  # noqa: E402
    collect_provenance,
    judge_provenance,
    locator_looks_cited,
)
from engineering.acceptance.result import Status  # noqa: E402

REQ = "R-E7"


@pytest.mark.parametrize(
    "loc",
    [
        "GB/T 1804-2000 表1",
        "GB 30871-2022 5.2.3",
        "ISO 2768",
        "JB/T 1234-2010",
        "表1",
        "图3",
        "第5.2.3条",
        "第 12 条",
        "§4.2",
        "Clause 7",
        "Annex A",
        "Appendix B",
        "5.2.3",
        "4.1",
    ],
)
def test_真出处不得误伤(loc: str) -> None:
    """★★ 右侧：这些都必须通过 —— 误伤比漏拦更糟。"""
    ok, why = locator_looks_cited(loc)
    assert ok is True, "★ %r 是合法定位形态，却被拒：%s" % (loc, why)


@pytest.mark.parametrize(
    "loc",
    ["", "  ", "-", "--", "?", "x", "N/A", "na", "none", "null",
     "无", "略", "见上", "见前", "见下", "同上", "同上文", "见附件", "见原文",
     "待补", "待定", "TBD", "TODO", "placeholder"],
)
def test_占位符必须被拒(loc: str) -> None:
    """★★ 左侧：占位符当出处 —— 这就是「假引用」最省事的形态。"""
    ok, why = locator_looks_cited(loc)
    assert ok is False, "★ %r 是占位符，却通过了" % loc
    assert why, "★ 拒绝时必须给理由"


def test_一堆没有定位形态的自由文本也拒() -> None:
    """★ 不是占位符、但也没有任何可指认形态的，同样不算出处。"""
    for loc in ("按规范执行", "see the doc", "厂里说的"):
        ok, _ = locator_looks_cited(loc)
        assert ok is False, "★ %r 没有可指认形态，应拒" % loc


def _obs(locator: str, *, resolved: bool = True):
    return collect_provenance(
        target="plate-rev1",
        claims=({"id": "C1", "text": "板厚 20 mm 满足刚度要求"},),
        citations=(
            {"claim_id": "C1", "locator": locator, "resolved": resolved},
        ),
        outputs={"deflection_mm": 0.03},
        source_kind="standard_clause",
        source_ref="GB/T 1804-2000 表1",
        artifact_version="rev1",
        evidence_version="rev1",
    )


def test_占位符加resolved_true仍判fail() -> None:
    """★★★ 核心伪造手法：`resolved=True` 是自己声明的，占位符照样能声称「解析得到」。"""
    res = judge_provenance(_obs("见上"), requirement_id=REQ)
    assert res.status is Status.FAIL, "★ 占位符 + resolved=True 应判 fail，实得 %s" % (
        res.status.value
    )
    assert "locator" in res.reason or "出处" in res.reason


def test_真出处判pass() -> None:
    """★ 右侧整链：合法 locator ⇒ 仍要能 pass（不能因为加严就永远 fail）。"""
    res = judge_provenance(_obs("GB/T 1804-2000 表1"), requirement_id=REQ)
    assert res.status is Status.PASS, "★ 合法 locator 应判 pass，实得 %s（%s）" % (
        res.status.value,
        res.reason,
    )


def test_未resolved的引用不走这条判据() -> None:
    """★ `resolved=False` 的引用由第 ④ 条（claim 覆盖）负责，不重复判。"""
    obs = collect_provenance(
        target="t",
        claims=({"id": "C1", "text": "x"},),
        citations=({"claim_id": "C1", "locator": "见上", "resolved": False},),
        outputs={"a": 1},
        source_kind="measured",
        source_ref="本机读数",
        artifact_version="v1",
        evidence_version="v1",
    )
    res = judge_provenance(obs, requirement_id=REQ)
    #: claim 没有 resolved 引用 ⇒ 第 ④ 条判 fail，理由应是「没有解析到引用」
    assert res.status is Status.FAIL
    assert "没有解析到引用" in res.reason, "★ 应由覆盖检查负责，实得：%s" % res.reason
