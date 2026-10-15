# Checklist — 314-ec12-capability-package-and-eval

**Feature**: `specs/314-ec12-capability-package-and-eval/`

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

- [x] ★ 留出集**指纹可复现** + 六项冻结条件
- [x] ★ **近似复制污染**必须检出（跨划分同指纹）
- [x] ★ **增益靠加无限重试 ⇒ 不算系统增益**
- [x] ★ **三率联合考核**（通过/拒绝/错误放行）
- [x] ★ **零事故 ≠ 零风险**（Wilson 上界 > 0）
- [x] ★ **各领域分别过门**（不合并成一个 approve）
- [x] ★ 单方法准入**七项** + 沙箱→生产**需独立审核**
