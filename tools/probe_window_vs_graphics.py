r"""@brief 探针：`SaveBMP(0,0)` 与 `SaveAs3` 的宽度差，是不是「窗口 vs 绘图区」？

## 待解的疑问（轮 146/147 留下的「未查明」）
```
同一份文档、同一个时刻：
  SaveBMP(0,0)  ⇒ (1460, 1049)
  SaveAs3 → png ⇒ (1232, 1049)
⇒ **高度一致、宽度差 228**
★ 假设：前者按**窗口**（含侧边面板/工具栏），后者按**绘图区**。
⚠ 轮 147 **没有验证**它 —— 本轮专门验。
```

## 判法（**有对照**，不是"看起来像"）
```
① 用 `EnumWindows` 按 PID 找 SolidWorks **主窗口** ⇒ 读 `GetWindowRect` ⇒ 窗口宽 W_win
② ★ 断言关系：
     SaveBMP(0,0).宽  ==  W_win.宽   ?   ⇒ 若成立 ⇒ **BMP 按窗口**（假设的第一半证成）
     SaveAs3.png.宽   <   W_win.宽   ⇒ 且**高度一致** ⇒ 与"绘图区"相符
③ ★★ **更强的一步**：把窗口**改宽度**再量一次
     ⇒ 若两者都跟着变、且 **BMP 的变化量 == 窗口的变化量** ⇒ 关系**成立**（不只是巧合）
```

## ⚠ 安全
**只在新零件上跑**；改窗口尺寸后**改回去**；收尾**关件不保存** + **查模态框**。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_window_vs_graphics.py
# 定位:   给 Spec Kit `067` 解掉轮 146/147 的「未查明」。
# 官方依据: `IModelDoc2.SaveBMP`（Remarks：宽高 ≤ 0 ⇒ 按窗口）·
#          `IModelDocExtension.SaveAs3`（无尺寸入参）· Win32 `GetWindowRect`/`SetWindowPos`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes as w
import json
import struct
import sys
import time
from pathlib import Path

from sw_guard import sw_pid

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "window-vs-graphics.json")
BMP = Path(Path(__file__).resolve().parents[1] / "output" / "probe-win.bmp")
PNG = Path(Path(__file__).resolve().parents[1] / "output" / "probe-win.png")
W, H, D = 100.0, 60.0, 20.0
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main_windows(pid: int) -> list:
    """该 PID 的**可见顶层窗口** `(hwnd, 类名, 标题, 宽, 高)`。"""
    u = ctypes.windll.user32
    out: list = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, w.HWND, w.LPARAM)
    def cb(h, _l):
        p = w.DWORD()
        u.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid and u.IsWindowVisible(h):
            cls = ctypes.create_unicode_buffer(128)
            u.GetClassNameW(h, cls, 128)
            txt = ctypes.create_unicode_buffer(256)
            u.GetWindowTextW(h, txt, 256)
            r = w.RECT()
            u.GetWindowRect(h, ctypes.byref(r))
            out.append((h, cls.value, txt.value, r.right - r.left, r.bottom - r.top))
        return True

    u.EnumWindows(cb, 0)
    return out


def bmp_size(path: Path):
    b = path.read_bytes()[:26]
    if len(b) < 26 or b[:2] != b"BM":
        return None
    return tuple(abs(v) for v in struct.unpack_from("<ii", b, 18))


def png_size(path: Path):
    b = path.read_bytes()[:24]
    if len(b) < 24 or b[:8] != PNG_MAGIC:
        return None
    return struct.unpack_from(">II", b, 16)


def modal_dialogs() -> tuple:
    """★ 已改为**委托共享实现**（2026-10-01 轮 149）。"""
    try:
        from scripts.sw_connect import residual_dialogs
    except ImportError:
        from sw_connect import dismiss_residual_dialogs, residual_dialogs
    #: ★ 2026-10-01（轮 169）：**查到了就点掉**（兜底）——
    #: 只查不点的脚本在真发现弹窗时**什么也没处置**，弹窗还在 ⇒ 下一轮挂在这儿。
    _dialogs, _scanned = residual_dialogs()
    if _dialogs:
        dismiss_residual_dialogs()
    return _dialogs, _scanned


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "rounds": []}
    sw = None
    doc = None
    orig_rect = None
    hwnd = None
    try:
        import sw_connect

        from scripts import sw_export, sw_part

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")
        sw_part.start_sketch(doc)
        sw_part.sketch_corner_rectangle(doc, 0.0, 0.0, W, H)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, "草图1", D)

        #: ① 找主窗口（**面积最大**的那个是主框架）
        wins = main_windows(sw_pid())
        if not wins:
            print("  ⚠ 没找到 SolidWorks 的可见顶层窗口")
            return 1
        hwnd, cls, title, ww, wh = max(wins, key=lambda x: x[3] * x[4])
        print(
            "  SolidWorks 主窗口: class=%s 标题=%r 尺寸=%dx%d"
            % (cls, title[:40], ww, wh)
        )
        ev["window"] = {"class": cls, "title": title[:60], "w": ww, "h": wh}

        u = ctypes.windll.user32
        r = w.RECT()
        u.GetWindowRect(hwnd, ctypes.byref(r))
        orig_rect = (r.left, r.top, r.right, r.bottom)

        def measure(tag):
            for f in (BMP, PNG):
                if f.exists():
                    f.unlink()
            sw_export.export_to_bmp(doc, BMP, 0, 0)
            sw_export.export_to_image(doc, PNG)
            b = bmp_size(BMP)
            p = png_size(PNG)
            rr = w.RECT()
            u.GetWindowRect(hwnd, ctypes.byref(rr))
            row = {
                "tag": tag,
                "win_w": rr.right - rr.left,
                "win_h": rr.bottom - rr.top,
                "bmp": b,
                "png": p,
            }
            ev["rounds"].append(row)
            print(
                "     %-14s 窗口 %dx%d · BMP(0,0)=%s · PNG=%s"
                % (tag, row["win_w"], row["win_h"], b, p)
            )
            return row

        print()
        print("  ── ① 原尺寸 ──")
        a = measure("原尺寸")

        #: ② ★★ 改窗口宽度（+200）再量 —— 有对照才叫验证
        print()
        print("  ── ② 把窗口**加宽 200px** 再量 ──")
        u.SetWindowPos(hwnd, 0, 0, 0, (a["win_w"] + 200), a["win_h"], 0x0004 | 0x0010)
        time.sleep(1.5)
        b = measure("加宽 200")

        #: ③ 复原
        print()
        print("  ── ③ 复原窗口 ──")
        u.SetWindowPos(
            hwnd,
            0,
            orig_rect[0],
            orig_rect[1],
            orig_rect[2] - orig_rect[0],
            orig_rect[3] - orig_rect[1],
            0x0004 | 0x0010,
        )
        time.sleep(1.0)
        measure("复原后")

        #: ── 判定（**只看关系，不猜**）──
        print()
        print("  ── 判定 ──")
        dwin = b["win_w"] - a["win_w"]
        dbmp = (b["bmp"][0] - a["bmp"][0]) if (a["bmp"] and b["bmp"]) else None
        dpng = (b["png"][0] - a["png"][0]) if (a["png"] and b["png"]) else None
        print(
            "     窗口宽变化 %+d · BMP 宽变化 %s · PNG 宽变化 %s" % (dwin, dbmp, dpng)
        )
        ev["deltas"] = {"window": dwin, "bmp": dbmp, "png": dpng}
        #: ① BMP(0,0) 是否 == 窗口宽？
        print(
            "     ① BMP(0,0).宽 == 窗口宽?  %s（%s vs %s）"
            % (
                a["bmp"] and a["bmp"][0] == a["win_w"],
                a["bmp"][0] if a["bmp"] else "?",
                a["win_w"],
            )
        )
        #: ② BMP 的变化量是否 == 窗口的变化量？
        print("     ② BMP 宽的变化量 == 窗口的变化量?  %s" % (dbmp == dwin))
        #: ③ PNG 是否不随窗口变化（若按**绘图区**且绘图区跟着窗口变，则它也应变化）
        print("     ③ PNG 宽是否也变了?  %s（变化 %s）" % (dpng not in (None, 0), dpng))
        print()
        print(
            "     ⚠ **只报关系，不下'一定是绘图区'的结论** —— "
            "本探针量的是「跟不跟着窗口走」。"
        )
    except Exception as exc:  # noqa: BLE001
        print("  ⚠ 探针出错：%s: %s" % (type(exc).__name__, str(exc)[:180]))
    finally:
        try:
            u = ctypes.windll.user32
            if hwnd and orig_rect:
                u.SetWindowPos(
                    hwnd,
                    0,
                    orig_rect[0],
                    orig_rect[1],
                    orig_rect[2] - orig_rect[0],
                    orig_rect[3] - orig_rect[1],
                    0x0004 | 0x0010,
                )
        except Exception:  # noqa: BLE001
            pass
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
                    print("   （已关闭临时零件 %s，不保存）" % t)
        except Exception:  # noqa: BLE001
            pass

    modals, _win_scanned = modal_dialogs()
    print(
        "   收尾模态框: %s（扫了 %d 个窗口）"
        % ("无" if not modals else modals, _win_scanned)
    )
    ev["modal_dialogs"] = modals
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("   证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
