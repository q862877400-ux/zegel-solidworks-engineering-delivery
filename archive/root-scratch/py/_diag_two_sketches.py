import sys
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
import sw_connect
from scripts import sw_part, sw_sketch

sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
try:
    sw.CommandInProgress = True
except Exception:      # noqa: BLE001
    pass


def sketches(doc):
    out = []
    try:
        n = int(doc.GetFeatureCount)
        for k in range(1, n + 1):
            f = doc.FeatureByPositionReverse(k)
            if f is None:
                continue
            nm = str(f.Name)
            if nm.startswith("草图") or nm.startswith("Sketch"):
                out.append(nm)
    except Exception as exc:      # noqa: BLE001
        out.append("ERR:%s" % str(exc)[:40])
    return out


def active(doc):
    try:
        skm = sw_connect.safe_get_com_member(doc, "SketchManager")
        sk = sw_connect.safe_get_com_member(skm, "ActiveSketch")
        if sk is None:
            return None
        return str(sw_connect.safe_get_com_member(sk, "Name") or "?")
    except Exception:      # noqa: BLE001
        return "EXC"


doc = sw_connect.new_document(sw, "part")
print("  新建后草图: %s" % sketches(doc))
for i in range(3):
    print()
    print("  ── 第 %d 轮 ──" % (i + 1))
    r = sw_part.start_sketch(doc)
    print("     start_sketch 返回 %r · 活动草图 = %s" % (r, active(doc)))
    y = float(i) * 30.0
    sw_part.sketch_line(doc, -20.0, y, 20.0, y)
    skm = sw_connect.safe_get_com_member(doc, "SketchManager")
    sk = sw_connect.safe_get_com_member(skm, "ActiveSketch")
    segs = sw_sketch.get_sketch_segments(sk)
    print("     画线后段数 = %d" % (len(segs) if isinstance(segs, list) else -1))
    try:
        doc.ForceRebuild3(False)
    except Exception:      # noqa: BLE001
        pass
    print("     rebuild 后草图: %s" % sketches(doc))
    sw_part.end_sketch(doc)
    print("     end_sketch 后草图: %s · 活动草图 = %s" % (sketches(doc), active(doc)))

t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
if t:
    sw.CloseDoc(t)
try:
    sw.CommandInProgress = False
except Exception:      # noqa: BLE001
    pass
print()
print("  （临时零件已关闭，不保存）")
