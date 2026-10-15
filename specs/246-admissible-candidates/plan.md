# Plan — `admissible` 候选的收表处置

**Feature**: `specs/246-admissible-candidates/`
**Prerequisites**: spec.md

---

## 一、官方源（本特性要查的源，及冲突裁决顺序）

| 源 | 路径 | 用途 | 许可 |
|---|---|---|---|
| 官方类型页（`C:\swapi`） | `C:/swapi/types/<接口>/<成员>.md` | ★ **两边签名**（被废弃页 vs 后继页）+ 页首行（废弃与否） | 官方文档，**只读引用** |
| 官方废弃索引 | `specs/202-user-coverage-gaps/recon/official-obsolete-index.json` | 候选集合 + 链终点 | 本仓自产 |
| 真树源码 | `scripts/sw_*.py` | 调用点 + **宿主表达式** | 本仓自产（上游 MIT） |
| 六关真源 | `tests/test_deprecated_table_admission._admission_failures` | ★ **直接调用**，不重写 | 本仓自产 |
| 调用口径真源 | `tests/test_deprecated_entry_interlock._scan_all_modules` / `_WRAPPERS` / `_REGISTERED` | ★ **直接 import** | 本仓自产 |

**裁决顺序**：① 官方页**两边签名** → ② 官方索引**链终点**（★ 不是字面后继）→ ③ 真树调用点的**宿主表达式**。
★ 三者冲突时**不猜**：判 `reject-*` 并写理由。

★ **本轮实际用到的冲突裁决**：
- `FeatureCircularPattern4` 的**字面后继** `FeatureCircularPattern5` **自己也废弃** ⇒ 取**链终点** `CreateFeature`
  （★ 242 定则；★ 关 2 就是这么判的）。
- `GetActiveSketch2` 的链终点 `SketchManager::ActiveSketch` **页不存在**（★ 缺 `I` 前缀）⇒ 关 6 判 `reject-successor-page-missing`。

---

## 二、技术方案

### 1. 候选集合（★ 复算，不自己造过滤器）

```
真树在调成员名 ∩ 索引成员名
  → 链终点唯一（不是 ambiguous-terminal）
  → 链终点名 ≠ 被废弃名（不是 successor-same-name）
  → 链终点名 ∈ 真树在调（不是 terminal-never-called）
  = admissible（15）
```
★ 口径**逐字**取自 `output/_probe243_admission.py`（★ 243 的「先量」脚本），★ **不新增任何过滤器**
（★ 243 的教训：自造过滤器会把读数从 49 压到 15）。

### 2. ★★ 宿主级判定（245 的教训）

★ **不做静态类型推断**（会引入不可审计的误判）。做法与 245 同：
**把宿主表达式源码导出来，人工逐条判接口**，并把判定**写进处置表的字段**（可审计、可冻结）。

| 宿主表达式 | 接口 | 与条目接口一致？ |
|---|---|---|
| `sw` / `dynamic_sw` | `ISldWorks` | ✅（`ActivateDoc2`） |
| `active`（`sketch or model.SketchManager.ActiveSketch`） | `ISketch` | ✅（`AutoDimension2`） |
| `model.FeatureManager` / `fm` / `_mgr` | `IFeatureManager` | ✅ |
| `doc`（`call_assembly_doc`）/ `asm_model` | `IAssemblyDoc` | ✅ |
| `selection` | `ISelectionMgr` | ✅ |
| `model.Extension` | `IModelDocExtension` | ✅（`SaveAs`） |
| `mgr`（`_manager(model)`） | **`IEquationMgr`** | ❌（条目是 `ICustomPropertyManager`） |
| `view` | **`IView`** | ❌（条目是 `IComponent2`） |
| `app`（`IModelDoc2.GetSldWorks`） | **`ISldWorks`** | ❌（条目是 `IModelDoc2`） |
| `get_com_member(model, "SketchManager")` | **`ISketchManager`** | ❌（条目是 `IModelDoc2`） |

### 3. 处置码（封闭词表）

| code | 含义 | 本轮条数 |
|---|---|---|
| `collected` | 六关全过 + 宿主一致 + 两边签名已读 ⇒ **收进靶子表** | **5** |
| `already-in-table` | 本轮之前已在表里（241 收的） | 2 |
| `reject-multi-successor` | 关 5：官方那句点名多个后继 | 4 |
| `reject-successor-page-missing` | 关 6：后继页在 `C:/swapi` 里不存在 | 1 |
| `reject-host-interface-mismatch` | ★★ 宿主接口 ≠ 条目接口（**假命中**） | 3 |

### 4. 收表的两处连带（★ 242 的教训 40）

1. `scripts/sw_com_traps.py` 的 `DEPRECATED_ENTRIES` **+5 条**（4 → **9**）。
2. `tests/test_deprecated_entry_interlock.py` 的 `_REGISTERED` **+5 处登记**
   （`sw_assembly.py` / `sw_export.py` / `sw_review.py` / `sw_part.py` / `sw_selection.py`）——
   ★ 否则判据①「不许新增对废弃入口的调用」会**当场红**。
3. ★ **改了 `scripts/` ⇒ 必须跑生成器链**（7 步）。

---

## 三、任务与验收

见 `tasks.md`（每条带 `→ 验收:` 与可复制命令）。

---

## 四、许可

| 来源 | 许可 | 义务 |
|---|---|---|
| 上游 `wzyn20051216/solidworks-automation-skill` | **MIT** | 保留版权声明（本特性**未抄任何上游文本**） |
| 四家外部 MCP 项目 | MIT / Apache-2.0 | 同上，本特性**未引用** |
| 官方 SolidWorks API 文档（`C:\swapi`） | 官方文档 | ★ **只读引用**签名与页首行，**不抄正文** |
| 本仓自产 | — | 无 |

★ 本特性**不新增任何外部代码或文本**。

---

## 五、风险与回退

| 风险 | 处置 |
|---|---|
| 收表会**改变公开 MCP 工具** `deprecated_successor()` 的输出 | ★ 只**增加**条目、不改已有 4 条；★ 由 `test_real_target_table_passes_admission` 保证新条目过六关 |
| 收表会让互锁判据①把**现有调用**判成违规 | ★ 同步补 `_REGISTERED`（判据 ⑧ 守这条） |
| 宿主接口判定靠人工 ⇒ 可能判错 | ★ 判错的兜底是判据 ⑤（宿主≠条目）与判据 ⑥（假命中不许进表） |
| 调用点漂移 ⇒ 证据行号过期 | ★ 判据 ⑦ 比对**重算站点** ⇒ 漂移即红 |
