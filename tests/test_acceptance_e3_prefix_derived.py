"""★ E3 的「前序可编辑」不许由调用方断言 —— 必须从两次实测推导。

## 缺陷（第 39 轮审计）

`judge_feature_tree` 末条：

```python
if not v["editable_prefix_verified"]:   # fail
```

而它是 `collect_feature_tree(..., editable_prefix_verified=True)` 的实参 ——
与第 38 轮 E2 的 `downstream_linked` 同一类：**声明了就算数**。

真机运行器当时的代理是「包围盒变大」：

```python
editable_prefix_verified=bool(changed and (bbox_after or 0) > (bbox_before or 0))
```

★ 这个代理**不够**：包围盒变大只说明几何变了，**没证明特征树没坏**
（可能掉了特征、或引入了重建错误）。

## 修法

新增 `feature_count_before_edit: int = -1`（`-1` = 没量），复用既有 `errors`（改后错误数）：

```
editable_prefix_verified = before >= 0 and feature_count == before and errors == 0
```

`complete` 要求 `before >= 0`。

★ 为什么「特征数不变 + 错误为 0」正是 E3 要的「可编辑」：
  「改前序草图/参数后，后续特征**仍在**且**能重建**」——掉特征或报错都直接否掉它。

## 本文件钉什么

① 形参里没有 `editable_prefix_verified`
② 特征数不变 + 无错误 ⇒ true
③ **掉特征** ⇒ false（这是原代理抓不到的那种坏）
④ 改后有错误 ⇒ false
⑤ 没量改前特征数 ⇒ `unknown`（不是 fail）
⑥ 反向：全绿仍 pass；其余判据（导入实体 / 悬空 / 错误）仍逐条生效
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import pytest  # noqa: E402

from engineering.acceptance.e2_e3_solid import (  # noqa: E402
    collect_feature_tree,
    judge_feature_tree,
)
from engineering.acceptance.result import Status  # noqa: E402

REQ = "R-E3"
_FULL = dict(
    target="板1副本",
    feature_count=15,
    native_features=10,
    imported_solids=0,
    dangling_refs=0,
    errors=0,
    warnings=0,
)


def _judge(**kw):
    obs = collect_feature_tree(**{**_FULL, **kw})
    return obs, judge_feature_tree(obs, requirement_id=REQ)


def test_形参里没有_editable_prefix_verified() -> None:
    """★★ 核心：不许再用布尔断言 —— 必须是推导。"""
    params = set(inspect.signature(collect_feature_tree).parameters)
    assert "editable_prefix_verified" not in params, (
        "★ 形参里又有 editable_prefix_verified ⇒ 调用方声明就能过：%r" % sorted(params)
    )
    assert "feature_count_before_edit" in params


def test_特征数不变且无错误推成可编辑() -> None:
    obs, res = _judge(feature_count_before_edit=15)
    assert obs.values["editable_prefix_verified"] is True
    assert res.status is Status.PASS


def test_掉特征推成不可编辑并fail() -> None:
    """★★ 原代理（包围盒变大）**抓不到**这种坏：几何变了但特征掉了两个。"""
    obs, res = _judge(feature_count=13, feature_count_before_edit=15)
    assert obs.values["editable_prefix_verified"] is False
    assert res.status is Status.FAIL, "★ 掉特征应判 fail，实得 %s" % res.status.value
    assert "可编辑性未证" in res.reason


def test_改后有错误推成不可编辑() -> None:
    obs, res = _judge(errors=2, feature_count_before_edit=15)
    assert obs.values["editable_prefix_verified"] is False
    assert res.status is Status.FAIL
    #: ★ 错误判据排在前面 ⇒ 先因「有错误」失败（更具体的原因）
    assert "错误" in res.reason


def test_没量改前特征数判unknown() -> None:
    """★★ 没量过 ≠ 不可编辑 —— 判 fail 是编事实。"""
    obs, res = _judge()
    assert obs.complete is False
    assert res.status is Status.UNKNOWN, (
        "★ 没量改前特征数应判 unknown，实得 %s" % res.status.value
    )


def test_改前特征数为负的其它值也算没量() -> None:
    for bad in (-2, -99):
        obs, res = _judge(feature_count_before_edit=bad)
        assert obs.complete is False, "★ %d 应算没量" % bad
        assert res.status is Status.UNKNOWN


def test_全绿仍然pass() -> None:
    obs, res = _judge(feature_count_before_edit=15)
    assert res.status is Status.PASS


@pytest.mark.parametrize(
    ("kw", "want"),
    [
        ({"native_features": 0, "imported_solids": 1}, "导入"),
        ({"dangling_refs": 2}, "悬空"),
        ({"errors": 1}, "错误"),
    ],
)
def test_其余判据仍生效(kw, want) -> None:
    """★ 推导化之后，别的判据不能被挤掉。"""
    args = {"feature_count_before_edit": 15}
    args.update(kw)
    _, res = _judge(**args)
    assert res.status is Status.FAIL, "★ %r 应 fail，实得 %s" % (kw, res.status.value)
    assert want in res.reason, "★ 理由应含 %r：%s" % (want, res.reason[:110])
