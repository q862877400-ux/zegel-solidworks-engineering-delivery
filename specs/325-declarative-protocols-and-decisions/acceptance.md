# 验收记录：Q1 + Q5 · 声明式协议与决策追责（325）

**规格**：`specs/325-declarative-protocols-and-decisions/spec.md`
**对应外部方案**：`output/PROJECT_STATUS_REVIEW_CONTINUATION.md` **Q1**（L10–34）· **Q5**（L59–94）
**验收日期**：2026-10-12
**状态**：**已交付**

---

## §1 判据逐条（对照 spec §4）

| 判据 | 目标 | 实测 | 结果 |
|---|---|---|---|
| **SC-001** | 四类协议**都在**，五要素齐 | ✅ `requirement` / `scheme_gate` / `layout` / `failure_transition` | ✅ |
| **SC-002** | `check_ref` **全部解析成功** | ✅ **15 个 · 未解析 0** | ✅ |
| **SC-003** | **`eval`/`exec`/任意 Python 零命中** | ✅ X4 塞进去**被检出** | ✅ |
| **SC-004** | **8 项必设检查全部实施** | ✅ 8 项 · 全过 | ✅ |
| **SC-005** | 改一处 ⇒ **三视图都变** | ✅ 4 份 · 三样齐 | ✅ |
| **SC-006** | 每个决策有 **`decision_id` + 五要素** | ✅ `dec-d666df89bc17` | ✅ |
| **SC-007** | ★★ **`Proposal` 不能直达 `Approved`** | ✅ `illegal-transition` | ✅ |
| **SC-008** | ★★ **LLM 自升被拒** | ✅ `not-authorized` | ✅ |
| **SC-009** | 缺必填 ⇒ `WAITING_INPUT`，★ **无"最坏工况"顶替** | ✅ 给了最坏工况**照样** `WAITING_INPUT` | ✅ |
| **SC-010** | 两次同错 ⇒ 诊断，★ **无"根因"字段** | ✅ `root_cause` **不在** `to_dict()` 里 | ✅ |
| **SC-011** | ★ **新 `check_ref` 无实现 ⇒ 拒** | ✅ `brand_new@1` 未解析 | ✅ |

### §2 R1~R10 实测

| # | 判据 | 结果 |
|---|---|---|
| **R1** | 四类协议齐 | ✅ 4 份 |
| **R2** | 每份五要素齐 | ✅ |
| **R3** | `check_ref` 全解析 | ✅ **15 个 · 未解析 0** |
| **R4** | 8 项必设检查 | ✅ 8 项全过（★ 第 9 项在测试层） |
| **R5** | 改一处 ⇒ 三视图重生成 | ✅ 4 份 · 文档/提示/目录三样齐 |
| **R6** | `decision_id` + 五要素 | ✅ |
| **R7** | 三态且 LLM 不能自升 | ✅ 跳级拒 · LLM 自升拒 · 代码过 · 人过 |
| **R8** | 缺需求先问 · 最坏工况不顶替 | ✅ |
| **R9** | 同错两次 ⇒ 诊断（不判根因） | ✅ |
| **R10** | 只改 YAML 不得获得新能力 | ✅ |

**证据**：`output/s325/protocols.json`

---

## §3 ★★ 三态闸门的设计（★ 本规格最硬的一条）

**Q1 L22 逐字**：

> LLM 输出都是 `Proposal`，**不能自行晋升为 `Validated` 或 `Approved`**。

**★ 判据是结构性的**（★ 不是靠"记得别让它升"）：

```
STEP_AUTHORITY = {
    (Proposal,  Validated): (code,),      #: ★ 只有代码
    (Validated, Approved):  (human,),     #: ★ 只有人
}
```

**★ 实测**：

| 谁 | 想做什么 | 结果 |
|---|---|---|
| LLM | `Proposal → Approved`（跳级） | ❌ `illegal-transition` |
| LLM | `Proposal → Validated`（自评 PASS） | ❌ `not-authorized` |
| **代码** | `Proposal → Validated`（带裁决 PASS） | ✅ |
| **人** | `Validated → Approved` | ✅ |

**★ 另加一条**：进 `Validated` **必须带代码裁决结果**，且**裁决必须是 PASS** ——
★ 即「代码只能裁决**已经形式化的性质**」（★ Q1 L22 后半句）。

---

## §4 ★★ `check_ref` 的两条判据（★ Q5 的核心）

**Q5 L88–90 逐字**：

> `check_ref` **必须解析到已登记的代码**，禁止任意 Python、`eval` 或
> LLM 生成脚本进入生产执行。
> 增加真正的新判定逻辑：**增加实现与测试，再登记引用**，
> **不能假装只改 YAML 就能获得新能力**。

**★ 判据**：

```
① 名字必须在 CHECK_REGISTRY 里（★ 已登记）
② ★ 且那个 (module, function) 真的 import 得到
```

**★★ ② 是关键** —— ★ 只登记不实现 = 「假装只改 YAML 就能获得新能力」。
★ 实测：`ghost_check@1` 登记了但函数不存在 ⇒ **拒**（★ 测试 `test_registered_but_missing_function_is_rejected`）。

**★ 15 个 `check_ref` 全部指向真代码**（★ 复用既有模块，不新造）：

| 协议 | check_ref | 后端 |
|---|---|---|
| requirement | `non_empty_requirement@1` 等 4 个 | `design_ir.parse_requirement` |
| scheme_gate | `hard_requirements_complete@1` 等 | `rule_verdicts.evaluate` · `linkage.solve_four_bar` |
| layout | `assembly_accessibility@1` 等 | `assembly.build_case` · `linkage.continuity_verdict` |
| failure_transition | `same_error_twice_triggers_diagnosis@1` | `decisions.SameErrorTrigger` |
| 8 项必设检查 | `schema@1` · `ref_resolution@1` … | `protocols.check_schema` · `recovery.invalidation_closure` … |

---

## §5 ★ 起点实测（**不猜，已核**）

| # | 事实 | 实测 |
|---|---|---|
| 1 | ★★ **没有 `decision_id`** | ✅ **缺口** |
| 2 | ★★ **没有三态** | ✅ **缺口** |
| 3 | ★★ **没有四类协议** | ✅ **缺口** |
| 4 | ★★ **没有「同错误两次停下」** | ✅ **缺口** |
| 5 | ★★ **没有「可见理由」与「受影响节点」** | ✅ **缺口** |
| 6 | ★★ **没有任何协议目录** | ✅ **缺口** |
| 7 | ★★ **没有 `check_ref` 解析器** | ✅ **缺口** |
| 8 | ✅ `WAITING_INPUT` **已有**（阶段 4） | ✅ 可复用 |

---

## §6 ★ 本轮抓到的 1 个真问题

| # | 问题 | 后果 | 处置 |
|---|---|---|---|
| **1** | **`validate_protocol` 只扫 `to_dict()`** | ★★ 而 `to_dict()` **不含 `extra`**（协议里**多出来的键**）⇒ ★ **把 `eval(...)` 塞进 `extra` 检不出来** ✗ —— ★ 而"塞进多出来的键"正是**绕过检查最自然的做法** | ✅ 改成**扫整份原始字典**（`to_dict()` ∪ `extra`） |

**★ 问题 1 的形状**：★ **检查器的覆盖面 ≠ 被检查对象的覆盖面** ——
★ 我的检查器只看它"认得"的字段，★ 而**攻击面是全部字段**。

---

## §7 ★ 反向验证（对照 spec §5）

| # | 突变 | 实测 | 结果 |
|---|---|---|---|
| **X1** | **`Proposal` 直接晋升 `Approved`** | `illegal-transition` | ✅ |
| **X2** | **LLM 自评就能 `Validated`** | `not-authorized` | ✅ |
| **X3** | **`check_ref` 指向不存在的函数** | ★ 模块里没有那个函数 | ✅ |
| **X4** | **协议里塞 `eval`** | 检出 **1 处** | ✅ |
| **X5** | **只改 YAML 加新检查** | 未解析 `['brand_new@1']` | ✅ |
| **X6** | **缺必填却继续** | `WAITING_INPUT` | ✅ |
| **X7** | **两次同错却继续重试** | `DIAGNOSIS_REQUIRED` | ✅ |
| **X8** | **把「最坏工况」当默认值** | `WAITING_INPUT` · 禁用项 `['worst_case_load']` | ✅ |

---

## §8 ★ 明确不做（★ 如实说明）

| 事项 | 状态 | 原因 |
|---|---|---|
| **一次转译整个知识库** | ❌ **不做** | ★ Q1 L34 逐字：「**不一次转译整个知识库**。完整覆盖按新增用例逐步推进」 |
| **记录隐藏思维链** | ❌ **不做** | ★ Q1 L24 逐字：「**无需记录模型隐藏思维链**」⇒ ★ **收进来就拒** |
| **LLM 真调用** | ❌ **不做** | ★ 业主已拍板；★ 只做**三态与晋升闸门** |
| **改 `design_ir`/`rule_verdicts`/`registry`** | ❌ **不做** | ★ 扩展，不推倒（★ `check_ref` 直接**指向**它们） |

**★ 最关键的一条**：**`check_ref` 全部指向既有模块** ——
★ 本规格**没有新造判定逻辑**，★ 而是把**已有的判定**登记成可被协议引用的名字。
★ 那正是 Q5 要的：★ **「增加实现与测试，再登记引用」**。

---

## §9 交付物

| # | 文件 | 内容 |
|---|---|---|
| 1 | `specs/325-declarative-protocols-and-decisions/spec.md` | 规格 |
| 2 | `metadata/protocols/requirement.yaml` | 协议①（含 `forbidden_defaults`） |
| 3 | `metadata/protocols/scheme_gate.yaml` | 协议②（含 `proposal_only`） |
| 4 | `metadata/protocols/layout.yaml` | 协议③（★ **逐字承 Q5 样例**） |
| 5 | `metadata/protocols/failure_transition.yaml` | 协议④（含 `empirical_ratios_allowed: false`） |
| 6 | `scripts/engineering/protocols.py` | **R1~R5 · R8 · R10** |
| 7 | `scripts/engineering/decisions.py` | **R6/R7/R9** |
| 8 | `tests/test_s325_protocols.py` | **43 条**（含 X1~X8） |
| 9 | `tools/run_s325_protocols.py` | 验收入口 |
| 10 | `specs/325-declarative-protocols-and-decisions/acceptance.md` | 本文件 |

---

## §10 全量验收

| 项 | 结果 |
|---|---|
| S325 契约测试 | ✅ **43 passed** |
| R1~R10 | ✅ **全过** |
| X1~X8 | ✅ **全过** |
| 语法门禁 | ✅ **1548 文件 · 0 失败** |

---

## §11 结论

**规格 325 的 10 项交付物全部产出；11 条判据全部通过；8 条反向验证全部生效。**

**★ 最硬的一条**：**LLM 一步都升不了** ——
★ `Proposal → Validated` 只有**代码**能升（★ 且要带 PASS 裁决），
★ `Validated → Approved` 只有**人**能升。★ 判据是**结构性**的。

**★ 最诚实的一条**：**`check_ref` 全部指向既有模块** ——
★ 本规格**没有新造判定逻辑**，★ 而是把**已有的判定**登记成可引用的名字。
★ 那正是 Q5 要的「**增加实现与测试，再登记引用**」。
