"""★ E2 的「保存重开仍成立」不许由调用方断言 —— 必须比对两次实测尺寸。

## 缺陷（第 40 轮）

`if not v["reopened_ok"]: fail` —— 调用方实参。运行器原来的算法是：

```python
reopened_ok = (solid_body_extent_mm(doc2).get("x_mm")) is not None
```

⇒ 只要**读得到数**就算 True。**重开后又变回 100mm（参数关系没落盘）也算 True** ——
   而那正是 E2 要抓的坏。

## 修法

收 `extent_before_save_mm` / `extent_after_reopen_mm`（`-1` = 没量）：

```
reopened_ok = 两者都量到 and |差| <= reopen_tol_mm（默认 0.01mm）
```

## 本文件钉什么

① 形参里没有 `reopened_ok`
② 两次尺寸一致 ⇒ true
③ **重开后回退**（120→100）⇒ false 并 fail（原算法抓不到的坏）
④ 容差内（0.005mm）算一致；容差可调
⑤ 没量 ⇒ `unknown`（不是 fail）
⑥ 反向：其余判据仍逐条生效
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
    positions_before=((10.0, 10.0),),
    positions_after=((30.0, 10.0),),
    rebuild_errors=0,
    extent_before_save_mm=120.0,
    extent_after_reopen_mm=120.0,
    #: ★ drawing_is_current 本轮**未**推导（理由见 commit）：它需要把这条拆成独立
    #:   check_id，否则 complete 要求修订号会把下游联动的真 fail 吞掉。
    #:   ⇒ 本文件只测重开推导，给它 True 以免挡住其他用例。
    drawing_revision='rev1',
     model_revision='rev1',
)


def _judge(**kw):
    obs = collect_rebuild(**{**_FULL, **kw})
    return obs, judge_rebuild(obs, requirement_id=REQ)


def test_形参里没有_reopened_ok() -> None:
    params = set(inspect.signature(collect_rebuild).parameters)
    assert "reopened_ok" not in params, (
        "★ 形参里又有 reopened_ok ⇒ 调用方声明就能过：%r" % sorted(params)
    )
    assert {"extent_before_save_mm", "extent_after_reopen_mm"} <= params


def test_尺寸一致推成重开成立() -> None:
    obs, res = _judge()
    assert obs.values["reopened_ok"] is True
    assert res.status is Status.PASS


def test_重开后回退必须fail() -> None:
    """★★ 原算法（读得到就算 True）抓不到这种坏 —— 正是 E2 要抓的。"""
    obs, res = _judge(extent_after_reopen_mm=100.0)
    assert obs.values["reopened_ok"] is False
    assert res.status is Status.FAIL, "★ 重开回退应判 fail，实得 %s" % res.status.value
    assert "保存后重开" in res.reason


def test_容差内算一致() -> None:
    obs, _ = _judge(extent_after_reopen_mm=120.005)
    assert obs.values["reopened_ok"] is True, "★ 0.005mm 在默认 0.01 容差内"


def test_容差可调() -> None:
    obs, _ = _judge(extent_after_reopen_mm=120.005, reopen_tol_mm=0.001)
    assert obs.values["reopened_ok"] is False, "★ 收紧容差后应判不一致"


def test_没量尺寸判unknown() -> None:
    obs, res = _judge(extent_before_save_mm=-1.0, extent_after_reopen_mm=-1.0)
    assert obs.complete is False
    assert res.status is Status.UNKNOWN, (
        "★ 没量尺寸应判 unknown，实得 %s" % res.status.value
    )
    assert "保存前" in obs.note or "重开" in obs.note


def test_只量到一边也算没量() -> None:
    obs, res = _judge(extent_after_reopen_mm=-1.0)
    assert obs.complete is False
    assert res.status is Status.UNKNOWN


@pytest.mark.parametrize(
    ("kw", "want"),
    [
        ({"opened_existing": False}, "新建文档重跑"),
        ({"rebuild_errors": 2}, "特征错误"),
        ({"extent_after_reopen_mm": 100.0}, "保存后重开"),
    ],
)
def test_其余判据仍生效(kw, want) -> None:
    args = dict(_FULL)
    args.update(kw)
    _, res = _judge(**args)
    assert res.status is Status.FAIL, "★ %r 应 fail，实得 %s" % (kw, res.status.value)
    assert want in res.reason, "★ 理由应含 %r：%s" % (want, res.reason[:110])
