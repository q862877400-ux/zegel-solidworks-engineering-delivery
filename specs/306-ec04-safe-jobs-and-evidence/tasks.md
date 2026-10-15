# Tasks & Acceptance — **EC04 安全作业、恢复、版本与证据链**

**Feature**: `specs/306-ec04-safe-jobs-and-evidence/`
**日期**: 2026-10-10
**上游**: `output/ENGINEERING_CONSTRUCTION_PLAN.md` **§5 EC04**（★ T01–T08 逐字）
**对应**: `spec.md`（★ 8 FR · 8 V）· `baseline.md`（★ G0）

---

## 二、★★★★★ 任务逐条（★ T01–T08）

| ★ 任务 | ★ 状态 | ★ 依据 |
|---|---|---|
| **EC04-T01** Job 状态与节点租约 | ✅ **完成** | ★ `JobState`（★ **9 态** + ★ **封闭迁移表** + ★ **`NEVER_RETRY_FROM`**） |
| **EC04-T02** 互斥 / 续期 / 围栏 | ✅ **完成** | ★ `NodeLease`（★ **只能一个持有** · ★ 续期须对令牌）· `FenceToken`（★ **单调递增**）· ★ `may_modify` 三条 |
| **EC04-T03** 版本比较交换 | ✅ **完成** | ★ `VersionBinding`（★ **contract/plan/model 三版本** · ★ `invalidated_by()` **具名**） |
| **EC04-T04** 幂等键 + 效果回读 | ✅ **完成** | ★ 由 ★ **`uncertain` 不能回 `running`** 保证（★ **结构性** · ★ 不靠纪律） |
| **EC04-T05** 检查点 + 前向补偿 | ✅ **完成** | ★ `RecoveryPlan`（★ **`HAS_GLOBAL_TRANSACTION = False`** · ★ **`deletes_user_files = False`**） |
| **EC04-T06** 独立验收器 | ✅ **完成** | ★ `IndependentVerifier`（★ **自评拒** · ★ **只读** · ★ **`design_advice_only`**） |
| **EC04-T07** 证据哈希/相对路径/脱敏 | ✅ **完成** | ★ `EvidenceChain`（★ **链式防篡改**）· `ArtifactRecord`（★ **相对路径**）· `filter_sensitive`（★ **替换不删键**） |
| **EC04-T08** 四类故障注入 | ✅ **完成**（★ 三类离线 · ★ 一类如实标「需 COM」） | ★ inject_worker_exit · inject_approval_expired · inject_model_externally_modified · ★ injection_coverage() **如实**标第四类属 EC05 · ★ 判据 5 例 |

---
