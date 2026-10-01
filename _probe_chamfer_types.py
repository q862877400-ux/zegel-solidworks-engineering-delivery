"""量：CreateChamfer 三种类型各试一次，看哪种通。"""
import sys
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
import sw_connect
from scripts import sw_part, sw_selection_spec, sw_sketch

sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
part = sw_connect.new_document(sw, "part")
try:
    sw.CommandInProgress = True
except Exception:      # noqa: BLE001
    pass
try:
    sw_part.start_sketch(part)
    sw_part.sketch_line(part, -20.0, 0.0, 0.0, 0.0)
    sw_part.sketch_line(part, 0.0, 0.0, 0.0, 20.0)
    skm = sw_connect.safe_get_com_member(part, "SketchManager")
    sketch = sw_connect.safe_get_com_member(skm, "ActiveSketch")
    segs = sw_sketch.get_sketch_segments(sketch)
    print("  线段 %d 条" % len(segs))

    #: (类型值, Distance(米), AngleORdist) —— 每种都先重选两条
    CASES = [
        (2, 0.005, 0.0),     # distance_equal  —— 忽略 AngleORdist
        (0, 0.005, 45.0),    # distance_angle  —— 角度给 45 度
        (0, 0.005, 0.0),     # distance_angle  —— 角度给 0（原来失败的形态）
        (1, 0.005, 0.005),   # distance_distance
    ]
    for t, d, a in CASES:
        sw_selection_spec.clear_selection(part)
        sw_selection_spec.select_object(part, segs[0], append=False)
        n = sw_selection_spec.select_object(part, segs[1], append=True)
        r = sw_connect.safe_get_com_member(skm, "CreateChamfer", t, d, a)
        print("  type=%d dist=%.4f angle=%s  选区=%s  -> %s"
              % (t, d, a, n, type(r).__name__ if r is not None else "**None**"))
finally:
    try:
        sw.CommandInProgress = False
    except Exception:      # noqa: BLE001
        pass
    ttl = str(sw_connect.safe_get_com_member(part, "GetTitle") or "")
    if ttl:
        sw.CloseDoc(ttl)
        print("  （已关 %s）" % ttl)
