"""量：新 GTol 的帧数到底变不变、GetFrame 各种形态返回什么。"""
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

    def gc():
        return sw_connect.get_com_member(g, "GetFrameCount")

    print("  初始 GetFrameCount = %r" % (gc(),))
    r = sw_connect.get_com_member(g, "AddFrame")
    print("  AddFrame 返回 = %r" % (r,))
    print("  AddFrame 后 GetFrameCount = %r" % (gc(),))

    for i in (0, 1, 2):
        try:
            v = sw_connect.get_com_member(g, "GetFrame", i)
            print("  GetFrame(%d) -> %s" % (i, type(v).__name__ if v is not None else "**None**"))
        except Exception as e:      # noqa: BLE001
            print("  GetFrame(%d) ✗ %s" % (i, str(e)[:80]))
finally:
    try:
        sw.CommandInProgress = False
    except Exception:      # noqa: BLE001
        pass
    t = str(sw_connect.safe_get_com_member(part, "GetTitle") or "")
    if t:
        sw.CloseDoc(t)
        print("  （已关 %s）" % t)
