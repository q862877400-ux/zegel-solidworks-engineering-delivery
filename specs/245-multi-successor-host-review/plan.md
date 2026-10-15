# Plan — 多后继「命中名」的宿主级复核

**Feature**: `specs/245-multi-successor-host-review/`
**Prerequisites**: spec.md

---

## 一、官方源（本特性要查的源，及冲突裁决顺序）

| 源 | 路径 | 用途 | 许可 |
|---|---|---|---|
| 官方类型页（`C:\swapi`） | `C:/swapi/types/<接口>/<成员>.md` | ★ 判「同名页**是否废弃**」（**页首行**） | 官方文档，**只读引用** |
| 官方废弃索引 | `specs/202-user-coverage-gaps/recon/official-obsolete-index.json`（`tools/build_obsolete_index.py` 生成） | 多后继条目集合（254 条） | 本仓自产 |
| 真树源码 | `scripts/sw_*.py` | 调用点 + 宿主表达式 | 本仓自产（上游 MIT，见 §四） |
| 调用口径真源 | `tests/test_deprecated_entry_interlock.py` 的 `_scan_calls` / `_scan_all_modules` / `_WRAPPERS` | ★ **口径一律 import，不重写** | 本仓自产 |
| 244 登记表 | `tests/test_obsolete_multi_successor.py` 的 `_KNOWN_WRONG` | FR-005 的靶子 | 本仓自产 |

**裁决顺序**：★ 与 244/243 一致 —— ① 官方页**页首行**（废弃与否）→ ② 官方索引（后继）→ ③ 真树调用点的**宿主表达式**（谁在调）。
★ 三者冲突时**不猜**：写进 `未过门`。

★ **冲突已发现并裁决**：`C:\swapi\types\IModelDoc2\SketchTrim.md` 说后继是 `ISketchManager::SketchExtend`（★ 索引照抄），
而 `ISketchManager::SketchTrim` 才是同名的那一个 ⇒ ★ 索引错、但**真树调的是后者** ⇒ 冲突**不影响**真树（FR-005 的结论）。

---

## 二、技术方案

### 1. 口径（★ 唯一真源 = 互锁测试）

```
_member_calls(tree, text)  ←  与 _scan_calls 逐条等价，只多带「宿主表达式源码」（ast.get_source_segment）
```
★ 判据 `test_scan_parity_with_interlock` **自证**两者一致 ⇒ 对方加形态时本文件**会红**。

### 2. 「宿主接口」怎么判（★ 不引入类型推断）

★ 本轮**不做**静态类型推断（会引入误判且不可审计）。做法是：
**把宿主表达式源码导出来，人工逐条判**（★ 与 244/243 的「登记 + 判据化」同规）。

| 宿主表达式形态 | 接口判据 |
|---|---|
| `extension`（`= get_extension(model)`） | `IModelDocExtension` |
| `model` | `IModelDoc2` |
| `model.FeatureManager` / `fm` / `_mgr`（`= get_com_member(model, "FeatureManager")`） | `IFeatureManager` |
| `sketch`（模块内形参，草图实体读取） | `ISketch` |
| `definition`（`= get_com_member(feature, "GetDefinition")`，BaseFlange） | `IBendsFeatureData` |
| `get_com_member(model, "SketchManager")` | `ISketchManager` |
| `view` | `IView` |

★ **可审计性**：每条判定的**依据都写在登记表的 `依据` 字段里**（★ 指到具体接口名）。

### 3. 机械信号（FR-002）

```
某名在 C:/swapi/types/*/<名>.md 里存在「首行非 Obsolete.」的页  ⇒  该名必须表态
```
★ 这条信号**独立于**人工判断 ⇒ 它是「**有盲区即红**」的形态。

### 4. 检查量下界（FR-004）

★ 表 ≥14 条、证据站点 ≥14 个 —— ★ 防止「表为空 ⇒ 逐条比对一条都不比」的空判据（事实 46）。

---

## 三、任务与验收

见 `tasks.md`（每条带 `→ 验收:` 与可复制命令）。

---

## 四、许可

| 来源 | 许可 | 义务 |
|---|---|---|
| 上游 `wzyn20051216/solidworks-automation-skill` | **MIT** | 保留版权声明（本特性**未抄任何上游文本**，只读本仓源码） |
| 四家外部 MCP 项目 | MIT / Apache-2.0 | 同上，本特性**未引用** |
| 官方 SolidWorks API 文档（`C:\swapi`） | 官方文档 | ★ **只读引用**页首行与签名，**不抄正文** |
| 本仓自产 | — | 无 |

★ 本特性**不新增任何外部代码或文本**。

---

## 五、风险与回退

| 风险 | 处置 |
|---|---|
| `C:/swapi/types` 不在本机 ⇒ FR-002 无数据源 | `pytest.skip`（★ 缺数据源 ≠ 检查失败） |
| 宿主接口判定靠人工 ⇒ 可能判错 | ★ 每条依据**指到接口名**；★ 判错由 FR-004（证据对不上）与 FR-005（落在错后继）**当场红** |
| 调用点漂移 ⇒ 证据行号过期 | ★ 判据 ④ 比对**重算站点** ⇒ 漂移即红（★ 这正是要它红的场景） |
