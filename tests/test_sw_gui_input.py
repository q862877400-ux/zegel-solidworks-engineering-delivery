"""@brief GUI 输入层（配置化输入 + 控件标注）的静态测试。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   microsoft/UFO  (MIT License, Copyright (c) Microsoft Corporation)
# 文件:   ufo/automator/ui_control/controller.py —— set_edit_text / keyboard_input
#         （仅作为**被测行为的对照物**，本测试不导入也不运行 UFO）
# 定位:   断言被测模块 scripts/sw_gui_input.py 的配置默认值与控件标注行为，
#         这些默认值来自本项目对嘉立创插件 GUI 的**本机实测结论**。
# 官方依据: 无 —— GUI 层工程约定，不涉及 SolidWorks API。
# 许可:   MIT（UFO 仅作对照与设计模式来源）· 本仓库 MIT（本文件原创）。
# ⚠ 本测试是**静态断言**（用假控件对象），未在本机实测 SolidWorks；
#   真实链路的实测由 scripts/sw_jlcfa_batch.py 承担（见 AGENTS.md 铁律 2）。
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import scripts.sw_gui_input as gi


class _FakeRect:
    def __init__(self, l: int, t: int, r: int, b: int) -> None:
        self.left, self.top, self.right, self.bottom = l, t, r, b


class _FakeInfo:
    def __init__(self, control_type: str) -> None:
        self.control_type = control_type


class _FakeEdit:
    """模仿 pywinauto 的 Edit 包装：有 get_value / window_text / element_info。"""

    def __init__(self, name: str, value: str = "", rect=None,
                 control_type: str = "Edit") -> None:
        self._name = name
        self._value = value
        self._rect = rect or _FakeRect(100, 200, 300, 224)
        self.element_info = _FakeInfo(control_type)
        self.set_calls: list[tuple[str, str]] = []

    def window_text(self) -> str:
        return self._name

    def get_value(self) -> str:
        return self._value

    def rectangle(self):
        return self._rect

    def set_edit_text(self, text: str) -> None:
        self.set_calls.append(("set_edit_text", text))
        self._value = text

    def set_text(self, text: str) -> None:
        self.set_calls.append(("set_text", text))
        self._value = text


class _NoValuePattern(_FakeEdit):
    """只有 window_text，没有 ValuePattern —— 模仿不支持设值的控件。"""

    def set_edit_text(self, text: str) -> None:  # type: ignore[override]
        raise RuntimeError("no ValuePattern")

    def set_text(self, text: str) -> None:  # type: ignore[override]
        raise RuntimeError("no ValuePattern")


# ── ① 配置默认值必须等于**实测结论** ────────────────────────────
def test_input_api_defaults_to_real_keystrokes() -> None:
    """@brief 默认必须是逐键输入。

    实测：``set_edit_text``（ValuePattern）写了字但该插件**不登记**
    （型号行仍是 ``【去填写】``），所以默认不能是 ``set_text``。
    """
    assert gi.CONFIG["input_api"] == "type_keys"


def test_commit_key_defaults_to_enter_not_tab() -> None:
    """@brief 提交键默认必须是 Enter。

    实测：同一字段同一个值 ``0.5``，Tab 后型号行仍 ``L【去填写】``，
    Enter 后变 ``L0.5`` ⇒ 该插件只认 Enter。
    """
    assert gi.CONFIG["commit_key"] == "enter"


def test_clear_strategy_and_pause_defaults() -> None:
    """@brief 清空方式与逐键间隔有明确默认值（间隔太快会吞键）。"""
    assert gi.CONFIG["clear_with"] == "ctrl_a"
    assert 0 < gi.CONFIG["inter_key_pause"] <= 0.5
    assert gi.CONFIG["verify"] is True


def test_config_is_overridable_without_code_change() -> None:
    """@brief 换策略只改配置，不改代码 —— 这是本模块存在的理由。"""
    old = gi.CONFIG["commit_key"]
    try:
        gi.CONFIG["commit_key"] = "tab"
        assert gi.CONFIG["commit_key"] == "tab"
    finally:
        gi.CONFIG["commit_key"] = old


def test_period_keycode_is_literal_not_win32con() -> None:
    """@brief 小数点键码是字面量 0xBE。

    实测 ``win32con`` **没有** ``VK_OEM_PERIOD``（AttributeError），
    所以不能写成 ``win32con.VK_OEM_PERIOD``。
    """
    assert gi.VK_PERIOD == 0xBE


def test_digit_vk_mapping_covers_all_ten() -> None:
    """@brief 0-9 的虚拟键码映射齐全且连续。"""
    assert len(gi.VK_DIGIT) == 10
    for i, ch in enumerate("0123456789"):
        assert gi.VK_DIGIT[ch] == 0x30 + i


# ── ② 控件标注：稳定、可读 ──────────────────────────────────────
def test_label_is_readable_and_carries_position() -> None:
    """@brief 标注含类型/名字/位置 —— 日志里要能一眼看出是哪个控件。"""
    gi.reset_labels()
    ctl = _FakeEdit("花键轴长度（L）", rect=_FakeRect(2225, 937, 2430, 961))
    txt = gi.label(ctl)
    assert "Edit" in txt
    assert "花键轴长度（L）" in txt
    assert "(2225,937)" in txt


def test_label_is_stable_for_same_control() -> None:
    """@brief 同一控件重复取标注，编号不变（否则日志无法对照）。"""
    gi.reset_labels()
    ctl = _FakeEdit("W", rect=_FakeRect(2225, 937, 2430, 961))
    assert gi.label(ctl) == gi.label(ctl)


def test_label_distinguishes_different_controls() -> None:
    """@brief 不同控件拿到不同编号。"""
    gi.reset_labels()
    a = _FakeEdit("W", rect=_FakeRect(2225, 937, 2430, 961))
    b = _FakeEdit("L", rect=_FakeRect(2225, 982, 2430, 1006))
    assert gi.label(a) != gi.label(b)


def test_reset_labels_restarts_numbering() -> None:
    """@brief 换页面后重置编号，避免膨胀。"""
    gi.reset_labels()
    ctl = _FakeEdit("W")
    first = gi.label(ctl)
    gi.reset_labels()
    assert gi.label(ctl) == first


def test_label_survives_broken_control() -> None:
    """@brief 属性读不到的控件也要能出标注（不能因日志而崩）。"""

    class _Broken:
        class element_info:  # noqa: N801
            @staticmethod
            def control_type() -> str:
                raise RuntimeError("boom")

        def window_text(self) -> str:
            raise RuntimeError("boom")

        def rectangle(self):
            raise RuntimeError("boom")

    txt = gi.label(_Broken())
    assert txt.startswith("ctl_")


# ── ③ 回读与设值 ────────────────────────────────────────────────
def test_get_text_prefers_value_pattern() -> None:
    """@brief 回读优先用 get_value（Edit 的真实内容）。"""
    assert gi.get_text(_FakeEdit("W", value="195")) == "195"


def test_get_text_falls_back_to_window_text() -> None:
    """@brief 没有 get_value 时退回 window_text。"""

    class _OnlyName:
        def window_text(self) -> str:
            return "abc"

    assert gi.get_text(_OnlyName()) == "abc"


def test_set_text_prefers_set_edit_text() -> None:
    """@brief 设值优先 ``set_edit_text``，成功就不再尝试 ``set_text``。"""
    ctl = _FakeEdit("W")
    assert gi.set_text(ctl, "42") is True
    assert ctl.set_calls == [("set_edit_text", "42")]
    assert ctl.get_value() == "42"


def test_set_text_reports_failure_when_no_value_pattern() -> None:
    """@brief 两种 ValuePattern 都不可用时返回 False，不假装成功。"""
    assert gi.set_text(_NoValuePattern("W"), "42") is False


# ── ④ type_keys 路径不依赖真实键盘（只在 set_text 模式测）────────
def test_type_text_set_text_mode_verifies_readback() -> None:
    """@brief ``input_api='set_text'`` 模式下，回读不到就打回 False。"""
    old = dict(gi.CONFIG)
    try:
        gi.CONFIG["input_api"] = "set_text"
        gi.CONFIG["verify"] = True
        ctl = _FakeEdit("W", value="")
        assert gi.type_text(ctl, "195") is True
        assert ctl.get_value() == "195"
    finally:
        gi.CONFIG.update(old)


def test_type_text_type_keys_mode_refuses_unclearable_field() -> None:
    """@brief 逐键模式下框清不空 ⇒ **宁可不打**，不拼出超范围值。

    实测：``195`` 留在框里再打一遍得到 ``195195``，超出 ``[195~1500]``
    ⇒ 插件弹模态框「请输入指定范围内的数字!」，挡掉后续所有点击。
    """
    old = dict(gi.CONFIG)
    try:
        gi.CONFIG["input_api"] = "type_keys"

        class _Stuck(_FakeEdit):
            def get_value(self) -> str:
                return "195"          # 永远清不掉

        ctl = _Stuck("W", value="195")
        assert gi.type_text(ctl, "195") is False
        assert ctl.set_calls == []
    finally:
        gi.CONFIG.update(old)
