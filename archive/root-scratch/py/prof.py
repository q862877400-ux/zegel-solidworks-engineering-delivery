import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\AI\SW")
import ctl
warnings.filterwarnings("ignore")
t=time.time(); h,w = ctl.connect(); print("uia connect: %.1fs" % (time.time()-t))
# A: 全树 descendants
t=time.time(); n=len(list(w.descendants())); print("A 全树 descendants: %.1fs (%d)" % (time.time()-t, n))
# B: children() 只一层
t=time.time()
try:
    n=len(list(w.children())); print("B children() 一层: %.1fs (%d)" % (time.time()-t, n))
except Exception as e: print("B 失败", str(e)[:40])
# C: 只取元素属性不取 children
t=time.time()
c0=list(w.children())[:1]
for c in c0:
    _=c.element_info.control_type; _=c.window_text(); _=c.rectangle()
print("C 单控件读三个属性: %.2fs" % (time.time()-t))
# D: win32 后端另开一个连接
t=time.time()
try:
    from pywinauto import Application
    app2 = Application(backend="win32").connect(process=h and None or None, handle=h)
    print("D win32 connect: %.1fs" % (time.time()-t))
    w2 = app2.window(handle=h)
    t=time.time(); n2=len(list(w2.descendants())); print("D win32 descendants: %.1fs (%d)" % (time.time()-t, n2))
except Exception as e:
    print("D win32 失败:", str(e)[:60])