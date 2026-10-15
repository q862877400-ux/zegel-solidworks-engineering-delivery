# Spec — 多后继「命中名」的宿主级复核（244 的 14 有一半是别的接口的同名成员）

**Feature**: `specs/245-multi-successor-host-review/`
**日期**: 2026-10-09
**上游**: `specs/244-multi-successor-rule/`（同名链接优先规则；★ 其 §五「未过门」第 3 条 = 「14 条命中名里只核了 1 条的语义」）
**本轮只做一件事**：把 244 那句「真树在调 ∩ 多后继条目 = **14** 个，其中 **1** 个落在错后继」**核到宿主级**，并据此**决定交接单待办 1 是否关闭**。

---

## 一、背景（为什么 244 的「14」要重核）

244 的口径是**裸成员名**：`真树被调成员名 ∩ 多后继条目的成员名`。

★ 而官方 API 里**同名成员横跨多个接口**，其中**只有一部分是废弃的**：

| 成员名 | 废弃页 | **非废弃**的同名页 |
|---|---|---|
| `SketchTrim` | `IModelDoc2::SketchTrim` | ★ **`ISketchManager::SketchTrim`**（正是索引该给的那个） |
| `GetArcs2` / `GetLines2` / `GetPolylines` / `GetSplines` / `GetEllipses3` | `IView::*` | ★ **`ISketch::*`** |
| `GetMassProperties` | `IModelDoc2::*` | ★ `IModelDocExtension::*`（**后继**本身） |
| `Name` | `IView::Name` / `IComponent2::Name` | ★ `IFeature::Name` / `IBody2::Name` 等 **22 个**接口 |

⇒ ★ 只看成员名会把「我们调的是**非废弃**的那一个」误读成「我们在调废弃成员」。

**本轮实证（靶子）**：`scripts/sw_sketch_edit_ops.py:148`

```
get_com_member(_sketch(model) and get_com_member(model, "SketchManager"), "SketchTrim", …)
```

★ 宿主是 **ISketchManager** ⇒ 我们调的是 `ISketchManager::SketchTrim`（**非废弃**）。
⇒ ★★ 244 说「`SketchTrim` 是唯一落在错后继里的**真靶子**」—— **那是错的**：索引把 `IModelDoc2::SketchTrim`
的后继取成 `SketchExtend`（确实错），★ 但**真树上没有任何站点调 `IModelDoc2::SketchTrim`** ⇒ **零影响**。

---

## 二、需求（每条带来源与验收场景）

### FR-001 命中名必须按**宿主表达式**逐条表态

- **来源**：官方文档 —— `C:/swapi/types/ISketch/GetArcs2.md`（首行非 `Obsolete.`）
  vs `C:/swapi/types/IView/GetArcs2.md`（首行 `Obsolete. Superseded by …`）。
- **规则**：244 量出的**每一个**命中名，必须进 `_HOST_REVIEW` 登记表，给出
  `code ∈ {real-hit, false-hit, mixed}` + 依据 + **证据站点**（`文件, 行号, 宿主表达式源码`）。
- **验收场景**：`test_every_hit_name_is_reviewed` 通过；★ 少一个名即红。

### FR-002 「有非废弃同名页」的名**必须**表态（机械信号）

- **来源**：本项目既有模式（224/225/226 的「未表态即红」；★ 事实 46「检查量为 0 判失败」）。
- **规则**：若某命中名在 `C:/swapi/types/*/<名>.md` 里存在**首行非 `Obsolete.`** 的页 ⇒ 该名**必须**已表态。
- **验收场景**：`test_live_same_name_pages_are_adjudicated` 通过；★ 该集合的**下界 11**（只增不减）。
  ★ `C:/swapi/types` 不在本机时 `pytest.skip`（★ 缺数据源 ≠ 检查失败）。

### FR-003 表态码必须落在**封闭词表**里

- **来源**：本项目既有模式（224 的 `#: enum-gate:` 封闭词表）。
- **规则**：`code ∈ {real-hit, false-hit, mixed}`；★ **不许**写「待定 / unknown / 存疑」糊过去。
- **验收场景**：`test_review_codes_are_closed_vocabulary` 通过。

### FR-004 证据站点必须与**重算结果**逐字对上

- **来源**：本项目既有模式（纪律「门禁要比对**原始转储**，不要比对测试里手抄的常量」）。
- **规则**：证据站点必须是**重算站点集合的子集**（文件 + 行号 + 宿主表达式三者全等）；
  ★ 并钉住**检查量**（表 ≥14 条、证据站点 ≥14 个）—— ★ 否则表为空时「逐条比对」**一条都不比**（空判据）。
- **验收场景**：`test_evidence_sites_match_recomputed_sites` 通过；★ 改任一行号即红；★ 清空表即红。

### FR-005 ★★ 真命中里**不许**有一条落在「索引取错」的后继上

- **来源**：244 的 `_KNOWN_WRONG`（6 条索引取错的登记表）+ 交接单待办 1 的关闭条件。
- **规则**：`code ∈ {real-hit, mixed}` 且成员名 ∈ `_KNOWN_WRONG` 的条目数 **必须为 0**。
  ★ 为 0 ⇒ 待办 1（「逐条复核 254 条多后继」）**在真树上没有靶子** ⇒ **写结论并关闭**。
- **验收场景**：`test_no_real_hit_falls_in_a_known_wrong_successor` 通过；
  ★★ **能红的判据**：把 `SketchTrim` 改成 `real-hit` ⇒ 当场红（★ 244 当初就是这么判的）。

### FR-006 调用口径必须与互锁测试**逐条一致**（防漂移）

- **来源**：本项目既有模式（纪律「口径要么 import 要么逐字抄」；244 曾因口径凭印象写读数差 4）。
- **规则**：本文件自带的宿主抽取（`_member_calls`）产出的 `(行号, 成员名)` 必须与
  `tests/test_deprecated_entry_interlock._scan_calls` **逐条相等**。
- **验收场景**：`test_scan_parity_with_interlock` 通过（★ 对方将来多认一种形态 ⇒ 本判据红）。

### FR-007 ★ **不许**改索引生成器、**不许**改靶子表

- **来源**：243/244 的既有裁决（交接单「不要做」第 1、4 条）。
- **规则**：`tools/build_obsolete_index.py` 与 `scripts/sw_com_traps.py` 一行不改。
- **验收场景**：`git status --short tools/build_obsolete_index.py scripts/sw_com_traps.py` 无输出。

---

## 三、非目标

- **不**修索引生成器（FR-007）。
- **不**把索引整表灌进 `DEPRECATED_ENTRIES`。
- **不**删 `_REGISTERED` 里的三处登记。
- **不**动需 COM 的四项（`HEM_POSITIONS` 真机复核、16 条 arity 定罪、`AddMate5` 换路由、`Extension.SaveAs` → `SaveAs3`）。
- **不**把 `real-hit` 当成缺陷去改调用点 —— ★ 「我们在调废弃成员」是**既有登记**（`_REGISTERED`）的管辖范围，
  且改路由**必须真机验**；本轮只**定性**，不改路由。

## 四、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 变异检验 5 组全红（见 `output/_probe245_redbaseline.py`） |
| SC-2 | 判据**是绿的** | `tests/test_obsolete_multi_successor_impact.py` **7/7 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | 生成器与靶子表未改 | `git status --short tools/build_obsolete_index.py scripts/sw_com_traps.py` 无输出 |

## 五、未过门（本轮不做，如实登记）

- **7 个真命中**（`DeleteRenderMaterial` / `FeatureLinearPattern5` / `FeatureLocalCurveDrivenPattern` /
  `InsertFormToolFeature` / `KFactor` / `MaterialIdName` / `Name`）⇒ ★ 我们**确实在调废弃成员**；
  ★ 其中索引后继**7/7 正确**。★ 换路由**必须真机验**（与 `_REGISTERED` 同规），本轮**不换**。
- **`Name` 的 51 处站点里只逐站点看了 2 处**（1 真 + 1 假）—— ★ 其余按宿主变量名归类，**未逐条读上下文**。
- **244 的 6 条索引错后继仍未修**（改生成器 = 独立工作）；本轮只证明它们**在真树上零影响**。
- 真机未验；223 的 8 条既有红未修；未提交未部署。
