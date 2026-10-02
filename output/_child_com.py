
import sys, time
sys.stdout.reconfigure(encoding="utf-8")
import pythoncom, win32com.client as w
try:
    pythoncom.CoInitialize()
    app = w.GetActiveObject("SldWorks.Application")
    #: ★ `RevisionNumber` 是**属性**（迟到绑定下），不是方法 —— 加括号会 TypeError
    print("CHILD_OK rev=%s" % app.RevisionNumber)
    if "--hang" in sys.argv:
        print("CHILD_HANGING")
        sys.stdout.flush()
        time.sleep(3600)          #: ★ 故意卡住 —— 看主进程受不受影响
except Exception as e:
    print("CHILD_ERR %s: %s" % (type(e).__name__, str(e)[:120]))
