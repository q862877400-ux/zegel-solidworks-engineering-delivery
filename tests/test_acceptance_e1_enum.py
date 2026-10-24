"""★ E1 的枚举采集路径（真机唯一可得的信号）。

判据来源：`specs/350-first-part-delivery/source-verification.md`

## 为什么单独一个文件

官方源核查发现：`ISketch.GetConstrainedStatus()` 返回的是
**`swConstrainedStatus_e` 状态枚举**，**不是数值自由度**。

⇒ E1 有两条采集路径，能力不同：

| 路径 | 信号 | 真机可取？ |
|---|---|---|
| 枚举 | `solver_status_int` | ✅ 可取 |
| 数值 | `entities` / `relations` / `dimensions` | ❌ 取不到，只能合成 |

本文件钉住枚举路径的判定，**并钉住「有枚举就不用数值」** ——
否则真机上会拿合成数据去覆盖权威信号。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from engineering.acceptance.e1_sketch import (  # noqa: E402
    collect_sketch_constraint,
    judge_sketch_constraint,
)
from engineering.acceptance.result import Status  # noqa: E402

REQ = "R-enum"


def _obs(
    status_int,
    *,
    intentional_dof=0,
    entities=0,
    relations=(),
    dimensions=(),
    driving_dimensions=1,
):
    """★ 构造一个「只有枚举」的观测（真机的典型形态）。

    ★ `driving_dimensions` 默认 **1** —— 因为「状态 3 + 零驱动尺寸」是**全固定**，
      按 E1 应判 fail（见 `test_全固定且零驱动尺寸必须判fail`）。
      要构造那种情形就显式传 0。
    """
    return collect_sketch_constraint(
        target="sketch-under-test",
        entities=entities,
        relations=relations,
        dimensions=dimensions,
        intentional_dof=intentional_dof,
        solver_state="from_api",
        solver_status_int=status_int,
        driving_dimensions=driving_dimensions,
    )


#: (status_int, 期望状态, 说明) —— 取值与官方表逐字对应
CASES = [
    (3, Status.PASS, "swFullyConstrained ⇒ 满足 E1"),
    (2, Status.FAIL, "swUnderConstrained ⇒ 未满足"),
    (4, Status.FAIL, "swOverConstrained ⇒ 约束过头"),
    (5, Status.FAIL, "swNoSolution"),
    (6, Status.FAIL, "swInvalidSolution"),
    (1, Status.UNKNOWN, "swUnknownConstraint ⇒ 判不了，不猜"),
    (7, Status.UNKNOWN, "swAutosolveOff ⇒ 状态没意义"),
    (99, Status.FAIL, "表外取值 ⇒ 不猜成 pass"),
    (0, Status.FAIL, "0 不在表里 ⇒ 不猜成 pass"),
]


@pytest.mark.parametrize("status_int,want,why", CASES, ids=["%s" % c[0] for c in CASES])
def test_枚举路径判定(status_int, want, why) -> None:
    """★ 每个官方取值都必须给出确定结论。"""
    res = judge_sketch_constraint(_obs(status_int), requirement_id=REQ)
    assert res.status is want, (
        "★ status=%d 期望 %s，实得 %s（%s）"
        % (status_int, want.value, res.status.value, why)
    )


def test_完全定义是唯一能让枚举路径判pass的值() -> None:
    """★★ 防「宽松通过」：只有 3 能 pass（2 要另看有意自由度）。"""
    passing = [
        s
        for s, want, _ in CASES
        if judge_sketch_constraint(_obs(s), requirement_id=REQ).status is Status.PASS
    ]
    assert passing == [3], "★ 只有 swFullyConstrained 该 pass，实得 %r" % passing


def test_全固定且零驱动尺寸必须判fail() -> None:
    """★★★ 这是本判据最容易漏的一个洞，真机实测出来的。

    `tools/probe_s3_autodim_why_fully_defined.py` 量到：
    **把草图每一段都加 `sgFIXED`、一条驱动尺寸都不加，`GetConstrainedStatus()` 也回 3。**

    ⇒ 只看枚举，「全固定」与「尺寸驱动」分不开。
      而 E1 的负例明令包含「全部固定却无驱动参数」。
    """
    res = judge_sketch_constraint(_obs(3, driving_dimensions=0), requirement_id=REQ)
    assert res.status is Status.FAIL, "★ 全固定零尺寸必须 fail，实得 %s" % res.status.value
    assert "全部固定" in res.reason or "驱动尺寸" in res.reason


def test_状态3但没数过尺寸必须判unknown() -> None:
    """★★ 「没数过」不等于「合格」—— unknown 不得判绿。"""
    res = judge_sketch_constraint(
        _obs(3, driving_dimensions=None), requirement_id=REQ
    )
    assert res.status is Status.UNKNOWN, "★ 没数过驱动尺寸应 unknown，实得 %s" % res.status.value
    assert "没数过" in res.reason


def test_欠定义加有意自由度算符合设计意图() -> None:
    """★ 2 + 已声明有意保留自由度 ⇒ pass（不是缺陷）。"""
    res = judge_sketch_constraint(_obs(2, intentional_dof=1), requirement_id=REQ)
    assert res.status is Status.PASS
    assert "有意保留" in res.reason


def test_有意自由度不能救过定义() -> None:
    """★★ 4（过定义）不因「有意保留自由度」而通过 —— 那两者不是一回事。"""
    res = judge_sketch_constraint(_obs(4, intentional_dof=1), requirement_id=REQ)
    assert res.status is Status.FAIL


def test_有枚举时不信数值() -> None:
    """★★ 有权威枚举就只判枚举。

    ★ 真机上拿不到 `entities/relations/dimensions`；若判定器在
      「枚举说 pass 但数值算出来不符」时改用数值，就会让合成数据
      覆盖真实信号。
    """
    #: 枚举说完全定义（3），但数值明显算不出 DOF=0 —— 结论必须跟枚举
    obs = _obs(3, entities=4, relations=("a",), dimensions=())
    res = judge_sketch_constraint(obs, requirement_id=REQ)
    assert res.status is Status.PASS, "★ 有枚举时应只信枚举，实得 %s" % res.status.value


def test_有枚举时重复关系不再单独判死() -> None:
    """★ 有枚举 ⇒ 走枚举分支；重复关系是**数值路径**的伪造检测。

    ⚠ 这不是放宽：真机上「关系是否重复」由判定器拿不到原始清单，
      所以那条检测只在合成/诊断场景生效。真机靠枚举。
    """
    obs = _obs(3, entities=4, relations=("same",) * 8, dimensions=())
    assert judge_sketch_constraint(obs, requirement_id=REQ).status is Status.PASS


def test_没有枚举时才走数值路径() -> None:
    """★ 无 `solver_status_int` ⇒ 退回数值判定（既有行为不变）。"""
    obs = collect_sketch_constraint(
        target="t",
        entities=4,
        relations=("h1", "h2", "v1", "v2", "c1", "c2"),
        dimensions=("d1", "d2"),
        intentional_dof=0,
        solver_state="fully_defined",
    )
    assert judge_sketch_constraint(obs, requirement_id=REQ).status is Status.PASS


def test_既无枚举又无数值判unknown() -> None:
    """★ 两条路径都没数据 ⇒ unknown，不是 fail 也不是 pass。"""
    obs = collect_sketch_constraint(
        target="t",
        entities=0,
        relations=(),
        dimensions=(),
        solver_state="",
    )
    res = judge_sketch_constraint(obs, requirement_id=REQ)
    assert res.status is Status.UNKNOWN


def test_枚举值非整数判unknown() -> None:
    """★ 拿到非整数 ⇒ 判不了，不猜。"""
    obs = _obs("not-an-int")
    res = judge_sketch_constraint(obs, requirement_id=REQ)
    assert res.status is Status.UNKNOWN


def test_枚举判定带出原始值() -> None:
    """★ 结果里要留原始枚举值，供报告指认。"""
    res = judge_sketch_constraint(_obs(3), requirement_id=REQ)
    assert res.observed["solver_status"] == 3
    assert res.expected["solver_status"] == 3


def test_全固定时的证据里带出驱动尺寸0() -> None:
    """★ 判 fail 时也要把读数留全，供报告指认。"""
    res = judge_sketch_constraint(_obs(3, driving_dimensions=0), requirement_id=REQ)
    assert res.observed["driving_dimensions"] == 0
    assert res.expected["driving_dimensions"] == ">=1"


def test_官方取值表归口在sw_sketch_status() -> None:
    """★ 取值表只有一个家：`scripts/sw_sketch_status.py`。

    ⚠ 曾经 `sw_sketch_relations.py` 也复制了一份，两处对「查得到/查不到」
      说法相反。本测试钉住归口。
    """
    from sw_sketch_status import CONSTRAINED_STATUS

    assert len(CONSTRAINED_STATUS) == 7, "★ 官方表是 7 个成员"
    assert CONSTRAINED_STATUS[3] == "swFullyConstrained"
    assert CONSTRAINED_STATUS[2] == "swUnderConstrained"
    assert CONSTRAINED_STATUS[4] == "swOverConstrained"
