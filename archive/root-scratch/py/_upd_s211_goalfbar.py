"""★ 更新规格 211 的 goal-bar（★ 进度行 + 21 项逐项状态表，★ 从人工终判表生成，不手写）。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "mcp-server"))
import spec211_manual_verdicts as MV   # noqa: E402

G = ROOT / "specs" / "211-user-feature-gaps" / "goal-bar.md"
text = G.read_text(encoding="utf-8")

# ── ① 进度行 ────────────────────────────────────────────────────────────────
import collections
c = collections.Counter(v[1] for v in MV.VERDICTS.values())
stage = ("**阶段：B0 台账完成（21 项**全部**有终判 + 依据）⇒ 下一批 B1 · "
         "★ 可做 %d · 不做 %d · 已覆盖 %d · 待实测 %d**"
         % (c["可做"], c["不做"], c["已覆盖"], c["待实测"]))
i = text.index("**阶段：")
j = text.index("\n", i)
text = text[:i] + stage + text[j:]

# ── ② 21 项逐项状态表（★ 从人工终判表生成）────────────────────────────────
MARK = "| 域 | 项 | 状态 |"
k = text.index(MARK)
k2 = text.index("\n\n", k)
rows = [MARK, "|---|---|---|"]
for item, (dom, verd, why) in MV.VERDICTS.items():
    rows.append("| %s | %s | **%s** |" % (dom, item, verd))
text = text[:k] + "\n".join(rows) + text[k2:]

# ── ③ 「下一个动作」段 ─────────────────────────────────────────────────────
a = text.index("## 下一个动作")
a2 = text.index("---", a)
nxt = """## 下一个动作（只写一条，免得没人知道该恢复哪个）

★★ **B0-4**：给 15 项「可做」**逐项准备"必然失败"的负例条件**（★ 本仓教训：**假负例等于没有** ——
★ 负例必须用**必然失败**的条件，★ 例：距离 ≤ 0 · 分辨率越界 · 空选择）。

★ 然后进 **B1**：**截面属性**（`GetSectionProperties2`）· **缩放/变形**（`InsertScale`）·
**边界凸台** ⇒ ★★ **注意 B1-3 已在 B0 判「不做」**（要 ACL）⇒ ★ B1 实际做**两项**（截面属性 · 缩放/变形），
★ 并**记速率**（分钟/件 + 通过率）供后续批排期 ✓

"""
text = text[:a] + nxt + text[a2:]

# ── ④ 调整记录追加 ─────────────────────────────────────────────────────────
text = text.rstrip() + """
- 2026-10-06 ★★ **B0 完成**：21 项全部有终判（★ 人工读官方页，★ 不是自动猜）。
  ★ 依据**事实 53**：`AccessSelections` 那个启发式改了 3 次 ⇒ ★ **停手**，改成「信号 + 人工终判」✓
- 2026-10-06 ★★ **人工终判把 5 项"待核实"全部澄清为「可做」** —— ★ 因为自动信号是**关键词共现**、
  ★ 会把**同关键词的别的页**（`swconst` 枚举、别的接口属性）算进来 ⇒ ★ 而 `swapi` 侧**真正的入口**
  （`FeatureCurvePattern` / `CreateFormTool2` / `GetFlatPatternCount` / `InsertGussetFeature3` /
  `InsertFilletBeadFeature3`）**都不带 ACL** ✓
- 2026-10-06 ★ **B1 的第三项「边界凸台」在 B0 就判了「不做」** ⇒ ★ B1 缩小为两项
  （★ 这是 B0 先做的收益：**没拿真机窗口去撞墙**）✓
"""
G.write_text(text, encoding="utf-8")
print("★ goal-bar 已更新；终判分布 =", dict(c))
