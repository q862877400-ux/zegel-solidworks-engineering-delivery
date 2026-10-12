# Feature Specification: 阶段 3 · 中断后能续，不重复打孔、不误认完成

**Feature Branch**: `318-stage3-crash-recovery`

**Created**: 2026-10-12

**Status**: Draft

**Input**: 外部方案 `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` **阶段 3**（L423–451）
+ 业主指令「全自动持续推进所有的阶段，每轮结束都提交一下」

---

## §0 这一份规格要解决什么

**外部方案阶段 3 的目标**（逐字）：

> **目标**：同一板件任务可跨进程和 SW 重启恢复，完成记录与真实文件一致。
> **前置／接口**：完整提交清单、检查点、版本锁、稳定引用与失效闭包；
> 单写者所有权与 `UNKNOWN_EFFECT` 状态。

---

## §1 ★ 起点实测（**不猜，已核**）

| # | 事实 | 实测 |
|---|---|---|
| 1 | `scripts/engineering/jobs.py`（479 行）**已有** `FenceToken` / `Lease` / `NodeLease` / `VersionBinding` / `ArtifactRecord` / `EvidenceChain` / `IndependentVerifier` / `RecoveryPlan` | ✅ |
| 2 | `scripts/engineering/nodes.py`（285 行）**已有** `SessionLeaseRegistry` / `AccessPolicy` / `CapabilityPackage` | ✅ |
| 3 | **已有 4 个测试**（`test_ec04_jobs_and_evidence.py` 306 行 · `test_ec04_fault_injection.py` 80 行 · `test_ec05_part_loop.py` 239 行 · `test_ec10_install_and_nodes.py` 257 行） | ✅ |
| 4 | **`JobState` 已有** 9 档（含 `UNCERTAIN` + `NEVER_RETRY_FROM`） | ✅ |
| 5 | **`VersionBinding.matches` 三版本全等**（contract/plan/model） | ✅ |
| 6 | **`NodeLease.acquire` 拒绝未过期的第二个持有者** + 令牌递增围栏 | ✅ |
| 7 | ★★ **5 个封闭码全仓没有**：`COMMITTED` · `STALE` · `REVISION_CONFLICT` · `UNKNOWN_EFFECT` · `BLOCKED_VERIFICATION` | ✅ **缺口** |
| 8 | ★★ **没有「三类崩溃窗口」的注入与恢复编排** —— 现有 `InjectionKind` 是 `WORKER_EXIT` / `APPROVAL_EXPIRED` / `MODEL_EXTERNALLY_MODIFIED`，**与验收 S3-A 要求的三处不同** | ✅ **缺口** |
| 9 | ★★ **没有失效闭包** —— `VersionBinding.invalidated_by` 只报「哪几个版本变了」，**没有「变了之后哪些节点要重新验证」** | ✅ **缺口** |
| 10 | ★★ **没有 `UNKNOWN_EFFECT` 状态** —— `JobState.UNCERTAIN` 语义相近但**不是**它 | ✅ **缺口** |

**⇒ 阶段 3 的真实工作量 = 补 4 个缺口（#7 #8 #9 #10）+ 把既有资产接起来。**

---

## §2 四件新增契约（逐条落到文件）

| # | 契约 | 落到哪 | 判据 |
|---|---|---|---|
| **E1** | **提交清单 + 检查点** | `scripts/engineering/recovery.py` | 三类崩溃窗口注入后**可恢复**；**无无证据 `COMMITTED`** |
| **E2** | **失效闭包** | `recovery.py` 的 `invalidation_closure()` | 版本变 ⇒ **受影响节点标 `STALE` 并重新进验证**；独立节点**不被无故清空** |
| **E3** | **过期证据/审批不可复用** | `recovery.py` 的 `resume_verdict()` | 旧 revision ⇒ `REVISION_CONFLICT`（★ **不接受该提交**） |
| **E4** | **`UNKNOWN_EFFECT` 状态** | `jobs.py` 扩展 | 效应不明 ⇒ `UNKNOWN_EFFECT`（★ **不重试、不标完成**） |

---

## §3 Requirements

### Functional Requirements

- **FR-001**: 系统 MUST 在**意图落盘后、调用前**留检查点（★ 崩溃窗口①）
- **FR-002**: 系统 MUST 在**操作已生效但结果未记账**时能恢复（★ 崩溃窗口② —— 用**回读**判，不用返回值）
- **FR-003**: 系统 MUST 在**CAD 已保存但提交清单未发布**时能恢复（★ 崩溃窗口③）
- **FR-004**: **任何未提交的方法 MUST NOT 被误认完成** —— `COMMITTED` 必须有证据
- **FR-005**: **恢复后的发布产物 MUST NOT 含重复操作**（★ 不重复打孔）
- **FR-006**: 版本变化时 MUST 计算**失效闭包**（受影响节点标 `STALE`）
- **FR-007**: **未变化的独立节点 MUST NOT 被无故清空**（★ 防「保守到失去能力」）
- **FR-008**: 提交旧计划 revision 或旧问题回答 MUST 回 `REVISION_CONFLICT` 且**不接受**
- **FR-009**: 效应不明时 MUST 标 `UNKNOWN_EFFECT`，**不重试、不标完成**
- **FR-010**: 系统 MUST 保证**单写者**（第二个写者被拒）
- **FR-011**: 旧尝试 MUST 保留（★ 不删用户数据）
- **FR-012**: 最终清单 MUST NOT 引用**不完整文件**

### Key Entities

- **Checkpoint**：`stage` · `intent_at` · `artifact` · `revision` · `evidence`
- **CommitManifest**：`entries`（每项带 `stage` + `sha256` + `evidence`）· `revision` · `complete`
- **InvalidationClosure**：`changed`（变了哪几个版本）· `stale_nodes` · `untouched_nodes`
- **ResumeVerdict**：`ok` · `code`（`REVISION_CONFLICT` / `STALE` / `UNKNOWN_EFFECT`）
- **CrashWindow**：`BEFORE_CALL`（意图落盘后调用前）· `AFTER_EFFECT`（生效未记账）· `AFTER_SAVE`（保存未发布）

---

## §4 Success Criteria

- **SC-001**: 三类崩溃窗口 × 3 次 = **9/9 恢复**
- **SC-002**: 恢复结果与无故障参考在**几何 / 孔数 / 参数 / 依赖 / 交付内容**上**等价**
- **SC-003**: **无无证据的 `COMMITTED`**
- **SC-004**: **无并发第二写者**
- **SC-005**: 旧尝试**保留**，最终清单**不引用不完整文件**
- **SC-006**: 文件/接口/规则摘要变化 ⇒ 相关节点标 **`STALE`** 且**重新进验证**
- **SC-007**: 提交旧 revision ⇒ **`REVISION_CONFLICT`** 且不接受
- **SC-008**: **未变化的独立节点不被无故清空**
- **SC-009**: 效应不明 ⇒ **`UNKNOWN_EFFECT`**（不重试、不标完成）

---

## §5 反向验证（★ 三条突变必须被发现）

| # | 突变 | 期望 |
|---|---|---|
| **P1** | 把「**工具返回成功**」直接当作**提交完成** | 提交不变量测试必须**失败** |
| **P2** | **取消重放前的检查点分支隔离** | 副作用重复的夹具必须**失败** |
| **P3** | **移除某个依赖摘要比较** | 该类突变必须被回归测试**发现** |

---

## §6 明确不做

- **不做**全局事务（★ COM 无事务 —— `RecoveryPlan.HAS_GLOBAL_TRANSACTION = False` 是**已定的**）
- **不做**删除用户文件（★ 只能**前向补偿**）
- **不做**阶段 4~7（各自独立规格）
- **不重写** `jobs.py` / `nodes.py`（★ 扩展，不推倒）

---

## §7 交付物清单

| # | 文件 | 内容 |
|---|---|---|
| 1 | `specs/318-stage3-crash-recovery/spec.md` | 本文件 |
| 2 | `specs/318-stage3-crash-recovery/data-model.md` | 数据结构 |
| 3 | `scripts/engineering/recovery.py` | **E1 提交清单+检查点 · E2 失效闭包 · E3 恢复判定** |
| 4 | `scripts/engineering/jobs.py` | 扩展：`UNKNOWN_EFFECT`（E4） |
| 5 | `tests/test_stage3_recovery.py` | E1~E4 契约 + 反向验证 P1/P2/P3 |
| 6 | `tools/run_stage3_recovery.py` | 真机/离线验收入口（9 次注入） |
| 7 | `specs/318-stage3-crash-recovery/acceptance.md` | 验收记录 |
