"""★ E6 必须能拒绝「删除必需检查」—— 第 35 轮补的判据。

## 缺口

E5 有 `required_items`（少一项 ⇒ fail），**E6 没有对应概念**。
实测确认：只要给**一项**适用检查（如「刀具可达」）就能 pass，
即使同时缺壁厚余量 / 孔深刀具 / 加工基准 / 装夹空间 ——
而 `ENGINEERING-PATH` 点名 E6 必须能拒绝「**删除必需检查**」。

## 修法与它的关键取舍

新增形参 `required_checks`，**必要项由调用方声明**（不发明任何要求）。
★★ `required_checks` 为空 ⇒ 判 **`unknown`**，不是 pass：

★ 若「默认空就跳过这条检查」，调用方少传一个参数就能绕过这条负例
  ⇒ 判据形同虚设。**不声明 ≠ 声明为空**（与 `missing_confirmations` 同一口径）。

## 两侧都要钉

只测「少一项会 fail」不够 —— 还要证明**必要项齐、检查全过时仍然 pass**，
否则这次加严会把判据变钝。
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import pytest  # noqa: E402

from engineering.acceptance.e5_e6_drawing import (  # noqa: E402
    collect_process,
    judge_process,
)
from engineering.acceptance.result import Status  # noqa: E402

REQ = "R-E"

_FULL = (
    {"name": "刀具可达", "applicable": True, "passed": True, "value": "⌀6 通孔"},
    {"name": "壁厚余量", "applicable": True, "passed": True, "value": "8 mm"},
)
_REQUIRED = ("刀具可达", "壁厚余量")


def _judge(checks, required=_REQUIRED):
    obs = collect_process(
        target="板1工艺",
        route="machined",
        checks=checks,
        verified_scope=("machined",),
        required_checks=required,
    )
    return obs, judge_process(obs, requirement_id=REQ)


# ── 新判据：必要项 ───────────────────────────────────────────────────


def test_缺一项必要检查必须fail() -> None:
    """★★ 核心：挡「删除必需检查」。"""
    _, res = _judge(_FULL[:1])
    assert res.status is Status.FAIL, "★ 缺一项必要检查应 fail，实得 %s" % res.status.value
    assert "必要工艺检查" in res.reason, "★ 理由应指认缺项：%s" % res.reason
    assert "壁厚余量" in res.reason, "★ 应点名缺的那一项"


def test_没声明必要项必须unknown() -> None:
    """★★ 空 `required_checks` ⇒ `unknown`：不声明 ≠ 合格。

    ★ 若这里判 pass，调用方少传一个参数就绕过了整条判据。
    """
    obs, res = _judge(_FULL, required=())
    assert obs.complete is False, "★ 没声明必要项应标采集不完整"
    assert res.status is Status.UNKNOWN, (
        "★ 没声明必要项应判 unknown，实得 %s" % res.status.value
    )
    assert "required_checks" in obs.note or "必要检查项" in obs.note


def test_缺多项时全部点名() -> None:
    _, res = _judge(
        ({"name": "刀具可达", "applicable": True, "passed": True, "value": None},),
        required=("刀具可达", "壁厚余量", "加工基准"),
    )
    assert res.status is Status.FAIL
    assert "2 项" in res.reason, "★ 应报缺 2 项：%s" % res.reason


# ── 反向：加严不能把判据变钝 ─────────────────────────────────────────


def test_必要项齐全且全过仍然pass() -> None:
    """★★ 防「一律 fail」式的假加严。"""
    obs, res = _judge(_FULL)
    assert obs.complete is True
    assert res.status is Status.PASS, "★ 必要项齐、全过应 pass，实得 %s" % res.status.value


def test_适用项不过仍fail() -> None:
    obs, res = _judge((
        {"name": "刀具可达", "applicable": True, "passed": False, "value": "⌀2 深 40"},
        {"name": "壁厚余量", "applicable": True, "passed": True, "value": "8 mm"},
    ))
    assert res.status is Status.FAIL
    assert "未过" in res.reason


def test_全标不适用仍fail() -> None:
    """★ 「删除必需检查」的姐妹手法：把检查全标成不适用。"""
    obs, res = _judge((
        {"name": "刀具可达", "applicable": False, "passed": True, "value": None},
        {"name": "壁厚余量", "applicable": False, "passed": True, "value": None},
    ))
    assert res.status is Status.FAIL
    assert "不适用" in res.reason or "适用" in res.reason


def test_工艺路线不在已验证范围仍fail() -> None:
    """★ 既有判据不能被新判据挤掉（顺序问题会让后面的判据永不生效）。"""
    obs = collect_process(
        target="板1工艺", route="翻砂", checks=_FULL,
        verified_scope=("machined",), required_checks=_REQUIRED,
    )
    res = judge_process(obs, requirement_id=REQ)
    assert res.status is Status.FAIL
    assert "已验证范围" in res.reason, "★ 路线越界的判据应先生效：%s" % res.reason


# ── 与 E5 的对称性 ───────────────────────────────────────────────────


@pytest.mark.parametrize("field", ["required_items", "required_checks"])
def test_E5与E6都有必要项概念(field: str) -> None:
    """★ E5 用 `required_items`、E6 用 `required_checks` —— 两边都必须有。

    ★ 这条是**结构断言**：它防的是「以后又出现一边有、一边没有」。
    """
    import inspect

    from engineering.acceptance import e5_e6_drawing as m

    src = inspect.getsource(m)
    assert field in src, "★ 缺 %s 的概念" % field
