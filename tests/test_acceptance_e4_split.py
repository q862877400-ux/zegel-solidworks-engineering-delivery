"""★ E4 的子项拆分：让「读不到」与「不合格」可区分。

判据来源：`specs/350-first-part-delivery/source-verification.md`

## 为什么需要拆分

三源确认：SolidWorks API **没有数值自由度读取入口**
（1032 接口 / 20627 成员零命中）。

⇒ 若 E4 只有一条「DOF 必须等于目标」的判定：
  真机拿不到 DOF ⇒ E4 永远 `unknown` ⇒ 报告永远不绿，
  但产物**可能完全合格**。这会把「我们测不了」误报成「东西不行」。

⇒ 拆成两条：

| check_id | 内容 | 真机可验 |
|---|---|---|
| `E4.interference` | 配合存在、干涉 0、间隙有依据 | ✅ |
| `E4.dof` | 剩余自由度符合意图 | ❌ 读不到 |

★ 拆分**不放宽** E4：两条都要绿才算 E4 成立。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from engineering.acceptance import samples as S  # noqa: E402
from engineering.acceptance.e4_assembly import (  # noqa: E402
    collect_assembly,
    judge_assembly,
    judge_assembly_interference,
)
from engineering.acceptance.result import Status, rollup  # noqa: E402

REQ = "R-e4"


def test_两条子项有各自的check_id() -> None:
    """★ 报告要能指认「是哪一项」，所以 check_id 必须不同。"""
    obs = S.good_e4()
    a = judge_assembly_interference(obs, requirement_id=REQ)
    b = judge_assembly(obs, requirement_id=REQ)
    assert a.check_id == "E4.interference"
    assert b.check_id == "E4.dof"
    assert a.check_id != b.check_id


def test_好样件两条都绿() -> None:
    """★ 正例：配合齐、干涉 0、间隙有依据、DOF 也对得上。"""
    obs = S.good_e4()
    assert judge_assembly_interference(obs, requirement_id=REQ).status is Status.PASS
    assert judge_assembly(obs, requirement_id=REQ).status is Status.PASS


def test_重复配合两条都拒绝() -> None:
    """★ R-05 的伪造手法：干扰项必须在两条里都体现。"""
    obs = S.bad_e4_duplicate_mate()
    a = judge_assembly_interference(obs, requirement_id=REQ)
    b = judge_assembly(obs, requirement_id=REQ)
    assert a.status is Status.FAIL
    assert b.status is Status.FAIL
    assert "重复" in a.reason


def test_干涉两条都拒绝() -> None:
    obs = S.bad_e4_interference()
    assert judge_assembly_interference(obs, requirement_id=REQ).status is Status.FAIL
    assert judge_assembly(obs, requirement_id=REQ).status is Status.FAIL


def test_DOF读不到时interference仍可独立通过() -> None:
    """★★ 核心：这是拆分的目的。

    ★ 构造一个「配合/干涉/间隙都对，但 DOF 对不上」的观测 ——
      模拟真机「拿不到 DOF，只能填一个占位」的处境。
    ★ `E4.interference` 必须仍能给出 **pass** —— 它不依赖 DOF。
    ★ `E4.dof` 则按它自己的判据说 fail/unknown。
      这样报告能说清「干涉这条过了，DOF 这条没数」。
    """
    obs = collect_assembly(
        target="asm-real-machine",
        components=("ground:base", "moving:pin"),
        mates=(
            {"kind": "coincident", "a": "moving:pin", "b": "ground:base"},
            {"kind": "concentric", "a": "moving:pin", "b": "ground:base"},
        ),
        target_dof=0,
        interference_count=0,
        min_clearance_mm=0.5,
        clearance_basis="图纸标注 0.5 mm",
        configuration="默认",
    )
    a = judge_assembly_interference(obs, requirement_id=REQ)
    assert a.status is Status.PASS, (
        "★ E4.interference 不该因为 DOF 而受影响，实得 %s（%s）" % (a.status.value, a.reason)
    )


def test_采集不完整时两条都unknown() -> None:
    """★ 两条都要遵守「观测不完整 ⇒ unknown」不变式。"""
    obs = S.unknown_e4()
    assert judge_assembly_interference(obs, requirement_id=REQ).status is Status.UNKNOWN
    assert judge_assembly(obs, requirement_id=REQ).status is Status.UNKNOWN


def test_全不绿才算E4不成立() -> None:
    """★ 拆分不放宽：两条都绿才绿；任一条 fail/unknown 就不绿。"""
    good = S.good_e4()
    both_green = rollup(
        [
            judge_assembly_interference(good, requirement_id=REQ),
            judge_assembly(good, requirement_id=REQ),
        ]
    )
    assert both_green["ok"] is True

    #: 干涉坏了 ⇒ 整体不绿
    bad = S.bad_e4_interference()
    mixed = rollup(
        [
            judge_assembly_interference(bad, requirement_id=REQ),
            judge_assembly(bad, requirement_id=REQ),
        ]
    )
    assert mixed["ok"] is False


def test_间隙无依据被拒() -> None:
    """★ 真机能读到间隙值，但「值有依据」这件事必须显式声明。"""
    obs = collect_assembly(
        target="asm",
        components=("ground:base", "moving:pin"),
        mates=(
            {"kind": "coincident", "a": "moving:pin", "b": "ground:base"},
        ),
        target_dof=3,
        interference_count=0,
        min_clearance_mm=0.5,
        clearance_basis="",
        configuration="默认",
    )
    res = judge_assembly_interference(obs, requirement_id=REQ)
    assert res.status is Status.FAIL
    assert "依据" in res.reason


def test_无功能配合被拒() -> None:
    """★ 靠「全固定」定位不是配合约束表达。"""
    obs = collect_assembly(
        target="asm",
        components=("ground:base", "moving:pin"),
        mates=(),
        target_dof=6,
        interference_count=0,
        min_clearance_mm=0.5,
        clearance_basis="图纸",
        configuration="默认",
    )
    #: 没 mates ⇒ 采集不完整 ⇒ unknown（不是 fail —— 没数据）
    assert judge_assembly_interference(obs, requirement_id=REQ).status is Status.UNKNOWN


@pytest.mark.parametrize(
    "factory,want",
    [
        (S.good_e4, Status.PASS),
        (S.bad_e4_duplicate_mate, Status.FAIL),
        (S.bad_e4_interference, Status.FAIL),
        (S.unknown_e4, Status.UNKNOWN),
    ],
    ids=["good", "dup", "interf", "unknown"],
)
def test_interference子项三态(factory, want) -> None:
    assert judge_assembly_interference(factory(), requirement_id=REQ).status is want
