import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
EV = Path(r"D:\AI\SW\_mold_ev.txt").read_text(encoding="utf-8").strip()
LIM = ("★★ 2026-10-03（轮 392）`insert_shut_off_surface` 已试三次（无孔 / 有孔 / 孔+分型线+分型面）"
       "⇒ 都回 true 而特征树不变 ⇒ ★ 穷尽式结论：不是缺前置，而是「没有可关的断面」"
       "（★ 假设：孔需穿过分型面）。★ 不再换条件试（事实 53）。"
       "★ 下一步只剩 `insert_core_cavity_solids` —— 它要一整条链（分离成型芯/型腔片体 + 建模坯草图），"
       "留作单独一轮。")
c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
x = next(y for y in d["capabilities"] if y["id"] == "mold_parting_geometry")
ev = list(x.get("evidence") or [])
if not any("穷尽式结论" in s for s in ev):
    ev.insert(0, EV)
x["evidence"] = ev
lim = list(x.get("limitations") or [])
if not any("已试三次" in t for t in lim):
    lim.insert(0, LIM)
x["limitations"] = lim
c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  ok ev=%d lim=%d level=%s" % (len(ev), len(lim), x.get("level")))
