import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import win32gui, shot
hwnd = int(open(r"D:\AI\SW\_sw_hwnd.txt").read().strip())
print("  hwnd=%d  标题=%r" % (hwnd, win32gui.GetWindowText(hwnd)[:50]))
try:
    img, ok, w, h = shot.capture(hwnd, r"D:\AI\SW\shots\sw_capture.png")
    print("  PrintWindow 返回 %s   尺寸 %dx%d" % (ok, w, h))
    print("  左上角像素 %s" % (img.getpixel((10, 10)),))
    sm = img.resize((200, int(200 * h / w)))
    n = len(set(sm.getdata()))
    print("  缩小后颜色种类 %d  %s" % (n, "空图？" if n < 12 else "有内容 ✅"))
    img.save(r"D:\AI\SW\shots\sw_full.png")
except Exception as e:
    import traceback; traceback.print_exc()