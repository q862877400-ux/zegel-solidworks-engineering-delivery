# Acceptance — **EC01 工程设计契约与对象模型**

**Feature**: `specs/303-ec01-engineering-contract/`
**日期**: 2026-10-10
**状态**: ★★ **offline 收口 · runtime/product = `not_run`**（★ 本特性**不碰 COM** —— ★ 承 `spec.md` §五）
**上游**: `output/ENGINEERING_CONSTRUCTION_PLAN.md` §5 EC01 · `spec.md`（★ 15 FR · 8 V）

---

## 一、★★★★★ 三级结论（★ 分字段记录 · ★ FR-013 同族）

| ★ 级别 | ★ 结论 | ★ 依据 |
|---|---|---|
| ★ **offline** | ✅ **pass** | ★ **47 例**（★ 3 个判据文件）全绿 |
| ★★ **runtime** | ⏸ **`not_run`** | ★★ **本特性**不碰 COM**（★ 承 `spec.md` §五 非目标）—— ★ **不是「没做」，是「不该做」** |
| ★★ **product** | ⏸ **`not_run`** | ★ 发布门未到 |

---

## 二、★★★★★ V1–V8 逐条读数（★ 逐字承 `spec.md` §四）

| ★ # | ★ 判据（★ 计划 §5 EC01 验收逐字） | ★ 判据文件 | ★ 结果 |
|---|---|---|---|
| **V1** | ★ **非法量纲在 COM 前阻断** | `test_ec01_quantity_reuse.py` | ✅ **pass**（★ 5 例：★ 量纲不符/非有限/未知单位/重复换算/**温度偏置**） |
| **V2** | ★ **缺关键工况在 COM 前阻断** | `test_ec01_quantity_reuse.py` | ✅ **pass**（★ 4 例：★ 缺工况/缺安全等级/`required_missing`/无依据假设） |
| **V3** | ★ **两个不同表述的同意图归一到同语义** | `test_ec01_quantity_reuse.py` | ✅ **pass**（★ 3 例：★ 80mm≡0.08m · ★ 可解释 · ★ **不同意图不混**） |
| **V4** | ★★ **新版本不能借用旧批准** | `test_ec01_contract_model.py` | ✅ **pass**（★ 6 例 · ★ **含红基线**） |
| **V5** | ★★★ **工程基准不能简单等同任一 CAD 基准面** | `test_ec01_contract_model.py` | ✅ **pass**（★ 3 例：★ 身份=语义角色 · ★ **CAD 改名身份不变**） |
| **V6** | ★ 旧 `design_plan` **适配**，★ 不足留 `unknown` | `test_ec01_legacy_and_kinds.py` | ✅ **pass**（★ 5 例：★ 10 字段认全 · ★ **不编默认值** · ★ **不改旧契约**） |
| **V7** | ★ **四类信息**齐全，★ 只有 `required_missing` 阻断 | `test_ec01_contract_model.py` | ✅ **pass**（★ 3 例） |
| **V8** | ★ **澄清问题是最小集**；★ 保守/禁止假设分开 | `test_ec01_contract_model.py` | ✅ **pass**（★ 2 例 · ★ **含「改依据也蒙混不过」的负例**） |
| — | ★ **T08 四类契约 + 三类负例** | `test_ec01_legacy_and_kinds.py` | ✅ **pass**（★ 7 例：★ 板/轴/机构/气动**可冻结** · ★ **语义互异** · ★ **哈希互异** · ★ 缺参数/错误单位/域冲突） |

---

## 三、★★★★★ 红基线证明（★ 事实 62：判据「写了」≠「有效」）

| ★ 判据 | ★ 怎么证它真在守 | ★ 红时读数 |
|---|---|---|
| ★★ V4（★ 旧批准不能借用） | ★ 把 `approval_is_valid` 改成恒 `True` | ★ **1 failed** ✓ |

★★★ **⇒ V4 的判据**真的**在守「新内容不能用旧批准」**（★ 不是关键词 grep）。

---

## 四、★★★★★ 关键设计决策（★ 每条都有依据）

### 4.1 ★★ `Quantity` **复用 EC00**（★ 不另建一套量纲）

★★★ **依据（★ 铁律 1「只做缝合」+ 计划 §5 EC01）**：★ EC00 已有 `Quantity`/`NormalizedQuantity`
（★ `specs/302-*/contracts/quantity.md`）⇒ ★★ **EC01 直接复用**。
★ 判据：★ `test_v1_rejection_codes_are_a_closed_vocabulary` —— ★ **拒绝码必须与 EC00 同一套**
（★ 逐条在 EC00 的契约文档里能查到）✓

### 4.2 ★★★ `Datum` 的身份 = **语义角色**（★ 不是 CAD 平面名）

★★★ **依据（★ 计划 §5 EC01 验收逐字）**：「★ **工程基准不能简单等同任一 CAD 基准面**」。
★★ **为什么这条重要**：★ CAD 平面名**随 UI 语言变**（★ 已知事实 9：`"Front Plane"` / `"前视基准面"`）
⇒ ★★ 若身份绑平面名，★ **换语言就换身份** ✗
★ 判据：★ `test_v5_datum_identity_survives_cad_plane_rename`（★ `"Front Plane"` 与 `"前视基准面"` **同身份**）✓

### 4.3 ★★★ 温度是**偏置单位** ⇒ 用加法不用乘法

★★ **依据（★ 承 EC00 `contracts/quantity.md` §2.3 逐字）**：
★「★ **偏置单位如温度独立定义，不混用乘法**」。
★ 判据：★ `test_v1_temperature_uses_offset_not_multiplication`（★ `0 degC` ⇒ **`273.15 K`**）✓

### 4.4 ★★★ 内容哈希**排除自指字段**

★★ **依据（★ FR-004）**：★ 哈希**不能**包含 `state`/`approvals`/`content_hash` 自身
—— ★★ 否则「加一个批准」就会改哈希 ⇒ ★ **批准自己让自己失效** ✗
★ 判据：★ `test_v4_hash_excludes_self_referential_fields` ✓

### 4.5 ★★★ 适配器**只读**旧计划

★★ **依据（★ `DSH_DECISIONS.md` **D-001**）**：★ 旧 MCP **标量参数、`required`/`default` 语义保持**。
★ 判据：★ `test_t05_adapter_does_not_write_back_to_the_legacy_plan`（★ 前后 JSON **逐字相同**）✓

---

## 五、★★★ 我在实现里**订正过**一处（★ 如实登记）

| ★ 版 | ★ `reject-kind-mismatch` vs `reject-unknown-unit` 的判法 | ★ 结果 |
|---|---|---|
| ★ 第一版 | ★ 查「**该量纲**有没有别的单位」 | ❌ **判反了** —— ★ `("length","deg")` 落进「单位不认识」✗ |
| ★ 第二版 | ★ 查「**`unit` 是否属于别的量纲**」 | ✅ **对** —— ★ `deg` 属于 `angle` ⇒ ★ `reject-kind-mismatch` ✓ |

★★★ **⇒ 可复用教训**：★ **两个拒绝码的**判据方向**容易写反** ——
★ 「量纲不对」要看**单位**的归属，★ 「单位不认识」要看**单位**谁都不属于。

---

## 六、★★★ 残余风险（★ 具名）

| ★ # | ★ 项 | ★ 处置 |
|---|---|---|
| ① | ★★ **`runtime` 未做** | ★★ **本特性**不该做**（★ 不碰 COM）—— ★ 建模在 EC05 |
| ② | ★ **`CoordinateFrame` / `Fit` / `DimensionChain` 未单独落** | ★ 它们目前由 `Datum` + `ParameterDomain` **承载**；★ 若 EC05 需要更细的链式公差，★ **那时再抽**（★ 铁律 1：**先复用**） |
| ③ | ★ **`FunctionRequirement` / `ApplicabilityDecision` 未单独落** | ★ 与 ② 同处置 —— ★ 它们属 EC02（★ 适用性）/EC03（★ 功能需求→方法）的**消费方** |
| ④ | ★ **未提交未部署** | ★ 红线（★ 提交/发布另行授权） |

★★★ **⇒ ② ③ 是**有意的**（★ 不是遗漏）**：★ **铁律 1 要求「先复用」** ——
★ 在 EC02/EC03 **真的需要**那两个对象之前，★ **不预先造**（★ 那会变成「三份 schema 各写一份」）。
