"""pytest 全局配置：**禁止任何测试真的注入键盘/鼠标**。

# ── 为什么必须有这个文件（2026-10-01 轮 63 实报事故） ──────────────────
用户报告「鼠标键盘忽然被影响：全选全屏文字（蓝底）/ 忽然回车 / 忽然 Ctrl」，**发生在我跑全量回归的时刻**。

**根因**：
```
tests/test_sw_gui_input.py  L212/L233  assert gi.type_text(ctl, "195") ...
  ⇒ type_text 的默认模式是 input_api == "type_keys"（**逐键真输入**）
  ⇒ 而它的默认清空策略是 clear_with == "ctrl_a"  ⇒ **真的发 Ctrl+A**
该文件里 **monkeypatch 出现 0 次** ⇒ **完全没有任何 mock**
仓库里 **没有任何 conftest.py** ⇒ **没有任何全局保护**
```
⇒ 跑一次全量回归，就等于**在用户的真实桌面上按键**。这不是测试，这是**副作用**。

## 本文件的立场
**测试**绝不允许**触碰真实输入设备。** 需要验证「按键被正确发出」的测试，
应当断言**注入层的调用记录**（本文件提供的记录器），而不是**真的去按**。

⚠ 与项目既有纪律的关系：`AGENTS.md` 铁律 2 要求实测时「先置 `CommandInProgress`、必须有超时、
收尾必做」—— 那是**真机实测**的规矩。**而单元测试根本不是实测**，它不该碰真机输入。
把两者混起来，就得到了本次事故。

# ── 来源 ──
# 仓库:   本项目自身（测试基础设施）
# 文件:   tests/conftest.py
# 定位:   一个 `autouse` 的会话级拦截器：把 `win32api.keybd_event` / `mouse_event` /
#         `SetCursorPos` 换成**记录器**，并把调用记进 `input_injection_log`。
# 官方依据: Win32 `keybd_event` / `mouse_event` / `SetCursorPos`（user32.dll）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 它**不改变**被测代码；只把「真的按键」换成「记账」。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys

import pytest

#: 本次测试会话里发生的**虚拟**注入调用（`(kind, args)`）。
#: ⚠ 测试可以断言它；**永远不会**有真实的键鼠动作。
input_injection_log: list = []


def _record(kind):
    def _fn(*args, **kwargs):
        input_injection_log.append((kind, args))
        return 0
    return _fn


@pytest.fixture(autouse=True)
def _forbid_real_input(monkeypatch):
    """★ **autouse**：每个测试都自动获得这层保护 —— 不可能漏掉。

    ⚠ 为什么要 `autouse` 而不是让测试自己声明：**漏一个就等于没保护**
      （本次事故正是「那个文件里 monkeypatch 出现 0 次」造成的）。
    ⚠ `sw_gui_input` 等模块是在**函数内** `import win32api` 的 ⇒ 拿到的是**同一个模块对象**
      ⇒ 在模块属性上打桩**能拦住**它们。
    """
    try:
        import win32api
    except ImportError:      # 没有 pywin32 的环境（如 CI 精简镜像）⇒ 本来就不可能注入
        yield
        return

    monkeypatch.setattr(win32api, "keybd_event", _record("keybd_event"), raising=False)
    monkeypatch.setattr(win32api, "mouse_event", _record("mouse_event"), raising=False)
    monkeypatch.setattr(win32api, "SetCursorPos", _record("SetCursorPos"), raising=False)
    yield


@pytest.fixture()
def input_log():
    """给需要断言「发了哪些键」的测试用：清空并返回记录列表。"""
    input_injection_log.clear()
    return input_injection_log
