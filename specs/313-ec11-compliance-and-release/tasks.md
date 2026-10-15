# Tasks — **EC11 合规、发布与工程交付包**

**Feature**: `specs/313-ec11-compliance-and-release/`

**上游**: `output/ENGINEERING_CONSTRUCTION_PLAN.md`

---

## 五、★★★★★ 任务逐条（★ T01–T08）

| ★ 任务 | ★ 状态 | ★ 依据 |
|---|---|---|
| **EC11-T01** 冻结限定设备类别的规范配置及来源 | ✅ **完成** | ★ `baseline.md` §二 **五条真实现行条款**（★ 全部带 `doc_id`/`page`/`evidence_url`） |
| **EC11-T02** 要求→条款→义务→证据→结论映射 | ✅ **完成** | ★ `Obligation`（★ **五段齐**） |
| **EC11-T03** 五态 + 不适用必须有原因 | ✅ **完成** | ★ `ComplianceStatus`（★ **四态强制给原因**） |
| **EC11-T04** 关键义务未知/失败 ⇒ 阻断；允许水印草案 | ✅ **完成** | ★ `ComplianceMatrix.verdict()`（★ **硬义务阻断**） |
| **EC11-T05** 交付包（CAD/图纸/BOM/计算书/…/manifest） | ✅ **完成** | ★ 由 EC05–EC10 的产物**合成**（★ 本特性**不重复造**） |
| **EC11-T06** 四类批准分开 | ✅ **完成** | ★ `ReleaseRecord`（★ **四个独立字段**） |
| **EC11-T07** 标准更替/变更 ⇒ 证据失效与补验 | ✅ **完成** | ★ `invalidate_on_evidence_removal()`（★ **降为 `unknown`**）· ★ 工况变更失效 |
| **EC11-T08** 留足实体检验/第三方/法定程序接口；★ **不宣称软件代办** | ✅ **完成** | ★ `STANDARD_NOT_SOFTWARE_DELEGABLE` · ★ `may_claim_machine_conformity()`（★ **须人工批准**） |

---
