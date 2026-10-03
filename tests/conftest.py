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
from pathlib import Path

import pytest

# ── ★★★★★★ 2026-10-04（轮 111）**在这里加 `sys.path`** —— 一处修、★ 16 个文件都好 ──────
# ★ **起因（★ 可核）**：★ 轮 110 我改了 `scripts/sw_drawing_view.py` 之后**单跑**
#   `tests/test_sw_drawing_view_contract.py` ⇒ ★★ **12 failed** ⇒ 看着像我改坏了 ✓
#   ★★★ **真因**：★ 那个文件 L83 `import sw_connect` ⇒
#     ★ **而它自己没把 `scripts/` 加进 `sys.path`** ⇒
#     ★★★★ **⇒ 那是**预先存在的**测试顺序依赖****（★ 与**事实 57**同族：
#       ★ "一直是绿的、只是环境恰好满足" —— ★ 同进程里**别的测试文件**加过 path）✓
#   ★★★★★ **静态扫出来的数**（★ `output/_audit_test_syspath.py`）：
#     · ★ 测试文件 **225 个** ⇒ ★★ **16 个**「导入了 `scripts/` 模块却**没自己加 `path`**」·
#     · ★★ **对照 94 个**自己加了 ⇒ ★★★ **⇒ 那 16 个是**少数派**** ✓
#     · ★★★ 名单里包括 `test_sw_mold_contract.py` · `test_sw_sketch_contract.py` ·
#       `test_sw_simulation_*_contract.py`（★ 4 个）· `test_sw_routing_contract.py` …
#   ★★★★★★ **⇒ 正解是**一处修、★ 处处好****：★ `tests/conftest.py` 是 pytest 的
#     **标准入口**、★ 它在**每个测试文件被导入之前**执行 ⇒
#     ★★ **在这里把三个目录加进 `sys.path`，★ 那 16 个文件一次性都好** ✓
#   ★★★★★ **⚠ 而本文件**早就有 `import sys`**（★ 原第 37 行）、★ **却一次都没用它** ——
#     ★★ **那正是"准备好加、★ 而没加"的痕迹** ✓
#   ★★★★ **⇒ 可复用判据**：★★★ **"一个 `import` 了却没用过的库，往往是一条**没走完的路**** ✓
#     （★ 与**事实 62**「写了不等于有效」**同族**）✓
#   ⚠ **本改动只影响测试进程的 `sys.path`、★ 不影响运行时**（★ 本文件不被任何 `scripts/` 代码导入）✓
_HERE = Path(__file__).resolve().parent
for _d in (_HERE.parent, _HERE.parent / "scripts", _HERE.parent / "mcp-server"):
    if _d.is_dir() and str(_d) not in sys.path:
        sys.path.insert(0, str(_d))
# ─────────────────────────────────────────────────────────────────────────────

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
