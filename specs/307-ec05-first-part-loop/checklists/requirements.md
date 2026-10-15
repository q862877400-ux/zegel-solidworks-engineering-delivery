# Checklist — 307-ec05-first-part-loop

**Feature**: `specs/307-ec05-first-part-loop/`

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

- [x] ★ 五项回读；**缺读数 ⇒ `unknown`**
- [x] ★ 独立参考值**手写**（不取自被测实现）
- [x] ★ **扰动集在 spec 里冻结**
- [x] ★ 三组扰动**类型必须互异**
- [x] ★ **失败点不许删**
- [x] ★ 有意保留的自由度**必须标注理由**
