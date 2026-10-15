# Plan — 造出多视图工程图，把 `IView::Name` == `GetName2` 的证据升到真实模型视图

**Feature**: `specs/255-multi-view-drawing-evidence/`
**日期**: 2026-10-10

---

## 一、三源与冲突裁决顺序

| 序 | 源 | 路径 | 用途 | 权威度 |
|---|---|---|---|---|
| 1 | ★★ **真机** | `SldWorks.Application` rev 34.4.1（★ 走护栏） | 造图 + 量 | ★★★ **最高** |
| 2 | **官方页** | `C:/swapi/types/IView/{Name,GetName2}.md` | 废弃关系 | ★★ |
| 3 | **254 的读数** | `output/_probe254_viewname.txt` | 旧样本（1 伪视图） | ★ |

**冲突裁决顺序**：1 > 2 > 3。

---

## 二、口径

| 口径 | 真源 | 怎么用 |
|---|---|---|
| 门槛 | 254 的 `ROUTING_THRESHOLD = 5` | ★ **import 语义**（★ 本文件写常量并注明来源） |
| 真机读数 | `output/_probe255_make_drawing.py` | ★ 冻结进判据 |
| 真机纪律 | `output/GOAL.md` §三 | ★ 走 `sw_guard`；★ 只用 3.14.7 |

★★ **教训（本轮踩的）**：★ `GetUserPreferenceStringValue(9)` **不是**工程图模板（★ 是装配）
⇒ ★ **模板索引要实测**，★ 别按印象写。

---

## 三、实现步骤

1. **造图**：`output/_probe255_make_drawing.py` ⇒ 打开现成零件 → 新建工程图（★ 模板索引 **10**）→ `Create3rdAngleViews2` → 遍历比对 → 存盘。
2. **写判据**：`tests/test_multi_view_drawing_evidence.py`（★ 含「真实模型视图 ≥3」与「门槛未达」两条）。
3. **证明它红**：`diff=1` / 真实视图 0 / 读数不全 ⇒ 三组负例。
4. **回写四处**：ROADMAP §一 · memory · `AUTO_HANDOFF.md` · `AUTO_RUN_*.md`。

---

## 四、改动面

| 文件 | 动作 |
|---|---|
| `tests/test_multi_view_drawing_evidence.py` | ★ **新增**（5 例） |
| `output/_probe255_make_drawing.py` / `.txt` · `output/_probe255_views.SLDDRW` | ★ **新增**（探针 + 读数 + 图纸） |
| `specs/255-multi-view-drawing-evidence/*.md` | ★ **新增**（四件齐） |
| `docs/ROADMAP.md` · memory · `AUTO_HANDOFF.md` · `.specify/feature.json` | 回写 |

★ **不改**：`scripts/sw_drawing_query.py` · `sw_drawing_view.py` · `sw_review.py`（★ 门槛未达，**只量不改**）⇒ ★ **不跑生成器链**。

---

## 五、风险与对策

| 风险 | 对策 |
|---|---|
| ★★ 造图会写盘 | ★ 已授权（C 级）；★ 只落 `output/`；★ 零件与图纸**用完都关**（★ `QuitDoc` 不保存） |
| ★ 模板索引写错 | ★ **实测**（本轮已踩：9 是装配、10 才是工程图） |
| ★★ 把 4 个视图当成「门槛已达」 | ★★ **单独立一条判据**（`test_routing_threshold_is_not_yet_met`）钉住 4 < 5 |
| `release_check` 约 3 min | ★ 后台跑 + 落盘日志 |
