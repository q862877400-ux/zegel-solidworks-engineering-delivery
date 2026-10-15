# Spec — 索引后继规则：**同名链接优先**（把 244 的裁决接进生成器）

**Feature**: `specs/251-index-successor-rule/`
**日期**: 2026-10-09
**上游**: `specs/244-multi-successor-rule/`（★ 裁决了「同名链接优先」规则，但**只登记了 6 条偏差、没改生成器**）
**本轮只做一件事**：把那条规则**接进 `tools/build_obsolete_index.py`**，重生成索引，并**同步所有连带判据**。

---

## 一、背景

244 定下规则：**多链接里「与被废弃成员同名」的那个才是真后继**（★ 官方用它表达**接口迁移**），
但当时只把 6 条偏差登记进 `_KNOWN_WRONG`，**生成器仍是 `re.search` 取第一个链接**（★ 有损）。

245 已证这 6 条**在真树上零靶子** ⇒ 优先级低；★ 但它仍是**索引本身的数据错误**。

---

## 二、★★ 先量（★ 动手前必须做）

`output/_probe251_rule_impact.py` → `.txt`：

| 读数 | 值 |
|---|---|
| 总条目 | **1671** |
| 多链接（≥2）条目 | **254** |
| 其中含「同名链接」 | **11** |
| ★★ **规则生效后后继会变的条目** | **6** |

★ 且探针自证：**现行索引确由现行规则生成**（与规则不符条数 **0**）。

⇒ ★★ **只改 6 条 ⇒ 修法安全。**

| 被废弃 | 旧后继（错） | 新后继（对） |
|---|---|---|
| `IFeature::GetBody` | `IFeatures::GetFaces` | `IFace2::GetBody` |
| `IFeature::IGetBody` | `IFeatures::GetFaces` | `IFace2::IGetBody` |
| `IModelDoc2::SketchTrim` | `ISketchManager::SketchExtend` | `ISketchManager::SketchTrim` |
| `INote::IGetTextFormat` | `IAnnotation::GetTextFormat` | `IAnnotation::IGetTextFormat` |
| `INote::ISetTextFormat` | `IAnnotation::SetTextFormat` | `IAnnotation::ISetTextFormat` |
| `ISheet::ICreateOLEObject` | `IModelDocExtension::CreateOLEObject` | `IModelDocExtension::ICreateOLEObject` |

★ **官方原句**（★ 逐条）：
- `C:/swapi/types/IFeature/GetBody.md:12` ——
  `Obsolete. Superseded by [[IFeatures::GetFaces]], [[IFeatures::IGetFaces2]], [[IFace2::GetBody]], and [[IFace2::IGetBody]].`
- `C:/swapi/types/IFeature/IGetBody.md` —— 同上（同名链接是 `IFace2::IGetBody`）。
- `C:/swapi/types/IModelDoc2/SketchTrim.md:12` ——
  `Obsolete. Superseded by [[ISketchManager::SketchExtend]] and [[ISketchManager::SketchTrim]].`
  ★ 语义实证：`ISketchManager::SketchTrim` = "Trims the selected sketch entities"；
  `SketchExtend` = "**Adds to the length**"（延伸）⇒ ★ 旧值语义完全不符。
- `C:/swapi/types/INote/IGetTextFormat.md` —— 同名链接 `IAnnotation::IGetTextFormat`。
- `C:/swapi/types/INote/ISetTextFormat.md` —— 同名链接 `IAnnotation::ISetTextFormat`。
- `C:/swapi/types/ISheet/ICreateOLEObject.md` —— 同名链接 `IModelDocExtension::ICreateOLEObject`。

---

## 三、需求

### FR-001 生成器必须实现「同名链接优先」

- **来源**：244 的裁决。
- **规则**：`tools/build_obsolete_index.py` 取后继时，先看**全部** `[[…]]` 链接；若其中某个链接的**成员名 == 被废弃成员名** ⇒ 取它；否则取第一个。
- **验收场景**：`test_fixed_by_251_successors_are_in_the_index` 通过；★ 索引里那 6 条的后继等于真后继。

### FR-002 ★★ 先量：改动面必须**恰好**是 6 条

- **来源**：本项目纪律（「先量：目标规模 + 加词的爆炸半径」）。
- **规则**：探针必须报出「规则生效后变的条目数」；★ 与 244 登记的 6 条**相等**。
- **验收场景**：`output/_probe251_rule_impact.txt` 读数 = **6**；★ 索引重生成后与备份 diff = **6**。

### FR-003 ★★ 清空后的登记表**不许让判据变空**

- **来源**：本仓铁律（「检查量为 0 判失败」；★「空的表 = 空判据」）。
- **规则**：`_KNOWN_WRONG` 清空的同时，必须补**正向**断言 `_FIXED_BY_251`（6 条：索引后继 == 真后继）；
  ★ 且「同名链接」判据要钉**检查量下界 11**。
- **验收场景**：`test_fixed_by_251_successors_are_in_the_index` + `test_...same_name...` 的 `checked >= 11`。

### FR-004 ★★ 连带判据必须同步（★ 4 处）

- **来源**：本项目纪律（「改了实现，登记表/钉死数量不会自己报错」）。
- **规则**：① `tests/test_obsolete_multi_successor.py` 的 `_KNOWN_WRONG` → 空 + `_FIXED_BY_251`；
  ② `tests/test_deprecated_table_admission.py` 的 `SketchTrim` 夹具值 → `"SketchTrim"`；
  ③ `tests/test_deprecated_multi_successor_adjudication.py` 同上；
  ④ `tests/test_deprecated_admissible_disposition.py` 删 `SketchTrim` 行 + 下界 **15 → 14**。
- **验收场景**：相关族 9 个文件全绿。

### FR-005 ★★ 修一个**潜伏的空判据**

- **来源**：本轮实测发现。
- **规则**：244 的 `test_known_wrong_registry_matches_index` 原写 `e["successor"] == _split(expected)`
  —— ★ **`str` 与 `tuple` 永不相等** ⇒ ★ 该「过期检测」**从未生效**（★ 空判据）。★ 必须两边都 `_split`。
- **验收场景**：修好后逻辑正确（★ 由 `_FIXED_BY_251` 的正向断言覆盖）。

---

## 四、非目标

- **不**改索引的**取行**逻辑（`head` / `OBS` / 位置口径）—— ★ 只改**取链接**那三行。
- **不**把索引整表灌进 `DEPRECATED_ENTRIES`。
- **不**动 245/248/249/250 的表态表（★ 它们的结论不依赖 `successor` 字段）。

## 五、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 改动面**恰好 6 条** | 索引 diff vs `output/_index_backup_251.json` = 6 |
| SC-2 | 6 条的后继 == 真后继 | `test_fixed_by_251_successors_are_in_the_index` |
| SC-3 | 相关族全绿 | 9 个文件 **67 passed** |
| SC-4 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-5 | 生成器链 | ★ **本轮改了 `tools/`** ⇒ ★ 需评估（见 `acceptance.md`） |

## 六、未过门（本轮不做，如实登记）

- **`SketchTrim` 的 4 处真命中仍未换路由**（★ 需 COM 授权；★ 索引修好**不等于**代码换路由）。
- **其余 248 条多链接条目的「字面后继」仍未核** —— ★ 本轮只处理**有同名链接**的 11 条。
- 真机未验；223 的 8 条既有红未修；未提交未部署。
