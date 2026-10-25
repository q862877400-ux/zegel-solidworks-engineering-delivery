"""★ `add_component` 失败必须抛，不得静默回 `None`。

## 缺陷（第 42 轮真机确认）

三层兜底（`AddComponent5` → `AddComponent4` → 开零件再切回）全失败时，
原实现只 `print` 然后 `return component`（`None`）⇒ 调用方拿到 `None` 但**调用成功返回**
⇒ 用 `try_call` 包会得到 `(True, None)` ⇒ **看起来成功了**。

★ 我第 22 轮就是被它误导的：`ok=True` 让我以为这条路调通了，实际组件数 0。

## 修法

加完**回读组件数**（独立读数），`0 → 0` 就 `raise RuntimeError`，把三级兜底的错误串一起抛出。

| 情形 | 动作 |
|---|---|
| 计数确实增加 | 正常返回 component |
| 计数没变 | **抛 RuntimeError**（带 `0 → 0` 证据） |
| 计数读不出（-1） | 不据此下结论（按原逻辑返回） |
| 计数增加但没拿到对象 | 如实 `print` 提示需按名称回查 |

## 怎么测（不连真机）

用**假对象**：一个 `GetComponents` 回空列表的桩，模拟「加不进去」。
本文件只验「失败会抛」与「`_component_count` 的 -1 约定」，
真机证据在 `output/e4-add-component-via-wrapper.json`。
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import pytest  # noqa: E402
import sw_assembly as asm  # noqa: E402


class _FakeAsm:
    """★ `GetComponents` 恒回空列表 ⇒ 组件数一直 0（模拟「加不进去」）。"""

    def GetComponents(self, *_a):  # noqa: N802
        return []

    def __getattr__(self, name):  # noqa: D105
        #: 任何 AddComponent* 调用都回 None（模拟真机现状）
        if name.startswith("AddComponent"):
            return lambda *a, **k: None
        raise AttributeError(name)


class _BrokenAsm:
    """★ `GetComponents` 直接抛 ⇒ 计数读不出，应回 -1。"""

    def GetComponents(self, *_a):  # noqa: N802
        raise RuntimeError("boom")


def test_加不进去必须抛() -> None:
    """★★ 核心：三层兜底都失败时，必须抛而不是静默回 None。"""
    with pytest.raises(RuntimeError) as ei:
        asm.add_component(_FakeAsm(), __file__, 0.0, 0.0, 0.0)
    msg = str(ei.value)
    assert "组件数" in msg, "★ 错误信息要带计数证据：%s" % msg
    assert "0 → 0" in msg, "★ 要能看出加之前加之后都是 0：%s" % msg


def test_组件数读不出回负一() -> None:
    """★ `-1` = 读不出（与 `open_doc_count` 同一约定），不得当成 0。"""
    assert asm._component_count(_BrokenAsm()) == -1


def test_组件数正常读出() -> None:
    assert asm._component_count(_FakeAsm()) == 0


def test_文件不存在仍先报文件错() -> None:
    """★ 前置校验不能被新判据挤掉。"""
    with pytest.raises(FileNotFoundError):
        asm.add_component(_FakeAsm(), str(REPO / "output" / "_不存在.SLDPRT"))
