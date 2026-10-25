"""★ 补 `E2.hole_readback` 与 `E3.tree` 的**失败/unknown 分支**端到端覆盖。

## 缺口（第 31 轮核实）

流水线两组样件覆盖到的 `(check_id, status)` 组合：

| check_id | 已覆盖 | 缺 |
|---|---|---|
| `E2.hole_readback` | pass · unknown | **fail** |
| `E3.tree` | pass | **fail** · unknown |
| `E1.dof` | pass | fail · unknown |

★ `E2.hole_readback` 的 fail 正是**真机现在命中的分支**
（第 31 轮真机：要求 4 孔 · 量到 4 孔 ⇒ fail），却从没在流水线里测过。

## 为什么这比「多写几条测试」重要

`E2.hole_readback` 有三条独立的失败路径，各自对应一种伪造手法：

| 失败路径 | 挡住的伪造手法 |
|---|---|
| 孔数不符 | 「四个 φ6 换成两个 φ12，体积一样」 |
| 孔径/孔位超差 | 「位置标错」 |
| 孔型不符 | 「用普通孔冒充沉头孔」 |

若只测 pass 与 unknown，**这三条防线一条都没被验证过**。

## 手法

用**真实** `collect_hole_readback` + `judge_hole_readback`（不手工拼 `CheckResult`），
逐条逼近每个分支，再用 `build_report` 汇总，断言：
① 落在 `E2` 的 `failed` 里（不在 `unassigned`）② 每条的理由指认出具体缺陷。
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import pytest  # noqa: E402

from engineering.acceptance.e2_e3_solid import (  # noqa: E402
    HOLE_TYPES,
    collect_feature_tree,
    collect_hole_readback,
    judge_feature_tree,
    judge_hole_readback,
)
from engineering.acceptance.report import build_report  # noqa: E402
from engineering.acceptance.result import Status  # noqa: E402

REQ = "R-E"

#: 期望：四个 ⌀6 通孔
_REQUESTED = tuple(
    {"id": "H%d" % i, "kind": "through", "diameter_mm": 6.0,
     "position_mm": [x, y, 0.0]}
    for i, (x, y) in enumerate(
        [(10.0, 10.0), (90.0, 10.0), (10.0, 50.0), (90.0, 50.0)], 1
    )
)


def _measured(holes):
    return {"holes": list(holes), "envelope_mm": [100.0, 60.0, 20.0]}


def _holes(n: int, *, kind="through", dia=6.0, shift=0.0):
    base = [(10.0, 10.0), (90.0, 10.0), (10.0, 50.0), (90.0, 50.0)]
    out = []
    for x, y in base[:n]:
        #: ★ 必须有 xis：alidate_hole_positions 用轴线算孔位距离，
        #:   缺轴线会让距离算成 inf（真机量测里恒有 xis=[0,0,1]）
        h = {"diameter_mm": dia, "position_mm": [x + shift, y, 0.0],
             "axis": [0.0, 0.0, 1.0]}
        if kind is not None:
            h["kind"] = kind
        out.append(h)
    return out


def _judge(holes, *, requested=_REQUESTED):
    obs = collect_hole_readback(
        target="板1", requested=requested, measured=_measured(holes)
    )
    return judge_hole_readback(obs, requirement_id=REQ)


# ── 三条失败路径 ──────────────────────────────────────────────────────


def test_孔数不符必须fail() -> None:
    """★★ 挡「四个 φ6 换成两个 φ12，总切除体积一样」——判定器 docstring 点名的伪造。"""
    res = _judge(_holes(2, dia=12.0))
    assert res.status is Status.FAIL, "★ 孔数不符应 fail，实得 %s" % res.status.value
    assert "孔数" in res.reason or "数量" in res.reason, "★ 理由应指认孔数：%s" % res.reason


def test_孔径超差必须fail() -> None:
    res = _judge(_holes(4, dia=8.0))
    assert res.status is Status.FAIL, "★ 孔径 8 而要求 6 应 fail，实得 %s" % res.status.value
    assert "孔径" in res.reason or "超差" in res.reason


def test_孔位超差必须fail() -> None:
    res = _judge(_holes(4, shift=5.0))
    assert res.status is Status.FAIL, "★ 孔位偏 5mm 应 fail，实得 %s" % res.status.value
    assert "孔位" in res.reason or "超差" in res.reason


def test_孔型不符必须fail() -> None:
    """★ 要求 `through` 而实测 `blind` ⇒ fail（不许用普通孔冒充）。"""
    res = _judge(_holes(4, kind="blind"))
    assert res.status is Status.FAIL, "★ 孔型不符应 fail，实得 %s" % res.status.value
    assert "孔型" in res.reason


def test_要求里的孔型是表外值必须fail() -> None:
    """★★ 要求侧的孔型必须是封闭词表内的词；表外值 ⇒ fail（不许自造词）。"""
    req = tuple(dict(h, kind="25/1") for h in _REQUESTED)
    res = _judge(_holes(4), requested=req)
    assert res.status is Status.FAIL
    assert "允许词表" in res.reason, "★ 理由应指出表外值：%s" % res.reason


def test_孔型词表是封闭的() -> None:
    """★ 词表内容固定 —— 加词要连带改判据与测试，不许悄悄扩。"""
    assert HOLE_TYPES == ("through", "blind", "counterbore", "countersink", "threaded")


def test_实测没有孔型时判unknown不是pass() -> None:
    """★ unknown ≠ pass：B-Rep 给不出孔型时不许判绿。"""
    res = _judge(_holes(4, kind=None))
    assert res.status is Status.UNKNOWN, "★ 没孔型应 unknown，实得 %s" % res.status.value


# ── E3.tree 的失败分支 ───────────────────────────────────────────────


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
    return judge_feature_tree(collect_feature_tree(**base), requirement_id=REQ)


@pytest.mark.parametrize(
    ("kw", "want"),
    [
        ({"native_features": 0, "imported_solids": 1}, "导入"),
        ({"dangling_refs": 2}, "悬空"),
        ({"errors": 1}, "错误"),
    ],
)
def test_E3的三种fail分支(kw, want) -> None:
    """★ `E3.tree` 的 fail 分支之前只测过 pass —— 逐条点名。"""
    res = _tree(**kw)
    assert res.status is Status.FAIL, "★ %r 应 fail，实得 %s" % (kw, res.status.value)
    assert want in res.reason, "★ 理由应含 %r：%s" % (want, res.reason)


# ── 汇总层：都不得掉进 unassigned ─────────────────────────────────────


def test_孔型读回的失败落到E2下() -> None:
    checks = [
        _judge(_holes(2, dia=12.0)),   # 孔数不符
        _judge(_holes(4, kind="blind")),  # 孔型不符
        _tree(errors=1),               # E3.tree 失败
    ]
    rep = build_report(checks)
    assert rep["unassigned"] == [], "★ 有检查掉进 unassigned：%r" % (rep["unassigned"],)
    assert "E2.hole_readback" in rep["criteria"]["E2"]["failed"]
    assert "E3.tree" in rep["criteria"]["E3"]["failed"]


def test_量测缺轴线时判fail而不是静默通过() -> None:
    """★ 第 31 轮写测试时发现的健壮性边界。

    `sw_review.validate_hole_positions` 用**轴线**算孔位距离；若量测里没有 `axis`，
    距离算成 `inf` ⇒ 孔位超差 ⇒ 判 fail。

    ★ 结论「fail」是**安全方向**（宁可误拒不可误放），所以不改 `sw_review`；
      但要在测试里钉住它，免得哪天真有人以为 `inf` 是被处理过的数。
    ★ 真机量测里恒有 `axis`（`output/s3-acceptance.json` 里是 `[0,0,1]`）。
    """
    holes = [
        {"diameter_mm": 6.0, "position_mm": [10.0, 10.0, 0.0], "kind": "through"}
    ] * 4
    res = _judge(holes)
    assert res.status is Status.FAIL, (
        "★ 缺 axis 时应判 fail（安全方向），实得 %s" % res.status.value
    )
    assert "inf" in res.reason or "超差" in res.reason, (
        "★ 理由应暴露孔位算不出来：%s" % res.reason
    )
