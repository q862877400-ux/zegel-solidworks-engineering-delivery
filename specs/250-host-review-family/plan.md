# Plan — 245 其余 13 条命中名的宿主表达式级表态

**Feature**: `specs/250-host-review-family/`
**日期**: 2026-10-09

---

## 一、三源与冲突裁决顺序

| 序 | 源 | 路径 | 用途 | 权威度 |
|---|---|---|---|---|
| 1 | **官方类型页** | `C:/swapi/types/<接口>/<成员>.md` | 判宿主接口（★ `## Returns` / `## Remarks`）+ 判「该成员是否 `Obsolete.`」 | ★★★ **最高** |
| 2 | **官方废弃索引** | `specs/202-user-coverage-gaps/recon/official-obsolete-index.json` | 取每个命中名的**全部条目接口** | ★★ 派生自 1 |
| 3 | **真树源码** | `scripts/sw_*.py`（AST） | 取站点 + **宿主表达式** + **赋值来源** | ★ 事实来源 |

**冲突裁决顺序**：1 > 2 > 3。★ 与 248/249 同。

---

## 二、口径（逐字对齐）

| 口径 | 真源 | 怎么用 |
|---|---|---|
| 命中名 → 站点（含宿主表达式） | `tests/test_obsolete_multi_successor_impact._hit_sites` | ★ **import** |
| 调用抽取（两形态） | `tests/test_deprecated_entry_interlock._scan_calls` | ★ **import**（判据 6 自证一致） |
| 多后继条目的 `(interface, member)` | `tests/test_obsolete_multi_successor._multi` | ★ **import** |
| 宿主 → 接口 | ★ **读赋值来源 + 官方 `## Returns`** | ★ 人工判读（★ 见下） |

★★ **定则（245/248/249 三次换来的）**：
1. ★ **不许按裸成员名判接口**（★ 同名跨多接口）。
2. ★ **不许按变量名猜接口**（`f`/`x`/`av`/`cfg`/`entry` 不携带信息）—— ★ 必须**读赋值来源**。
3. ★ **「读」与「写」分开**（★ 249 的教训；★ 本切片全是**读**站点）。

★ **本轮的判读实例**（逐条）：
- `extension` = `model.Extension` ⇒ `IModelDocExtension`（★ 官方 `IModelDoc2/Extension.md`）
- `model.FeatureManager` / `get_com_member(model,"FeatureManager")` ⇒ `IFeatureManager`
- `_mgr` / `fm` = 同上的两种写法 ⇒ `IFeatureManager`
- `sketch` = 草图实体读取器的形参（`_require(sketch)`）⇒ `ISketch`
- `definition` = `get_com_member(feature, "GetDefinition")`（BaseFlange）⇒ `IBendsFeatureData`
- `model` ⇒ `IModelDoc2`
- `get_com_member(model, "SketchManager")` ⇒ `ISketchManager`

---

## 三、实现步骤

1. **先量**：`output/_probe250_family_sites.py` → `.txt`
   ⇒ 13 个名、**14 处站点**、每个宿主表达式的分组 + 逐站点 ±2 行上下文。
2. **判读**：每个宿主表达式读赋值来源 ⇒ 定接口。
3. **先写能红的判据**：`tests/test_obsolete_host_review_family.py`
   ⇒ 纯函数 `_adjudication_failures`（四查：覆盖 / 失效 / **自洽** / 站点逐字）+ 三组合成负例。
4. **证明它红**：清空表 ⇒ **13 条**；翻 `SketchTrim` / `GetArcs2` ⇒ 「表态与接口矛盾」。
5. **跨规格一致**：`test_consistent_with_245_name_level_verdict`（★ 本表 vs 245 的名级结论）。
6. **回写四处**：ROADMAP §一 · memory（append）· `output/AUTO_HANDOFF.md`（覆盖）· `output/AUTO_RUN_*.md`。

---

## 四、改动面（预期）

| 文件 | 动作 |
|---|---|
| `tests/test_obsolete_host_review_family.py` | ★ **新增**（6 例） |
| `specs/250-host-review-family/*.md` | ★ **新增**（四件齐） |
| `docs/ROADMAP.md` · `memory/2026-10-09.md` · `output/AUTO_HANDOFF.md` · `.specify/feature.json` | 回写 |

★ **不改**：`tests/test_obsolete_multi_successor_impact.py`（★ 245 的登记表**不动** —— 本轮是**独立复核**）·
`tools/build_obsolete_index.py` · `scripts/sw_com_traps.py` · `scripts/sw_*.py` · `scripts/release_check.py` ·
`docs/gate-classification.json`。
★ **不跑生成器链**（★ 没改 `scripts/`）。

---

## 五、风险与对策

| 风险 | 对策 |
|---|---|
| 按名级结论「抄一遍」= 无价值 | ★★ 本切片的价值 = **加接口字段 + 机检自洽 + 覆盖全部 14 处站点**（★ 245 只有 1 处/名） |
| 判据首跑全绿 = 可疑 | ★★ **必做红基线**（★ 清空表 / 翻码 / 删条目 三组） |
| `sketch` 的接口未逐字核官方页 | ★ 245 已判 `ISketch`；★ 本表沿用并**机检自洽**（★ 若哪天翻案 ⇒ 判据红） |
| 改名/移动 ⇒ 判据红 | ★ 设计意图；★ 红时按新站点补表态 |
| `release_check` 约 2m40s | ★ **后台跑 + 落盘日志** |
