# Feature Specification: Q4 + Q6 · 任务域与受控多标签，分面检索与暴露面

**Feature Branch**: `323-task-domains-and-faceted-retrieval`

**Created**: 2026-10-12

**Status**: Draft

**Input**: 外部方案 `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` **Q4**（L36–57）
与 **Q6**（L96–112）；业主指令「要」

---

## §0 这一份规格要解决什么

**Q4 的目标**（逐字）：

> 确定八个一级任务域：需求与计算、草图与基准、实体成形与修改、孔系与连接接口、
> 装配与机构、工程图与标注、分析与检验、文档与交付。
> 每个工具一个主域，另有受控多标签：`object_kind / operation / result_kind /
> precondition / effect / backend / availability`。
> **实现模块仅保留为定位信息，不作为检索分类。**

**Q6 的目标**（逐字）：

> 候选方法和工具定义的单次上限定为 **4096 token**……
> 1. 按任务类型、文档状态、后端可达性和能力范围**过滤**。
> 2. 用**本地词法检索、中文 n-gram、受控中英文同义词**召回；本期不引入 GPU 嵌入模型。
> 3. 返回**少量方法卡**……
> 4. 选中方法后，**只加载该方法**及当前步骤所需的完整参数契约。
> 5. 内部依赖和工具序列由编译器展开，**不把全部工具 schema 塞给 LLM**。
> 必须同时改 **MCP 暴露面**：自主模式的 `tools/list` 只返回规划入口与必要查询工具。

**★★ 为什么这两问最要紧**（★ 实测）：上一轮证明「agent 够不到判断层」——
★ MCP 工具面 **0/521**、`SKILL.md` **0/21**。★ 根因就在这两问没做：
**没有域 ⇒ 没有检索层 ⇒ agent 只能靠工具名字符串找工具。**

---

## §1 ★ 起点实测（**不猜，已核**）

| # | 事实 | 实测 |
|---|---|---|
| 1 | `capabilities.yaml` 存在（576,076 字节） | ✅ |
| 2 | `tools/union-sources.json` · `docs/effect-declarations.json` · `docs/gate-classification.json` 都在 | ✅ |
| 3 | ★★ **没有任何元数据目录**（`metadata/` / `catalog/` / `protocols/` / `schemas/` **全部不存在**） | ✅ **缺口** |
| 4 | ★★ `ToolSpec` **没有域字段**（21 个字段里 `domain`/`main_domain`/`tags`/`labels` 全无） | ✅ **缺口** |
| 5 | ★★ `capabilities.yaml` 里 `domain`/`task_group`/`tags` 出现 **0 次** | ✅ **缺口** |
| 6 | ★★ **没有中文 n-gram**（全仓 `n_gram`/`ngram` **0 命中**） | ✅ **缺口** |
| 7 | ★★ **没有分面检索**（`facet` 的命中全是别处的假阳性） | ✅ **缺口** |
| 8 | 有 4 个**索引类**脚本（`sw_jlcfa_index` / `sw_jlcfa_search` / `sw_misumi` / `sw_toolbox_index`） | ✅ 可参考写法 |
| 9 | `registry.py` 已有 `ToolDescriptor`（★ Q12 要的「注册时合成」已有一半） | ✅ |

**⇒ 本规格的工作量 = 补 4 个缺口（#3~#7）+ 复用 `ToolDescriptor`。**

---

## §2 交付物（逐条落到文件）

| # | 契约 | 落到哪 | 判据 |
|---|---|---|---|
| **N1** | **8 个一级任务域 + 每工具一个主域** | `metadata/domains.yaml` + `scripts/engineering/catalog.py` | **521/521 个工具都有主域**；★ 域取自**8 个封闭值** |
| **N2** | **受控多标签 7 个** | `metadata/facets.yaml` + `catalog.py` | 每个标签**取值受控**（不是自由文本） |
| **N3** | **实现模块仅作定位信息** | `catalog.py` 的 `ToolCard` | ★ 卡片里 `module` 是**定位字段**，**不参与检索匹配** |
| **N4** | **分面检索** | `catalog.py` 的 `retrieve()` | 按**任务类型 / 文档状态 / 后端可达性 / 能力范围**过滤 |
| **N5** | **本地词法 + 中文 n-gram + 同义词** | `catalog.py` 的 `ngrams()` / `SYNONYMS` | ★ 中文能召回（★ 不是只按英文名匹配） |
| **N6** | **4096 token 候选上限** | `catalog.py` 的 `retrieve()` | ★ 与阶段 4 的 `CANDIDATE_TOKEN_BUDGET` **同口径** |
| **N7** | **recall / chain_hit 指标** | `catalog.py` 的 `evaluate_recall()` | 平均 recall ≥95% · 完整链命中 ≥90% · ≥90% 任务 ≤3 域 |
| **N8** | **阈值冻结** | `metadata/thresholds.json` | ★ **首次评测前**写死；★ 有 `frozen_at` 与摘要 |
| **N9** | **MCP 暴露面：自主/兼容两模式** | `catalog.py` 的 `exposure()` | 自主模式只返回**规划入口 + 必要查询**；★ 隐藏工具**仍在分发处检查权限** |
| **N10** | **选中后只加载该方法的完整契约** | `catalog.py` 的 `load_contract()` | ★ 单方法契约 ≤4096 token；★ **不塞全部 schema** |

---

## §3 Requirements

### Functional Requirements

- **FR-001**: 系统 MUST 把**每个**工具分到**一个**主域（★ 8 个封闭值之一）
- **FR-002**: 每个工具 MUST 有 7 个受控多标签（★ 取值受控）
- **FR-003**: **实现模块 MUST 只作定位信息**（★ 不作检索分类）
- **FR-004**: 检索 MUST 支持**分面过滤**（任务类型 / 文档状态 / 后端可达性 / 能力范围）
- **FR-005**: 检索 MUST 用**本地词法 + 中文 n-gram + 受控同义词**（★ 不引 GPU 嵌入）
- **FR-006**: 候选 MUST **≤4096 token**
- **FR-007**: 选中后 MUST **只加载该方法的完整契约**（★ 不塞全部 schema）
- **FR-008**: 系统 MUST 能算 **recall / chain_hit / 域跨度**
- **FR-009**: 阈值 MUST **在首次评测前冻结**（★ 不能看过结果后下调）
- **FR-010**: MCP MUST 支持**自主模式**（只暴露规划入口 + 必要查询）与**兼容模式**
- **FR-011**: **隐藏工具 MUST 仍在分发处检查权限**（★ 不能靠隐藏列表防旁路）
- **FR-012**: 结构标签 MUST **从注册信息生成**；语义标签 MUST **只自动给候选**，
  试点工具 MUST **人工确认**（★ 语料由**业主**编，★ 我不代编）
- **FR-013**: 无标签的新工具 MUST 能进**管理目录**，但 MUST **不自动进自主执行集合**

### Key Entities

- **TaskDomain**：`id` · `name` · `order`（★ 8 个封闭值）
- **FacetValue**：`facet` · `value` · `label`
- **ToolCard**：`name` · `domain` · `facets` · `module`（★ 仅定位）· `title` · `tokens`
- **RetrievalQuery**：`text` · `domain` · `doc_state` · `backend` · `capability` · `budget`
- **RetrievalResult**：`cards` · `tokens` · `truncated` · `facets_used`
- **Thresholds**：`avg_recall` · `chain_hit` · `domain_span` · `token_budget` · `frozen_at`

---

## §4 Success Criteria

- **SC-001**: **521/521 个工具都有主域**，且域是 8 个封闭值之一
- **SC-002**: 每个工具有 7 个受控多标签
- **SC-003**: **`module` 不出现在检索匹配里**（★ 结构性保证）
- **SC-004**: 分面过滤**四类都生效**
- **SC-005**: **中文查询能召回**（★ n-gram 生效）
- **SC-006**: 候选 **≤4096 token**
- **SC-007**: 单方法契约 **≤4096 token**
- **SC-008**: recall / chain_hit / 域跨度 **三个指标都算得出**
- **SC-009**: 阈值文件带 **`frozen_at`**
- **SC-010**: 自主模式暴露面 **≤ 兼容模式的 10%**
- **SC-011**: 隐藏工具在分发处**仍被权限检查**（★ 负例证明）

---

## §5 反向验证

| # | 突变 | 期望 |
|---|---|---|
| **V1** | **把 `module` 当检索字段** | 检索结果必须**变化** ⇒ ★ 证明它现在**不参与** |
| **V2** | **移除 n-gram，只留精确词** | 中文查询**召回率必须下降** |
| **V3** | **去掉分面过滤** | 返回**超预算**或**跨域污染** ⇒ 被检出 |
| **V4** | **隐藏工具但不检查权限** | ★ 负例必须**失败**（★ 证明检查真的在） |
| **V5** | **给一个工具删掉主域** | `521/521` 断言必须**失败** |
| **V6** | **阈值下调**（看过结果之后） | ★ `frozen_at` 检查必须**发现** |

---

## §6 明确不做

- **不引 GPU 嵌入模型**（★ Q6 逐字「本期不引入」）
- **不代编 60 条语料**（★ Q4 逐字「先由**业主**编写」；★ 我只建**指标与评测机**）
- **不散改 75 个模块**（★ Q12：元数据**外挂单一源**）
- **不重写** `registry.py` / `planner.py`（★ 扩展，不推倒）

---

## §7 交付物清单

| # | 文件 | 内容 |
|---|---|---|
| 1 | `specs/323-task-domains-and-faceted-retrieval/spec.md` | 本文件 |
| 2 | `metadata/domains.yaml` | **8 个一级任务域** |
| 3 | `metadata/facets.yaml` | **7 个受控多标签的取值表** |
| 4 | `metadata/thresholds.json` | **冻结阈值** |
| 5 | `scripts/engineering/catalog.py` | **N1~N10** |
| 6 | `tests/test_s323_catalog.py` | N1~N10 契约 + V1~V6 |
| 7 | `tools/run_s323_catalog.py` | 验收入口 |
| 8 | `specs/323-task-domains-and-faceted-retrieval/acceptance.md` | 验收记录 |
