# Checklist — 306-ec04-safe-jobs-and-evidence

**Feature**: `specs/306-ec04-safe-jobs-and-evidence/`

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

- [x] ★ `uncertain` **不能回 `running`**
- [x] ★ 节点租约 + **围栏令牌**（单调递增）
- [x] ★ 批准**绑 contract/plan/model 三版本**
- [x] ★ **`HAS_GLOBAL_TRANSACTION = False`**
- [x] ★ 前向补偿**绝不删用户文件**
- [x] ★ 独立验收器**只读** + **自评拒**
- [x] ★ 无许可 ⇒ **`design_advice_only`**
