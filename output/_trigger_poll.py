import sys
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_connect
from scripts import sw_mold
sys.stdout.reconfigure(encoding="utf-8")
sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
doc = sw_connect.new_document(sw, "part")
print("TRIGGER: 空零件已就绪 ⇒ 调 b_coord_input=False（会阻塞）", flush=True)
try:
    sw_mold.mold_undercut_detect(doc, b_coord_input=False, dx=0.0, dy=0.0, dz=1.0)
except Exception as exc:
    print("TRIGGER: 抛错 %s" % type(exc).__name__, flush=True)
print("TRIGGER: 调用已返回（阻塞解除）", flush=True)
try:
    t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
    if t:
        sw.CloseDoc(t)
except Exception:
    pass
