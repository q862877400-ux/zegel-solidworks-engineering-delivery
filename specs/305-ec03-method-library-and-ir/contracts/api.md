# Contract — 305-ec03-method-library-and-ir 的公开接口

**Feature**: `specs/305-ec03-method-library-and-ir/`

**来源**: ★ **AST 提取**（★ 真签名）

---

| ★ 函数 | ★ 说明 |
|---|---|
| `score_elegance` | ★★ **按多指标打分**（★ 可算 —— ★ 不是形容词）。 |
| `compile_contract` | ★★★★★ **编译**（★ EC03 的主入口）。 |
| `assert_no_com_imports` | ★★★★ **纯离线自证**（★ V5：★「不需要 COM 即可检验计划正确性」）。 |
| `is_production_method` | ★★★★ **是不是生产方法**（★ EC03-T08 逐字：★「★ 建**沙箱探索通道**； |
| `list_sandbox_methods` | ★ 从候选里挑出**沙箱产物**（★ 便于审查 —— ★ 不是直接入库）。 |
| `find_unsat_core` | ★★★★ **不可满足核心**（★ EC03-T05 逐字：★「★ 定义**不可满足核心**/未知/超时/多方案排序」） |
| `solve_with_budget` | ★★★ **带预算的求解**（★ EC03-T05 逐字：★「★ **超时**……★ `unknown` 不能落入默认可 |
| `rank_plans` | ★★ **多方案排序**（★ EC03-T05 逐字：★「★ 多方案排序」）。 |
