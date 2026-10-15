import sys
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
import sw_connect
from scripts import sw_part

sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
try:
    sw.CommandInProgress = True
except Exception:      # noqa: BLE001
    pass
doc = sw_connect.new_document(sw, "part")
for i in range(2):
    sw_part.start_sketch(doc)
    y = float(i) * 30.0
    sw_part.sketch_line(doc, -20.0, y, 20.0, y)
    sw_part.end_sketch(doc)

n = int(doc.GetFeatureCount)
print("  特征树 %d 个（从新到旧）:" % n)
for k in range(1, n + 1):
    f = doc.FeatureByPositionReverse(k)
    if f is not None:
        try:
            tn = f.GetTypeName2()
        except Exception:      # noqa: BLE001
            tn = "?"
        print("    %2d) %-16s 类型=%s" % (k, str(f.Name)[:16], tn))

#: 试**两种**选法：中文名 vs 英文名
callout = sw_part._empty_callout()
print()
for names in (("草图2", "草图1"), ("Sketch2", "Sketch1")):
    doc.ClearSelection2(True)
    a = bool(doc.Extension.SelectByID2(names[0], "SKETCH", 0, 0, 0, False, 1, callout, 0))
    b = bool(doc.Extension.SelectByID2(names[1], "SKETCH", 0, 0, 0, True, 1, callout, 0))
    cnt = int(doc.SelectionManager.GetSelectedObjectCount2(-1))
    print("  选法 %s ⇒ 两次返回 %s/%s · 选择集计数 = %d" % (names, a, b, cnt))
    try:
        r = sw_part.insert_composite_curve(doc)
        print("      ⇒ insert_composite_curve = %r ✓" % r)
        break
    except Exception as exc:      # noqa: BLE001
        print("      ⇒ 仍失败: %s" % str(exc)[:80])

t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
if t:
    sw.CloseDoc(t)
try:
    sw.CommandInProgress = False
except Exception:      # noqa: BLE001
    pass
print("  （临时零件已关闭，不保存）")
