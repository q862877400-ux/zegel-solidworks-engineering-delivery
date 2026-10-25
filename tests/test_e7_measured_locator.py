"""E7 的 locator 判据：`measured` 证据要认「文件 + 字段」。

## 为什么改（第 64 轮）

`VALID_SOURCES` 里有 `measured`，但 locator 词表只认「表 1 / 图 3 / 第 5 条 / § 2 /
GB 30871 / 5.2」这些**文档形态**。而一条实测结论的自然出处是
`output/e3-feature-tree.json#features` —— 它过不了。

⇒ 结果只能是二选一：编一个「第 3 条」的假 locator（伪造），或者这条证据永远进不了 E7。
⇒ 所以改判据：加一类「仓库相对路径 + 字段标记」。

## 边界（这些测试也钉住它）

- `output/x.json#features` ✓
- `output/x.json → features` ✓
- `output/x.json` ✗ —— 只给文件名等于「去看那个文件」，与「见附件」同类
- `见上` / `待补` ✗ —— 占位符照旧拦
- `表 1` / `第 5 条` / `GB 30871 5.2` ✓ —— 文档形态不受影响
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO))

from engineering.acceptance.e7_provenance import (  # noqa: E402
    VALID_SOURCES,
    collect_provenance,
    judge_provenance,
    locator_looks_cited,
)
from engineering.acceptance.result import Status  # noqa: E402

REQ = "R-E7"


def test_文件加字段被接受() -> None:
    for loc in (
        "output/e3-feature-tree.json#features",
        "output/x.json → features",
        "output/a.yaml::steps.clearance",
        "output/b.md#L10",
    ):
        ok, why = locator_looks_cited(loc)
        assert ok, "★ 文件+字段形态被拒了：%r（%s）" % (loc, why)


def test_只给文件名被拒() -> None:
    for loc in ("output/x.json", "output/e3-feature-tree.json", "output/目录/"):
        ok, why = locator_looks_cited(loc)
        assert not ok, "★ 只给文件名不该算出处：%r" % loc


def test_占位符仍被拒() -> None:
    for loc in ("见上", "待补", "tbd", "无"):
        ok, _ = locator_looks_cited(loc)
        assert not ok, "★ 占位符不该算出处：%r" % loc


def test_文档形态不受影响() -> None:
    for loc in ("表 1", "图 3", "第 5 条", "§ 2", "GB 30871 第 5.2 条", "4.1.3"):
        ok, _ = locator_looks_cited(loc)
        assert ok, "★ 文档形态被误伤了：%r" % loc


def test_measured_是合法来源() -> None:
    assert "measured" in VALID_SOURCES


def _good_obs(claims, cites, outputs=None):
    #: ★ 判据还要求「有计算输出 ⇒ 可复算」。空 outputs 会被判 fail
    #:   （理由「结论没有任何计算输出 ⇒ 无复算依据」）—— 这条也钉在下面。
    return collect_provenance(
        target="t",
        claims=tuple(claims),
        citations=tuple(cites),
        outputs={"E3": {"feature_count": 11}} if outputs is None else outputs,
        source_kind="measured",
        source_ref="output/s3-acceptance.json",
        artifact_version="v1",
        evidence_version="v1",
        version="v1",
    )


def test_实测出处能过判据() -> None:
    """★ 端到端：一条实测结论 + 文件#字段 出处 ⇒ pass。"""
    obs = _good_obs(
        [{"id": "E3", "text": "特征树 11 项"}],
        [{"claim_id": "E3", "locator": "output/s3-acceptance.json#E3.tally", "resolved": True}],
    )
    assert judge_provenance(obs, requirement_id=REQ).status is Status.PASS


def test_没挂出处的结论被拒() -> None:
    """★ R-09 的伪造手法：claims 有、citations 空。"""
    obs = _good_obs([{"id": "E3", "text": "特征树 11 项"}], [])
    res = judge_provenance(obs, requirement_id=REQ)
    assert res.status is Status.FAIL


def test_只给文件名的出处被拒() -> None:
    obs = _good_obs(
        [{"id": "E3", "text": "特征树 11 项"}],
        [{"claim_id": "E3", "locator": "output/s3-acceptance.json", "resolved": True}],
    )
    res = judge_provenance(obs, requirement_id=REQ)
    assert res.status is Status.FAIL, "★ 只给文件名不该算「可指认的出处」"


def test_没有计算输出被拒() -> None:
    """★ 「无复算依据」：claims 与出处都齐，但没有任何计算输出 ⇒ fail。"""
    obs = _good_obs(
        [{"id": "E3", "text": "特征树 11 项"}],
        [{"claim_id": "E3", "locator": "output/s3-acceptance.json#E3.tally", "resolved": True}],
        outputs={},
    )
    res = judge_provenance(obs, requirement_id=REQ)
    assert res.status is Status.FAIL
    assert "复算" in res.reason
