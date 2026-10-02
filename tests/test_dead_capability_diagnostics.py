"""「后端拿不到成员」时必须抛**可诊断**的错（不是裸 `TypeError` / `com_error`）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_dead_capability_diagnostics.py
# 定位:   守轮 95（Spec Kit `015`）对两个**跑不通**的孤立函数的修法 ——
#         与 `IModeler.Create*Surface` 的先例一致（已知事实 40）：
#         **返回值/调用不可靠时，唯一能修的是「让失败可见」**。
# 官方签名依据: 不适用（纯桩测）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ **核心价值**：修之前，这两处抛的是
#   `TypeError: 'NoneType' object is not callable` 与裸 `com_error` ——
#   **都看不出「是成员取不到」**。本测试把「抛什么」钉住。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import sw_export, sw_weldment  # noqa: E402


class _NoSuchMember:
    """桩：任何成员都取不到（模拟 pywin32 分发解析为 `None`）。"""

    def __getattr__(self, name):
        return None


class _BoomOnCall:
    """桩：`Extension` 取得，但 `GetMassProperties` 调用时抛（模拟 `com_error`）。"""

    class _Ext:
        def __getattr__(self, name):
            def _call(*_a, **_k):
                raise RuntimeError("(-2147352561, '非选择性的参数。', None, None)")
            return _call

    def __getattr__(self, name):
        if name == "Extension":
            return _BoomOnCall._Ext()
        return None


def test_create_cut_list_raises_diagnosable_error_when_member_missing(monkeypatch):
    """@brief 成员取不到时，必须是**带成员名与后端**的 `RuntimeError`。

    ⚠ 不许退化成 `TypeError: 'NoneType' object is not callable` —— 那看不出真因。
    """
    monkeypatch.setattr(sw_weldment, "get_com_member",
                        lambda obj, name, *args: None)
    with pytest.raises(RuntimeError) as ei:
        sw_weldment.create_cut_list(_NoSuchMember())
    msg = str(ei.value)
    assert "InsertWeldmentCutList2" in msg, msg
    assert "后端" in msg, msg


def test_mass_property_override_wraps_com_error_into_runtime_error():
    """@brief COM 调用失败时，必须转成**带成员名**的 `RuntimeError`（不裸抛 `com_error`）。"""
    with pytest.raises(RuntimeError) as ei:
        sw_export.get_mass_property_override_options(_BoomOnCall())
    msg = str(ei.value)
    assert "GetMassProperties" in msg, msg
    assert "不可用" in msg, msg


def test_both_docstrings_say_the_capability_is_unavailable():
    """@brief 两处 docstring 必须写明「当前后端不可用」——**文档串与代码同步**。

    ⚠ 本仓库踩过「文档串声称做了两层自检、代码只做一层」（`sw_surface._invoke` 的来源块）
    ⇒ 这条把这个坑钉住。
    """
    for fn in (sw_weldment.create_cut_list, sw_export.get_mass_property_override_options):
        doc = fn.__doc__ or ""
        assert "跑不通" in doc or "不可用" in doc, fn.__name__
        assert "后端" in doc, fn.__name__
