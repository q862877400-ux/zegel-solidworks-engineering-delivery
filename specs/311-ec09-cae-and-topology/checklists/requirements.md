# Checklist — 311-ec09-cae-and-topology

**Feature**: `specs/311-ec09-cae-and-topology/`

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

- [x] ★ **独立参考解**（闭式解 —— 取自求解器的不算）
- [x] ★ **反力平衡**（外载为 0 ⇒ **不能判平衡**）
- [x] ★ 网格收敛**至少三档** + **追峰 ⇒ 拒**
- [x] ★ **六道门**：solve/reference/balance/convergence/closure/reanalysis
- [x] ★ **工程通过 ≠ 可以写「真实工况已验证」**
- [x] ★ **优化后必须复分析**
- [x] ★ 敏感性**归一化排序** + **不可改域冻结**
