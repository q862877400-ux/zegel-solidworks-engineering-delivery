# Plan — `AddMate5` 分流语义复核

**Feature**: `specs/291-addmate5-dispatch-semantics/`
**日期**: 2026-10-10
**上游**: `specs/241-deprecated-entry-interlock-coverage/`（核心事实四 / 五）

---

## 一、施工顺序（★ 先量 → 判据先红 → 改 → 判据后绿 → 门禁 → 回写）

| # | 步 | ★ 内容 | ★ 为什么这个顺序 |
|---|---|---|---|
| 1 | **先量** | 读两处 docstring 的「该怎么换」+ 官方三页 + 241 核心事实四/五 + `sw_com_traps.py` 登记表 + `_REGISTERED` | ★ 本仓铁律：**动手前先量**；★ 且要**先确认「三处权威记录都对」** ⇒ 才敢说 docstring 错 |
| 2 | **查钉住** | `tests/test_obsolete_addmate5_kept_on_purpose.py`（4 条）· `tests/test_deprecated_entry_interlock.py`（`_REGISTERED`）· `tests/test_sw_assembly_doc_contract.py`（**无** docstring 断言） | ★ **铁律 28**：改实现前先搜「有没有测试钉住旧行为」 |
| 3 | **写判据（先红）** | `tests/test_addmate5_dispatch_semantics.py`（6 条） | ★ 先写**能红的**判据；★ 取点**按名字 + 按标记**，★ **不按行号** |
| 4 | **跑红基线** | `pytest … -q` ⇒ 期望 **3 failed, 3 passed** | ★ **不能红的判据 = 空判据** ⇒ 必须留下红读数 |
| 5 | **改** | 只改**两处 docstring** 的「该怎么换」段 | ★ **只订正记档**；★ 路由**一字不动** |
| 6 | **跑绿** | 本判据 **6 passed** + 三条既有回归（合计 **28 passed**） | ★ 绿了才算改对 |
| 7 | **跑生成器链** | `sync_bundled_skill` → `gen_level_audit` → `gen_metrics` → `gen_harvest_digest` → `build_union_map` → `gen_dead_ends` → `sync_bundled_skill` | ★ **改了 `scripts/` 必须重跑**（★ 286 的教训：打包副本 + digest 会过期） |
| 8 | **门禁** | `release_check.py` @**3.14.7**（★ 后台 + 落盘 `output/_gate291.log`） | ★ 受管 3.13.12 缺 COM ⇒ 假红 + 挂死 |
| 9 | **回写四处** | `GOAL.md` §七 · `AUTO_HANDOFF.md` · `ROADMAP.md` §一 · `memory/2026-10-09.md` · `AUTO_RUN_*.md` | ★ `GOAL.md` §五 收工三件 |

---

## 二、改动面（★ 只有 2 个文件 · ★ 都只动 docstring）

| # | 文件 | ★ 函数 | ★ 改什么 | ★ 不改什么 |
|---|---|---|---|---|
| 1 | `scripts/sw_assembly.py` | `add_mate5_checked` | ★ 「该怎么换」段：加**限定词** + **「定不下来」表态** + **后继前置** | ★ **不动** `asm_model.AddMate5(...)` 调用 |
| 2 | `scripts/sw_assembly_doc.py` | `add_mate` | ★ 「该怎么换」段：**改真调用方名** `add_mate5_checked` + 同上 | ★ **不动** `get_com_member(doc, "AddMate5", *args)` |

---

## 三、判据设计（★ 取点方式与词表）

### 3.1 取点（★ 按名字 + 按标记，**不按行号**）

```python
_func_names(path)          # ★ AST 取全部 def 名
_docstring(path, funcname) # ★ 按函数名取 docstring；★ 找不到 ⇒ None（★ 调用方显式判红）
_how_to_switch(ds)         # ★ 从「该怎么换」标记 → 下一个「前置」标记；★ 缺标记 ⇒ None
```

★★ **为什么按标记而不是行窗口**：★ 本仓纪律「判据按**名字**定位，不按行号」；
★ 行号会漂（★ 试点文件那条 `(916, "SaveAs")` 就是这么烂掉的）。

### 3.2 词表（★ 人写死的约定 —— 铁律 5：门禁不得「自动挑选约定」）

| 词表 | ★ 内容 | ★ 锚回哪里 |
|---|---|---|
| `CONCENTRIC_QUALIFIERS` | `偏心` · `misaligned` · `Misaligned` | ★ FR-001 锚 `AddConcentricMateWithTolerance.md` 的 `parent/standard/must already exist/AddMate5` |
| `DISTANCE_QUALIFIERS` | `圆柱` · `cylindrical` · `Cylindrical` | ★ FR-001 锚 `AddDistanceMate.md` 的 `cylindrical` / `cylindrical faces` |
| `MATE_TYPE_INSUFFICIENT` | `定不下来` · `不足以` · `不能只凭` | ★ 241 核心事实四**逐字** |
| `REAL_CALLER` / `PHANTOM_CALLER` | `add_mate5_checked` / `add_mate` | ★ 241 核心事实五 |

★★ **为什么要有 FR-001 这条「锚点断言」**：★ 铁律 6 —— **门禁要比对「原始转储」，不要比对测试里手抄的常量**。
★ 所以 `CONCENTRIC_QUALIFIERS` 里那个中文词**必须**由官方英文原文**锚住**（★ 官方页变了 ⇒ 锚点先红）。

### 3.3 边界冻结（★ FR-005）

★ 「**断言"不加什么"必须不命中**」：★ 两处**仍然**调 `AddMate5` ⇒ ★ 若有人借"修文档"之名**顺手换路由** ⇒ **当场红**。

---

## 四、风险与对策

| # | ★ 风险 | ★ 对策 |
|---|---|---|
| 1 | ★ 改 docstring 会让**既有契约测试**红 | ★ 步骤 2 已核：`test_sw_assembly_doc_contract.py` **无** docstring 断言；`test_obsolete_addmate5_kept_on_purpose.py` 的 4 条**只要求**「记档保留 / Obsolete / ≥2 条分流 / `IMateFeatureData` / 仍调 `AddMate5`」⇒ ★ 全保留 ✓ |
| 2 | ★ 改 `scripts/` ⇒ 打包副本 / digest **过期** | ★ 步骤 7 **重跑生成器链**（★ 头尾各一次 sync） |
| 3 | ★ 判据把**行号/行窗口**写死 | ★ 步骤 3 用 **AST 按名字** + **按标记取段** |
| 4 | ★ 判据**静默降级**（取不到段 = 通过） | ★ `_how_to_switch` 取不到 ⇒ 返回 `None` ⇒ ★ 测试**显式判红**（★ 铁律 2） |
| 5 | ★★ 有人把「订正记档」读成「可以换路由了」 | ★ FR-005 **边界冻结** + 两处 docstring 都补「**本轮只订正记档、不动路由**」 |

---

## 五、不做

- ★ **不跑 COM**（★ 本轮是**文档订正**，★ 真机不在本轮范围）。
- ★ **不动** `sw_com_traps.py` / `_REGISTERED`（★ 它们**已经是对的**）。
- ★ **不动**路由（★ 两处仍调 `AddMate5`）。
