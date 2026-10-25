"""读「对话框里的**文字内容**」—— 尤其是尺寸「修改」框里的**数值**。

## 为什么（根因 D）

PSR 只记「在某个控件上输入了键盘」，**不记输入了什么**：

```
| 36 | 21:54:06 | keyboard input on "RichEdit Control" in "修改" [... Enter] |
```

业主那次实操 4 次开「修改」框（输入 100 / 80 / 45 / 31.815），
`steps.md` 里**一个数字都没有**。而截图里明明能看到 `D3@草图1 = 31.81533422度`。

⇒ 根因是「把记录内容的职责外包给了一个不负责内容的工具」。
   修法：录制期自己**轮询读对话框控件文本**（含 RichEdit 的 WM_GETTEXT 内容）。

## 怎么读

```
EnumWindows            → 找候选对话框（按类名/标题特征）
EnumChildWindows       → 每个子控件的文本：GetWindowTextW
SendMessage(WM_GETTEXT)→ RichEdit / Edit 的内容（GetWindowText 常读不到）
```

## 用法

```python
from sw_dialog_text import read_dialogs
for d in read_dialogs():
    print(d["title"], d["fields"])
```
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（示教器 · 对话框文字读取）
# 文件:   scripts/sw_dialog_text.py
# 定位:   录制期读取对话框（尤其尺寸「修改」框）里的**实际文字/数值**。
#          起因：2026-10-26 PSR 只记「在修改框按了 Enter」，数值全丢（根因 D）。
# 官方依据: Win32 `EnumWindows` / `EnumChildWindows` / `GetWindowTextW` /
#          `SendMessageW(WM_GETTEXT)`；均为 user32 API，无第三方依赖。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

_u = ctypes.windll.user32
WM_GETTEXT = 0x000D
WM_GETTEXTLENGTH = 0x000E

#: 想要抓到的对话框标题特征（SolidWorks 尺寸「修改」框就是 `修改`）
WANTED_TITLES = ("修改", "Modify", "尺寸", "Dimension", "距离", "角度")
#: 值得读内容的控件类名（Edit/RichEdit 才有用户输入）
_TEXT_CLASSES = ("Edit", "RichEdit", "RichEdit20W", "RichEdit50W", "RICHEDIT50W",
                 "NECSPIN", "ComboBox")


def _title(hwnd) -> str:
    n = _u.GetWindowTextLengthW(hwnd)
    if n <= 0:
        return ""
    buf = ctypes.create_unicode_buffer(n + 1)
    _u.GetWindowTextW(hwnd, buf, n + 1)
    return buf.value


def _cls(hwnd) -> str:
    """控件类名 —— 复用 `tools/sw_guard.py` 的同一实现（避免两份重复代码）。"""
    import sys
    from pathlib import Path

    _tools = Path(__file__).resolve().parents[1] / "tools"
    if str(_tools) not in sys.path:
        sys.path.insert(0, str(_tools))
    from sw_guard import _cls as _guard_cls

    return _guard_cls(hwnd)


def _content(hwnd) -> str:
    """读控件内容：先 GetWindowTextW，读不到再发 WM_GETTEXT。"""
    s = _title(hwnd)
    if s:
        return s
    try:
        n = int(_u.SendMessageW(hwnd, WM_GETTEXTLENGTH, 0, 0))
        if n > 0:
            buf = ctypes.create_unicode_buffer(n + 1)
            _u.SendMessageW(hwnd, WM_GETTEXT, n + 1, buf)
            return buf.value
    except Exception:  # noqa: BLE001
        pass
    return ""


def _children(hwnd) -> list:
    """枚举直接子控件（回 [(类名, 内容)]）。"""
    out = []
    _wndenumproc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def cb(h, _l):
        cls = _cls(h)
        if any(c.lower() in cls.lower() for c in _TEXT_CLASSES):
            txt = _content(h)
            if txt:
                out.append((cls, txt))
        return True

    _u.EnumChildWindows(hwnd, _wndenumproc(cb), 0)
    return out


def read_dialogs() -> list:
    """回「可见 + 标题像 修改」的对话框（结构见下）。"""
    found = []
    _wndenumproc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def cb(hwnd, _l):
        if not _u.IsWindowVisible(hwnd):
            return True
        title = _title(hwnd)
        if not title:
            return True
        if not any(w in title for w in WANTED_TITLES):
            return True
        fields = _children(hwnd)
        if fields:
            found.append({"title": title, "class": _cls(hwnd), "fields": fields})
        return True

    _u.EnumWindows(_wndenumproc(cb), 0)
    return found


def numeric_fields(dlg: dict) -> list:
    """从对话框字段里挑出**像数值**的项（含小数点/度/毫米），供记录用。"""
    out = []
    for cls, txt in dlg.get("fields") or []:
        s = txt.strip()
        if not s:
            continue
        has_digit = any(ch.isdigit() for ch in s)
        looks_num = has_digit and (
            "." in s or "度" in s or "mm" in s.lower() or s.replace(".", "").isdigit())
        if looks_num:
            out.append({"control": cls, "text": s[:120]})
    return out


def snapshot() -> list:
    """录制期调用：回**所有**待记的对话框文字（含数值筛选结果）。"""
    rows = []
    for dlg in read_dialogs():
        rows.append({"title": dlg["title"], "class": dlg["class"],
                     "fields": [t for _c, t in dlg["fields"]][:12],
                     "numbers": numeric_fields(dlg)})
    return rows
