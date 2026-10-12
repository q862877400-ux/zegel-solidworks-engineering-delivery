# 验收记录：阶段 3 · 中断后能续，不重复打孔、不误认完成（318）

**规格**：`specs/318-stage3-crash-recovery/spec.md`
**验收日期**：2026-10-12
**状态**：**已交付**

---

## §1 判据逐条（对照 spec §4）

| 判据 | 目标 | 实测 | 结果 |
|---|---|---|---|
| **SC-001** | 三类窗口 × 3 次 = **9/9 恢复** | **9/9** | ✅ |
| **SC-002** | 与无故障参考**等价**（五项） | 几何/孔数/参数/依赖/交付 **全等** | ✅ |
| **SC-003** | **无无证据的 `COMMITTED`** | `manifest_complete=True` · `incomplete_refs=[]` | ✅ |
| **SC-004** | **无并发第二写者** | 二写者**被拒**（9/9） | ✅ |
| **SC-005** | 旧尝试保留 · 清单不引用不完整文件 | `duplicate_stages=[]` | ✅ |
| **SC-006** | 版本变 ⇒ 节点标 `STALE` | 文件/接口/规则三种变化都标脏 | ✅ |
| **SC-007** | 提交旧 revision ⇒ `REVISION_CONFLICT` | 旧计划 + 旧问答**都拒** | ✅ |
| **SC-008** | 独立节点**不被无故清空** | 6/6 用例的独立节点都保留 | ✅ |
| **SC-009** | 效应不明 ⇒ `UNKNOWN_EFFECT` | ✅（且**压过** `REVISION_CONFLICT`） | ✅ |

### §2 S3-A 的实测数据（★ 三类窗口 × 3 次）

| 窗口 | # | 重放 | 跳过 | 重复 | 清单完整 | 二写者被拒 | pass |
|---|---|---|---|---|---|---|---|
| `before_call` | 1/2/3 | **8** | 0 | 无 | ✅ | ✅ | ✅ |
| `after_effect` | 1/2/3 | **4** | **4** | **无** | ✅ | ✅ | ✅ |
| `after_save` | 1/2/3 | **4** | **4** | **无** | ✅ | ✅ | ✅ |

**★★ 关键一行**：`after_effect` 窗口 **重放 4 · 跳过 4 · 无重复** ——
★ 那 4 个**已经生效但没记账**的步骤被**回读判出来并跳过** ⇒ **不重复打孔** ✓

**★ 三个窗口的语义差别**（★ 这是本阶段的核心）：

| 窗口 | 崩在哪 | 恢复时 | 为什么 |
|---|---|---|---|
| `before_call` | 意图落盘、**COM 没调** | **全部重放 8 步** | ★ 还没生效 ⇒ 重放**安全** |
| `after_effect` | **生效了、没记账** | **回读判 4 个已生效 ⇒ 跳过** | ★★ 重放会**重复打孔** |
| `after_save` | **记了账、没发布** | **清单里 4 个 ⇒ 跳过** | ★ 已在清单 ⇒ 跳过 |

### §3 S3-B 的实测数据（★ 过期不可复用）

| 用例 | 结果 | 独立节点保留 |
|---|---|---|
| 文件内容变 | `['holes', 'plate']` 标脏 | ✅ |
| 接口版本变 | `['holes']` 标脏 | ✅ |
| 规则摘要变 | `['calc']` 标脏 | ✅ |
| 提交旧计划 revision | **`REVISION_CONFLICT`** | ✅ |
| 提交旧问题回答 | **`REVISION_CONFLICT`** | ✅ |
| 效应不明 | **`UNKNOWN_EFFECT`** | ✅ |

**证据**：`output/stage3/recovery.json`

---

## §4 反向验证（对照 spec §5）

| # | 突变 | 测试 | 结果 |
|---|---|---|---|
| **P1** | 把「工具返回成功」当**提交完成** | `test_p1_tool_success_is_not_a_commit` | ✅ 真提交器**拒绝**、突变体放行 |
| **P2** | **取消重放前的检查点分支隔离** | `test_p2_no_checkpoint_isolation_causes_duplicates` | ✅ 突变体**产生重复** |
| **P3** | **移除某个依赖摘要比较** | `test_p3_removing_a_dependency_hides_invalidation` | ✅ 两者**不同** ⇒ 能被发现 |

**★ 另加一条纪律测试**：`test_p3_each_change_affects_exactly_one_mechanism`
—— ★ **只改一个变量检验一个失效机制**（S3-B ④ 逐字）。

---

## §5 ★ 起点实测（**不猜，已核**）

| # | 事实 | 实测 |
|---|---|---|
| 1 | `jobs.py` **已有** `FenceToken`/`Lease`/`NodeLease`/`VersionBinding`/`ArtifactRecord`/`EvidenceChain`/`IndependentVerifier`/`RecoveryPlan` | ✅ |
| 2 | `nodes.py` **已有** `SessionLeaseRegistry`/`AccessPolicy`/`CapabilityPackage` | ✅ |
| 3 | **已有 4 个测试** | ✅ |
| 4 | `JobState` 已有 9 档（含 `UNCERTAIN` + `NEVER_RETRY_FROM`） | ✅ |
| 5 | `VersionBinding.matches` **三版本全等** | ✅ |
| 6 | `NodeLease.acquire` **拒绝未过期的第二持有者** + 令牌递增围栏 | ✅ |
| 7 | ★★ **5 个封闭码全仓没有** | ✅ **缺口**（已补） |
| 8 | ★★ **没有三类崩溃窗口的注入与恢复编排** | ✅ **缺口**（已补） |
| 9 | ★★ **没有失效闭包** | ✅ **缺口**（已补） |
| 10 | ★★ **没有 `UNKNOWN_EFFECT`** | ✅ **缺口**（已补） |

**⇒ 阶段 3 的真实工作量 = 补 4 个缺口 + 把既有资产接起来。**
★ **既有的 8 个类没有重写**（★ 规格 §6 明确「不推倒」）。

---

## §6 ★ 本轮抓到的 2 个真问题

| # | 问题 | 后果 | 处置 |
|---|---|---|---|
| **1** | **`resume_from_checkpoints` 把 `applied` 误判成「已提交」** —— 第一版用 `set(manifest.stages)`（★ 只要在 `entries` 里就算） | ★★ 而 `entries` 里**正是有没进清单的 `applied`**（★ 那正是窗口②）⇒ 它被**跳过而不回读** ⇒ **窗口② 的判据失效** | ✅ 判据改成 **`state == committed`**（★ 不是「在 entries 里」）；★ 是 `test_window2_without_readback_refuses_to_replay` 抓到的 |
| **2** | `JobState.TRANSITIONS` 的**完备性**没有测试 | ★ 新增一档忘了加迁移 ⇒ 运行期才炸 | ✅ 加 `test_transitions_cover_all_states`（★ 逐档查表） |

**★ 问题 1 的价值**：它说明「**在集合里**」与「**是那个状态**」是**两件事** ——
★ 而「窗口②」的全部意义就在于**区分这两件事**。

---

## §7 `UNKNOWN_EFFECT` 与 `UNCERTAIN` 的分工（★ 新增契约）

| 状态 | 含义 | 能去 | 为什么 |
|---|---|---|---|
| `UNCERTAIN` | **调用**结果不明 | `validating`（回读）/ `blocked` / `failed` | ★ 知道该回读什么 ⇒ 给回读机会 |
| `UNKNOWN_EFFECT` | ★★ **这个工具到底写没写**都不知道 | **只有** `blocked` / `failed` | ★★ **连该回读什么都不知道** ⇒ 进 `validating` 会**假装有回读判据** |

**★ 依据**：外部方案阶段 3 逐字要求「单写者所有权与 **`UNKNOWN_EFFECT` 状态**」。

---

## §8 交付物

| # | 文件 | 内容 |
|---|---|---|
| 1 | `specs/318-stage3-crash-recovery/spec.md` | 规格 |
| 2 | `specs/318-stage3-crash-recovery/data-model.md` | 数据结构 + 不变式 K1~K4 |
| 3 | `scripts/engineering/recovery.py` | **E1 检查点+提交清单 · E2 失效闭包 · E3 恢复判定** |
| 4 | `scripts/engineering/jobs.py` | 扩展：**E4 `UNKNOWN_EFFECT`** |
| 5 | `tests/test_stage3_recovery.py` | **29 条**（含 P1/P2/P3） |
| 6 | `tools/run_stage3_recovery.py` | 验收入口（9 次注入 + S3-B 六项） |
| 7 | `specs/318-stage3-crash-recovery/acceptance.md` | 本文件 |

---

## §9 全量验收

| 项 | 结果 |
|---|---|
| 阶段 3 契约测试 | ✅ **29 passed** |
| S3-A 9 次注入 | ✅ **9/9** |
| S3-B 六项 | ✅ **6/6** |
| 语法门禁 | ✅ **1525 文件 · 0 失败** |
| `release_check` | ✅ exit=0 |

---

## §10 结论

**规格 318 的 7 项交付物全部产出；9 条判据全部通过；3 条反向验证全部生效。**

**★ 最硬的一条**：`after_effect` 窗口 **重放 4 · 跳过 4 · 无重复** ——
★ 已生效但没记账的步骤被**回读判出来并跳过** ⇒ **不重复打孔** ✓

**★ 最诚实的一条**：既有的 8 个类**没有重写**，★ 本阶段只**补了 4 个缺口**
并把它们接起来 —— ★ 那 4 个缺口（5 个封闭码 / 三类窗口编排 / 失效闭包 /
`UNKNOWN_EFFECT`）**在没有本阶段之前是查不到的**。
