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


def see(doc, tag):
    """用**三种独立方式**看"草图在不在"（方法①位置枚举 ②按名查 ③活动草图）。"""
    by_pos = []
    try:
        n = int(doc.GetFeatureCount)
        for k in range(1, n + 1):
            f = doc.FeatureByPositionReverse(k)
            if f is not None:
                nm = str(f.Name)
                if nm.startswith("草图") or nm.startswith("Sketch"):
                    by_pos.append(nm)
    except Exception as exc:      # noqa: BLE001
        by_pos = ["ERR:%s" % str(exc)[:30]]
    by_name = {}
    for nm in ("草图1", "草图2", "草图3"):
        try:
            f = doc.FeatureByName(nm)
            by_name[nm] = "有" if f is not None else "无"
        except Exception as exc:      # noqa: BLE001
            by_name[nm] = "EXC:%s" % str(exc)[:22]
    try:
        skm = sw_connect.safe_get_com_member(doc, "SketchManager")
        act = sw_connect.safe_get_com_member(skm, "ActiveSketch")
        act = str(sw_connect.safe_get_com_member(act, "Name")) if act is not None else None
    except Exception:      # noqa: BLE001
        act = "EXC"
    total = int(doc.GetFeatureCount)
    print("     %-14s 位置枚举=%s · 按名查=%s · 活动=%s · 树总数=%d"
          % (tag, by_pos, by_name, act, total))


doc = sw_connect.new_document(sw, "part")
print("  新建后:")
see(doc, "新建")
for i in range(3):
    print("  ── 第 %d 轮 ──" % (i + 1))
    r = sw_part.start_sketch(doc)
    see(doc, "start_sketch")
    sw_part.sketch_line(doc, -20.0, float(i) * 30.0, 20.0, float(i) * 30.0)
    see(doc, "画线后")
    sw_part.end_sketch(doc)
    see(doc, "end_sketch")

t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
if t:
    sw.CloseDoc(t)
try:
    sw.CommandInProgress = False
except Exception:      # noqa: BLE001
    pass
print("  （已关闭）")
