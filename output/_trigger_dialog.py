import sys, time
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_connect
from scripts import sw_part, sw_mold
sys.stdout.reconfigure(encoding="utf-8")
sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
print("TRIGGER: 已连接", flush=True)
doc = sw_connect.new_document(sw, "part")
#: ⚠⚠⚠ **必须用空零件** —— 轮 167 实测：**有实体**的零件上 SolidWorks 能自己推断方向
#: ⇒ **不会弹框**（第一次复现因此失败：「竟然没弹框就返回了」）；
#: 而**空零件**上无方向可推断 ⇒ 才会弹「此拔模方向尚未定义。」
print("TRIGGER: 空零件已建好（**故意的**）", flush=True)
print("TRIGGER: 现在**故意**用 b_coord_input=False（退回『用模型已定义方向』）", flush=True)
try:
    #: ★ 故意触发：模型没有已定义的拔模方向 ⇒ 官方弹「此拔模方向尚未定义。」
    sw_mold.mold_undercut_detect(doc, b_coord_input=False, dx=0.0, dy=0.0, dz=1.0)
    print("TRIGGER: 竟然没弹框就返回了", flush=True)
except Exception as exc:
    print("TRIGGER: 抛错 %s: %s" % (type(exc).__name__, str(exc)[:80]), flush=True)
print("TRIGGER: 调用返回 ⇒ 阻塞已解除", flush=True)
try:
    t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
    if t:
        sw.CloseDoc(t)
except Exception:
    pass
