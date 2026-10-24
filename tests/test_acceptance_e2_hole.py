"""★ E2 子项：孔型/孔位逐项回读 —— 不许用聚合量代替。

判据来源：`docs/ENGINEERING-PATH.md` 第四节 E2，及
`specs/350-first-part-delivery/s3-prep.md`。

## 为什么单列一条

「四个 φ6 孔」换成「两个 φ12 孔」，**总切除体积一样**，但需求是四个孔。
任何用聚合量（总体积、总切除量、孔数×面积）代替逐项核对的判据都会放过它。

## 复用既有能力（铁律 1）

孔位与孔径复用 `scripts/sw_review.py:validate_hole_positions` —— 它逐孔给
「孔径误差 / 孔位误差 / 是否通过」。

★ 但它的 docstring **自己声明**未覆盖孔型：
  「盲孔深度、通孔状态和沉头类型必须继续使用特征参数回读」
⇒ 本判据补的正是那一项；补不上时回 `unknown`，不假装通过。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from engineering.acceptance.e2_e3_solid import (  # noqa: E402
    HOLE_TYPES,
    collect_hole_readback,
    judge_hole_readback,
)
from engineering.acceptance.result import Status  # noqa: E402

REQ = "R-hole"


def _req(n: int = 4, kind: str = "through", dia: float = 6.0) -> tuple:
    """★ 需求：n 个孔，等距 20 mm，距边 10 mm。"""
    return tuple(
        {
            "id": "h%d" % (i + 1),
            "kind": kind,
            "diameter_mm": dia,
            "position_mm": [10.0 + i * 20.0, 10.0, 0.0],
        }
        for i in range(n)
    )


def _meas(
    n: int = 4, dia: float = 6.0, kind: str | None = None, shift: float = 0.0
) -> dict:
    """★ B-Rep 实测（`collect_geometry_measurements` 的形状）。"""
    holes = []
    for i in range(n):
        h = {
            "diameter_mm": dia,
            "position_mm": [10.0 + i * 20.0 + shift, 10.0, 0.0],
            "axis": [0.0, 0.0, 1.0],
        }
        if kind is not None:
            h["kind"] = kind
        holes.append(h)
    return {"holes": holes}


def _judge(requested, measured):
    obs = collect_hole_readback(target="plate", requested=requested, measured=measured)
    return judge_hole_readback(obs, requirement_id=REQ)


# ────────────────── 通过 ──────────────────


def test_孔数孔径孔位孔型全对时通过() -> None:
    res = _judge(_req(), _meas(kind="through"))
    assert res.status is Status.PASS
    assert res.check_id == "E2.hole_readback"


# ────────────────── ★ 聚合量代替 ──────────────────


def test_数量不对时拒绝即使总体积相同() -> None:
    """★★ 核心：两个 φ12 的总切除面积 ≈ 四个 φ6。

    φ12 单孔面积 = π·36；两个 = 72π
    φ6 单孔面积 = π·9；四个 = 36π
    ⚠ 严格说体积不同（2 倍），但**数量**这一条独立成立 ——
      本测试要钉的是「不靠体积那种聚合量判断」。
    """
    res = _judge(_req(4, dia=6.0), _meas(2, dia=12.0))
    assert res.status is Status.FAIL
    assert "数量不符" in res.reason


def test_孔数少一个也拒绝() -> None:
    res = _judge(_req(4), _meas(3, kind="through"))
    assert res.status is Status.FAIL


def test_孔数多一个也拒绝() -> None:
    res = _judge(_req(4), _meas(5, kind="through"))
    assert res.status is Status.FAIL


# ────────────────── 孔径 / 孔位 ──────────────────


def test_孔径超差被拒() -> None:
    res = _judge(_req(4, dia=6.0), _meas(4, dia=8.0, kind="through"))
    assert res.status is Status.FAIL
    assert "孔径" in res.reason or "孔位" in res.reason


def test_孔位偏移超差被拒() -> None:
    res = _judge(_req(4), _meas(4, kind="through", shift=0.5))
    assert res.status is Status.FAIL
    assert "孔位误差" in res.reason


def test_容差内的小偏移通过() -> None:
    res = _judge(_req(4), _meas(4, kind="through", shift=0.02))
    assert res.status is Status.PASS


# ────────────────── 孔型 ──────────────────


def test_孔型不符被拒() -> None:
    res = _judge(_req(4, kind="through"), _meas(4, kind="blind"))
    assert res.status is Status.FAIL
    assert "孔型" in res.reason
    assert "blind" in res.reason


def test_孔型给不出时判unknown不是pass() -> None:
    """★★ 这是最重要的一条：**没测到**不等于**合格**。

    `sw_review.validate_hole_positions` 的 docstring 自己写着孔型不在它覆盖范围。
    ⇒ B-Rep 不给 kind 时，本判据必须回 `unknown`。
    """
    res = _judge(_req(4), _meas(4, kind=None))
    assert res.status is Status.UNKNOWN, (
        "★ 拿不到孔型时不得判 pass，实得 %s" % res.status.value
    )
    assert "孔型" in res.reason


def test_要求里的孔型不在词表时被拒() -> None:
    """★ 封闭词表：表外孔型不算「已识别」。"""
    req = (
        {
            "id": "h1",
            "kind": "magic_hole",
            "diameter_mm": 6.0,
            "position_mm": [10.0, 10.0, 0.0],
        },
    )
    res = _judge(req, _meas(1, kind="magic_hole"))
    assert res.status is Status.FAIL
    assert "词表" in res.reason


def test_孔型词表覆盖五种常见孔() -> None:
    assert set(HOLE_TYPES) == {
        "through",
        "blind",
        "counterbore",
        "countersink",
        "threaded",
    }


@pytest.mark.parametrize("kind", HOLE_TYPES, ids=list(HOLE_TYPES))
def test_每种允许孔型都能通过(kind) -> None:
    res = _judge(_req(2, kind=kind), _meas(2, kind=kind))
    assert res.status is Status.PASS, "★ %r 应能通过，实得 %s" % (kind, res.status.value)


# ────────────────── 结构 ──────────────────


def test_没有要求孔清单时unknown() -> None:
    obs = collect_hole_readback(target="plate", requested=(), measured=_meas(0))
    assert judge_hole_readback(obs, requirement_id=REQ).status is Status.UNKNOWN


def test_结果带出逐孔明细() -> None:
    """★ 报告要能指认是哪个孔、差多少。"""
    res = _judge(_req(4), _meas(4, kind="through", shift=0.5))
    assert res.observed["count"] >= 1
    assert res.observed["failed"]
