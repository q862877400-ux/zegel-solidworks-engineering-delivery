"""轴语义与场景描述：把「谁在谁的哪一侧」钉成**可测的**代码。

## 为什么这套测试重要（业主 2026-10-26 指令）

> 你通过视觉检查出来的错误，不能够打个补丁就了事儿，你要从根本上去修复问题。
> …你要从工具层面、根本的层面去解决问题。

本轮那件事的根因：**我从三个坐标数字自己脑补空间关系，而轴方向从没核过**。
⇒ 修法不是改那句描述，而是：
  ① 轴语义变成**常量**（`AXIS_SCREEN`），并有测试钉住
  ② 关系描述由代码**生成**（`describe_scene`），我不再手写
  ③ 描述必须**区分「高矮」与「前后/左右」** —— 这正是业主一眼看出的差别

★ 下面第三组测试专门钉「不能把 Z 方向的错开说成高」。
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO))

from sw_scene import AXIS_NAME, AXIS_SCREEN, describe_scene, relation_text  # noqa: E402


def _box(name: str, lo, hi) -> dict:
    return {
        "name": name,
        "lo": lo,
        "hi": hi,
        "center": tuple(round((lo[i] + hi[i]) / 2.0, 1) for i in range(3)),
        "size": tuple(round(hi[i] - lo[i], 1) for i in range(3)),
    }


# ── ① 轴语义是常量，且有明确对错 ─────────────────────────────────────


def test_Y是竖直方向() -> None:
    """★★ 「抬高」= +Y。这条如果被改成 Z，整个描述体系就错了。"""
    assert AXIS_SCREEN["y"] == ("上", "下")


def test_X是左右() -> None:
    assert AXIS_SCREEN["x"] == ("右", "左")


def test_Z是前后() -> None:
    """★ Z 是深度（朝观察者），**不是高** —— 本轮错误的直接原因。"""
    assert AXIS_SCREEN["z"] == ("前", "后")


def test_三轴齐全() -> None:
    assert set(AXIS_SCREEN) == {"x", "y", "z"}
    assert set(AXIS_NAME) == {"x", "y", "z"}


# ── ② 关系描述按轴说人话 ────────────────────────────────────────────


def test_上方关系() -> None:
    """b 在 a 正上方 30mm。"""
    a = _box("A", (0, 0, 0), (100, 20, 100))
    b = _box("B", (0, 50, 0), (100, 70, 100))
    txt = relation_text(a, b)
    assert "Y（上下）" in txt and "上" in txt and "30.0mm" in txt


def test_下方关系() -> None:
    a = _box("A", (0, 50, 0), (100, 70, 100))
    b = _box("B", (0, 0, 0), (100, 20, 100))
    txt = relation_text(a, b)
    assert "下" in txt and "30.0mm" in txt


def test_右侧关系() -> None:
    a = _box("A", (0, 0, 0), (100, 20, 100))
    b = _box("B", (130, 0, 0), (230, 20, 100))
    txt = relation_text(a, b)
    assert "右" in txt and "30.0mm" in txt


def test_重叠也要说() -> None:
    a = _box("A", (0, 0, 0), (100, 20, 100))
    b = _box("B", (50, 30, 0), (150, 50, 100))
    txt = relation_text(a, b)
    assert "重叠" in txt


# ── ③ 总述必须区分「高矮」与「前后/左右」 ────────────────────────────


def test_Z方向错开不能被称为高() -> None:
    """★★★ 本轮错误的回归测试。

    两块板 X 错开 30mm、Z 错开 50mm、Y **完全相同**
    ⇒ 前视图里它们**一样高**。描述必须说「前后（深度）」，不许说「高」。
    """
    a = _box("A", (-50, -30, -10), (50, 30, 10))
    b = _box("B", (-20, -30, 40), (80, 30, 60))
    txt = describe_scene([a, b])
    assert "**不是高**" in txt or "不是高" in txt, (
        "★ Z 方向的错开被说成了高 —— 这正是业主当场指出的错误：\n%s" % txt
    )
    assert "前后" in txt


def test_Y方向错开要明说是高() -> None:
    a = _box("A", (-50, -30, -10), (50, 30, 10))
    b = _box("B", (-50, 60, -10), (50, 120, 10))
    txt = describe_scene([a, b])
    assert "高/低" in txt or "竖直" in txt, "★ Y 方向分离没被说成高矮：\n%s" % txt


def test_X方向错开要明说不是高() -> None:
    a = _box("A", (-50, -30, -10), (50, 30, 10))
    b = _box("B", (80, -30, -10), (180, 30, 10))
    txt = describe_scene([a, b])
    assert "左右" in txt and "不是高" in txt


# ── ④ 顺序无关（实测 GetComponents 顺序 ≠ 插入顺序）────────────────────


def test_顺序不影响关系判定() -> None:
    a = _box("A", (-50, -30, -10), (50, 30, 10))
    b = _box("B", (-50, 60, -10), (50, 120, 10))
    t1 = describe_scene([a, b])
    t2 = describe_scene([b, a])
    #: 两者都要指出「Y 方向分离」，只是主语不同
    assert ("竖直" in t1) and ("竖直" in t2)


def test_空场景不炸() -> None:
    assert describe_scene([]) == "（没有组件）"


def test_单组件只列自身() -> None:
    txt = describe_scene([_box("A", (0, 0, 0), (10, 10, 10))])
    assert "组件 A" in txt
    assert "相对" not in txt
