# Checklist — 303-ec01-engineering-contract

**Feature**: `specs/303-ec01-engineering-contract/`

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

- [x] ★ 唯一入口的判据是 `required_missing`
- [x] ★ `Datum` 的身份 = **语义角色**，不是 CAD 平面名
- [x] ★ 温度用**偏移单位**（`OFFSET_UNITS`），不是乘法
- [x] ★ `compute_hash` **排除自指字段**
- [x] ★ `com_eligible()` **只在冻结后**为真
