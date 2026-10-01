"""量：GetBodyBox 返回的原始值到底是米还是毫米。"""
import sys
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
import sw_connect
from scripts import sw_part

sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
part = sw_connect.new_document(sw, "part")
try:
    sw.CommandInProgress = True
except Exception:      # noqa: BLE001
    pass
try:
    sw_part.start_sketch(part)
    sw_part.sketch_corner_rectangle(part, 0.0, 0.0, 80.0, 60.0)
    sw_part.end_sketch(part)
    sw_part.extrude_boss(part, "草图1", 50.0)

    # ★ 直接读 COM，不走我们的换算
    bodies = sw_connect.get_com_member(part, "GetBodies2", 0, False)
    body = bodies[0]
    raw = sw_connect.get_com_member(body, "GetBodyBox")
    print("  GetBodyBox 原始 = %r" % ([round(float(v), 9) for v in raw],))
    print("  设计尺寸      = 80 × 60 × 50 mm")
    print("  ⇒ 若原始值 ≈ 80/60/50  ⇒ 单位是**毫米**")
    print("  ⇒ 若原始值 ≈ 0.08/0.06/0.05 ⇒ 单位是**米**")

    ext = sw_connect.safe_get_com_member(part, "Extension")
finally:
    try:
        sw.CommandInProgress = False
    except Exception:      # noqa: BLE001
        pass
    t = str(sw_connect.safe_get_com_member(part, "GetTitle") or "")
    if t:
        sw.CloseDoc(t)
        print("  （已关 %s）" % t)
