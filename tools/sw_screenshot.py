"""把 SolidWorks 主窗口截成 PNG —— 用视觉看它**实际**显示了什么。

## 为什么需要（换了路数）

配合那条我一直在**盲试返回值**（`CreateMate` 回 `None`），从没看过屏幕上发生了什么：
是不是弹了个框？PropertyManager 停在某个状态？还是根本没反应？

★ 用户提示可以用截图 + 视觉。这是对的做法：**返回值不等于实际结果**这条教训，
  用在这里就是「API 返回 None ≠ 界面没反应」。

## 手法

`PrintWindow(hwnd, hdc, PW_RENDERFULLCONTENT=2)` —— 被别的窗口遮住也能拍到内容
（比 `CopyFromScreen` 截图整屏更可靠，也不会受用户正在看什么影响）。

## 用法

```
python -B tools/sw_screenshot.py                # 存 output/shots/sw-<时间>.png
python -B tools/sw_screenshot.py --out x.png    # 指定路径
```

★ 只截图，**不点任何东西**、不改模型。
"""
from __future__ import annotations

import ctypes
import sys
import time
from ctypes import wintypes
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
OUT_DIR = R / "output" / "shots"


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · SolidWorks 窗口截图）
# 文件:   tools/sw_screenshot.py
# 定位:   把 SolidWorks 主窗口截成 PNG 供视觉检查 —— 配合那条一直盲试返回值，
#          需要看界面实际状态（是否弹框 / PropertyManager 停在哪）。
# 官方依据: 不适用（Win32 `PrintWindow` / `GetWindowRect`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

u = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

PW_RENDERFULLCONTENT = 0x00000002
SRCCOPY = 0x00CC0020


class _RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


def _cls(h: int) -> str:
    b = ctypes.create_unicode_buffer(256)
    u.GetClassNameW(h, b, 256)
    return b.value


def _title(h: int) -> str:
    n = u.GetWindowTextLengthW(h)
    b = ctypes.create_unicode_buffer(n + 1)
    u.GetWindowTextW(h, b, n + 1)
    return b.value


def find_sw_window() -> int:
    """★ 找 SolidWorks 主框架窗口：class 以 `Afx:` 开头且标题含 SOLIDWORKS。"""
    hits: list = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def _cb(h, _l):
        if not u.IsWindowVisible(h):
            return True
        if _cls(h).startswith("Afx:") and "SOLIDWORKS" in _title(h).upper():
            hits.append(int(h))
        return True

    u.EnumWindows(_cb, 0)
    return hits[0] if hits else 0


def capture(hwnd: int, out: Path) -> tuple:
    """★ `PrintWindow` 拍到 `out`。返回 `(ok, w, h, err)`。"""
    r = _RECT()
    if not u.GetWindowRect(hwnd, ctypes.byref(r)):
        return False, 0, 0, "GetWindowRect 失败"
    w, h = r.right - r.left, r.bottom - r.top
    if w <= 0 or h <= 0:
        return False, 0, 0, "窗口尺寸为 0（可能被最小化）"

    hdc_screen = u.GetWindowDC(hwnd)
    hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
    hbmp = gdi32.CreateCompatibleBitmap(hdc_screen, w, h)
    gdi32.SelectObject(hdc_mem, hbmp)
    try:
        ok = bool(u.PrintWindow(hwnd, hdc_mem, PW_RENDERFULLCONTENT))
        if not ok:
            #: 退路：直接位块拷贝（要求窗口未被遮挡，但至少能出图）
            gdi32.BitBlt(hdc_mem, 0, 0, w, h, hdc_screen, 0, 0, SRCCOPY)

        #: 用 GDI 把 HBITMAP 落成 PNG（不引入 PIL）
        from struct import pack

        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [
                ("biSize", wintypes.DWORD),
                ("biWidth", wintypes.LONG),
                ("biHeight", wintypes.LONG),
                ("biPlanes", wintypes.WORD),
                ("biBitCount", wintypes.WORD),
                ("biCompression", wintypes.DWORD),
                ("biSizeImage", wintypes.DWORD),
                ("biXPelsPerMeter", wintypes.LONG),
                ("biYPelsPerMeter", wintypes.LONG),
                ("biClrUsed", wintypes.DWORD),
                ("biClrImportant", wintypes.DWORD),
            ]

        class BITMAPINFO(ctypes.Structure):
            _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", wintypes.DWORD * 3)]

        bi = BITMAPINFO()
        bi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bi.bmiHeader.biWidth = w
        bi.bmiHeader.biHeight = -h           #: 负值 = 自上而下
        bi.bmiHeader.biPlanes = 1
        bi.bmiHeader.biBitCount = 32
        bi.bmiHeader.biCompression = 0       #: BI_RGB
        buf = ctypes.create_string_buffer(w * h * 4)
        gdi32.GetDIBits(hdc_mem, hbmp, 0, h, buf, ctypes.byref(bi), 0)

        #: 写 PNG（zlib 压缩，纯标准库）
        import zlib

        raw = bytearray()
        for y in range(h):
            raw.append(0)                    #: filter=None
            row = buf.raw[y * w * 4:(y + 1) * w * 4]
            #: BGRA → RGB
            for x in range(w):
                raw += bytes((row[x * 4 + 2], row[x * 4 + 1], row[x * 4]))

        def chunk(tag: bytes, data: bytes) -> bytes:
            return (
                pack(">I", len(data))
                + tag
                + data
                + pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
            )

        png = b"\x89PNG\r\n\x1a\n"
        png += chunk(b"IHDR", pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
        png += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
        png += chunk(b"IEND", b"")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(png)
        return True, w, h, ""
    finally:
        gdi32.DeleteObject(hbmp)
        gdi32.DeleteDC(hdc_mem)
        u.ReleaseDC(hwnd, hdc_screen)


def main() -> int:
    out_arg = ""
    if "--out" in sys.argv:
        k = sys.argv.index("--out")
        if k + 1 < len(sys.argv):
            out_arg = sys.argv[k + 1]
    hwnd = find_sw_window()
    if not hwnd:
        print("★ 找不到 SolidWorks 主窗口")
        return 2
    out = Path(out_arg) if out_arg else OUT_DIR / ("sw-%s.png" % time.strftime("%H%M%S"))
    ok, w, h, err = capture(hwnd, out)
    if ok:
        print("已截图：%s（%dx%d）" % (out, w, h))
        return 0
    print("★ 截图失败：%s" % err)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
