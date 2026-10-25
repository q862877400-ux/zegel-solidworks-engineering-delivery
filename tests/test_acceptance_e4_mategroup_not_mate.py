"""★ 配合文件夹不能冒充配合（第 44 轮真机搭装配时发现的判定器漏洞）。

## 漏洞

`judge_assembly_interference` 的 ② 逐字是 `if not mates:` —— 只判「列表非空」。
而仓库自己的 `collect_mate_feature_summary` **把 `MateGroup` 文件夹也收进列表**
⇒ 零个真实配合时它的长度也是 1 ⇒ ② 被绕过，再配上「干涉 0」就 **判 pass（假绿）**。

★★ 这正是 E4 明令要拒绝的「用聚合量/目录冒充配合」，也是
  「返回值 ≠ 实际结果」在判据层的形态（第 33–41 轮同族）。

## 真机佐证

同一个装配里：

```
· try_mate {'ok': False, 'err': 'AddMate5 失败: type=0, error_status=4', 'mates': 1}
```

`swAddMateError_e` 逐字：**4 = `swAddMateError_IncorrectSelections`**（选择不正确）
⇒ 配合**没建成**；而 `mates` 读成 1，那 1 就是 `MateGroup`。

## 本文件钉什么

① 只有 `MateGroup` 条目 ⇒ **fail**，且理由点名「没有一条带配合对象」
② 有真实配合（`a`/`b` 非空）⇒ 能继续判（干涉 0 ⇒ pass）
③ 空列表 ⇒ 仍是原来那条「没有功能配合」的 fail
④ 真实配合 + 干涉 > 0 ⇒ 仍 fail（③ 判据不被新逻辑挤掉）
⑤ 只有一个组件（配合指向不存在的一侧）—— 仍按现判据走，不静默通过
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import pytest  # noqa: E402
from engineering.acceptance.e4_assembly import (  # noqa: E402
    collect_assembly,
    judge_assembly_interference,
)
from engineering.acceptance.result import Status  # noqa: E402

REQ = "R-E4"


def _judge(mates, *, interference=0, components=("板1-1", "板1-2")):
    obs = collect_assembly(
        target="装配",
        components=components,
        mates=mates,
        target_dof=0,
        interference_count=interference,
        min_clearance_mm=2.0,
        clearance_basis="GB/T 5277 中等装配",
        configuration="默认",
    )
    return judge_assembly_interference(obs, requirement_id=REQ)


_MATEGROUP = ({"name": "Mates", "type": "MateGroup", "depth": 0},)
_REAL = (
    {"a": "板1-1", "b": "板1-2", "kind": "coincident"},
)


def test_只有配合文件夹必须fail() -> None:
    """★★ 核心：零个真实配合时，不能靠 `MateGroup` 通过。"""
    res = _judge(_MATEGROUP)
    assert res.status is Status.FAIL, (
        "★ 只有配合文件夹应判 fail，实得 %s（这就是假绿）" % res.status.value
    )
    assert "没有一条带配合对象" in res.reason, "★ 理由要点名：%s" % res.reason
    assert "MateGroup" in res.reason, "★ 理由要指出典型来源"


def test_配合文件夹加真实配合仍可pass() -> None:
    """★ 不该误伤：文件夹 + 真配合一起给（真机常见），应能继续判。"""
    res = _judge(_MATEGROUP + _REAL)
    assert res.status is Status.PASS, "★ 有真配合时应 pass，实得 %s" % res.status.value


def test_空列表先被采集完整性挡住() -> None:
    """★ 现状：`collect_assembly` 的 `complete` 要求 `mates` 非空
    ⇒ 空列表是 **unknown**（「没采到」），不是 fail（「产物不合格」）。

    ★ 这与第 33 轮的纪律一致：采集缺失不得说成不合格。
      真机上「装配确实零配合」要用非空观测表达（例如采一条 MateGroup 条目），
      那样就会走到下面那条 fail。
    """
    res = _judge(())
    assert res.status is Status.UNKNOWN, (
        "★ 空 mates 应先判 unknown（采集不完整），实得 %s" % res.status.value
    )


def test_零配合的防御分支仍在() -> None:
    """★ 判定器里那条「没有功能配合」的 fail 分支要保留 —— 用构造观测直接测它。

    ★ 为什么要测：它挡住了「靠全固定定位、不写配合」这种产物。
      采集层加了完整性门槛之后，这条分支在正常链路上不可达，
      但它是判据的一部分，不许悄悄消失。
    """
    from engineering.acceptance.result import Observation

    obs = Observation(
        target="装配",
        complete=True,          #: ★ 人为声明采集完整（模拟「确实零配合」的产物）
        values={
            "components": ["板1-1", "板1-2"],
            "mates": [],
            "target_dof": 0,
            "interference_count": 0,
            "min_clearance_mm": 2.0,
            "clearance_basis": "GB/T 5277 中等装配",
            "configuration": "默认",
            "version": "",
        },
    )
    res = judge_assembly_interference(obs, requirement_id=REQ)
    assert res.status is Status.FAIL, "★ 零配合应判 fail，实得 %s" % res.status.value
    assert "没有功能配合" in res.reason, "★ 理由应指出：%s" % res.reason


def test_真配合加干涉仍fail() -> None:
    """★ ③ 干涉判据不能被新逻辑挤掉。"""
    res = _judge(_REAL, interference=3)
    assert res.status is Status.FAIL, "★ 有干涉应 fail，实得 %s" % res.status.value
    assert "干涉" in res.reason


@pytest.mark.parametrize(
    "entry",
    [
        {"a": "", "b": "板1-2", "kind": "coincident"},
        {"a": "板1-1", "b": "", "kind": "coincident"},
        {"a": "", "b": "", "kind": ""},
    ],
)
def test_一侧为空也算没有对象(entry) -> None:
    """★ `a`/`b` 任一为空都不算有对象 —— 半条配合等于没有。"""
    res = _judge((entry,))
    assert res.status is Status.FAIL, "★ %r 应判 fail" % (entry,)
    assert "没有一条带配合对象" in res.reason


def test_重复配合判据仍生效() -> None:
    """★ ① 重复配合判据不能被新逻辑挤掉。"""
    res = _judge(_REAL + _REAL)
    assert res.status is Status.FAIL
    assert "重复配合" in res.reason
