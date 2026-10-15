# Plan — 多后继的机械化表态

**Feature**: `specs/247-multi-successor-adjudication/`
**Prerequisites**: spec.md

---

## 一、官方源（本特性要查的源，及冲突裁决顺序）

| 源 | 路径 | 用途 | 许可 |
|---|---|---|---|
| 官方类型页（`C:\swapi`） | `C:/swapi/types/<接口>/<成员>.md` | ★ **那句的措辞** + 两边签名 + 页首行 | 官方文档，**只读引用** |
| 官方废弃索引 | `specs/202-user-coverage-gaps/recon/official-obsolete-index.json` | 条目与 `obsolete_line` | 本仓自产 |
| 六关真源 | `tests/test_deprecated_table_admission._admission_failures` | ★ **直接调用**，不重写 | 本仓自产 |
| 调用口径真源 | `tests/test_deprecated_entry_interlock._scan_all_modules` / `_REGISTERED` | ★ **直接 import** | 本仓自产 |

**裁决顺序**：① 官方页**措辞**（几个真后继）→ ② 官方索引**链终点**（★ 不是字面后继）→ ③ 真树调用点。
★ 冲突时**不猜**：判 `拒` 并写理由。

---

## 二、技术方案

### 1. ★★ 三态判据（纯函数）

```
_official_successor_links(line) -> list[str] | None
   Superseded by <clause>              ⇒ clause 内全部链接
   See <clause> and the Remarks in/of … ⇒ Remarks 之前的链接
   其它 See …                          ⇒ None（★ 顺序不可靠 ⇒ 判不出）
```

★ **为什么「其它 `See …`」判不出**（★ 实测，不是推测）：
`Obsolete. See [[IProjectionCurveFeatureData]] and [[IFeatureManager::CreateDefinition]].`
⇒ ★ **数据接口在前、真后继在后** ⇒ ★ 按位置取必错。

### 2. 关 5 的三态

| `n` | 处置 |
|---|---|
| `1` | ★ 过（但那个链接必须**在通往本表后继的链上** —— 允许 242 的跳代） |
| `> 1` | ★ **拒**（表表达不了「两个都要」；★ **表态也不放行**） |
| `None` | ★ **必须有表态**（`_MULTI_SUCCESSOR_ADJUDICATED`），否则 `successor-count-undecidable` |

### 3. 收 / 拒

| 条目 | 措辞 | 决定 |
|---|---|---|
| `IFeatureManager::FeatureLinearPattern5` | `See [[CreateFeature]] and the Remarks in …` | ★ **收** → `CreateFeature` |
| `IFeatureManager::FeatureLocalCurveDrivenPattern` | `See [[CreateFeature]] and the Remarks in …` | ★ **收** → `CreateFeature` |
| `IFeatureManager::InsertFormToolFeature` | `Superseded by [[CreateDefinition]] and [[CreateFeature]]` | ★ **拒**（两个都是后继） |
| `IModelDoc2::SketchTrim` | `Superseded by [[SketchExtend]] and [[SketchTrim]]` | ★ **拒**（★ 关 4：真后继同名） |

### 4. 收表的连带（★ 242 的教训 40 + 246 的教训 53）

1. `scripts/sw_com_traps.py` 的 `DEPRECATED_ENTRIES` **+2 条**（9 → **11**）。
2. `tests/test_deprecated_entry_interlock.py` 的 `_REGISTERED` **+2 处**
   （`sw_part.py` 的 `FeatureLinearPattern5` ×2 · `sw_pattern.py` 的 `FeatureLocalCurveDrivenPattern` ×1）。
3. `tests/test_deprecated_table_admission.py` 里写着「**11 条**」的**正文**同步。
4. ★ **改了 `scripts/` ⇒ 必须跑生成器链**（7 步）。

---

## 三、任务与验收

见 `tasks.md`。

---

## 四、许可

| 来源 | 许可 | 义务 |
|---|---|---|
| 上游 `wzyn20051216/solidworks-automation-skill` | **MIT** | 保留版权声明（本特性**未抄任何上游文本**） |
| 四家外部 MCP 项目 | MIT / Apache-2.0 | 同上，本特性**未引用** |
| 官方 SolidWorks API 文档（`C:\swapi`） | 官方文档 | ★ **只读引用**措辞与签名，**不抄正文** |
| 本仓自产 | — | 无 |

★ 本特性**不新增任何外部代码或文本**。

---

## 五、风险与回退

| 风险 | 处置 |
|---|---|
| 改关 5 语义会**动摇 243 的契约** | ★ 243 的负例（`SketchTrim` 期望 `multiple-official-successors`）**仍然成立**（★ 该句的真后继数 = 2）⇒ 已实测 |
| 表态表为空 ⇒ 判据**空满足** | ★ 把三态抽成**纯函数**，由**合成表态表**驱动 ⇒ 真表为空也**有检查量**（FR-002/FR-004） |
| 措辞分类漏了形态 | ★ 已量**全部 254 条**的分布（235 / 14 / 5），★ 并把 `Remarks of` 形态**单列一条用例** |
| 收表会改变公开工具输出 | ★ 只**增**不改；★ 新条目全部过六关 |
