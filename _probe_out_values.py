"""量：GetHoleStandards 传对之后，两个出参里装的是什么。"""
import sys
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
import pythoncom
from win32com.client import VARIANT
import sw_connect


def byref():
    return VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)


sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
try:
    sw.CommandInProgress = True
except Exception:      # noqa: BLE001
    pass
try:
    data = sw_connect.safe_get_com_member(sw, "GetHoleStandardsData", 0)
    print("  data: %s" % type(data).__name__)
    a, b = byref(), byref()
    r = sw_connect.safe_get_com_member(data, "GetHoleStandards", a, b)
    print("  返回: %r" % (r,))
    for name, v in (("Standards", a), ("Types", b)):
        try:
            val = v.value
        except Exception as exc:      # noqa: BLE001
            print("  %-10s .value ✗ %s" % (name, str(exc)[:60])); continue
        print("  %-10s .value: %s = %r" % (name, type(val).__name__, str(val)[:120]))
        if hasattr(val, "__len__") and not isinstance(val, str):
            try:
                print("             len=%d · 前 3 个: %r" % (len(val), list(val)[:3]))
            except Exception as exc:      # noqa: BLE001
                print("             取元素 ✗ %s" % str(exc)[:60])
finally:
    try:
        sw.CommandInProgress = False
    except Exception:      # noqa: BLE001
        pass
