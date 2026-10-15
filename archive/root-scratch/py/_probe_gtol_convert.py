"""量：走 ConvertFormat 之后，GetFrame 能不能拿到东西。"""
import sys
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
import sw_connect

sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
part = sw_connect.new_document(sw, "part")
try:
    sw.CommandInProgress = True
except Exception:      # noqa: BLE001
    pass
try:
    g = sw_connect.get_com_member(part, "InsertGtol")
    print("  InsertGtol -> %s" % type(g).__name__)
    can = sw_connect.get_com_member(g, "CanConvertFormat")
    print("  CanConvertFormat -> %r" % (can,))
    code = sw_connect.get_com_member(g, "ConvertFormat")
    print("  ConvertFormat -> %r （0 = 成功）" % (code,))
    print("  ConvertFormat 后 GetFrameCount = %r" % (sw_connect.get_com_member(g, "GetFrameCount"),))
    for i in (1, 2):
        v = sw_connect.safe_get_com_member(g, "GetFrame", i)
        print("  GetFrame(%d) -> %s" % (i, type(v).__name__ if v is not None else "**None**"))
        if v is not None:
            r = sw_connect.safe_get_com_member(v, "AddIndicator", 0, 23, "A")
            print("     AddIndicator(0, 23, 'A') -> %r" % (r,))
            break
finally:
    try:
        sw.CommandInProgress = False
    except Exception:      # noqa: BLE001
        pass
    t = str(sw_connect.safe_get_com_member(part, "GetTitle") or "")
    if t:
        sw.CloseDoc(t)
        print("  （已关 %s）" % t)
