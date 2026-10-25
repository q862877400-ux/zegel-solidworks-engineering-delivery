"""★ E2 的「图纸与模型同修订」是**独立子项**，不许混在主判据里。

## 为什么拆（第 41 轮）

`judge_rebuild` 原本末条是 `if not v["drawing_is_current"]: fail`，而它是调用方布尔。
想推导化时发现一个真张力：

- 首件当前**还没有图** ⇒ 两个修订号都空
- 若把「必须声明修订号」放进 `obs.complete` ⇒ `E2.rebuild` 直接 `unknown`
  ⇒ **把「下游没联动」这个真 fail 吞掉**

⇒ 一个 check_id 装两件互相独立的事，任一件缺数据就污染另一件。
  E4 已遇到同一问题（DOF 读不到 ⇒ 拆 `E4.dof` / `E4.interference`），照同一形态拆。

| check_id | 内容 | 首件当前 |
|---|---|---|
| `E2.rebuild` | 改既有参数后下游联动 + 重开仍成立 | 真结论（fail） |
| `E2.drawing_current` | 图纸修订 == 模型修订 | 还没图 ⇒ **unknown**（如实） |

## 本文件钉什么

① 两个 check_id 各自独立，`E2.rebuild` 不再含图纸判据
② 图纸修订 == 模型修订 ⇒ pass
③ 不同 ⇒ fail（旧图）
④ 任一为空 ⇒ **`unknown`**（还没有图就是这一档，如实）
⑤ **关键**：图纸缺数据时 `E2.rebuild` 仍能给出真结论（这正是拆的理由）
⑥ 采集器不再收 `drawing_is_current` 布尔
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
    judge_rebuild_drawing,
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
)


def _obs(**kw):
    return collect_rebuild(**{**_FULL, **kw})


def test_采集器不再收drawing_is_current布尔() -> None:
    params = set(inspect.signature(collect_rebuild).parameters)
    assert "drawing_is_current" not in params, (
        "★ 形参里又有 drawing_is_current ⇒ 调用方声明就能过：%r" % sorted(params)
    )
    assert {"drawing_revision", "model_revision"} <= params


def test_两个check_id各自独立() -> None:
    obs = _obs(drawing_revision="rev1", model_revision="rev1")
    main = judge_rebuild(obs, requirement_id=REQ)
    draw = judge_rebuild_drawing(obs, requirement_id=REQ)
    assert main.check_id == "E2.rebuild"
    assert draw.check_id == "E2.drawing_current"


def test_修订一致pass() -> None:
    obs = _obs(drawing_revision="rev1", model_revision="rev1")
    assert judge_rebuild_drawing(obs, requirement_id=REQ).status is Status.PASS


def test_修订不同fail() -> None:
    obs = _obs(drawing_revision="rev1", model_revision="rev2")
    res = judge_rebuild_drawing(obs, requirement_id=REQ)
    assert res.status is Status.FAIL, "★ 旧图应判 fail，实得 %s" % res.status.value
    assert "旧图" in res.reason


@pytest.mark.parametrize(
    ("draw", "model"),
    [("", ""), ("rev1", ""), ("", "rev1")],
)
def test_修订号缺失判unknown(draw: str, model: str) -> None:
    """★★ 「还没有图」就是这一档 —— 如实报 unknown，不许当合格。"""
    obs = _obs(drawing_revision=draw, model_revision=model)
    res = judge_rebuild_drawing(obs, requirement_id=REQ)
    assert res.status is Status.UNKNOWN, (
        "★ 缺修订号应判 unknown，实得 %s" % res.status.value
    )
    assert "还没验" in res.reason


def test_图纸缺数据时主判据仍给真结论() -> None:
    """★★★ 这是拆分**核心理由**：图纸没数据不该污染「下游没联动」的真 fail。

    ★ 若这条红了，说明拆得不对（图纸又混回主判据了）。
    """
    obs = _obs(
        positions_after=((10.0, 10.0),),  #: 孔没动 ⇒ 下游未联动
        drawing_revision="",               #: 还没有图
        model_revision="",
    )
    main = judge_rebuild(obs, requirement_id=REQ)
    draw = judge_rebuild_drawing(obs, requirement_id=REQ)
    assert main.status is Status.FAIL, (
        "★ 下游没联动必须仍判 fail，实得 %s（图纸缺数据不该把它变成 unknown）"
        % main.status.value
    )
    assert "下游没联动" in main.reason
    assert draw.status is Status.UNKNOWN, "★ 图纸那一项独立报 unknown"


def test_主判据里不再含图纸判据() -> None:
    """★ 结构断言：防止以后有人把图纸判据又塞回主判据。"""
    src = inspect.getsource(judge_rebuild)
    assert "drawing" not in src.lower(), (
        "★ judge_rebuild 里又出现 drawing 字样 ⇒ 图纸判据混回主判据了"
    )
