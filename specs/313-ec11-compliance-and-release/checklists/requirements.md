# Checklist — 313-ec11-compliance-and-release

**Feature**: `specs/313-ec11-compliance-and-release/`

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

- [x] ★ 条款**必须带 KS 定位**（`doc_id` + `page_start`）
- [x] ★ 五态 + **四态必须给原因**（不适用/未知/失败/过期）
- [x] ★ **推荐标准不能出「强制」结论**
- [x] ★ **删证据/改工况 ⇒ 放行失效**（降为 `unknown`）
- [x] ★ **四类批准分开**（软件包/CAD/审签/整机符合性）
- [x] ★ 整机符合性**不能软件自签**（须人工批准）
