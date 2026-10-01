"""量：GetFastenerTableTypes 的第二个 Int32 到底用哪个数。"""
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
    ids, sizes = list(val(a)), list(val(b))
    print("  Types(ids) = %r" % (ids[:6],))
    print("  Sizes      = %r" % (sizes[:3],))

    # 试三种候选当那个 Int32
    for label, n in (("Types[0]", ids[0]), ("index 0", 0), ("Types[2]", ids[2])):
        c = byref()
        try:
            r = sw_connect.safe_get_com_member(data, "GetFastenerTableTypes", tn, int(n), c)
            v = val(c)
            print("  GetFastenerTableTypes(%r, %s=%r) -> %r · TableTypes=%s"
                  % (tn, label, n, r, ("len=%d 前 4: %r" % (len(v), list(v)[:4]))
                     if isinstance(v, (list, tuple)) else repr(v)))
        except Exception as exc:      # noqa: BLE001
            print("  GetFastenerTableTypes(%r, %s=%r) ✗ %s" % (tn, label, n, str(exc)[:70]))
finally:
    try:
        sw.CommandInProgress = False
    except Exception:      # noqa: BLE001
        pass
