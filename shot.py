# -*- coding: utf-8 -*-
"""不受遮挡地抓 SolidWorks 窗口：ctypes 直接调 GDI + PrintWindow。

⚠ pywin32 的 ``win32ui`` **不含** GDI 绘图函数（无 CreateCompatibleDC），
   所以这里全用 ctypes 调 user32/gdi32。
"""
import ctypes
import sys
from ctypes import wintypes

sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
# ⚠⚑ 64 位下 GDI/USER 句柄是 64 位；ctypes 的 restype/argtypes 默认按 32 位
#   ⇒ 不声明就报 "int too long to convert"。
#   逐个按**真实签名**声明（不要图省事统一套，那个会让调用错位）。
c_void_p = ctypes.c_void_p
c_int = ctypes.c_int
c_uint = ctypes.c_uint
gdi32.CreateCompatibleDC.restype = c_void_p
gdi32.CreateCompatibleDC.argtypes = [c_void_p]
gdi32.CreateCompatibleBitmap.restype = c_void_p
gdi32.CreateCompatibleBitmap.argtypes = [c_void_p, c_int, c_int]
gdi32.SelectObject.restype = c_void_p
gdi32.SelectObject.argtypes = [c_void_p, c_void_p]
gdi32.DeleteObject.argtypes = [c_void_p]
gdi32.DeleteDC.argtypes = [c_void_p]
gdi32.GetDIBits.restype = c_int
gdi32.GetDIBits.argtypes = [c_void_p, c_void_p, c_uint, c_uint,
                            c_void_p, c_void_p, c_uint]
user32.GetWindowDC.restype = c_void_p
user32.GetWindowDC.argtypes = [c_void_p]
user32.ReleaseDC.argtypes = [c_void_p, c_void_p]
user32.PrintWindow.restype = ctypes.c_bool
user32.PrintWindow.argtypes = [c_void_p, c_void_p, c_uint]

SRCCOPY = 0x00CC0020
DIB_RGB_COLORS = 0
PW_RENDERFULLCONTENT = 2


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", wintypes.DWORD), ("biWidth", ctypes.c_long),
                ("biHeight", ctypes.c_long), ("biPlanes", wintypes.WORD),
                ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
                ("biSizeImage", wintypes.DWORD),
                ("biXPelsPerMeter", ctypes.c_long),
                ("biYPelsPerMeter", ctypes.c_long),
                ("biClrUsed", wintypes.DWORD), ("biClrImportant", wintypes.DWORD)]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER),
                ("bmiColors", wintypes.DWORD * 3)]


def capture(hwnd: int, path: str = None) -> Image.Image:
    """抓窗口自身内容（PW_RENDERFULLCONTENT 能拿到 DWM 合成界面）。"""
    import win32gui
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    w, h = right - left, bottom - top
    if w <= 0 or h <= 0:
        raise ValueError("窗口尺寸异常 %dx%d" % (w, h))

    hwndDC = user32.GetWindowDC(hwnd)
    memDC = gdi32.CreateCompatibleDC(hwndDC)
    bmp = gdi32.CreateCompatibleBitmap(hwndDC, w, h)
    old = gdi32.SelectObject(memDC, bmp)
    ok = user32.PrintWindow(hwnd, memDC, PW_RENDERFULLCONTENT)

    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = w
    bmi.bmiHeader.biHeight = -h          # 负数 = 自上而下
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 32
    bmi.bmiHeader.biCompression = 0      # BI_RGB

    buf = ctypes.create_string_buffer(w * h * 4)
    got = gdi32.GetDIBits(memDC, bmp, 0, h, buf, ctypes.byref(bmi), DIB_RGB_COLORS)

    gdi32.SelectObject(memDC, old)
    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(memDC)
    user32.ReleaseDC(hwnd, hwndDC)

    if not got:
        raise RuntimeError("GetDIBits 失败")
    img = Image.frombuffer("RGB", (w, h), buf, "raw", "BGRX", 0, 1)
    if path:
        img.save(path)
    return img, bool(ok), w, h
