"""量：为什么同一个 GetFastenerTypes 早先 True、现在 False？"""
import sys
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
import pythoncom
from win32com.client import VARIANT
import sw_connect


def byref():
    return VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)


def val(v):
    return getattr(v, "value", None)


sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
try:
    sw.CommandInProgress = True
except Exception:      # noqa: BLE001
    pass
try:
    # A：拿到 data 后**直接**调 GetFastenerTypes
    d1 = sw_connect.safe_get_com_member(sw, "GetHoleStandardsData", 0)
    a, b = byref(), byref()
    r = sw_connect.safe_get_com_member(d1, "GetFastenerTypes", "ANSI Inch", a, b)
    print("  A 直接调   -> %r" % (r,))

    # B：同一对象先调 GetHoleStandards，再调 GetFastenerTypes
    d2 = sw_connect.safe_get_com_member(sw, "GetHoleStandardsData", 0)
    x, y = byref(), byref()
    sw_connect.safe_get_com_member(d2, "GetHoleStandards", x, y)
    c, e = byref(), byref()
    r2 = sw_connect.safe_get_com_member(d2, "GetFastenerTypes", "ANSI Inch", c, e)
    print("  B 先 GetHoleStandards 再调 -> %r · Types=%r" % (r2, (list(val(c))[:4] if val(c) else None)))

    # C：A 那一个对象，**再调一次**
    f, g = byref(), byref()
    r3 = sw_connect.safe_get_com_member(d1, "GetFastenerTypes", "ANSI Inch", f, g)
    print("  C A 的对象再调一次 -> %r" % (r3,))

    # D：换名字试（"ISO"）
    h, i2 = byref(), byref()
    r4 = sw_connect.safe_get_com_member(d1, "GetFastenerTypes", "ISO", h, i2)
    print("  D d1 换 'ISO' -> %r" % (r4,))
finally:
    try:
        sw.CommandInProgress = False
    except Exception:      # noqa: BLE001
        pass
