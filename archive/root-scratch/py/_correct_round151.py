import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── ① 更正事实 91（那句"根因是只留下 1 个草图"是**测量假象**）────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
MARK = "⚠ 本轮**未查明**：为什么两次建草图只留下 1 个"
CORRECT = "".join([
    "〔⚠⚠⚠ **2026-10-01 轮 152 就地更正**：本条把根因写成「**只留下 1 个草图**」——",
    "**那是测量假象，不是事实**。轮 152 用**三种独立方式**核对同一次操作：",
    "**树总数 18→19→20→21（每轮 +1）· 按名查 草图1/草图2/草图3 全在 · 活动草图 草图1/2/3** ⇒ ",
    "★ **每轮都真的建了草图**。假象来自 **`FeatureByPositionReverse` 滞后一格**",
    "（它枚举**已提交**的特征，而「最后建的那个」要等下一个特征建了才出现）⇒ ",
    "位置枚举看到的是 `[] → ['草图1'] → ['草图2','草图1']`。",
    "★★ 更正后的实况：**前提满足（2 个草图）之后 `InsertCompositeCurve` 仍返回 False** ⇒ ",
    "**真因仍未查明**（但「草图没建出来」这个解释已被排除）。〕 ",
])
if MARK in tk and "轮 152 就地更正" not in tk:
    K.write_text(tk.replace(MARK, CORRECT + MARK, 1), encoding="utf-8")
    print("  ok 事实 91 已就地更正")
else:
    print("  事实 91：锚点在=%s 已更正=%s" % (MARK in tk, "轮 152 就地更正" in tk))

# ── ③ 能力条目：更正上轮那句"根因是前提" ───────────────────────────
Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
OLD = "但真机上它返回 **False**，**根因是前提没满足**"
NEW = ("但真机上它返回 **False**。⚠⚠ **2026-10-01 轮 152 就地更正**：轮 151 把根因写成"
       "「前提没满足（只留下 1 个草图）」—— **那是测量假象**（`FeatureByPositionReverse` **滞后一格**；"
       "用三种独立方式核对后确认**每轮都真的建了草图**）。★ 更正后的实况："
       "**前提满足（2 个草图）之后它仍返回 False** ⇒ **真因仍未查明**")
n = 0
for c in d["capabilities"]:
    lim = c.get("limitations") or []
    for i, s in enumerate(lim):
        if OLD in str(s):
            lim[i] = str(s).replace(OLD, NEW)
            n += 1
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  ok capabilities 更正 %d 处" % n)
