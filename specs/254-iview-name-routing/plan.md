# Plan — `IView::Name` ⇒ `GetName2` 换路由的真机等价性先量

**Feature**: `specs/254-iview-name-routing/`
**日期**: 2026-10-10

---

## 一、三源与冲突裁决顺序

| 序 | 源 | 路径 | 用途 | 权威度 |
|---|---|---|---|---|
| 1 | ★★ **真机** | `SldWorks.Application` rev 34.4.1（★ 走护栏） | `Name` vs `GetName2` 的**行为** | ★★★ **最高** |
| 2 | **官方页** | `C:/swapi/types/IView/{Name,GetName2}.md` | 废弃关系 | ★★ |
| 3 | **真树源码** | 4 处站点 | 写法与兜底结构 | ★ 事实来源 |

**冲突裁决顺序**：1 > 2 > 3。

---

## 二、口径

| 口径 | 真源 | 怎么用 |
|---|---|---|
| 4 处靶子 | `tests/test_obsolete_multi_successor_impact._HOST_REVIEW["Name"]` | ★ **import**（★ 不重写） |
| 真机读数 | `output/_probe254_viewname.py` | ★ 冻结进判据 |
| 真机纪律 | `output/GOAL.md` §三 | ★ 走 `sw_guard`；★ 只用 3.14.7 |

---

## 三、实现步骤

1. **先量**：`output/_probe254_viewname.py` ⇒ 打开现成图纸、遍历视图、比对两个属性。
2. **写判据**：`tests/test_iview_name_successor_machine.py`（★ 含「弱证据必须显式标注」那条）。
3. **证明它红**：样本 0 / `diff=1` / 站点全缺 ⇒ 三组负例。
4. **回写四处**：ROADMAP §一 · memory · `AUTO_HANDOFF.md` · `AUTO_RUN_*.md`。

---

## 四、改动面

| 文件 | 动作 |
|---|---|
| `tests/test_iview_name_successor_machine.py` | ★ **新增**（5 例） |
| `output/_probe254_viewname.py` / `.txt` | ★ **新增**（真机探针 + 读数） |
| `specs/254-iview-name-routing/*.md` | ★ **新增**（四件齐） |
| `docs/ROADMAP.md` · memory · `AUTO_HANDOFF.md` · `.specify/feature.json` | 回写 |

★ **不改**：`scripts/sw_drawing_query.py` · `scripts/sw_drawing_view.py` · `scripts/sw_review.py`（★ 证据弱，**只量不改**）⇒ ★ **不跑生成器链**。

---

## 五、风险与对策

| 风险 | 对策 |
|---|---|
| ★★ 真机打开用户图纸 | ★ **只读**打开（`OpenDoc6` options=1）· ★ `finally` 里 `QuitDoc`（**不保存**）· ★ 事后护栏预检确认 0 个文档 |
| ★★ 把弱证据当强证据 | ★★ **单独立一条判据**（`test_sample_is_explicitly_weak`）钉住样本规模 |
| ★ 再踩「属性 vs 方法」 | ★ 已写进 `MACHINE_PITFALLS` |
| `release_check` 约 2m40s | ★ 后台跑 + 落盘日志 |
