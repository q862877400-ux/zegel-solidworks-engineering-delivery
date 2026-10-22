r"""GUI 输入层 —— **配置化的输入方式** + **稳定的控件标注**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   microsoft/UFO  (MIT License, Copyright (c) Microsoft Corporation)
# 文件:   ufo/automator/ui_control/controller.py  —— set_edit_text / keyboard_input
#         ufo/automator/ui_control/ui_tree.py     —— _generate_node_id / _get_ui_tree
# 定位:   ① 配置化的输入策略（对应 UFO 的 system.input_text_api /
#           input_text_enter / input_text_inter_key_pause 三个配置项）；
#         ② 给控件发稳定标注（对应 UFO 的 node_N + control_dict 寻址）。
#         **只借设计模式，不抄代码**；本文件为独立实现，运行时零依赖 UFO。
# 官方依据: 无 —— 本模块是 GUI 层工程约定，不涉及任何 SolidWorks API。
# 许可:   MIT（UFO）· 本仓库 MIT（本文件原创，无第三方代码引入）。
# ⚠ 本模块的配置默认值来自本机实测（Enter 提交 / 逐键输入 / 超范围弹模态框），
#   但**模块本身未单独跑过端到端实测**；实测链路见调用方
#   scripts/sw_jlcfa_fill.py（见 AGENTS.md 铁律 2）。
# 覆盖:   后续同级定义
# ────────────────────────────────────────────────────────────────────

# ⚑⚑⚑ 借了什么（逐条对照，其余是我们自己的）
# ------------------------------------------------------------------
#   UFO 的配置项                    → 本模块对应
#     system.input_text_api         → CONFIG["input_api"]      set_text | type_keys
#     system.input_text_enter       → CONFIG["commit_key"]     enter | tab | none
#     system.input_text_inter_key_pause → CONFIG["inter_key_pause"]
#   UFO 的 ``_generate_node_id()`` 给每个控件发 ``node_N``
#     → 本模块 ``label()`` 发**可读的本地标注**（便于日志与自愈定位）
#
# ⚑⚑⚑ 哪些**不是**从 UFO 来的（我们自己实测得到的，UFO 只是独立印证）
# ------------------------------------------------------------------
#   · **Enter 才是提交键**：Tab 无效（同一字段同一个 0.5，Tab 后型号行
#     仍 ``L【去填写】``，Enter 后变 ``L0.5``）
#   · **超范围输入会弹模态框**「请输入指定范围内的数字!」，弹窗挡掉后续所有点击
#   · **打之前必须清空并回读确认**，否则拼成 ``195195`` 触发上面那条
#   · ``win32con`` **没有** ``VK_OEM_PERIOD``，小数点用 0xBE

# 覆盖:   后续同级定义
# ⚠ 会驱动键盘；调用方须先确保目标窗口持有键盘焦点。
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from pathlib import Path

import sys
import time
import warnings
from typing import Any


#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"" + _ROOT_S + r"\scripts")

warnings.filterwarnings("ignore")

#: 输入行为配置 —— 与 UFO 的三项同名同义，**改这里就能换策略，不用改代码**
CONFIG: dict[str, Any] = {
    # "set_text" = UIA ValuePattern（快，但插件可能不登记）
    # "type_keys" = 真逐键（慢，插件监听 KeyPress 时**必须**用这个）
    "input_api": "type_keys",
    # 提交键：实测该插件只认 Enter；"tab" 无效，"none" 不提交
    "commit_key": "enter",
    # 逐键间隔（秒）；太快会被吞键
    "inter_key_pause": 0.04,
    # 清空方式："ctrl_a"（Ctrl+A 后 Delete）或 "backspace"（纯退格）
    "clear_with": "ctrl_a",
    # 打完是否回读验证
    "verify": True,
}

VK_DIGIT = {c: 0x30 + i for i, c in enumerate("0123456789")}
#: 主键盘句点的虚拟键码。⚠ ``win32con`` **没有** ``VK_OEM_PERIOD``（实测
#: AttributeError），所以写死字面量。
VK_PERIOD = 0xBE


def _press(vk: int, pause: float = 0.06) -> None:
    """按一下某键（**抬起由 `finally` 保证**）。

    ⚠⚠ **为什么不能写成 `keybd_event(按下); sleep(); keybd_event(抬起)`**（2026-10-01 轮 62 修）：
    那三段之间**任何**异常（`KeyboardInterrupt`、线程被停、进程退出、`sleep` 被中断）
    都会让**抬起永远到不了** ⇒ **修饰键卡在按下态**。
    后果与用户报告的现象**逐一吻合**：
      * **Ctrl 卡住** ⇒ 之后按 `A` 就是 `Ctrl+A` = **全选（蓝底）**；点击变 `Ctrl+点击`
      * **Alt 卡住** ⇒ 菜单栏被激活、按键被吃掉
      * ⚠ **它不需要周期性** —— 一次事故就够，持续到用户**单独按一下那个键**为止。

    ⇒ 定则：**凡是「按下」就必须有一个 `finally` 里的「抬起」**。
    """
    import win32api
    import win32con

    win32api.keybd_event(vk, 0, 0, 0)
    try:
        time.sleep(0.03)
    finally:
        win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(pause)


def _tap(vk: int, pause: float = 0.06) -> None:
    """按一下某键（`_press` 的旧名，保留以免打断既有调用方）。"""
    _press(vk, pause)


def _hold(mods, vk: int, pause: float = 0.1) -> None:
    """按住修饰键 `mods`、点一下 `vk`、**在 `finally` 里抬起所有修饰键**。

    ⚠ `mods` 里**每一个**都在 `finally` 里抬起 ⇒ 中途异常也不会让 Ctrl/Alt 卡住。
    ⚠ 抬起顺序**逆序**（与按下相反）—— 与真实键盘的语义一致。
    """
    import win32api
    import win32con

    mods = list(mods)
    held = []
    try:
        for m in mods:
            win32api.keybd_event(m, 0, 0, 0)
            held.append(m)
        time.sleep(0.03)
        win32api.keybd_event(vk, 0, 0, 0)
        try:
            time.sleep(0.03)
        finally:
            win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
    finally:
        for m in reversed(held):
            try:
                win32api.keybd_event(m, 0, win32con.KEYEVENTF_KEYUP, 0)
            except Exception:  # noqa: BLE001 —— 收尾失败不该掩盖主异常，但必须逐个尝试
                pass
    time.sleep(pause)


def _tap_ctrl(vk: int, pause: float = 0.1) -> None:
    """Ctrl + 某键 ⇒ 走 `_hold`（**Ctrl 一定被抬起**）。"""
    import win32con

    _hold([win32con.VK_CONTROL], vk, pause)


# ── 控件标注（对应 UFO 的 node_N，但做成可读的）──────────────────
_LABEL_SEQ: dict[str, int] = {}


def label(ctrl, prefix: str = "ctl") -> str:
    """给控件发一个**稳定、可读**的本地标注，用于日志与自愈定位。

    ⚑ 为什么不直接抄 UFO 的 ``node_N``：我们跑的是**确定性脚本**，
      日志里需要一眼看出「这是哪个控件」。所以标注含类型 + 名字 + 位置，
      并在同一次会话里保持稳定（同名同位的控件复用同一个编号）。

    形如 ``ctl_03 Edit「花键轴长度（L）」@(2225,937)``
    """
    try:
        ct = ctrl.element_info.control_type
    except Exception:
        ct = "?"
    try:
        nm = (ctrl.window_text() or "").strip()[:20]
    except Exception:
        nm = ""
    try:
        r = ctrl.rectangle()
        pos = "(%d,%d)" % (r.left, r.top)
    except Exception:
        pos = "(?,?)"
    key = "%s|%s|%s" % (ct, nm, pos)
    if key not in _LABEL_SEQ:
        _LABEL_SEQ[key] = len(_LABEL_SEQ) + 1
    return "%s_%02d %s「%s」@%s" % (prefix, _LABEL_SEQ[key], ct, nm, pos)


def reset_labels() -> None:
    """清空标注表（换页面后调用，避免编号膨胀）。"""
    _LABEL_SEQ.clear()


# ── 输入 ────────────────────────────────────────────────────────────
def set_text(ctrl, text: str) -> bool:
    """UIA ValuePattern 设值。**快，但插件可能不登记**（见模块头 ②）。

    ⚠ 该插件实测：框里有字，型号行仍是 ``【去填写】`` ⇒ 只能用 type_text。
      保留此函数是为了**别的应用**（如搜索框）能用快路。
    """
    for meth in ("set_edit_text", "set_text"):
        try:
            getattr(ctrl, meth)(text)
            return True
        except Exception:
            continue
    return False


def get_text(ctrl) -> str:
    """回读控件当前文字（Edit 用 ValuePattern，其余用名字）。"""
    try:
        v = ctrl.get_value()
        if v is not None:
            return str(v)
    except Exception:
        pass
    try:
        return str(ctrl.window_text() or "")
    except Exception:
        return ""


def clear(ctrl, log=None) -> bool:
    """清空输入框并**回读确认**。返回是否确认为空。"""
    import win32con

    for _ in range(3):
        if CONFIG["clear_with"] == "backspace":
            for _ in range(20):
                _tap(win32con.VK_BACK, 0.02)
        else:
            _tap_ctrl(ord("A"), 0.05)
            _tap(win32con.VK_DELETE, 0.05)
            for _ in range(16):
                if not get_text(ctrl).strip():
                    break
                _tap(win32con.VK_BACK, 0.02)
        time.sleep(0.2)
        if not get_text(ctrl).strip():
            return True
    if log:
        log("      ⚠ 未能清空（现 %r）" % get_text(ctrl)[:14])
    return False


def commit(log=None) -> None:
    """按配置提交（实测该插件**只认 Enter**，Tab 无效）。"""
    import win32con

    k = CONFIG["commit_key"]
    if k == "enter":
        _tap(win32con.VK_RETURN, 0.3)
    elif k == "tab":
        _tap(win32con.VK_TAB, 0.2)
    time.sleep(0.8)


def type_text(ctrl, text: str, log=None) -> bool:
    """用**真键盘逐键**把 ``text`` 打进 ``ctrl`` 并提交。**不做焦点管理**（调用方负责）。

    返回是否**文本已落地**（``CONFIG["verify"]`` 为真时回读确认）。
    """
    if CONFIG["input_api"] == "set_text":
        ok = set_text(ctrl, text)
        if CONFIG["verify"] and ok:
            got = get_text(ctrl)
            ok = text in got
        commit(log)
        return ok
    # type_keys：逐键
    if not clear(ctrl, log=log):
        return False
    pause = float(CONFIG["inter_key_pause"])
    for ch in text:
        if ch in VK_DIGIT:
            _tap(VK_DIGIT[ch], pause)
        elif ch == ".":
            _tap(VK_PERIOD, pause)
        elif ch == "-":
            _tap(0xBD, pause)
        else:
            import win32api

            vk = win32api.VkKeyScan(ch) & 0xFF
            if vk and vk != 0xFF:
                _tap(vk, pause)
    time.sleep(0.3)
    got = get_text(ctrl)
    if log:
        log("      打完 框内=%r（目标 %s）" % (got, text))
    commit(log)
    if CONFIG["verify"]:
        return text in get_text(ctrl) or text in got
    return True
