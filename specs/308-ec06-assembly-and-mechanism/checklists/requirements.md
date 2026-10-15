# Checklist — 308-ec06-assembly-and-mechanism

**Feature**: `specs/308-ec06-assembly-and-mechanism/`

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

- [x] ★ 五类约束状态**分开**（欠约束/冗余/过约束/预期运动/完全）
- [x] ★ 预期运动**不是**欠约束
- [x] ★ 干涉扫描**无全域证明 ⇒ `unknown`**
- [x] ★ 空扫描覆盖率 **0.0**（不是 1.0）
- [x] ★ 错轴向检测（`PARALLEL`/`PERPENDICULAR` 豁免）
- [x] ★ 公差链**复用 EC02**（结果逐字相同）
