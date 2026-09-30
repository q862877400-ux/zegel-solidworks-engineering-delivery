import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import win32gui, win32api, win32con
from PIL import ImageGrab
warnings.filterwarnings("ignore")
# 直接问 win32：客户区原点在哪
import ctl
h, w = ctl.connect()
l,t,r,b = win32gui.GetWindowRect(h)
cl,ct,cr,cb = win32gui.GetClientRect(h)
ox,oy = win32gui.ClientToScreen(h,(0,0))
print("窗口 rect   : (%d,%d,%d,%d)  %dx%d" % (l,t,r,b,r-l,b-t))
print("客户区 rect : (0,0,%d,%d)  %dx%d" % (cr,cb,cr,cb))
print("客户区原点屏幕坐标: (%d,%d)" % (ox,oy))
print("DPI: %d" % (win32gui.GetDpiForWindow(h) if hasattr(win32gui,"GetDpiForWindow") else 96))
# 在客户区原点画个记号，截图看它落在哪
win32api.SetCursorPos((ox+20, oy+20)); time.sleep(0.3)
img = ImageGrab.grab()
px = img.load()
# 找光标附近的绿色标记不好找；改为：取 (ox+20,oy+20) 附近的像素与 (ox+200,oy+200) 比
print("图像尺寸: %s" % (img.size,))
print("像素(ox+20,oy+20)=%s   (ox+200,oy+200)=%s" % (px[ox+20,oy+20][:3], px[ox+200,oy+200][:3]))