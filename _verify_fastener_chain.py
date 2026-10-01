"""真机验证：把能通的 3 条都跑一遍。"""
import sys
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
import sw_connect
from scripts import sw_hole_features as H

sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
try:
    sw.CommandInProgress = True
except Exception:      # noqa: BLE001
    pass
try:
    std = H.list_hole_standards(sw, 0)
    print("  list_hole_standards -> %d 条" % len(std))

    ft = H.list_fastener_types(sw, "ANSI Inch", 0)
    print("  list_fastener_types('ANSI Inch') -> %d 条 · 前 3: %s"
          % (len(ft), ft[:3]))

    if ft:
        tt = H.list_fastener_table_types(sw, "ANSI Inch", ft[0]["id"], 0)
        print("  list_fastener_table_types('ANSI Inch', %r) -> %r" % (ft[0]["id"], tt))

    try:
        H.get_fastener_table(sw, "ANSI Inch", ft[0]["id"], 0, 0)
        print("  get_fastener_table -> 竟然通了？！")
    except Exception as exc:      # noqa: BLE001
        print("  get_fastener_table ✗ %s" % str(exc)[:90])
finally:
    try:
        sw.CommandInProgress = False
    except Exception:      # noqa: BLE001
        pass
