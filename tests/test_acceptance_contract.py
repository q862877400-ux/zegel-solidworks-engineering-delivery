"""★ 采集器 / 判定器 的接口契约。

判据来源：`specs/349-e1-e7-acceptance/spec.md` 的 FR-001～FR-009。

## 为什么需要这个文件

`docs/ENGINEERING-PATH.md` 第四节要求「采集器从实际产物取数，判定器对冻结要求判断」。
如果两者混在一起，「我已经检查过」与「真的取到了数」在代码上无法区分。

本文件把三条结构性要求钉成断言：

① **采集器不判断** —— 它返回 `Observation`，里面没有 `status` 字段
② **判定器不取数** —— 它只接受 `Observation`，签名里没有取数参数
③ **观测不完整 ⇒ 必为 unknown** —— 不许在没取到数时判 pass 或 fail
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from engineering.acceptance import samples as S  # noqa: E402
from engineering.acceptance.e1_sketch import (  # noqa: E402
    collect_sketch_constraint,
    judge_sketch_constraint,
)
from engineering.acceptance.e2_e3_solid import (  # noqa: E402
    collect_feature_tree,
    collect_rebuild,
    judge_feature_tree,
    judge_rebuild,
)
from engineering.acceptance.e4_assembly import (  # noqa: E402
    collect_assembly,
    judge_assembly,
)
from engineering.acceptance.e5_e6_drawing import (  # noqa: E402
    collect_drawing,
    collect_process,
    judge_drawing,
    judge_process,
)
from engineering.acceptance.e7_provenance import (  # noqa: E402
    collect_provenance,
    judge_provenance,
)
from engineering.acceptance.result import (  # noqa: E402
    CheckResult,
    Observation,
    Status,
    rollup,
)

REQ = "R-contract"

#: 七对采集器 / 判定器
PAIRS = [
    ("E1", collect_sketch_constraint, judge_sketch_constraint),
    ("E2", collect_rebuild, judge_rebuild),
    ("E3", collect_feature_tree, judge_feature_tree),
    ("E4", collect_assembly, judge_assembly),
    ("E5", collect_drawing, judge_drawing),
    ("E6", collect_process, judge_process),
    ("E7", collect_provenance, judge_provenance),
]


@pytest.mark.parametrize("name,collector,judge", PAIRS, ids=[p[0] for p in PAIRS])
def test_采集器返回_Observation_不含状态(name, collector, judge) -> None:
    """★ ① 采集器只装数，不判断。

    `Observation` 没有 `status` 字段 —— 采集器想说「合格」在类型上就做不到。
    """
    assert "status" not in [f for f in Observation.__dataclass_fields__], (
        "★ Observation 不该有 status 字段 —— 那会让采集器自己下判断"
    )


@pytest.mark.parametrize("name,collector,judge", PAIRS, ids=[p[0] for p in PAIRS])
def test_判定器只接受_Observation(name, collector, judge) -> None:
    """★ ② 判定器不取数：第一个位置参数必须是 `Observation`。"""
    sig = inspect.signature(judge)
    params = list(sig.parameters.values())
    assert params, "★ 判定器没有参数"
    first = params[0]
    assert first.name == "obs", "★ 判定器第一参数应叫 `obs`，实为 %r" % first.name
    ann = str(first.annotation)
    assert "Observation" in ann, (
        "★ 判定器第一参数的类型注解应是 Observation，实为 %r" % ann
    )


@pytest.mark.parametrize("name,collector,judge", PAIRS, ids=[p[0] for p in PAIRS])
def test_判定器返回_CheckResult(name, collector, judge) -> None:
    """★ 判定器必须返回统一结果结构。"""
    obs = _sample_for(name)
    res = judge(obs, requirement_id=REQ)
    assert isinstance(res, CheckResult), "★ %s 的判定器没返回 CheckResult" % name
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
        assert key in d, "★ %s 缺字段 %r" % (name, key)


def _sample_for(name: str) -> Observation:
    return {
        "E1": S.good_e1,
        "E2": S.good_e2,
        "E3": S.good_e3,
        "E4": S.good_e4,
        "E5": S.good_e5,
        "E6": S.good_e6,
        "E7": S.good_e7,
    }[name]()


def test_观测不完整时构造_CheckResult_会被拒() -> None:
    """★ ③ 不变式：`observation_complete=False` 却给 pass/fail ⇒ 构造即抛。

    这不是靠判定器自觉 —— 是 `CheckResult.__post_init__` 的硬约束。
    """
    for bad_status in (Status.PASS, Status.FAIL, Status.NOT_APPLICABLE):
        with pytest.raises(ValueError):
            CheckResult(
                check_id="X",
                requirement_id=REQ,
                target="t",
                observation_complete=False,
                status=bad_status,
            )


def test_观测完整时可以给任意合法状态() -> None:
    """★ 对照组：完整观测下四值都允许。"""
    for st in (Status.PASS, Status.FAIL, Status.UNKNOWN, Status.NOT_APPLICABLE):
        r = CheckResult(
            check_id="X",
            requirement_id=REQ,
            target="t",
            observation_complete=True,
            status=st,
        )
        assert r.status is st


def test_status_必须是枚举不接受裸字符串() -> None:
    """★ FR-009：禁止把其他非空字符串当 true。"""
    with pytest.raises(TypeError):
        CheckResult(
            check_id="X",
            requirement_id=REQ,
            target="t",
            observation_complete=True,
            status="pass",  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "raw,want",
    [
        ("pass", Status.PASS),
        ("PASS", Status.PASS),
        ("ok", Status.PASS),
        ("true", Status.PASS),
        ("是", Status.PASS),
        ("fail", Status.FAIL),
        ("false", Status.FAIL),
        ("no", Status.FAIL),
        ("unknown", Status.UNKNOWN),
        ("", Status.UNKNOWN),
        ("随便什么", Status.UNKNOWN),
        (True, Status.PASS),
        (False, Status.FAIL),
        ("n/a", Status.NOT_APPLICABLE),
        ("不适用", Status.NOT_APPLICABLE),
    ],
)
def test_外部verdict显式映射(raw, want) -> None:
    """★ `Status.of` 把外部 verdict 显式映射，表外一律 unknown（不猜成 pass）。"""
    assert Status.of(raw) is want


def test_只有pass和不适用让报告变绿() -> None:
    """★ 判据：`is_green` 只对 pass / not_applicable 为真。"""
    assert Status.PASS.is_green is True
    assert Status.NOT_APPLICABLE.is_green is True
    assert Status.FAIL.is_green is False
    assert Status.UNKNOWN.is_green is False


def test_rollup_空结果不绿() -> None:
    """★ 空结果集不得判绿（防「什么都没测却通过」）。"""
    assert rollup([])["ok"] is False


def test_rollup_计数正确() -> None:
    results = [
        CheckResult("A", REQ, "t", True, status=Status.PASS),
        CheckResult("B", REQ, "t", True, status=Status.FAIL),
        CheckResult("C", REQ, "t", True, status=Status.UNKNOWN),
        CheckResult("D", REQ, "t", True, status=Status.NOT_APPLICABLE),
    ]
    agg = rollup(results)
    assert agg["total"] == 4
    assert agg["pass"] == 1
    assert agg["fail"] == 1
    assert agg["unknown"] == 1
    assert agg["not_applicable"] == 1
    assert agg["failed_ids"] == ["B"]
    assert agg["unknown_ids"] == ["C"]
    assert agg["ok"] is False
