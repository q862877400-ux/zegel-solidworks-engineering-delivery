# Spec — `admissible` 候选的收表处置（六关 + 宿主级 + 两边签名）

**Feature**: `specs/246-admissible-candidates/`
**日期**: 2026-10-09
**上游**: `specs/243-admission-gate-tightening/`（六关准入）· `specs/245-multi-successor-host-review/`（**宿主级**复核的教训）
**本轮只做一件事**：把「242/243 口径的 **15** 个 `admissible` 候选」**逐条处置**，并把 `collected` 的**收进靶子表**。

---

## 一、背景（为什么 242/243 的 `admissible` 也要复核）

243 交接单待办 3 写的是「15 个 `admissible` 候选 —— ★ **须先过待办 1**（★ `SketchTrim` 已证索引会给**错后继**）
⇒ ★ **每条读两边签名后**才收表」。★ 245 已把待办 1 **关闭**（真树上零靶子）。

★★ 而 245 同时证明了一件事：**「真树在调 ∩ 索引」按裸成员名量会一半是假命中**
（`SketchTrim` 的宿主是 `ISketchManager`、`GetArcs2` 的宿主是 `ISketch`…）。
⇒ ★ **同一个坑对 `admissible` 候选同样成立** —— 242/243 的分桶也**按裸成员名**算。

**本轮先量（`output/_probe246_candidates.py`）**：

| 读数 | 值 |
|---|---|
| 分桶（242/243 口径） | `successor-same-name 34 · terminal-never-called 23 · admissible 15 · ambiguous-terminal 9 · chain-broken-all 1` |
| 六关失败 | `multiple-official-successors 4 · successor-page-missing 1` |
| ★★ 宿主接口不匹配（假命中） | **3**（`Add2` → IEquationMgr · `GetModelDoc` → IView · `GetUserPreferenceIntegerValue` → ISldWorks） |

---

## 二、需求（每条带来源与验收场景）

### FR-001 每个候选必须**逐条处置**

- **来源**：本项目既有模式（243 的「未表态即红」）。
- **规则**：15 个候选全部进 `_DISPOSITION` 表，每条给 `code` + **宿主接口** + 依据 + **证据站点**。
- **验收场景**：`test_all_candidates_are_dispositioned` 通过；★ 少一个即红。

### FR-002 处置码必须落在**封闭词表**里

- **来源**：本项目既有模式（224 的 `#: enum-gate:` 封闭词表）。
- **词表**：`collected` · `already-in-table` · `reject-multi-successor` · `reject-successor-page-missing` ·
  `reject-host-interface-mismatch`。★ **不许**写「待定 / 存疑」。
- **验收场景**：`test_codes_are_closed_vocabulary` 通过。

### FR-003 ★★ `collected` 的每条必须**真过六关**

- **来源**：官方索引 + 243 的 `_admission_failures`（**直接调真函数**，不手抄结论）。
- **规则**：`collected` 的条目按 `(接口, 成员) -> 链终点` 造表项喂进 `_admission_failures` ⇒ **必须无失败**。
- **验收场景**：`test_collected_entries_pass_admission` 通过；
  ★★ **能红的判据**：把 `FeatureCircularPattern4` 的后继改成**字面后继** `FeatureCircularPattern5` ⇒ 关 2 当场红。

### FR-004 `collected` 的必须在靶子表里，且后继**逐字一致**

- **来源**：本项目既有模式（登记表与现状一致）。
- **验收场景**：`test_collected_entries_are_in_the_target_table` 通过；★ 删表项即红；★ 两处漂移即红。

### FR-005 ★★★ 宿主接口必须与条目接口一致（245 的教训判据化）

- **来源**：**245 的实测**（★ 按裸成员名判会一半是假命中）。
- **规则**：`collected` 的条目，其**真树调用点的宿主接口**必须 == **条目接口**。
- **验收场景**：`test_collected_entries_have_matching_host_interface` 通过；
  ★★ **能红的判据**：把 `Add2` 判成 `collected` ⇒ 宿主 `IEquationMgr` ≠ 条目 `ICustomPropertyManager` ⇒ 红。

### FR-006 ★★ 宿主不匹配的**不许**进靶子表

- **来源**：245 的教训 + 本仓「判据不许指错人」。
- **规则**：`reject-host-interface-mismatch` 的名**不许**出现在 `DEPRECATED_ENTRIES` 的**成员名**集合里。
- **验收场景**：`test_host_mismatch_candidates_are_not_collected` 通过；★ 把 `Add2` 收进表即红。

### FR-007 证据站点必须与**重算结果**逐字对上（含检查量下界）

- **来源**：本项目既有模式（纪律「比对原始转储，不比对测试里手抄的常量」；事实 46「检查量为 0 判失败」）。
- **验收场景**：`test_evidence_sites_match_recomputed_sites` 通过；★ 改行号即红；★ 清空表即红。

### FR-008 ★★ `collected` 且真树有调用点 ⇒ **必须**有 `_REGISTERED` 登记

- **来源**：242 的教训 40（★ 加一条进表 ⇒ 互锁会把**现有调用**判成违规）。
- **验收场景**：`test_collected_entries_are_registered_where_called` 通过；★ 删登记即红。

### FR-009 ★ **不许**改索引生成器

- **来源**：243/244/245 的既有裁决。
- **验收场景**：`git status --short tools/build_obsolete_index.py` 无输出。

---

## 三、非目标

- **不**改 `tools/build_obsolete_index.py`。
- **不**收 `reject-*` 的四类候选（★ 理由逐条写在处置表里）。
- **不**改任何**调用点**（★ 换路由**必须真机验** —— 与 `_REGISTERED` 同规；本轮只**定性**）。
- **不**动需 COM 的六项。

## 四、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 变异检验 **8 组全红**（`output/_probe246_redbaseline.py`） |
| SC-2 | 判据**是绿的** | `tests/test_deprecated_admissible_disposition.py` **8/8 通过** |
| SC-3 | 靶子表扩容**不破互锁族** | 互锁族 **49 passed**（含 246 的 8） |
| SC-4 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-5 | 生成器链已跑 | `scripts/release_check.py` 等 7 步全跑（★ 改了 `scripts/`） |
| SC-6 | 生成器未改 | `git status --short tools/build_obsolete_index.py` 无输出 |

## 五、未过门（本轮不做，如实登记）

- **被拒的 10 个候选**（4 多后继 + 1 页缺失 + 3 宿主不匹配 + 2 已在表）—— ★ 本轮**只登记理由**，不收。
  ★ 其中 `FeatureLinearPattern5` / `FeatureLocalCurveDrivenPattern` / `InsertFormToolFeature` **是真命中**
  （我们确实在调），★ 但**官方那句点名多个后继** ⇒ 按 243 关 5，**必须人工表态**，本轮不做。
- **5 条新收条目的调用点一律不换路由** —— ★ 五条**都不是 drop-in**（参数都变了），换它们**必须真机验**。
- 真机未验；223 的 8 条既有红未修；未提交未部署。
