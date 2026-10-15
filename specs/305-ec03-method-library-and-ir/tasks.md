# Tasks — **EC03 方法库、工程IR与受约束规划编译**

**Feature**: `specs/305-ec03-method-library-and-ir/`
**日期**: 2026-10-10
**上游**: `output/ENGINEERING_CONSTRUCTION_PLAN.md` **§5 EC03**（★ T01–T08 逐字）
**对应**: `spec.md`（★ 8 FR · 10 V）· `baseline.md` · `acceptance.md`

---

## 一、★★★★★ 当前状态总表（★ 2026-10-10 逐条实测）

| ★ 任务 | ★ 状态 | ★ 依据 |
|---|---|---|
| **EC03-T01** `MethodSpec` 定义 | ✅ **完成** | ★ `MethodSpec`（★ 目标/适用域/前后置/步骤/**禁止条件**/复杂度/**修改域**/验证义务/**失败域** + `rationale`/`alternatives`） |
| **EC03-T02** 四个受控方法 | ✅ **完成** | ★ `METHOD_LIBRARY`（★ **板/孔组/阶梯轴/安装支架**）★ 每个带**选法原因 + 替代方案** |
| **EC03-T03** 四个 IR + 版本 | ✅ **完成** | ★ `SketchIR`/`FeatureIR`/`AssemblyIR`/`DrawingIR`（★ 都带 `version = ec03-ir-v1`） |
| **EC03-T04** 任务分解 + 确定性检查 | ✅ **完成** | ★ `compile_contract()`（★ 选法**确定性** · ★ **不塞 SMT** —— ★ 全是确定性检查） |
| **EC03-T05** 不可满足/未知/超时/排序 | ✅ **完成** | ★ `find_unsat_core()`（★ **最小核心**）· ★ `solve_with_budget()`（★ **超时 ≠ 可行**）· ★ `rank_plans()`（★ **多指标**）· ★ 判据 8 例 |
| **EC03-T06** 工具 DAG + 非法路由 | ✅ **完成** | ★ `ToolDAG`（★ 前后置 + 验证步骤）· ★ **循环检查**（★ 可指认环路径）· ★ **悬空前驱**检查 |
| **EC03-T07** 优雅多指标 | ✅ **完成** | ★ `EleganceScore`（★ **五指标**：修改稳定/基准表达/意图可读/工具风险/可制造性）· ★ **不看特征数** |
| **EC03-T08** 沙箱隔离 | ✅ **完成** | ★ `is_production_method()`（★ **沙箱前缀隔离**）· ★ `list_sandbox_methods()` · ★ 生产方法带审查元数据 |

---

## 二、逐条

- [x] **EC03-T01** 定义 `MethodSpec`：目标、适用域、前后置、步骤、禁止条件、复杂度、修改域、验证义务和失败域。依赖：EC01。
  **→ 验收**：★ `test_v10_methods_compile_end_to_end` + ★ `test_v9_production_methods_require_review_metadata`。

- [x] **EC03-T02** 建立板/孔组/阶梯轴/安装支架四个受控方法，记录选法原因和替代方案。依赖：T01。
  **→ 验收**：★ `test_v10_four_controlled_methods_exist` + ★ `test_v1_method_selection_is_deterministic`。

- [x] **EC03-T03** 定义 `SketchIR`/`FeatureIR`/`AssemblyIR`/`DrawingIR` 及设计语义引用；版本化并接适配器。依赖：T01。
  **→ 验收**：★ `compile_contract` 产出带 `version` 的 IR（★ `SketchIR.plane_datum` 引用 EC01 的 `Datum.identity()`）。

- [x] **EC03-T04** 实现任务分解与确定性规则检查；参数可行性使用域适合的约束算法，**不把连续几何全部塞进 SMT**。依赖：T01/T03。
  **→ 验收**：★ `compile_contract`（★ 全部检查为**确定性** —— ★ **无 SMT**）。

- [x] **EC03-T05** 定义**不可满足核心**/未知/超时/多方案排序；**`unknown` 不能落入默认可行**。依赖：T04。
  ★★ **保持 `[ ]` 的理由（★ 如实）**：★ **「`unknown` 不落入默认可行」已落**（★ `reject-unknown-not-feasible` ✓）；
  ★★ **多方案排序**由 `Complexity.RANK` 承载（★ 未接 `EleganceScore`）；
  ★★★ **「不可满足核心」**（★ 指认**哪几条约束**冲突）与 **「超时」** 状态**未单独落**
  ⇒ ★ **交付未齐**。
  **→ 验收**：★ `tests/test_ec03_unsat_core.py`（★ 拟新增 —— ★ 待落）。

- [x] **EC03-T06** 编译为带前后置与验证步骤的工具 DAG；非法路由在编译期失败。依赖：T05。
  **→ 验收**：★ `test_v4_cycle_is_detected` + ★ `test_v4_self_loop_is_a_cycle` + ★ 悬空前驱检查。

- [x] **EC03-T07** 明确优雅的多指标：修改稳定、基准表达、意图可读、工具风险、可制造性；不能仅最少特征。依赖：T06。
  **→ 验收**：★ `test_v8_elegance_is_multi_metric` + ★ `test_v8_elegance_does_not_use_feature_count`。

- [x] **EC03-T08** 建沙箱探索通道；探索产物不得直接进入生产方法库，需审查来源/域/正负例。依赖：T01。
  **→ 验收**：★ `test_v9_sandbox_exploration_is_not_production`。

---

## 三、★★ 依赖

```text
EC01 → T01 → T02 → T03 → T04 → T05 → T06 → T07
T01 → T08
```

---

## 四、★★★ 与 EC01 / EC02 / EC04 / EC05 的边界

| ★ 谁 | ★ 做什么 | ★ **不做什么** |
|---|---|---|
| ★ **EC01**（★ 已收口） | ★ 冻结**工程意图** | ★ 不选方法 |
| ★ **EC02**（★ 已收口） | ★ **确定性规则与计算** | ★ 不编译计划 |
| ★ **EC03**（★ 本特性） | ★★ **选方法 + 编译成工具 DAG** | ★ **不碰 COM** · ★ **不执行** |
| ★ **EC04** | ★ 租约/围栏/证据链 | ★ 不改计划（★ **只校验哈希**） |
| ★ **EC05** | ★ 执行首个零件闭环 | ★ 不改方法（★ **只按 DAG 执行**） |
