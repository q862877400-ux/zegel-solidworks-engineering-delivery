# Checklist — 304-ec02-rules-and-standards

**Feature**: `specs/304-ec02-rules-and-standards/`

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

- [x] ★ `Verdict` 五态，**只有 `PASS` 放行**
- [x] ★ `Effectiveness`：**只有 `EFFECTIVE` 算 `BINDING`**
- [x] ★ `ObligationKind.HARD` = 仅 `MANDATORY`+`CONTRACTUAL`
- [x] ★ 仲裁**按优先级**；**平局 ⇒ `UNKNOWN`，绝不投票**
- [x] ★ RSS 法**不声明分布 ⇒ `UNKNOWN`**
- [x] ★ 未知类别 ⇒ `NEEDS_CLARIFICATION`，**绝不**「无标准适用」
