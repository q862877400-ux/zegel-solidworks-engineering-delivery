import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")

FACT = "| 92 | " + "".join([
    "**`FeatureByPositionReverse` 枚举的是「已提交」的特征 —— 用它数「刚建的那个」会**滞后一格**（少数一个）** —— ",
    "2026-10-01（轮 152）实测：连续三轮 `start_sketch`+`sketch_line`+`end_sketch`，同一时刻三种数法对照：",
    "**树总数 18→19→20→21**（★ 每轮 +1 ⇒ 都建了）· ",
    "**按名查 `FeatureByName`：草图1 → 草图2 → 草图3**（★ 都查得到）· ",
    "**活动 `SketchManager.ActiveSketch`：草图1 / 草图2 / 草图3**；",
    "⚠ 而 **`FeatureByPositionReverse`：`[] → ['草图1'] → ['草图2','草图1']`** ← **滞后一格**。",
    "⇒ ★★ **「刚建的那个草图」要等下一个特征建了才会被位置枚举看到。**",
    "★★★ 这就是轮 151 我得出「只留下 1 个草图」那个**错误根因**的来源 —— ",
    "而它又导致我把 `InsertCompositeCurve` 的 `False` **误判成「前提未满足、属应然」**。",
    "⇒ ★ 更正后：**前提满足（2 个草图）之后它仍返回 `False`** ⇒ **真因仍未查明**。",
    "★ **可复用的判据**：核对「建了几个」要**按名查**（`FeatureByName`）或看**总数变化**，",
    "**不要只用位置枚举**；⚠ 而 `GetFeatureCount` 是**属性**不是方法（事实 84 那一族记过）。",
    " | `_diag_sketch_visibility.py`（三法对照）；`_diag_two_sketches.py`；事实 9 / 84 / 91 |",
])
if "| 92 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 92")
else:
    print("  已有 92")
