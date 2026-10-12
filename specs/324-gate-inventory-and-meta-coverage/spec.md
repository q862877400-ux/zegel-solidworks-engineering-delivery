# Feature Specification: Q16 · 门禁清单四类 + 责任人 + 元门禁覆盖 tools/

**Feature Branch**: `324-gate-inventory-and-meta-coverage`

**Created**: 2026-10-12

**Status**: Draft

**Input**: 外部方案 `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` **Q16**（L329–347）；
业主指令「要」

---

## §0 这一份规格要解决什么

**Q16 的目标**（逐字）：

> ### 未接线门禁
> 为**全部检查文件**建立清单，类别只能是：
> `release_static / release_hardware / diagnostic / retired`。
> **每个文件必须有类别、理由、环境与责任人。**
>
> 必需门禁**接进 release**；真机门禁**单独编排并明确 `NOT_RUN`**，
> **不能跳过仍报全部通过**；诊断工具保留但**明确不是门禁**；
> 失效检查**不删除，先标明替代关系**。
> **元门禁同时覆盖 `scripts/`、`tools/`，并核对「应执行集合」与「实际执行结果」，
> 不只检查文件被发现。**

---

## §1 ★ 起点实测（**不猜，已核**）

| # | 事实 | 实测 |
|---|---|---|
| 1 | `docs/gate-classification.json` 存在，**50 条** | ✅ |
| 2 | ★★ 类别只有 **`{'hard': 47, 'diagnostic': 3}`** | ✅ **缺三类** |
| 3 | ★★ 字段并集只有 **`['gate', 'kind', 'reason', 'runner']`** | ✅ **缺 `环境` 与 `责任人`** |
| 4 | ★★ Q16 要的四类 = `release_static / release_hardware / diagnostic / retired` | ✅ **只有 1 个对得上**（`diagnostic`） |
| 5 | ★★ **「责任人」字段 0/50 条有** | ✅ **缺口** |
| 6 | ★★ 元门禁 `check_gate_wiring.py`（343 行）提到 `"scripts"` **3 次**、`"tools"` **0 次** | ✅ **缺口** |
| 7 | 元门禁**已有五层**：接线 / 分类 / `skipped` 合法性 / 汇总完整性 | ✅ **可复用** |
| 8 | `hard` 与 `release_static` 是**同一件事的两种叫法** | ⚠ **需要映射** |

**⇒ 本规格的工作量 = ① 把 `kind` 扩到四类 ② 补 `环境`+`责任人` ③ 元门禁覆盖 `tools/`。**

---

## §2 ★★ 关键设计决策：`hard` 与 `release_static` 的关系

**Q16 只给了四个类别**：`release_static / release_hardware / diagnostic / retired`。
**而本仓现在用的是 `hard` / `diagnostic`。**

| 问题 | 处置 |
|---|---|
| `hard` 是不是 `release_static`？ | ★ **是** —— `hard` 门禁都是**静态**检查（语法/单位/接线/约定），★ 不需要真机 |
| 那 `release_hardware` 呢？ | ★ **本仓现在一条都没有** —— ★ 真机门禁（要 SolidWorks）**全走 `tools/sw_guard.py`**，★ **没接进 `release_check`** |
| 怎么改才不破坏既有 46 道门禁？ | ★★ **不改语义，只改名字 + 加映射** —— `hard` ⇒ **别名** `release_static` |

**★★ 判据**：`kind` 的**枚举扩到四个**，而**既有的 47 条 `hard` 全部映射到 `release_static`**
（★ 一个都不丢）—— ★ 并**如实报** `release_hardware` 与 `retired` 现在是 **0 条**。

---

## §3 交付物

| # | 契约 | 落到哪 | 判据 |
|---|---|---|---|
| **P1** | **四类枚举** | `docs/gate-classification.json` | ★ `kind` ∈ 四类之一；★ `hard` ⇒ `release_static` |
| **P2** | **每文件有类别+理由+环境+责任人** | 同上 | ★ **四项都非空**（★ 缺一即失败） |
| **P3** | **必需门禁接进 release** | 元门禁第 1 层（既有） | ★ 已接线 |
| **P4** | **真机门禁单独编排 · 明确 `NOT_RUN`** | `metadata/gate-inventory.json` | ★ 有 `NOT_RUN` 字段；★ **不能跳过仍报全过** |
| **P5** | **诊断工具明确不是门禁** | 分类表的 `diagnostic` | ★ 它们**不进** release 的 fail 集 |
| **P6** | **失效检查不删除 · 标明替代关系** | 分类表的 `retired` | ★ `replaced_by` 字段 |
| **P7** | **元门禁覆盖 `scripts/` + `tools/`** | `check_gate_wiring.py` | ★ **两边都扫** |
| **P8** | **核对「应执行集合」与「实际执行结果」** | 元门禁新层 | ★ **不只检查文件被发现** |
| **P9** | **清点 `tools/` 里的检查文件** | `metadata/gate-inventory.json` | ★ 每个都有一类 |

---

## §4 Requirements

- **FR-001**: `kind` MUST 取 `release_static` / `release_hardware` / `diagnostic` / `retired` 之一
- **FR-002**: 每条 MUST 有**类别 / 理由 / 环境 / 责任人**四者**非空**
- **FR-003**: `hard` MUST **映射到** `release_static`（★ 不丢语义）
- **FR-004**: 真机门禁 MUST **单独编排**并明确 `NOT_RUN`
- **FR-005**: **跳过 ≠ 通过** —— `NOT_RUN` 的必须**如实报**
- **FR-006**: 诊断工具 MUST **保留**但**明确不是门禁**
- **FR-007**: `retired` MUST 带 **`replaced_by`**（★ 不删除）
- **FR-008**: 元门禁 MUST **同时扫 `scripts/` 与 `tools/`**
- **FR-009**: 元门禁 MUST 核对**「应执行集合」**与**「实际执行结果」**
- **FR-010**: 系统 MUST **如实报**哪些类别现在是 **0 条**（★ 不假装四类都满）

### Key Entities

- **GateEntry**：`gate` · `runner` · `kind` · `reason` · `environment` · `owner` · `replaced_by`
- **GateInventory**：`scripts`（静态）· `tools`（含真机）· `not_run`（★ 明确列出）· `counts`
- **KindCounts**：四类各几条（★ **0 条也要报**）

---

## §5 Success Criteria

- **SC-001**: **50 条全部** `kind` ∈ 四类
- **SC-002**: **50 条全部**有类别+理由+环境+责任人（★ 四项非空）
- **SC-003**: 47 条 `hard` **全部映射到** `release_static`（★ 一条不丢）
- **SC-004**: 真机门禁有 **`NOT_RUN`** 标记，★ **不报成全过**
- **SC-005**: `diagnostic` **不进** release 的 fail 集
- **SC-006**: `retired` 带 `replaced_by`
- **SC-007**: 元门禁**扫到 `tools/`**（★ 有非零结果）
- **SC-008**: 元门禁核对**应执行 vs 实际**
- **SC-009**: 四类计数**如实报**（★ 0 条也报）

---

## §6 反向验证

| # | 突变 | 期望 |
|---|---|---|
| **W1** | **给一条门禁删掉责任人** | 校验必须**失败** |
| **W2** | **把 `kind` 写成第五种** | 校验必须**失败** |
| **W3** | **把真机门禁标成 `release_static`** | 必须被**检出**（★ 它需要真机） |
| **W4** | **让元门禁只扫 `scripts/`** | `tools/` 的检查文件必须**被漏报**（★ 证明现在扫到了） |
| **W5** | **把 `NOT_RUN` 说成 `pass`** | 必须**被检出** |
| **W6** | **删掉 `retired` 的 `replaced_by`** | 必须**被检出** |

---

## §7 明确不做

- **不删任何检查文件**（★ Q16 逐字「失效检查不删除」）
- **不改既有 46 道门禁的语义**（★ 只改名 + 加映射）
- **不假装 `release_hardware` / `retired` 有内容**（★ 如实报 0 条）

---

## §8 交付物清单

| # | 文件 | 内容 |
|---|---|---|
| 1 | `specs/324-gate-inventory-and-meta-coverage/spec.md` | 本文件 |
| 2 | `docs/gate-classification.json` | **扩到四类 + 补环境/责任人** |
| 3 | `metadata/gate-inventory.json` | **清点 + `NOT_RUN`** |
| 4 | `scripts/check_gate_wiring.py` | **扩到 `tools/` + 应执行 vs 实际** |
| 5 | `scripts/check_gate_inventory.py` | **P1/P2/P6 的判据** |
| 6 | `tests/test_s324_gate_inventory.py` | P1~P9 契约 + W1~W6 |
| 7 | `tools/run_s324_gates.py` | 验收入口 |
| 8 | `specs/324-gate-inventory-and-meta-coverage/acceptance.md` | 验收记录 |
