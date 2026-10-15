import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

EV = ("python 真机（轮 384）★ **只读那半 5/5 pass**（`tools/verify_mold_evidence_smoke.py`，走 `sw_guard` 护栏，"
      "2.49 s 无弹窗）：`mold_evidence()` 可调用且返回 dict · 含官方只读入口的键 **6/6** · "
      "新零件上这些读数都是 0/空（非 0 就是读错了对象）。"
      "★ **写入那半的穷尽式结论**（`tools/prove_mold_parting_geometry.py`）：官方 Remarks 要求"
      "「**拔模方向 mark 1 + 分型线边线 mark 4**，且必须用 `SelectByID2`」；★ 而真机上"
      "**「给边线打 mark 4」做不到** —— `IEntity.Select4` 只有 2 个参数（传 mark 报 "
      "`-2147352562 '无效的参数数目。'`，事实 32），而 `SelectByID2(\"\", \"EDGE\", x, y, z, …, 4, …)` "
      "**回 True 而 `GetSelectedObjectCount2(-1)` = 0**（事实 8：bool 返回值不可信）。"
      "⇒ `insert_parting_line` 恒回 None（官方在缺前置时返回 None）⇒ 那是**同族的后端限制**，"
      "不是我们没做对。证据 output/mold-parting-geometry-evidence.json · output/mold-evidence-smoke.json。")

LIM = ("★★★★★ 2026-10-02（轮 384）**写入那半走到死路（穷尽式）**：官方 `InsertMoldPartingLine` 的 Remarks 要求"
       "**拔模方向 mark 1 + 分型线边线 mark 4**，且指定**必须用 `SelectByID2`**；"
       "★ 而真机上**「给边线打 mark 4」做不到**：① `IEntity.Select4` **只有 2 个参数**"
       "（传 mark 报 `com_error: (-2147352562, '无效的参数数目。')` —— 与事实 32 一致）；"
       "② `SelectByID2(\"\", \"EDGE\", x, y, z, False, 4, callout, 0)` **回 True 而 "
       "`SelectionManager.GetSelectedObjectCount2(-1)` = 0**（事实 8：bool 返回值不可信，要计数回读 —— "
       "★ 我第一版信了 True）。⇒ `insert_parting_line` 恒回 None ⇒ **同族后端限制**，"
       "★ **不再换参数试**（事实 47 的定则）。⚠ 只读那半（`mold_evidence`）**已真机 5/5**。")

c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
x = next(y for y in d["capabilities"] if y["id"] == "mold_parting_geometry")
ev = list(x.get("evidence") or [])
if not any("只读那半 5/5" in t for t in ev):
    ev.insert(0, EV)
x["evidence"] = ev
lim = list(x.get("limitations") or [])
if not any("走到死路（穷尽式）" in t for t in lim):
    lim.insert(0, LIM)
x["limitations"] = lim
c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  ok · mold_parting_geometry level=%s ev=%d lim=%d" % (x.get("level"), len(ev), len(lim)))
