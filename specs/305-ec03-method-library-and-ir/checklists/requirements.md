# Checklist — 305-ec03-method-library-and-ir

**Feature**: `specs/305-ec03-method-library-and-ir/`

---

## ★★ 六道管理门（★ 承计划 §3）

| ★ 门 | ★ 判据 | ★ 本特性 |
|---|---|---|
| **G0** 基线 | ★ 编号/权属/写入面明确 | ✅ `baseline.md` |
| **G1** 需求冻结 | ★ FR 逐条可测 | ✅ `spec.md` |
| **G2** 技术冻结 | ★ 接口与数据模型定死 | ✅ `contracts/api.md` · `data-model.md` |
| **G3** 可施工 | ★ 任务有依赖与落点 | ✅ `tasks.md` |
| **G4** 实现验证 | ★ 判据全绿 + **红基线** | ✅ `acceptance.md` |
| **G5** 收口发布 | ★ 生成器链 + `release_check` + `goal_gate` | ✅ EXIT 0 |

## ★★ 本特性专属

- [x] ★ 编译器**只吃** `EngineeringContract`
- [x] ★ **全部检查在编译期**
- [x] ★ 编译器**不 import 任何 COM 模块**（AST 自证）
- [x] ★ 冻结计划带**内容哈希** + 执行前校验
- [x] ★ 优雅 = **五指标**，**不看特征数**
- [x] ★ **不可满足核心是**最小**的**（不是「全都冲突」）
- [x] ★ **超时 ≠ 可行**
