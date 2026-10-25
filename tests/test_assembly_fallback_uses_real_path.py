"""★ `add_component` 兜底必须用**实际打开那份**的路径，不是调用方原始路径。

## 真机证据链（第 43 轮）

① 官方 `AddComponent5.md` Remarks 逐字：「**The specified file must be loaded in memory.**」

② 按前置重测：先 `OpenDoc6` 打开零件、再建装配并激活
   ⇒ `AddComponent5`（8 参）**加得进去**（组件数 **0 → 1**，返回真实 `IComponent2`）。

③ ★★ 第二层根因：`sw_guard` 沙箱会**复制改名**零件（`板1_rev-1__12.SLDPRT`），
   而封装兜底把**调用方原始路径**传给 `AddComponent5` ⇒ 原路径不在内存 ⇒ 回 `None`。
   改用 `opened.GetPathName()` 后封装也通（0 → 1，返回 `CDispatch`）。

⇒ 「输入 ≠ 实际」的又一例：输入是**我想要什么**，`GetPathName()` 是**实际发生了什么**。

## 本文件钉什么

① 兜底里必须出现 `GetPathName()`
② 兜底**不得**直接把调用方 `component_path` 传给 `_add_component5`
③ 失败时的错误信息要带**试过的路径**（否则下次又分不清是「前置没成」还是「路径不对」）
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import sw_assembly as asm  # noqa: E402


def _src() -> str:
    return inspect.getsource(asm.add_component)


def test_兜底用实际打开那份的路径() -> None:
    """★★ 核心：沙箱会改名，必须回读 `GetPathName()`。"""
    src = _src()
    assert "GetPathName" in src, (
        "★ 兜底里没有 GetPathName ⇒ 沙箱改名后会把原路径传给 COM，"
        "而原路径不在内存 ⇒ AddComponent5 回 None（第 43 轮真机就是这个问题）"
    )


def test_兜底不再直接把原始路径交给_add_component5() -> None:
    """★★ 结构断言：`_add_component5` 的实参必须是「内存里那份」的路径变量。"""
    src = _src()
    #: 兜底那一段里，_add_component5 的第一个实参是 in_memory（回读值），不是 component_path
    assert "in_memory" in src, "★ 兜底没有用回读到的路径变量"
    i = src.find("open_then_AddComponent5")
    assert i > 0, "★ 找不到兜底的重试段"
    seg = src[:i]
    #: 兜底段最后一次 _add_component5 调用应传 in_memory
    last = seg.rfind("_add_component5(")
    assert last > 0
    call = seg[last:last + 220]
    assert "in_memory" in call, (
        "★ 兜底的 _add_component5 没传 in_memory，实际传的是：%r" % call[:160]
    )


def test_失败信息带试过的路径() -> None:
    """★ 不带路径的话，下次又分不清「前置没成」和「路径不对」。"""
    src = _src()
    assert "试过路径" in src, "★ 兜底失败信息应带出试过的路径"


def test_加不进去仍然抛() -> None:
    """★ 第 42 轮那条修复不能被这次改动弄丢。"""
    import pytest

    class _FakeAsm:
        def GetComponents(self, *_a):  # noqa: N802
            return []

        def __getattr__(self, name):  # noqa: D105
            if name.startswith("AddComponent"):
                return lambda *a, **k: None
            raise AttributeError(name)

    with pytest.raises(RuntimeError):
        asm.add_component(_FakeAsm(), __file__, 0.0, 0.0, 0.0)
