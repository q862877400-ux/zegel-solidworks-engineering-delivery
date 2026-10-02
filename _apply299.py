import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

EV_NEW = ("python 真机（轮 382）★ **绝对 mm 判据第一次真机使用 · PASS** —— "
          "`tools/prove_absolute_criteria.py`（走 `sw_guard` 护栏）建 100×60×20 mm 板，"
          "**数据取自真机几何**（顶点坐标差实测 `delta_mm = [0.0, 0.0, -20.0]` = 板厚；"
          "`volume = 120000.0` mm³ · `area = 18400.0` mm² 与手算精确一致），"
          "三条判据各带**正例与负例**：`check_axis_alignment` / `check_radii` / `check_same_level` "
          "**全部「正例 ok=True 且负例 ok=False」** ⇒ `verdict: pass`。"
          "证据 output/absolute-criteria-evidence.json。"
          "★ 依据调研 v2 发现①：**定位用绝对、等价用相对** —— 两条互补，只留一条会各瞎一半；"
          "**现在两条都真机 PASS 过**（相对判据见 compare_geometry 的既有 evidence）。")

LIM_NEW = ("⚠ **绝对判据的容差默认 `ABS_TOL_MM` / `RADIUS_TOL_MM`**（0.05 / 0.1 mm）—— "
           "真机验过的是**这两档**；★ 改容差要重跑 `tools/prove_absolute_criteria.py` 复验。"
           "★ 另：`check_same_level` 的 `z_pairs_mm` 契约是 **`[(z_a, z_b), …]`（二元组）**，"
           "传三元组会被它自己接住并回 `ok=False`（★ 判据行为正确）。")

c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
x = next(y for y in d["capabilities"] if y["id"] == "geometry_measurement")
ev = list(x.get("evidence") or [])
if not any("绝对 mm 判据第一次真机使用" in t for t in ev):
    ev.insert(0, EV_NEW)
x["evidence"] = ev
lim = list(x.get("limitations") or [])
if not any("ABS_TOL_MM" in t for t in lim):
    lim.insert(0, LIM_NEW)
x["limitations"] = lim
c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  ok · geometry_measurement ev=%d lim=%d level=%s" % (len(ev), len(lim), x.get("level")))
