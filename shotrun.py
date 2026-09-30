import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui, shot
hwnd = 0
def cb(h, _):
    global hwnd
    if win32gui.IsWindowVisible(h) and win32gui.GetWindowText(h).upper().startswith("SOLIDWORKS"):
        hwnd = h
win32gui.EnumWindows(cb, None)
if not hwnd:
    print("  没有可见的 SOLIDWORKS 窗口"); raise SystemExit(1)
print("  hwnd=%d  %r" % (hwnd, win32gui.GetWindowText(hwnd)[:50]))
img, ok, w, h = shot.capture(hwnd, r"D:\AI\SW\shots\sw_capture.png")
px = img.getpixel((10, 10))
print("  PrintWindow 返回 %s" % ok)
print("  尺寸 %dx%d  左上角像素 %s" % (w, h, px))
sm = img.resize((160, int(160 * h / w)))
colors = len(set(sm.getdata()))
print("  缩小后颜色种类 %d %s" % (colors, "（过少，可能是空图）" if colors < 12 else "（有内容）"))