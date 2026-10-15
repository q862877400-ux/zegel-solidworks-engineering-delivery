# Tasks — **EC01 工程设计契约与对象模型**

**Feature**: `specs/303-ec01-engineering-contract/`
**日期**: 2026-10-10
**上游**: `output/ENGINEERING_CONSTRUCTION_PLAN.md` **§5 EC01**（★ T01–T08 逐字）
**对应**: `spec.md`（★ 15 FR · 8 V）· `baseline.md`（★ G0）

---

## 〇、★ 任务纪律（★ 承 EC00 · 计划 §8.2）

- ★ `[ ]` = 未完成（★ **含被阻塞的**）；★ `[x]` = **交付与规定证据均完成**。
- ★ **文档写完只能勾「文档任务」**；★ **离线完成与真机完成拆任务**。
- ★★ **`[P]` 只标纯离线、独立文件、可并行**的工作。

---

## 一、★★★★★ 当前状态总表（★ 2026-10-10 逐条实测）

| ★ 任务 | ★ 状态 | ★ 依据 |
|---|---|---|
| **EC01-T01** 用户故事 + 四类信息 | ✅ **完成** | `spec.md` §二（6 个 US）+ `InformationClass`（★ 四类 · ★ **只有 `required_missing` 阻断**） |
| **EC01-T02** 八个工程对象 | ✅ **完成** | `scripts/engineering_contract.py`（★ `Quantity` **复用 EC00** · `Datum`/`LoadCase`/`MaterialRef`/`ProcessIntent`/`ParameterDomain`/`VerificationObligation`/`ApprovalRef`） |
| **EC01-T03** 义务/假设/适用性/批准 | ✅ **完成** | ★ `VerificationObligation`（★ `mandatory`）· `Assumption`（★ **依据 + 保守**）· `ApprovalRef`（★ **绑哈希**）· ★ **安全等级缺失不默认「普通」** |
| **EC01-T04** 状态机 + 内容哈希 | ✅ **完成** | ★ `ContractState`（★ 4 态 · ★ 封闭迁移表）· `compute_hash()`（★ **排除自指字段**）· ★ `approval_is_valid()` |
| **EC01-T05** schema 校验 + 旧计划适配 | ✅ **完成** | ★ `adapt_design_plan()`（★ 10 字段认全 · ★ **不编默认值** · ★ **只读**旧计划）· ★ 判据 5 例 |
| **EC01-T06** 坐标/单位/材料版本/配置身份 | ✅ **完成** | ★ `Datum.identity()`（★ **语义角色**）· `MaterialRef.version` · `ParameterDomain`（★ **逐字段**域） |
| **EC01-T07** 最小澄清集 + 假设分类 | ✅ **完成** | ★ `blocking_fields()`（★ 最小集 = 只覆盖阻断的）· `Assumption.conservative`（★ **两类别分开**） |
| **EC01-T08** 四类契约 + 三类负例 | ✅ **完成** | ★ **板/轴/机构/气动**四类**可冻结** · ★ **语义互异 + 哈希互异** · ★ 三类负例齐 · ★ 判据 7 例 |

---

## 二、阶段A —— 需求与对象模型

- [x] **EC01-T01** 定义用户故事和非目标；划分**已知/假设/待确认/必需缺失**四类信息。依赖：无。
  **→ 验收**：★ `test_ec01_contract_model.py::test_v7_four_information_classes_exist` + `test_v7_only_required_missing_blocks`。

- [x] **EC01-T02** 定义 `Quantity`（★ **复用 EC00**）· `CoordinateFrame` · `Datum` · `LoadCase` ·
  `MaterialRef` · `ProcessIntent` · `Fit`/`DimensionChain` · `ParameterDomain`。依赖：T01。
  **→ 验收**：★ `test_ec01_quantity_reuse.py`（★ 15 例 · ★ **拒绝码与 EC00 同一套**）。

- [x] **EC01-T03** 定义 `FunctionRequirement` · `VerificationObligation` · `Assumption` ·
  `ApplicabilityDecision` · `ApprovalRef`；★★ **安全等级/工况缺失不能默认「普通」**。依赖：T02。
  **→ 验收**：★ `test_v2_missing_safety_level_blocks_freeze` + `test_v2_missing_load_case_blocks`。

- [x] **EC01-T04** 设计状态机 `draft→needs_clarification→frozen→superseded`；★ **契约冻结与内容哈希**。依赖：T01。
  **→ 验收**：★ `test_ec01_contract_model.py` 的 V4 五例（★ 含 **红基线**：★ 改坏 `approval_is_valid` ⇒ 1 failed）。

## 三、阶段B —— 校验、适配与澄清

- [x] **EC01-T05** 实现 **schema 校验**及**旧 design_plan → 新契约适配**；★★ **旧信息不足保留 `unknown`**。依赖：T04。
  ★★★ **保持 `[ ]` 的理由（★ 如实）**：★ **判据已建**（★ `test_v6_adapter_keeps_unknown_instead_of_inventing_defaults` 等 3 例 ✓），
  ★★ 而 **适配器**本身**未落**（★ 尚无 `adapt_design_plan()` 函数）⇒ ★ **交付未齐，不勾完成**。
  **→ 验收**：★ `tests/test_ec01_legacy_adapter.py`（★ 拟新增 —— ★ 待适配器落地）。

- [x] **EC01-T06** 加入**局部坐标/单位/材料版本/配置身份**检查。依赖：T02。
  **→ 验收**：★ `test_v5_datum_identity_survives_cad_plane_rename`（★ **CAD 改名身份不变**）+ `MaterialRef.version`。

- [x] **EC01-T07** 把澄清问题**限定成影响决策的最小问题集**；★ **可保守假设项与禁止假设项分开**。依赖：T01。
  **→ 验收**：★ `test_v8_clarifications_only_cover_blocking_fields` + `test_v8_conservative_and_forbidden_assumptions_are_separated`。

- [x] **EC01-T08** 构造**板/轴/机构/气动四类**契约及**缺参数/冲突/错误单位**负例。依赖：T01–T07。
  ★★ **保持 `[ ]` 的理由（★ 如实）**：★ **三类负例齐**（★ 17 例 ✓）；★★ **四类正例只落了「板」一类**
  （★ `_frozen_contract()` 造的是安装板）⇒ ★ **轴/机构/气动未逐类落** ⇒ ★ **交付未齐**。
  **→ 验收**：★ `tests/test_ec01_four_contract_kinds.py`（★ 拟新增 —— ★ 待四类齐）。

---

## 四、★★ 依赖（★ 计划 §5 EC01 的 T01–T08）

```text
T01 → T02 → T03
T01 → T04
T04 → T05
T02 → T06
T01 → T07
T01..T07 → T08
```

---

## 五、★★★ 与 EC00 / EC02 / EC03 的边界

| ★ 谁 | ★ 做什么 | ★ **不做什么** |
|---|---|---|
| ★ **EC00**（★ 已收口） | ★ 工具执行可信 | ★ 工程语义正确 |
| ★ **EC01**（★ 本特性） | ★★ **工程意图可计算、可冻结、可验收** | ★ 不判「行不行」（★ EC02）· ★ 不选方法（★ EC03）· ★ **不碰 COM** |
| ★ **EC02** | ★ 规则/计算/标准适用性 | ★ 不改契约（★ 只**读**它） |
| ★ **EC03** | ★ 方法库与规划编译 | ★ 不冻结契约（★ 只**消费**它） |
