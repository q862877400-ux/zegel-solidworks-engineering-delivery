"""★ `count_sketch_dimensions` 的契约：`-1` 与 `0` 必须分开。

## 为什么这条重要

E1 的判定器现在要求：状态 3（全约束）时必须再核 `driving_dimensions`：

| 值 | 结论 |
|---|---|
| `>= 1` | pass（尺寸在驱动） |
| `== 0` | **fail**（全固定，不是尺寸驱动） |
| `None` | **unknown**（没数过） |

⇒ 如果 `count_sketch_dimensions` 在「数不到」时错回 `0`，
  调用方就会把「没测到」当成「全固定」⇒ **误判成不合格**（比误判成合格好，但仍错）。
反过来说，如果它在「确实是 0 个」时回 `-1`，就会把「真全固定」说成「没测」。

★ 所以这个函数必须能区分两种「零」。

真机依据：`tools/probe_s3_e1_real_machine.py` 实测 ——
矩形草图（无尺寸）→ 回 **0**；全固定后 → 仍回 **0**（确实没有驱动尺寸）。
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import pytest

import sw_sketch_dimensions as D  # noqa: E402


class _DD:
    """★ 一个显示尺寸；`GetNext2` 串成链。"""

    def __init__(self, nxt=None) -> None:
        self._next = nxt

    def GetNext2(self):  # noqa: N802
        return self._next


class _Feat:
    def __init__(self, first=None) -> None:
        self._first = first

    def GetFirstDisplayDimension(self):  # noqa: N802
        return self._first


def _patch(monkeypatch, names, feats):
    """★ 替身要照 `get_com_member` 的**正式语义**：有实参就传，无实参**先无参调一次**。

    ⚠ 第一版只 `getattr` 不调用 ⇒ `GetNext2` 回的是**方法对象**（真值）
      ⇒ 被当成成员一直循环，计数错。这是本测试自己踩到的坑。
    """
    monkeypatch.setattr(D, "feature_names", lambda model: names)

    def _gcm(obj, name, *a):
        if name == "FeatureByName" and a:
            return feats.get(a[0])
        val = getattr(obj, name, None)
        if val is None:
            return None
        if a:
            return val(*a)
        #: ★ 无实参：COM 成员「取可能等于调」
        return val() if callable(val) else val

    monkeypatch.setattr(D, "get_com_member", _gcm)


def test_一个草图两个尺寸回2(monkeypatch) -> None:
    #: 两个尺寸 = 两个 _DD 节点（链尾 None）
    chain = _DD(_DD(None))
    _patch(monkeypatch, ["草图1"], {"草图1": _Feat(chain)})
    assert D.count_sketch_dimensions(object()) == 2


def test_草图零尺寸回0而不是负一(monkeypatch) -> None:
    """★★ 关键：**确实是 0 个**必须回 `0`（不是 `-1`）。"""
    _patch(monkeypatch, ["草图1"], {"草图1": _Feat(None)})
    assert D.count_sketch_dimensions(object()) == 0, (
        "★ 有草图特征但没尺寸 ⇒ 应回 0（确实零个），不是 -1（没数到）"
    )


def test_没有草图特征回负一(monkeypatch) -> None:
    """★★ 关键：**一个草图特征都没有**必须回 `-1`（没数到），不是 `0`。"""
    _patch(monkeypatch, ["凸台-拉伸1"], {})
    assert D.count_sketch_dimensions(object()) == -1, (
        "★ 找不到任何草图特征 ⇒ 应回 -1（没数到），不是 0（确实零个）"
    )


def test_取不到特征名回负一(monkeypatch) -> None:
    """★ `feature_names` 抛错 ⇒ 回 -1，不猜。"""

    def _boom(_model):
        raise RuntimeError("COM 挂了")

    monkeypatch.setattr(D, "feature_names", _boom)
    assert D.count_sketch_dimensions(object()) == -1


def test_多个草图累加(monkeypatch) -> None:
    _patch(
        monkeypatch,
        ["草图1", "草图2"],
        {"草图1": _Feat(_DD(None)), "草图2": _Feat(_DD(_DD(None)))},
    )
    assert D.count_sketch_dimensions(object()) == 3


@pytest.mark.parametrize("nm", ["草图1", "Sketch1", "sketch2"], ids=["中文", "Sketch", "sketch"])
def test_草图名两种写法都认(monkeypatch, nm) -> None:
    """★ 中文 `草图` 与英文 `sketch`（大小写不敏感）都要认。"""
    _patch(monkeypatch, [nm], {nm: _Feat(_DD(None))})
    assert D.count_sketch_dimensions(object()) == 1


def test_非草图特征不计入(monkeypatch) -> None:
    """★ 拉伸等非草图特征上的尺寸不算「草图驱动尺寸」。"""
    _patch(
        monkeypatch,
        ["草图1", "凸台-拉伸1"],
        {"草图1": _Feat(None), "凸台-拉伸1": _Feat(_DD(_DD(None)))},
    )
    assert D.count_sketch_dimensions(object()) == 0
