"""关掉「修改尺寸」框（ESC），然后**复核尺寸数** —— 判 `Extension.AddDimension` 是否真建成了。

## 为什么需要这个

第 52 轮实测：`IModelDocExtension.AddDimension` 调用后**没有崩**，
而是弹出 SolidWorks 的「修改」属性框（控件树 `BUTTON × 3 · SLIDER · THUMB WHEEL`，
全是资源占位符）⇒ 分级为 `needs_llm`，护栏不点 ⇒ 调用阻塞。

★ 这个框**本身就是「尺寸已创建」的信号** —— SolidWorks 建完尺寸会立刻让你输数值。

## 做法

① 找到那个框的 hwnd，发 `WM_KEYDOWN/UP VK_ESCAPE`（等价人手按 ESC）
② 再发一次 ESC 退出草图编辑
③ 读草图的显示尺寸数 —— 0 → 1 才算真建成

★ 不点任何 BUTTON：那是数值框，点错会改模型。
"""
from __future__ import annotations

import ctypes
import json
import sys
import time
from ctypes import wintypes
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))
sys.path.insert(0, str(R / "tools"))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 关掉「修改尺寸」框并复核尺寸数）
# 文件:   tools/close_modify_box_and_count.py
# 定位:   `Extension.AddDimension` 建完尺寸会弹 SolidWorks「修改」属性框（占位符控件，
#         分级 needs_llm ⇒ 护栏不点）⇒ 调用阻塞。本脚本按 ESC 关掉它，再回读尺寸数。
# 官方依据: 不适用（Win32 消息 + 本仓既有 `_dim_count`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

_DIM = R / "output" / "modify-box-close.json"
VK_ESCAPE = 0x1B
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101

import sw_connect as c_  # noqa: E402
import sw_guard as g  # noqa: E402
from probe_hv_dimension_with_selection import _dim_count  # noqa: E402


def _send_esc(hwnd: int) -> bool:
    u = ctypes.windll.user32
    u.PostMessageW(hwnd, WM_KEYDOWN, VK_ESCAPE, 0)
    u.PostMessageW(hwnd, WM_KEYUP, VK_ESCAPE, 0)
    return True


def _main_frame_hwnd() -> int:
    """★ 找 SolidWorks 主框架窗口（class 以 Afx: 开头、标题含 SOLIDWORKS）。"""
    u = ctypes.windll.user32
    out = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def _cb(h, _l):
        if not u.IsWindowVisible(h):
            return True
        cls = ctypes.create_unicode_buffer(256)
        u.GetClassNameW(h, cls, 256)
        if not cls.value.startswith("Afx:"):
            return True
        n = u.GetWindowTextLengthW(h)
        if n <= 0:
            return True
        buf = ctypes.create_unicode_buffer(n + 1)
        u.GetWindowTextW(h, buf, n + 1)
        if "SOLIDWORKS" in buf.value.upper():
            out.append(int(h))
        return True

    u.EnumWindows(_cb, 0)
    return out[0] if out else 0


def main() -> int:
    ev: dict = {"probe": "close-modify-box"}
    conn = c_.connect_solidworks(wait_seconds=20)
    sw = conn[0] if isinstance(conn, tuple) else conn
    try:
        sw.CommandInProgress = True
    except Exception:  # noqa: BLE001
        pass

    doc = None
    try:
        doc = c_.get_com_member(sw, "ActiveDoc")
        ev["doc_title"] = str(c_.get_com_member(doc, "GetTitle") or "") if doc else None
        print("① 活动文档：%s" % ev["doc_title"])

        #: ① 关掉那个「修改」框
        found = g.scan_family_windows(None)
        ev["windows"] = [
            {"class": d.get("class"), "title": d.get("title"), "hwnd": d.get("hwnd")}
            for d in found
        ]
        for w in found:
            _send_esc(int(w.get("hwnd") or 0))
            print("   ESC → hwnd=%s class=%s" % (w.get("hwnd"), w.get("class")))
            time.sleep(0.4)

        #: ② 再 ESC 一次退出草图编辑（只在该退的时候）
        for _ in range(2):
            time.sleep(0.4)
            try:
                sk = c_.get_com_member(doc, "GetActiveSketch2")
            except Exception:  # noqa: BLE001
                sk = None
            if sk is None:
                break
            #: ★ ISldWorks.GetActiveWindow **不存在**（实测 AttributeError）
            #:   ⇒ 直接找 SolidWorks 主框架窗口（class 以 Afx: 开头那个）
            main = _main_frame_hwnd()
            if main:
                _send_esc(main)
                print("   ESC（退草图）→ hwnd=%s" % main)

        #: ③ 复核尺寸数
        left = g.scan_family_windows(None)
        ev["windows_after"] = [{"class": d.get("class")} for d in left]
        n = _dim_count(doc) if doc is not None else -1
        ev["dim_count"] = n
        ev["ok"] = n >= 1
        ev["conclusion"] = (
            "★ 尺寸已建成（当前草图显示尺寸 %s 个）⇒ `Extension.AddDimension` 可用，"
            "之前「崩」其实是被这个「修改」框挡住" % n
            if ev["ok"]
            else "★ 尺寸仍为 %s ⇒ 这一次没建成（但进程没崩）" % n
        )
        print("② " + ev["conclusion"])
        return 0 if ev["ok"] else 1
    finally:
        if doc is not None:
            try:
                ttl = str(c_.get_com_member(doc, "GetTitle") or "")
                if ttl:
                    sw.CloseDoc(ttl)
            except Exception:  # noqa: BLE001
                pass
        if sw is not None:
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
            try:
                ev["docs_left"] = c_.open_doc_count(sw)
            except Exception:  # noqa: BLE001
                pass
        _DIM.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("   证据已写：%s" % _DIM)


if __name__ == "__main__":
    raise SystemExit(main())
