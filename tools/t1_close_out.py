"""★ T1 收口：修正 `docs/tool-aliases.md`（采纳 10 → 5）+ 写事实 520 的正文。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
joint = json.loads((ROOT / "output" / "t1-joint-gain.json").read_text(encoding="utf-8"))
keep = [r for r in joint["rows"] if r["delta"] and r["delta"] > 0]
drop = [r for r in joint["rows"] if not (r["delta"] and r["delta"] > 0)]

p = ROOT / "docs" / "tool-aliases.md"
src = p.read_text(encoding="utf-8")
add = [
    "",
    "## 六 · ★★ T1-5 / T1-6 收口：**实测把采纳面从 10 缩到 5**（2026-10-04）",
    "",
    "### 6.1 两面都测（★ 避免只报有利的一面）",
    "",
    "| 面 | 测什么 | 现状（剥掉别名）| 装上别名后 | 差 |",
    "|---|---|---|---|---|",
    "| **A** | 48 题的**中文**查询 | top-1 19% · top-5 25% | top-1 19% · top-5 25% | ★★ **精确的 0** |",
    "| **B** | 别名**自己的词**当查询 | top-1 7 · top-5 37% | top-1 10 · top-5 38% | ★ 几乎不动 |",
    "",
    "★★ **面 A 是 0 的原因**：别名是**英文**，中文查询与它**词元不重叠** ⇒ ★ **英文别名对中文用户无效** ✓",
    "",
    "### 6.2 ★★★ 但平均值**掩盖了**真实效果（本轮第三个方法论发现）",
    "",
    "逐工具量（十个别名同时装）却是：**提升 5 · 不变 5 · 变差 0** ——",
    "★ 因为不变的那 5 个里有 **4 个本来就是 rank 1**（**没有上升空间**）✓",
    "⇒ ★★ **平均值既不能证明有效、也不能证明无效** —— 必须看**逐项** ✓",
    "",
    "### 6.3 ★ 按 D-2 判据收口（别名必须挣到字节）",
    "",
    "| 工具 | 联合下的排名 | 处置 |",
    "|---|---|---|",
]
for r in sorted(keep, key=lambda x: -(x["delta"] or 0)):
    add.append("| `%s` | **%s → %s** | ★ **留下** |"
               % (r["tool"], r["rank_stripped"], r["rank_joint"]))
for r in sorted(drop, key=lambda x: x["tool"]):
    add.append("| `%s` | %s → %s | ✗ **已回退**（挣不到字节）|"
               % (r["tool"], r["rank_stripped"], r["rank_joint"]))
add += [
    "",
    "⇒ ★★ **最终只保留 5 条别名行**（`doc` 里追加一行，不动 schema 契约；已实测工具总数仍 **433**）✓",
    "",
    "### 6.4 ★★★ 三条方法论教训（★ 比这 5 条别名值钱）",
    "",
    "1. ★★ **「增益实测」分不开对错** —— 查询词就是被追加的别名本身 ⇒ 语义上错的别名一样会提升"
    "（★ 要与语义闸配合，见 §二/§四）；",
    "2. ★★ **「逐条增益」推不出「整体增益」** —— 孤立测时 45/52 提升、最大 56→1；"
    "十个一起装后平均几乎不动（★ 同族缺陷：**局部外推到整体**）；",
    "3. ★★ **平均值会掩盖天花板** —— 『平均只涨 1 个点』说的是那 5 个**已经在 rank 1** 的工具，"
    "不是那 5 个真提升的工具 ✓",
]
p.write_text(src.rstrip("\n") + "\n" + "\n".join(add) + "\n", encoding="utf-8")
print("★ 已修正 %s（+%d 行）" % (p.name, len(add)))

#: ★ 事实 520 的正文写到 output/，由下一条命令搬进 known-facts
facts = ROOT / "output" / "_facts-520.md"
facts.write_text("""
---

| 520 | **★★★★★ 别名这条路的三条方法论教训 —— ★ 本项目已实测出「局部增益 ≠ 整体增益」且「平均值会掩盖天花板」** —— 2026-10-04（接手轮 T1-5/T1-6，规格 `specs/206-c1c6-harvest/`）。

**背景**：T1 把 C5 手核的「换名已有」做成别名，过三道闸（机械筛 → 增益实测 → 语义闸）后
采纳 10 条，按 D-2 把别名行追加进 `doc`。★ 然后用**两面**复测（★ 刻意不只报有利的一面）：

| 面 | 测什么 | 现状（剥掉别名）| 装上后 | 差 |
|---|---|---|---|---|
| **A** | 48 题的**中文**查询 | top-1 19% · top-5 25% | top-1 19% · top-5 25% | ★★ **精确的 0** |
| **B** | 别名**自己的词**当查询 | top-1 7 · top-5 37% | top-1 10 · top-5 38% | ★ 几乎不动 |

★★ **面 A = 0 的原因**：别名是**英文**，中文查询与它**词元不重叠** ⇒
**英文别名对中文用户无效**（★ 本条与事实 519 的「英语工具面」是同一条线的两端）✓

★★★ **但逐工具量（十个别名同时装）却是：提升 5 · 不变 5 · 变差 0** ——
★ 因为「不变」那 5 个里 **4 个本来就是 rank 1**（**没有上升空间**）✓

**⇒ 三条可复用的方法论教训**：
```
① ★★ 「增益实测」分不开对错 —— 查询词就是被追加的别名本身，
   语义上错的别名一样提升（★ 事实 519 已记）
② ★★ 「逐条增益」推不出「整体增益」 —— 孤立测 45/52 提升、最大 56→1；
   十个一起装后平均几乎不动 ⇒ ★ 这是【局部外推到整体】的错，与 ① 同族
③ ★★ 「平均值会掩盖天花板」 —— 『平均只涨 1 个点』说的是那 5 个**已在 rank 1** 的工具，
   不是那 5 个真提升的 ⇒ ★★ 平均值**既不能证明有效、也不能证明无效**，必须看逐项
```

**★ 处置**：按 D-2 自己的判据（**别名必须挣到字节**）**只留 5 条、回退 5 条**：
留 `assembly_list_components`（15→1）· `entities_on_body`（2→1）· `collect_appearance_evidence`（2→1）·
`drawing_create_revision_table`（2→1）· `drawing_insert_datum_tag`（4→2）；
回退 `assembly_check_interference` / `automation_explain_hresult` / `gtol_insert` /
`insert_global_bounding_box` / `part_bounding_box`（★ 全是 1→1 或 2→2）✓
★ 工具总数实测仍 **433**（★ 只追加 `doc` 文本，未动 schema 契约）✓

★ **依据**：`tools/t1_remeasure_sc1.py`（两面 A/B）· `tools/t1_joint_gain.py`（联合逐工具）·
`tools/t1_revert_nonearning_aliases.py`（回退）· `tools/t1_apply_aliases_to_doc.py`（追加）·
`output/t1-joint-gain.json` · `docs/tool-aliases.md` §六 · `tools/metric_scope.py` 的 `alias_gain` 口径 ✓
""", encoding="utf-8")
print("★ 事实 520 正文: %s" % facts)
