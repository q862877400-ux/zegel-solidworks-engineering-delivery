"""量：GetFastenerTable 的三个入参分别是什么、返回什么。"""
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
    data = sw_connect.safe_get_com_member(sw, "GetHoleStandardsData", 0)
    std, names = byref(), byref()
    sw_connect.safe_get_com_member(data, "GetHoleStandards", std, names)
    tn = "ANSI Inch"
    a, b = byref(), byref()
    sw_connect.safe_get_com_member(data, "GetFastenerTypes", tn, a, b)
    ids = list(val(a))
    tid = int(ids[0])
    c = byref()
    sw_connect.safe_get_com_member(data, "GetFastenerTableTypes", tn, tid, c)
    kinds = list(val(c))
    print("  tid=%r kinds=%r" % (tid, kinds))

    # GetFastenerTable(String, Int32, Int32, Object&)
    for kind in kinds[:3]:
        d = byref()
        try:
            r = sw_connect.safe_get_com_member(data, "GetFastenerTable", tn, tid, int(kind), d)
            v = val(d)
            if isinstance(v, (list, tuple)):
                print("  GetFastenerTable(%r, %r, %r) -> %r · len=%d 前 6: %r"
                      % (tn, tid, kind, r, len(v), list(v)[:6]))
            else:
                print("  GetFastenerTable(%r, %r, %r) -> %r · %s: %r"
                      % (tn, tid, kind, r, type(v).__name__, str(v)[:90]))
        except Exception as exc:      # noqa: BLE001
            print("  GetFastenerTable(%r, %r, %r) ✗ %s" % (tn, tid, kind, str(exc)[:70]))
finally:
    try:
        sw.CommandInProgress = False
    except Exception:      # noqa: BLE001
        pass
