# Spec — 多后继条目的后继选取规则（同名链接优先）

**Feature**: `specs/244-multi-successor-rule/`
**日期**: 2026-10-09
**上游**: `specs/243-admission-gate-tightening/`（准入六关；★ 其待办 1 = 「逐条复核 254 条多后继条目」）
**本轮只做一件事**：把「**官方那句点多个链接时，与被废弃成员同名的那个才是真后继**」这条规则**量出来、变成判据**。

---

## 一、背景（为什么需要这条规则）

`tools/build_obsolete_index.py` 用 `re.search` 抓后继 ⇒ 官方写「Superseded by A and B」时**只留第一个**。
`official-obsolete-index.json` 的 **1671** 条里，**254** 条受影响（`obsolete_line` 含 ≥2 个 `[[…]]`）。

**索引是准入判据（`_admission_failures`）与靶子表扩容的数据源** ⇒ 后继取错会**一路传下去**。

**实证（本轮的靶子）**：

| 页 | 原文 |
|---|---|
| `C:/swapi/types/IModelDoc2/SketchTrim.md:12` | `Obsolete. Superseded by [[ISketchManager::SketchExtend]] and [[ISketchManager::SketchTrim]].` |

- `ISketchManager::SketchExtend` 的语义是 **"Adds to the length of the selected sketch entity"**（**延伸**）
- `ISketchManager::SketchTrim` 的语义是 **"Trims the selected sketch entities"**（**剪裁**）

⇒ 索引取了第一个（`SketchExtend`）是**错的**；真后继是**与被废弃成员同名**的 `ISketchManager::SketchTrim`（接口迁移）。

---

## 二、需求（每条带来源与验收场景）

### FR-001 多后继条目必须被**普查**出来，且张数冻结下界

- **来源**：本项目既有模式（`tests/test_deprecated_table_admission.py` 的 `_census` 同族）。
- **验收场景**：索引里 `obsolete_line` 含 ≥2 个 wikilink 的条目数 **≥ 254**（★ 下界，只许增不许减 —— 减少 = 读取器漏了）。

### FR-002 「同名链接优先」规则必须被**判据化**

- **来源**：官方文档 —— `C:/swapi/types/IModelDoc2/SketchTrim.md:12` 的实证（见 §一）。
- **规则**：对每条多后继条目，**若句中存在与被废弃成员同名的链接**，则索引记录的 `successor` 必须是它。
- **验收场景**：`tests/test_obsolete_multi_successor.py::test_same_name_link_is_the_real_successor` 通过；
  ★ 清空偏差登记表后必须**红**（能红的判据，不是空判据）。

### FR-003 已知偏差必须**具名登记**，不许静默

- **来源**：本项目既有模式（`tests/test_deprecated_table_admission.py` 的 `_AMBIGUOUS_NAME_ALLOWLIST` 同族）。
- **规则**：索引取错但**真后继已查证**的条目，进 `_KNOWN_WRONG` 表；每条必须带**真后继全名 + 依据（读了哪一页、为什么）**。
- **验收场景**：`test_registry_entries_have_evidence`（每条依据 ≥20 字、真后继写成 `接口::成员`）。

### FR-004 偏差登记表必须**与索引现状一致**（防过期）

- **来源**：本项目既有模式（「棘轮下调必须补内容断言」，见 `MEMORY.md` 判据写作纪律 22）。
- **规则**：若索引将来改好（后继变成真后继），登记表那一行**必须删**；不删即红。
- **验收场景**：`test_known_wrong_registry_matches_index` 通过。

### FR-005 ★ **不许**改索引生成器

- **来源**：243 交接单待办 1 ③（本项目既有裁决）。
- **规则**：`tools/build_obsolete_index.py` 一行不改 —— 改它要重跑索引并复核全部 **1671** 条，**属独立一件工作**。
- **验收场景**：`git status --short tools/build_obsolete_index.py` 无输出。

---

## 三、非目标

- **不**修索引生成器（FR-005）。
- **不**把索引整表灌进 `DEPRECATED_ENTRIES`（243 交接单「不要做」第 1 条）。
- **不**删 `_REGISTERED` 里的三处登记。
- **不**动需 COM 的四项（`HEM_POSITIONS` 真机复核、16 条 arity 定罪、`AddMate5` 换路由、`Extension.SaveAs` → `SaveAs3`）。

## 四、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 清空 `_KNOWN_WRONG` 后 `test_same_name_link_is_the_real_successor` 报 **6 条**失败 |
| SC-2 | 判据**是绿的** | 带登记表时 `tests/test_obsolete_multi_successor.py` **4/4 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` |
| SC-4 | 生成器未改 | `git status --short tools/build_obsolete_index.py` 无输出 |

## 五、未过门（本轮不做，如实登记）

- **6 条错后继未修**（★ 修要动生成器 ⇒ 独立工作）。本轮只**登记 + 判据化**。
- `INote::IGetTextFormat` / `INote::ISetTextFormat` / `ISheet::ICreateOLEObject` 三条的真后继是**进程内变体**（`I` 前缀）
  ⇒ 结构上正确，但按已知事实 47 **pywin32 调不到** ⇒ **消费端要不要用是另一个问题**，本轮只判「索引取错了」。
- 真树在调的 **82** 个废弃名里，落在多后继条目的有 **14** 个（见 `output/_probe244_multi_successor.py`），
  其中落在**错后继**里的有 **1** 个（`SketchTrim`，调用模块 `sw_sketch_edit_ops.py`）。
