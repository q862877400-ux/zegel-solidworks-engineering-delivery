import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
body = Path(r"D:\AI\SW\_fact307.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
if "\n| 307 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")
    print("  (1) wrote 307")

c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
x = next(y for y in d["capabilities"] if y["id"] == "mold_parting_geometry")
EV = ("python 真机（轮 390）★ **`insert_parting_surface` PASS**：`parting_surface` ⇒ **`分型面1`** · "
      "特征树 8 → 9（★ 官方 8 参；★ Remarks：**有分型线后不必再选方向与边**）。"
      "★ 同轮另两个的现状：`insert_shut_off_surface` **回 Feature 非 None 而特征树不变**"
      "（★ 最可能：模型上**没有通孔**可关）；`insert_core_cavity_solids` 报 RuntimeError"
      "「未先建分型面」**而分型面已建**（★ 我们的错误文案是猜测 ⇒ 待读官方 Remarks 核对）。"
      "证据 output/mold-family-rest-evidence.json。"
      "★ 同轮**抓到一条真问题**：`scripts/sw_mold.py` 的 `insert_core_cavity_solids(model, *, scale, "
      "thickness, flip, offset)` 与 `insert_parting_surface(model, *, surface_type, flip, use_trim, "
      "distance, angle, option, tolerance, alternate)` 的**参数名与官方不符**（官方是 Dist1/Dist2/"
      "Setback/Angle 与 Radiate/ReverseAlignment/ReverseOffset/OffsetDistance/Angle/Smooth/"
      "SmoothDistance/Knit）⇒ ★ 功能能跑而**语义对应关系不清**（★ 待单独一轮改签名 + 调用方）。")
ev = list(x.get("evidence") or [])
if not any("insert_parting_surface" in s and "PASS" in s for s in ev):
    ev.insert(0, EV)
x["evidence"] = ev
LIM = ("★ 2026-10-03（轮 390）进度：★ **4 个工具里 2 个真机通过**（`insert_parting_line` ⇒ `分型线1` · "
       "`insert_parting_surface` ⇒ `分型面1`）。⚠ 另两个待查：`insert_shut_off_surface` 回 Feature 而"
       "**特征树不变**（★ 可能模型上没有通孔）· `insert_core_cavity_solids` 报「未先建分型面」"
       "**而分型面已建**（★ 该文案是我们的猜测，待核对官方 Remarks）。"
       "⚠★ **参数名与官方不符**（`scale`/`thickness`/`use_trim`/`tolerance`/`alternate` 等 —— 官方是 "
       "`Dist1`/`Dist2`/`Setback`/`Radiate`/`Smooth`/`Knit`）⇒ ★ 调用方无法对应官方语义，待单独一轮改。")
lim = list(x.get("limitations") or [])
if not any("2 个真机通过" in t for t in lim):
    lim.insert(0, LIM)
x["limitations"] = lim
c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  (2) mold_parting_geometry level=%s ev=%d lim=%d" % (x.get("level"), len(ev), len(lim)))
