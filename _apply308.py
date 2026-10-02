import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
body = Path(r"D:\AI\SW\_fact308.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
if "\n| 308 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")
    print("  (1) wrote 308")

c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
x = next(y for y in d["capabilities"] if y["id"] == "mold_parting_geometry")
PRECOND = ("★★ 2026-10-03（轮 391）**`insert_core_cavity_solids` 的真前置（官方 Remarks 八条，逐条抄）**："
           "① Parting Line 特征必须已存在 ② 分型面必须已生成 ③ ★★ **件必须已**分离成型芯/型腔（片体）** "
           "④ **模坯轮廓草图**必须已存在 ⑤ 该草图**垂直于拔模方向** ⑥ 通常是**含住件（型芯+型腔）的矩形** "
           "⑦ 草图平面位置决定 setback 时的分型面 ⑧ **无 setback 时，分型面必须**伸出模坯草图之外**"
           "（好让模坯把它切掉）。"
           "⇒ ★ **我们轮 390 那句「未先建分型面」的文案不准**（★ 那是猜测）—— "
           "★ 真因是**缺 ③ 与 ④**。"
           "★ 另：`insert_shut_off_surface` **官方该页 Remarks 为空** ⇒ 真机试了两次"
           "（**无孔** / **先打 8 mm 通孔** ⇒ `faces 6→7`），★ **两次都 `returned=true` 而特征树不变** ⇒ "
           "「缺通孔」那个推测**不成立**；★ 下一假设：要先有**分型线 + 分型面**（那两次都没建）。")
lim = list(x.get("limitations") or [])
lim = [t for t in lim if "该文案是我们的猜测" not in t]
if not any("真前置（官方 Remarks 八条" in t for t in lim):
    lim.insert(0, PRECOND)
x["limitations"] = lim
c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  (2) mold_parting_geometry lim=%d" % len(lim))
