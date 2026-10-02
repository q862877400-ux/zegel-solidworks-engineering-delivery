import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

EV = ("python 真机（轮 386）★ **PASS** —— objective② 补的第一个真缺 `extend_surface`："
      "`scripts/sw_surface_features.py` 新增 `insert_extend_surface_report`（官方 "
      "`IModelDoc2.InsertExtendSurface(bool ExtendLinear, int EndCondition, double Distance)`，**3 参**，"
      "回 `void` ⇒ 判据是**特征树 diff**）。真机（走 `sw_guard` 护栏，5.16 s 无弹窗）："
      "前置曲面 `曲面-拉伸1`（tree 6→7）· 负例（距离 0）被入口拒 · "
      "**`extend_surface` ⇒ feature `曲面-延伸1` · faces_selected=4 · tree 7→8** ⇒ `verdict: pass`。"
      "证据 output/extend-surface-evidence.json。"
      "\u2605 \u26a0 \u771f\u673a\u63a8\u7ffb\u4e86\u300c\u4e0d\u9009\u9762\u300d\u5f53\u8d1f\u4f8b\u7684\u5047\u8bbe \u2014\u2014 **\u4e0d\u9009\u9762\u5b83\u4e5f\u80fd\u6210**\uff08\u5b83\u81ea\u5df1\u4f1a\u627e\u9762\uff09\uff0c"
      "故负例换成参数校验（距离 ≤ 0）。")

LIM = ("⚠ 本入口只验了 `end_condition = 0`（**按距离**）；★ `end_condition = 1`（**延伸到选定点**）"
       "需要先选中一个点，★ **未真机验**。★ 另：真机发现**不选面它也能成**（它自己会找面）⇒ "
       "`faces_selected = 0` **不构成失败**（入口里的那条检查是**保守**的，不是官方要求）。")

c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
#: \u2605 \u627e\u5230\u66f2\u9762\u7279\u5f81\u65cf\u7684\u6761\u76ee
target = None
for y in d["capabilities"]:
    if any("surface" in str(t) for t in (y.get("mcp_tools") or [])) or "surface" in y["id"]:
        if y.get("level") in ("verified", "stitched", "source_verified"):
            print("  \u5019\u9009: %-38s level=%s tools=%d" % (y["id"], y.get("level"), len(y.get("mcp_tools") or [])))
            if target is None and "feature" in y["id"]:
                target = y
if target is None:
    for y in d["capabilities"]:
        if "surface" in y["id"]:
            target = y
            break
if target is not None:
    ev = list(target.get("evidence") or [])
    if not any("extend_surface" in t for t in ev):
        ev.insert(0, EV)
    target["evidence"] = ev
    lim = list(target.get("limitations") or [])
    if not any("end_condition = 1" in t for t in lim):
        lim.insert(0, LIM)
    target["limitations"] = lim
    c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ok \u2192 %s ev=%d lim=%d" % (target["id"], len(ev), len(lim)))
