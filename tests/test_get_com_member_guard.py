"""★ `get_com_member` 的「不可调用」守卫契约测试（不连 SolidWorks）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_get_com_member_guard.py —— 本文件自身
# 定位:   ★ 2026-10-03（轮 493）★ 给 `scripts/sw_connect.get_com_member` 的**新守卫**立契约。
#
#   ★★ **为什么要有这个守卫**（★ 真机实证，轮 492）：
#     · `IModelDocExtension.InsertChainDimensions` 官方是 `kind: method`，
#       而真机 `type(getattr(ext, "InsertChainDimensions"))` = **`tuple`**、
#       `callable(...)` = **`False`**、`repr(...)` = **`(None, None, None)`**、
#       `dir(ext)` 里**没有该名字** ⇒ ★ **pywin32 迟到绑定造不出调用包装**。
#     · 而那时 `get_com_member` 报的是 **`TypeError: 'tuple' object is not callable`**
#       —— ★★ **完全看不出是「后端限制」**，会被误当成"参数没传对"（★ 我当轮就差点往那走）。
#     · ★ 与**事实 28**（「反射里有」≠「运行期调用得到」）同族，已记成**事实 386**；
#       ★ 而**事实 40** 的定则在此适用：「★ **修的只能是「让失败可见」**」。
#
#   ★ **设计约束（本测试就是在钉住它）**：★ 守卫**只加在"有实参"那条路**上 ——
#     因为"无实参"那条（`sw_connect.py` 的 `member() if callable(member) else member`）
#     **早就检查了 callable**、且它的"照旧返回成员本身"是**全仓依赖的既有语义**（轮 143 定的）
#     ⇒ ★ **不许动它**。
#
#   ★★ **本测试是负例驱动的**（事实 62：一个门禁「写了」不等于它「有效」——
#     **负例测试是唯一的证明**）：用例 ① 用的正是真机那个 `(None, None, None)` 形态。
#
# 官方依据: `C:\swapi\types\IModelDocExtension\InsertChainDimensions.md`（`kind: method`）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from sw_connect import get_com_member  # noqa: E402


class _NotCallableMember:
    """★ 复刻**真机那个形态**：名字在、而 `getattr` 回一个不可调用的元组。"""

    #: ★ 逐字就是真机拿到的那个值
    InsertChainDimensions = (None, None, None)
    Name = "fake"


class _CallableMember:
    def Twice(self, value):  # noqa: D102
        return value * 2


def test_not_callable_with_args_raises_with_reason():
    """① 有实参 + 不可调用 ⇒ **抛带原因的 `TypeError`**（★ 而不是裸的 `'tuple' …`）。"""
    with pytest.raises(TypeError) as ei:
        get_com_member(_NotCallableMember(), "InsertChainDimensions", [1, 2])
    msg = str(ei.value)
    #: ★ 错误信息里**必须**出现这三样（★ 那才是"带原因"）
    assert "不可调用" in msg, msg
    assert "事实 28 / 386" in msg, msg
    assert "不要改参数" in msg, msg
    #: ★ 并且要**点名**那个成员
    assert "InsertChainDimensions" in msg, msg


def test_not_callable_without_args_returns_member_unchanged():
    """② 无实参 + 不可调用 ⇒ **照旧返回成员本身**（★ 轮 143 的既有语义，不许动）。"""
    got = get_com_member(_NotCallableMember(), "InsertChainDimensions")
    assert got == (None, None, None)


def test_callable_member_still_called():
    """③ 可调用的成员 ⇒ 照旧被调用并回结果（★ 守卫**不能**误伤正常路径）。"""
    assert get_com_member(_CallableMember(), "Twice", 21) == 42


def test_guard_only_on_the_args_path():
    """④ ★ 结构约束：守卫**只**加在"有实参"那条路上（★ 读源码钉住，防后人挪位置）。"""
    src = (REPO_ROOT / "scripts" / "sw_connect.py").read_text(encoding="utf-8")
    i_args = src.index("if args:")
    i_guard = src.index("if not callable(member):")
    #: ★ 守卫必须在 `if args:` **之后**、且**紧接着**（中间只许有注释）
    assert i_args < i_guard, "守卫必须在 `if args:` 之后"
    between = src[i_args:i_guard]
    assert "return member(*args)" not in between, (
        "守卫必须在 `return member(*args)` **之前**，否则不生效")
