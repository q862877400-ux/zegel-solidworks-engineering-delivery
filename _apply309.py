import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
body = Path(r"D:\AI\SW\_fact309.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
if "\n| 309 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")
    print("  (1) wrote 309")

c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
x = next(y for y in d["capabilities"] if y["id"] == "mold_parting_geometry")
EV = ("python 真机（轮 392）★ **`insert_shut_off_surface` 的穷尽式结论**：三次尝试"
      "（① 无孔 · ② 先打 8 mm 通孔 · ③ 孔 + `分型线1` + `分型面1` **前置全齐**）"
      "**都是 `returned=true` 而特征树不变**（末次树 10→10）⇒ ★★ **不是"缺前置"，"
      "而是这个件上"没有可关的断面"**（★ 记为假设：孔需**穿过分型面**才算断面，本轮两者不相交）。
      "★ 依据事实 53：同一启发式试 ≥3 次即停，★ 不再换条件试。"
      "证据 output/shut-off-surface-evidence.json。"
      "★★ 模具族准确进度（4 个工具）：**2 个真机通过**（`insert_parting_line` ⇒ `分型线1` · "
      "`insert_parting_surface` ⇒ `分型面1`）· **1 个穷尽式无效果**（`insert_shut_off_surface`）· "
      "**1 个前置已查清未做**（`insert_core_cavity_solids` —— 要"把件分离成型芯/型腔片体" + "模坯轮廓草图"）。")
ev = list(x.get("evidence") or [])
if not any("穷尽式结论" in s and "shut_off" in s for s in ev):
    ev.insert(0, EV)
x["evidence"] = ev
LIM = ("★★ 2026-10-03（轮 392）**`insert_shut_off_surface` 已试三次**（无孔 / 有孔 / "
       "孔+分型线+分型面）⇒ **都回 `true` 而特征树不变** ⇒ ★ **穷尽式结论：不是缺前置，"
       "而是"没有可关的断面"**（★ 假设：孔需**穿过分型面**）。★ **不再换条件试**（事实 53）。"
       "★ 下一步只剩 `insert_core_cavity_solids` —— ★ 它要一整条链（分离成型芯/型腔片体 + 建模坯草图），"
       "★ 留作单独一轮。")
lim = list(x.get("limitations") or [])
if not any("已试三次" in t for t in lim):
    lim.insert(0, LIM)
x["limitations"] = lim
c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  (2) mold_parting_geometry ev=%d lim=%d" % (len(ev), len(lim)))
