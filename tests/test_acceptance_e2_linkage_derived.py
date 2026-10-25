"""★ E2 的「下游联动」不许由调用方断言 —— 必须从实测孔位推导。

## 缺陷（第 38 轮审计）

`judge_rebuild` 的五条判据全是调用方给的布尔。其中 ③ 是 E2 的核心：

```python
if not v["downstream_linked"]:   # fail
```

而 `downstream_linked` 原本是 `collect_rebuild(..., downstream_linked=True)` 的实参
⇒ **任何调用方声明 True 就能让 E2 通过，不需要任何实测**。

这与 `AGENTS.md`「采集器从实际产物取数」直接冲突，也是
「返回值 ≠ 实际结果」在采集层的又一形态（第 33/35/36/37 轮同族）。

## 修法

`collect_rebuild` 改为收**实测孔位**（改前/改后各一组），自己比：

| 输入 | `downstream_linked` | 判定 |
|---|---|---|
| 有一对位移 > 0.1mm | True | 可继续判（其余项满足则 pass） |
| 全部没动 | False | **fail** |
| 没给位置 | 采集不完整 | **unknown** |

## 本文件钉什么

① 传布尔已经不可能 —— 形参里没有 `downstream_linked`
② 位移 > 容差 ⇒ 联动为真（`values` 里读得到）
③ 位移 0 ⇒ 联动为假 ⇒ 判 fail
④ 没给位置 ⇒ unknown（**不是** fail：没量过 ≠ 没联动）
⑤ 位置数量对不上 ⇒ unknown（配不了对就不能比）
⑥ 反向：全绿路径仍然 pass
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import pytest  # noqa: E402
from engineering.acceptance.e2_e3_solid import (  # noqa: E402
    collect_rebuild,
    judge_rebuild,
)
from engineering.acceptance.result import Status  # noqa: E402

REQ = "R-E2"
_FULL = dict(
    target="板1副本",
    opened_existing=True,
    changed_params=("w",),
    rebuild_errors=0,
    extent_before_save_mm=120.0,
    extent_after_reopen_mm=120.0,

    drawing_is_current=True,
)


def _judge(**kw):
    obs = collect_rebuild(**{**_FULL, **kw})
    return obs, judge_rebuild(obs, requirement_id=REQ)


# ── ① 布尔已被移除 ───────────────────────────────────────────────────


def test_形参里没有_downstream_linked() -> None:
    """★★ 核心：不许再用布尔断言 —— 它必须是**推导**出来的。"""
    params = set(inspect.signature(collect_rebuild).parameters)
    assert "downstream_linked" not in params, (
        "★ 形参里又有 downstream_linked ⇒ 调用方声明就能过：%r" % sorted(params)
    )
    assert "positions_before" in params and "positions_after" in params


# ── ②③ 位移推导 ─────────────────────────────────────────────────────


def test_有位移推成联动() -> None:
    obs, res = _judge(
        positions_before=((10.0, 10.0), (90.0, 10.0)),
        positions_after=((30.0, 10.0), (110.0, 10.0)),
    )
    assert obs.values["downstream_linked"] is True
    assert obs.values["shifts_mm"] == [20.0, 20.0], (
        "★ 位移量要记进 values：%r" % (obs.values["shifts_mm"],)
    )
    assert res.status is Status.PASS


def test_零位移推成未联动并fail() -> None:
    """★★ E2 的核心负例：板变宽了，孔没动。"""
    obs, res = _judge(
        positions_before=((10.0, 10.0), (90.0, 10.0)),
        positions_after=((10.0, 10.0), (90.0, 10.0)),
    )
    assert obs.values["downstream_linked"] is False
    assert res.status is Status.FAIL, "★ 零位移应判 fail，实得 %s" % res.status.value
    assert "下游没联动" in res.reason


@pytest.mark.parametrize("shift", [0.05, 0.1])
def test_位移不超过容差算没动(shift: float) -> None:
    """★ 容差口径：`> tol` 才算动了（`tol` 默认 0.1mm）。"""
    obs, _ = _judge(
        positions_before=((10.0, 10.0),),
        positions_after=((10.0 + shift, 10.0),),
    )
    assert obs.values["downstream_linked"] is False


def test_容差可调() -> None:
    obs, _ = _judge(
        positions_before=((10.0, 10.0),),
        positions_after=((10.05, 10.0),),
        position_tol_mm=0.01,
    )
    assert obs.values["downstream_linked"] is True, "★ 收紧容差后 0.05mm 应算动了"


# ── ④ 没给位置 ───────────────────────────────────────────────────────


def test_没给位置判unknown不是fail() -> None:
    """★★ 没量过 ≠ 没联动 —— 判 fail 是编事实。"""
    obs, res = _judge()
    assert obs.complete is False
    assert res.status is Status.UNKNOWN, (
        "★ 没给位置应判 unknown，实得 %s" % res.status.value
    )
    #: ★ 钉语义：note 要说清「缺什么」和「因此无法判哪件事」
    assert "孔位" in obs.note, "★ note 应指出缺孔位：%r" % obs.note
    assert "无法判" in obs.note, "★ note 应说清无法判什么：%r" % obs.note


def test_位置数量对不上判unknown() -> None:
    """★ 配不了对就不能比 —— 也不许只比前 N 个。"""
    obs, res = _judge(
        positions_before=((10.0, 10.0), (90.0, 10.0)),
        positions_after=((30.0, 10.0),),
    )
    assert obs.complete is False
    assert res.status is Status.UNKNOWN


# ── ⑤ 反向：其余判据与全绿路径不受影响 ───────────────────────────────


def test_全绿仍然pass() -> None:
    obs, res = _judge(
        positions_before=((10.0, 10.0),),
        positions_after=((30.0, 10.0),),
    )
    assert res.status is Status.PASS


@pytest.mark.parametrize(
    ("kw", "want"),
    [
        ({"opened_existing": False}, "新建文档重跑"),
        ({"rebuild_errors": 2}, "特征错误"),
        (
            {"extent_before_save_mm": 120.0, "extent_after_reopen_mm": 100.0},
            "保存后重开",
        ),
        ({"drawing_is_current": False}, "图纸"),
    ],
)
def test_其余四条判据仍生效(kw, want) -> None:
    """★ 联动改由推导之后，别的判据不能被挤掉。"""
    args = {"positions_before": ((10.0, 10.0),), "positions_after": ((30.0, 10.0),)}
    args.update(kw)
    _, res = _judge(**args)
    assert res.status is Status.FAIL, "★ %r 应 fail，实得 %s" % (kw, res.status.value)
    assert want in res.reason, "★ 理由应含 %r：%s" % (want, res.reason[:110])
