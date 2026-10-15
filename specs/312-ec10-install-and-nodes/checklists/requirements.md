# Checklist — 312-ec10-install-and-nodes

**Feature**: `specs/312-ec10-install-and-nodes/`

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

- [x] ★ 诊断失败项**必须给修法**（`remedy`）
- [x] ★ 诊断**只读**（`read_only = True`）
- [x] ★ **宿主级互斥**（DSH vs WorkBuddy）
- [x] ★ 能力包**整包扫凭据**（含 JSON 形态）
- [x] ★ 跨项目读 **拒**（且列出它只能读什么）
- [x] ★ **没记已知良好版本 ⇒ 不许升级**
- [x] ★ 回滚**不动用户全局环境**
