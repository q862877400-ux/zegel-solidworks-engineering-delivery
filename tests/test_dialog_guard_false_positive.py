"""★ 弹窗判据的两个假阳性/漏处置边界（第 46–47 轮真机发现）。

## ① 欢迎页不是弹窗（第 47 轮）

实测：常驻监控 `pending_needs_llm` **永远停在 1**，枚举出来是

```
class=swWelcomeScreen  title=''
controls=[('Button','主页'),('Button','最近'),…,('Button','零件'),('Button','装配体'),…]
```

那是 SolidWorks 的**启动欢迎页**，有 20+ 个 Button ⇒ 被 `classify_dialog` 判成
`needs_llm` ⇒ **那个信号等于废掉**：真来一个需要人的弹窗时，人和脚本都分不出。

★ 这与「判据的假阳性会让真信号失效」同族（事实 53/62 一族）。

## ② 报告器弹窗点不干净（第 46 轮）

`SLDEXITAPP.exe` 的 `SOLIDWORKS Design 错误报告`（CEIP 遥测失败）**点掉即重弹**：
2 分钟内被点 **13 万余次**仍在弹。⇒ 处置改成**结束进程**。

## ③ 日志去重（第 46 轮）

同一弹窗每 2 秒写一行完整 JSON ⇒ `events.jsonl` 长到 **254 MB**。
⇒ 同一签名 60 秒内只落一行。

## 本文件钉什么

①②③ 都做**静态结构断言**（不连真机）：源码里必须有对应判据/常量。
★ 为什么不连真机：这三条要真的复现，得让 SolidWorks 崩一次（产生报告器框）
  或把欢迎页切出来 —— 前者是破坏性操作，不应为了测试做。
  行为级验证在 `tools/probe_dialog_watch_fixes.py`（去重 + 结束进程，已跑通）。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import sw_guard  # noqa: E402
import sw_dialog_watch as w  # noqa: E402


def _guard_src() -> str:
    return (REPO / "tools" / "sw_guard.py").read_text(encoding="utf-8")


def _watch_src() -> str:
    return (REPO / "tools" / "sw_dialog_watch.py").read_text(encoding="utf-8")


# ── ① 欢迎页 ─────────────────────────────────────────────────────────


def test_欢迎页类名在排除表里() -> None:
    """★★ 核心：`swWelcomeScreen` 不是弹窗，必须排除。

    ★ 若这条红了，`pending_needs_llm` 会重新永久停在 1。
    """
    src = _guard_src()
    assert '"swWelcomeScreen"' in src, (
        "★ 类名排除表里没有 swWelcomeScreen ⇒ 欢迎页会被判成 needs_llm 弹窗，"
        "pending_needs_llm 永远停在 1"
    )


def test_排除表仍是排除表() -> None:
    """★ 结构断言：那张表里必须仍是「不是弹窗」的类名，没有被改成别的东西。"""
    src = _guard_src()
    i = src.find('"swWelcomeScreen"')
    assert i > 0
    seg = src[max(0, i - 700):i + 200]
    assert "ToolbarWindow32" in seg, "★ 排除表应仍含已知的非弹窗类名（结构未被改坏）"


# ── ② 报告器 ─────────────────────────────────────────────────────────


def test_报告器清单存在且含_SLDEXITAPP() -> None:
    """★★ `SLDEXITAPP.exe` 的框点不干净 ⇒ 必须走「结束进程」而不是反复点。"""
    assert "sldexitapp.exe" in w._REPORTER_EXES, (
        "★ 报告器清单里没有 sldexitapp.exe ⇒ 会退回「点掉即重弹」的 13 万次循环"
    )


def test_有结束进程的实现() -> None:
    assert callable(w._terminate_process)
    src = _watch_src()
    assert "TerminateProcess" in src, "★ 没有真的结束进程 ⇒ 只是记了个字段"


def test_处置分支在点按钮之前() -> None:
    """★ 顺序问题：报告器分支必须在「auto 才点」之前，否则永远走不到。"""
    src = _watch_src()
    i_rep = src.find("terminated-reporter")
    i_auto = src.find('mode == "auto"')
    assert i_rep > 0, "★ 找不到报告器处置分支"
    assert i_auto > 0, "★ 找不到 auto 点按分支"
    assert i_rep < i_auto, (
        "★ 报告器分支排在 auto 之后 ⇒ 永远走不到（顺序问题会让判据静默失效）"
    )


# ── ③ 日志去重 ───────────────────────────────────────────────────────


def test_去重窗口是正数且有限() -> None:
    """★ 去重窗口要有限（否则真事件会被永久吞掉），也要够大（否则等于没去重）。"""
    assert 0 < w._DEDUPE_WINDOW_S <= 600, (
        "★ 去重窗口 = %r 不合理" % (w._DEDUPE_WINDOW_S,)
    )


def test_同签名在窗口内只记一次() -> None:
    """★ 行为断言：同一签名连写 5 次，只第一次返回 True。"""
    w._recent.clear()
    row = {
        "exe": "SLDEXITAPP.exe",
        "class": "#32770",
        "title": "SOLIDWORKS Design 错误报告",
        "controls": [
            {"class": "Button", "text": "确定"},
            {"class": "Static", "text": "CEIP 发送失败"},
        ],
    }
    verdicts = [w._should_log(dict(row)) for _ in range(5)]
    assert verdicts == [True, False, False, False, False], (
        "★ 去重没生效：%r" % (verdicts,)
    )


def test_不同签名各自记录() -> None:
    """★ 不该误伤：不同标题的弹窗要各记一条。"""
    w._recent.clear()
    base = {"exe": "SLDWORKS.exe", "class": "#32770", "controls": []}
    a = dict(base, title="A")
    b = dict(base, title="B")
    assert w._should_log(a) is True
    assert w._should_log(b) is True, "★ 不同弹窗被吞了"


def test_签名不含_hwnd() -> None:
    """★★ 重弹时 `hwnd` 会变 —— 若签名含 `hwnd`，去重就永远不命中。"""
    row = {
        "hwnd": 111,
        "exe": "SLDEXITAPP.exe",
        "class": "#32770",
        "title": "T",
        "controls": [{"class": "Static", "text": "x"}],
    }
    other = dict(row, hwnd=999)
    assert w._signature(row) == w._signature(other), (
        "★ 签名里混进了 hwnd ⇒ 重弹的同一个框会各记一行"
    )


def test_签名取第一个非按钮文本() -> None:
    """★ 判据要贴合「同一个框」的本质：按钮文字变化不影响，说明文字变化才影响。"""
    row = {
        "exe": "x.exe",
        "class": "#32770",
        "title": "T",
        "controls": [
            {"class": "Button", "text": "确定"},
            {"class": "Static", "text": "第一句"},
        ],
    }
    changed_button = dict(
        row,
        controls=[
            {"class": "Button", "text": "知道了"},
            {"class": "Static", "text": "第一句"},
        ],
    )
    assert w._signature(row) == w._signature(changed_button), "★ 按钮文字不该进签名"


def test_源码里_append_走去重() -> None:
    """★ 结构断言：`_append` 必须先过 `_should_log`，否则去重只是摆设。"""
    src = _watch_src()
    i = src.find("def _append(")
    assert i > 0
    seg = src[i:i + 900]
    assert "_should_log(" in seg, "★ `_append` 没有调 `_should_log` ⇒ 日志仍会暴涨"
    assert re.search(r"if not _should_log", seg), "★ 去重判断没包成 early-return"
