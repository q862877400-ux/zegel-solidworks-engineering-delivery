"""★ E1–E7 的三态判据：好输入通过 / 已知坏输入拒绝 / 缺证据 unknown。

判据来源：`specs/349-e1-e7-acceptance/spec.md` 的 SC-001。

★ 每条 E 三态都要成立 —— 只测「好输入通过」等于没测（判定器可能永远返回 pass）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from engineering.acceptance import samples as S  # noqa: E402
from engineering.acceptance.e1_sketch import judge_sketch_constraint  # noqa: E402
from engineering.acceptance.e2_e3_solid import (  # noqa: E402
    judge_feature_tree,
    judge_rebuild,
)
from engineering.acceptance.e4_assembly import judge_assembly  # noqa: E402
from engineering.acceptance.e5_e6_drawing import (  # noqa: E402
    judge_drawing,
    judge_process,
)
from engineering.acceptance.e7_provenance import judge_provenance  # noqa: E402
from engineering.acceptance.result import Status, rollup  # noqa: E402

REQ = "R-1"

#: 判据表：(名字, 判定函数, 样件工厂, 期望状态)
CASES = [
    # ── E1 ──
    ("e1_good", judge_sketch_constraint, S.good_e1, Status.PASS),
    ("e1_bad_dup", judge_sketch_constraint, S.bad_e1_duplicate_relation, Status.FAIL),
    ("e1_bad_fixed", judge_sketch_constraint, S.bad_e1_all_fixed_no_dimension, Status.FAIL),
    ("e1_unknown", judge_sketch_constraint, S.unknown_e1, Status.UNKNOWN),
    # ── E2 ──
    ("e2_good", judge_rebuild, S.good_e2, Status.PASS),
    ("e2_bad_newdoc", judge_rebuild, S.bad_e2_new_document, Status.FAIL),
    ("e2_bad_nodown", judge_rebuild, S.bad_e2_no_downstream, Status.FAIL),
    ("e2_unknown", judge_rebuild, S.unknown_e2, Status.UNKNOWN),
    # ── E3 ──
    ("e3_good", judge_feature_tree, S.good_e3, Status.PASS),
    ("e3_bad_imported", judge_feature_tree, S.bad_e3_imported_solid, Status.FAIL),
    ("e3_bad_dangling", judge_feature_tree, S.bad_e3_dangling, Status.FAIL),
    ("e3_unknown", judge_feature_tree, S.unknown_e3, Status.UNKNOWN),
    # ── E4 ──
    ("e4_good", judge_assembly, S.good_e4, Status.PASS),
    ("e4_bad_dupmate", judge_assembly, S.bad_e4_duplicate_mate, Status.FAIL),
    ("e4_bad_interf", judge_assembly, S.bad_e4_interference, Status.FAIL),
    ("e4_unknown", judge_assembly, S.unknown_e4, Status.UNKNOWN),
    # ── E5 ──
    ("e5_good", judge_drawing, S.good_e5, Status.PASS),
    ("e5_bad_emptyev", judge_drawing, S.bad_e5_empty_evidence, Status.FAIL),
    ("e5_bad_missing", judge_drawing, S.bad_e5_missing_item, Status.FAIL),
    ("e5_bad_stale", judge_drawing, S.bad_e5_stale_drawing, Status.FAIL),
    ("e5_unknown", judge_drawing, S.unknown_e5, Status.UNKNOWN),
    # ── E6 ──
    ("e6_good", judge_process, S.good_e6, Status.PASS),
    ("e6_bad_tool", judge_process, S.bad_e6_tool_unreachable, Status.FAIL),
    ("e6_bad_na", judge_process, S.bad_e6_all_not_applicable, Status.FAIL),
    ("e6_unknown", judge_process, S.unknown_e6, Status.UNKNOWN),
    # ── E7 ──
    ("e7_good", judge_provenance, S.good_e7, Status.PASS),
    ("e7_bad_nocite", judge_provenance, S.bad_e7_no_citations, Status.FAIL),
    ("e7_bad_fakesrc", judge_provenance, S.bad_e7_fake_source, Status.FAIL),
    ("e7_bad_stale", judge_provenance, S.bad_e7_stale_evidence, Status.FAIL),
    ("e7_unknown", judge_provenance, S.unknown_e7, Status.UNKNOWN),
]


@pytest.mark.parametrize("name,judge,factory,want", CASES, ids=[c[0] for c in CASES])
def test_三态判定(name, judge, factory, want) -> None:
    """★ 每条判据都必须给出预期的三态之一。"""
    obs = factory()
    res = judge(obs, requirement_id=REQ)
    assert res.status is want, (
        "★ %s 期望 %s，实得 %s（原因：%s）" % (name, want.value, res.status.value, res.reason)
    )


@pytest.mark.parametrize("name,judge,factory,want", CASES, ids=[c[0] for c in CASES])
def test_每条结果都带齐十一个字段(name, judge, factory, want) -> None:
    """★ FR-008：统一结果必须含 11 个必填字段。"""
    res = judge(factory(), requirement_id=REQ)
    d = res.to_dict()
    for key in (
        "check_id",
        "requirement_id",
        "target",
        "observation_complete",
        "observed",
        "unit",
        "expected",
        "basis",
        "status",
        "reason",
        "evidence",
        "artifact_version",
        "checker_version",
    ):
        assert key in d, "★ %s 的结果少了字段 %r" % (name, key)
    assert d["reason"], "★ %s 没给原因 ⇒ 无法判读" % name


@pytest.mark.parametrize(
    "name,judge,factory,want",
    [c for c in CASES if c[3] is Status.FAIL],
    ids=[c[0] for c in CASES if c[3] is Status.FAIL],
)
def test_坏样件的原因必须指向具体缺陷(name, judge, factory, want) -> None:
    """★ 坏样件不能只说「不合格」—— 原因要能指认是什么问题。"""
    res = judge(factory(), requirement_id=REQ)
    assert len(res.reason) >= 8, "★ %s 的原因太短，读不出缺陷是什么：%r" % (name, res.reason)


def test_unknown_不等于_fail() -> None:
    """★★ 两者必须可区分：unknown = 没测到；fail = 测到了且不合格。"""
    good = judge_sketch_constraint(S.good_e1(), requirement_id=REQ)
    unk = judge_sketch_constraint(S.unknown_e1(), requirement_id=REQ)
    bad = judge_sketch_constraint(S.bad_e1_duplicate_relation(), requirement_id=REQ)
    assert good.status is Status.PASS
    assert unk.status is Status.UNKNOWN
    assert bad.status is Status.FAIL
    assert unk.status is not bad.status


def test_汇总_unknown_使报告不绿() -> None:
    """★ rollup：任一 fail 或任一 unknown 都不绿。"""
    results = [
        judge_sketch_constraint(S.good_e1(), requirement_id=REQ),
        judge_sketch_constraint(S.unknown_e1(), requirement_id=REQ),
    ]
    agg = rollup(results)
    assert agg["ok"] is False
    assert agg["unknown"] == 1


def test_汇总_全绿才绿() -> None:
    """★ 全是 pass / not_applicable 时才算绿。"""
    results = [judge_sketch_constraint(S.good_e1(), requirement_id=REQ)]
    agg = rollup(results)
    assert agg["ok"] is True
    assert agg["pass"] == 1


def test_七条判据都有三态覆盖() -> None:
    """★ 每条 E 都必须有 pass / fail / unknown 三种样件。"""
    for e in ("e1", "e2", "e3", "e4", "e5", "e6", "e7"):
        got = {c[3] for c in CASES if c[0].startswith(e + "_")}
        assert Status.PASS in got, "★ %s 没有 pass 样件" % e
        assert Status.FAIL in got, "★ %s 没有 fail 样件" % e
        assert Status.UNKNOWN in got, "★ %s 没有 unknown 样件" % e
