"""量：孔标准 → 紧固件类型 → 尺寸 → 表类型 → 表，这条链每一步要什么、返回什么。"""
import sys
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
import pythoncom
from win32com.client import VARIANT
import sw_connect


def byref():
    return VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)


def show(name, v):
    val = getattr(v, "value", "<no .value>")
    if isinstance(val, (list, tuple)):
        print("    %-12s len=%d 前 4: %r" % (name, len(val), list(val)[:4]))
    else:
        print("    %-12s %r" % (name, val))


sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
try:
    sw.CommandInProgress = True
except Exception:      # noqa: BLE001
    pass
try:
    data = sw_connect.safe_get_com_member(sw, "GetHoleStandardsData", 0)
    std, names = byref(), byref()
    sw_connect.safe_get_com_member(data, "GetHoleStandards", std, names)
    nms = list(names.value)
    print("  标准名（前 8）: %r" % (nms[:8],))

    # ① 紧固件类型：table_name 用**名字**试
    for tn in (nms[0], nms[6] if len(nms) > 6 else nms[0]):
        a, b = byref(), byref()
        r = sw_connect.safe_get_com_member(data, "GetFastenerTypes", tn, a, b)
        print("  GetFastenerTypes(%r) -> %r" % (tn, r))
        show("Types", a)
        show("Sizes", b)
        if r and isinstance(b.value, (list, tuple)) and len(b.value):
            size = list(b.value)[0]
            # ② 表类型
            c = byref()
            r2 = sw_connect.safe_get_com_member(data, "GetFastenerTableTypes", tn, size, c)
            print("  GetFastenerTableTypes(%r, %r) -> %r" % (tn, size, r2))
            show("TableTypes", c)
            # ③ 表本体
            if r2 and isinstance(c.value, (list, tuple)) and len(c.value):
                kind = list(c.value)[0]
                d = byref()
                r3 = sw_connect.safe_get_com_member(data, "GetFastenerTable", tn, size, kind, d)
                print("  GetFastenerTable(%r, %r, %r) -> %r" % (tn, size, kind, r3))
                show("TableData", d)
            break
finally:
    try:
        sw.CommandInProgress = False
    except Exception:      # noqa: BLE001
        pass
