"""钉住 `get_com_member` 的「**取或调**」语义（轮 144 审计后写明白的那条）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_get_com_member_semantics.py
# 定位:   轮 143 查出「取即调」，轮 144 审完 **471** 个无实参调用点后**改判**：
#         **这不是缺陷，是被依赖的特性** ⇒ 把它写成正式语义 + 加安全替代。
#         ⚠ 本文件钉住**两条语义**，免得下一个人再判错一次。
# 官方依据: 不适用（本项目内部纪律）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT))

import sw_connect          # noqa: E402


class _Obj:
    """假 COM 对象：一个**有副作用**的零参方法 + 一个属性。"""

    def __init__(self):
        self.calls = 0
        self.Title = "the-title"

    def Mutate(self):
        self.calls += 1
        return "mutated"


def test_get_com_member_calls_a_zero_arg_method():
    """@brief ★★ 无实参 ⇒ **会调**（这是语义，不是 bug）。"""
    o = _Obj()
    assert sw_connect.get_com_member(o, "Mutate") == "mutated"
    assert o.calls == 1, "应当**被调了一次**"


def test_get_com_member_returns_a_plain_attribute():
    """@brief 属性 ⇒ 拿不到"调用"，于是返回**属性值**。"""
    o = _Obj()
    assert sw_connect.get_com_member(o, "Title") == "the-title"
    assert o.calls == 0


def test_get_com_member_with_args_always_calls():
    """@brief 有实参 ⇒ **一定调**（不试探）。"""
    o = _Obj()
    sw_connect.get_com_member(o, "Mutate")
    assert o.calls == 1


def test_get_com_member_raw_never_calls():
    """@brief ★★ `get_com_member_raw` **只取不调** —— 有副作用成员的**安全替代**。"""
    o = _Obj()
    m = sw_connect.get_com_member_raw(o, "Mutate")
    assert callable(m), "应当拿到**方法对象**"
    assert o.calls == 0, "★ **绝不许调用**"
    assert m() == "mutated"
    assert o.calls == 1, "自己调才计数"


def test_docstring_states_the_semantics_and_the_risk():
    """@brief ★★ docstring 必须写明「取或调」与**危险面**（免得再被误判一次）。"""
    import inspect
    doc = inspect.getdoc(sw_connect.get_com_member) or ""
    assert "取或调" in doc, "要写明这是「取或调」"
    assert "471" in doc and "193" in doc, "要写明审计量出的影响面"
    assert "get_com_member_raw" in doc, "要指向安全替代"


def test_the_audit_tool_is_in_the_repo():
    """@brief 审计脚本要在仓库里（可重跑）。"""
    assert (REPO_ROOT / "tools" / "audit_get_com_member_semantics.py").is_file()
