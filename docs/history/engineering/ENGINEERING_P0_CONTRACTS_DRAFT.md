# EC00 Contracts 草案——接口、数据模型与失败语义

- 日期：2026-10-08；状态：DRAFT／待正式schema评审。
- [Spec](ENGINEERING_P0_SPEC_DRAFT.md)｜[Plan](ENGINEERING_P0_PLAN_DRAFT.md)｜[Tasks](ENGINEERING_P0_TASKS_DRAFT.md)｜[Acceptance](ENGINEERING_P0_ACCEPTANCE_DRAFT.md)
- 本文描述工程执行包装契约，不伪造SolidWorks COM成员签名，不表示新接口已经实现。
- 正式立项后拆入`contracts/`与`data-model.md`；唯一权威schema与本仓现有结构对齐，不能重复定义。

## 1. 公开接口与内核边界

```text
Agent/宿主适配器
  submit(ToolExecutionRequest)
    → 现有公开ToolSpec路由
      → 校验/规范化/上下文/互斥/护栏
        → 官方确认的COM调用
          → 实际效果回读
            → ExecutionOutcome + EvidenceManifest
```

以上为逻辑接口，不承诺函数名或网络协议已经存在。DSH/WorkBuddy只在宿主适配层不同；工程语义与门禁共享。现有ToolSpec注入约定仍由本仓注册器定义，包装层不能另猜需要model、sw_app还是study。

## 2. Quantity：量值契约

| 字段 | 类型 | 规则 |
|---|---|---|
| value | 有限数值 | 禁止NaN/无穷；域约束由参数定义 |
| unit | 受支持单位标识 | 必填；旧入口仅在明确历史契约时可补 |
| quantity_kind | 物理量枚举/受控类型 | 长度、角度、力、应力、转速等不能互换 |
| source | 来源 | supplied／legacy_contract_default，不把模型猜测写成用户输入 |

规范化值独立为NormalizedQuantity，至少含规范单位、原始值、转换规则版本。它不能再次作为原始Quantity转换；是否采用类型标记还是专用对象由正式实现决定。

示例：10 mm与0.01 m均对应长度0.01 m；90 deg对应角度π/2 rad。不同API边界可能不同，**不设"所有COM参数都是SI"全局假设**。需要先逐成员确认单位；**同一成员只允许一次转换**（在已确认的边界做，不得在 Agent／工具／COM 各转一次）。

## 3. ToolExecutionRequest

| 字段 | 必需性 | 语义 |
|---|---|---|
| request_id | 必需 | 唯一请求标识，不等于幂等键 |
| tool_name / tool_contract_version | 必需 | 正式公开ToolSpec身份与版本 |
| arguments | 必需 | 按ToolSpec定义，不把COM对象经网络裸传 |
| expected_context | 修改操作必需 | 文档、配置、预期版本、编辑上下文 |
| object_refs | 涉及对象时必需 | 持久引用/语义锚点/几何签名/所属文档 |
| verification_obligations | 按工具契约 | 预期关系、尺寸、体数、状态等；Agent不能删掉硬义务 |
| execution_policy_ref | 修改时必需 | 超时、允许目录、恢复、互斥与权限的可信配置引用 |
| approval_ref | 风险策略需要时 | 外部批准记录，不能由Agent自己编造 |
| idempotency_key | 适用时 | 绑定工具/参数/上下文与执行版本，不能跨版本重复使用 |

同一request_id收到不同内容必须拒绝，不能覆盖旧审计记录。同一幂等键的重试只能返回可验证已有结果或进入核验，不等于允许再次执行非幂等操作。

## 4. ContextSnapshot与对象引用

### 4.1 文档上下文

- session_document_id：会话内唯一，未保存文档也必须可区分。
- saved_identity：可选保存路径/保存版本；空路径不是唯一身份。
- configuration_id：目标配置，不能只凭当前活动配置。
- model_revision：可靠来源的内存/受控状态标识；不可得则unknown。**既有指纹（九类状态）不是完整 `model_revision`**：它只覆盖有限状态类，且含已知不可用桶（`scripts/sw_fingerprint.py` 的 `KNOWN_UNAVAILABLE.display`），读不到不能证明没变。
- saved_artifact_hash：可选文件字节哈希，不能代替未保存内存版本。
- edit_state：当前是否编辑草图/特征等；与公开工具前置一致。
- ownership/scope：自有测试工件或获授权用户工件及可操作范围。

EC00只接现有本地互斥与上下文边界；完整节点租约、围栏令牌和批准失效机制属于EC04。没有可靠内存指纹时采用保守策略并明确unknown，不把“有字段”当“强一致已实现”。

### 4.2 ObjectReference

必须能够解释引用指向什么：所属文档/配置、实体类型、持久引用、语义锚点、几何签名与容差。几何签名只辅助核验，不是遇到引用失效时自动挑邻近面的授权。

解析结果：resolved_unique／not_found／ambiguous／wrong_context／unsupported。只有resolved_unique允许进入修改。重建后的引用应重新核验，不能仅复用旧对象指针。

## 5. 前后置与效果义务

| 义务类型 | 示例 | 放行依据 |
|---|---|---|
| 输入 | 长度、合法实体数量、支持关系 | 类型/量纲/参数域/注册契约校验 |
| 上下文 | 文档、配置、编辑态、对象 | 独立上下文观察与唯一解析 |
| 几何效果 | 孔径/坐标/轮廓/体数 | 实际模型回读，按冻结容差比较 |
| 关系效果 | 重合/相等/相切 | 关系身份/对象加几何语义回读 |
| 持久效果 | 保存重开后关系/尺寸仍正确 | 重开最终工件并核验指定配置 |
| 状态效果 | 不产生多余文档/未批准关闭 | 前后文档状态与工件权属核验 |

硬义务由工具/方法契约提供，不允许调用者提交一个空数组来绕过。前态已满足的操作可no_op，但必须证明满足且结果绑定当前版本。

数值容差：`abs(error) <= abs_tol + rel_tol * scale`。scale、abs_tol、rel_tol及单位/来源随义务冻结；不得自动扩大到通过。特征存在、关系存在、几何满足、自由度符合意图可能是不同义务，不能只验其中一项。

## 6. EffectObservation

| 字段 | 要求 |
|---|---|
| obligation_id / type | 唯一对应预期义务 |
| expected / observed / unit | 保留真实值与单位，读不到写null加原因，不编造 |
| tolerance_ref | 数值比较需要，版本冻结 |
| result | pass／fail／unknown |
| observer_version / source | 回读方式、算法和来源 |
| context_revision | 观察时版本，不允许混合版本合并为一次通过 |
| reason / evidence_refs | 失败/unknown具名；pass也要有可追溯依据 |

单个硬义务unknown则整体效果不能pass；出现硬义务fail则整体fail，同时保留其他unknown。范围外义务不默认为pass，应在需求层标not_applicable并说明。

## 7. ExecutionOutcome：别再用一个success

### 7.1 分开四个轴

| 轴 | 值与语义 |
|---|---|
| execution_state | rejected、not_started、running、returned、uncertain、recovered、failed |
| effect_status | pass、fail、unknown；未执行时通常unknown并写原因 |
| verification_level | 沿用仓库等级与记录口径，不新造“已验证”定义 |
| stage_result | offline/runtime/product各自not_run/pass/fail/blocked |

另含request_id、tool_version、前后上下文、API原始返回摘要、观察列表、错误、恢复动作和证据引用。

API返回true但关系没生效：execution_state=returned，effect_status=fail。

COM超时而模型可能已改变：execution_state=uncertain，effect_status=unknown。首先核验，不重放。

离线桩全绿但无COM环境：offline=pass，runtime=not_run，product=not_run。不能升级能力真机等级。

**承载方式（不改造旧表面）**：`ExecutionOutcome`／`EffectObservation` 是新增工程结构，经**新工程适配入口的版本化扩展**或**旁路证据**承载；旧公开调用仍经 `run_locked` 返回字符串，其形状不变（PLAN §10 决策 3）。`unknown`/`uncertain` **不通过**：单个硬义务 `unknown` ⇒ 整体效果不能 `pass`；`execution_state=uncertain` ⇒ 先核验不重放。

### 7.2 恢复允许动作

inspect／stop／request_decision／resume_from_checkpoint／compensate_owned_artifact／retry_if_proven_safe。

动作由工具风险策略和观察决定，不能由模型自由选择。删除/关闭/重启必须遵守工件权属和现有护栏；不默认恢复所有文档，不把kill调用子进程等同SW操作撤销。

## 8. 错误契约

| 代码族 | 含义 | 默认处理 |
|---|---|---|
| INPUT_INVALID | 类型/数量/有限值错误 | 修改前拒绝 |
| UNIT_INVALID / UNIT_UNKNOWN | 量纲错误/缺失且无历史依据 | 修改前拒绝，澄清单位 |
| CONTEXT_MISMATCH | 文档/配置/版本/编辑态不匹配 | 停止或经批准重新计划 |
| REFERENCE_INVALID / AMBIGUOUS | 对象不唯一或错误上下文 | 不选择近邻，不继续 |
| PRECONDITION_UNSATISFIED | 工具前置不满足 | 拒绝，不能偷偷改计划 |
| EFFECT_MISMATCH | 已读到实际效果不满足 | fail并保留证据 |
| OBSERVATION_UNAVAILABLE | 无可靠回读 | unknown，补验 |
| EXECUTION_UNCERTAIN | 超时/异常可能已产生效果 | 先inspect，不自动retry |
| EXECUTION_BUSY | 单会话被占用 | 不启动第二修改者 |
| POLICY_DENIED | 权限/风险/写入面不允许 | 拒绝，不询问模型绕过 |
| EVIDENCE_STALE | 证据版本与目标不匹配 | 禁止放行，重新验证 |
| ENVIRONMENT_UNAVAILABLE | COM/SW/许可/插件未就绪 | runtime阻塞，离线独立记录 |

错误代码为逻辑草案，正式实现应对齐既有错误模块。原始HRESULT可保留，但恢复策略不能只按数值盲重试；官方符号名及语义以实际文档为准。**按 HRESULT 数值盲重试属既有旧风险，本特性只登记、不宣称消除。**

## 9. EvidenceManifest

最小项：feature/task/FR/SC、request与工具版本、执行环境、前后模型/配置、观察者/容差/规则版本、工件相对路径及实际哈希、执行时间、错误与未知、验证阶段、验收责任者。

- 相对路径必须约束到批准工件根目录，拒绝目录穿越和跨项目引用。
- 所有真实哈希/时间/工件身份由执行过程取得，不用文档示例值。
- 哈希保障完整性，不自动证明观察真实或算法正确。
- 保留敏感设计的访问控制；日志/包不带明文密钥。
- 模型/配置/单位契约/验证规则变化后按影响范围使旧证据过期。
- 生成者不能自行签发安全关键审签；软件阶段通过与工程审签不同。

## 10. 向后兼容与迁移表

正式施工逐公开工具填写：

| 字段 | 必填内容 |
|---|---|
| tool_name | 实际ToolSpec名，不写内部函数名冒充 |
| old_contract_version | 原公开参数/默认单位/返回语义 |
| new_contract_version | 新输入/结果/硬门禁 |
| mapping | 无损映射、显式默认依据、拒绝情形 |
| regression_case | 新旧对照与门禁负例 |
| activation/retirement | 受控启用与旧入口退出条件 |
| known_limitations | 仍未验证/不支持/已知失败 |

迁移原则：不默默改单位，不压缩unknown为true，不移除验证义务；**仅限已纳入本特性迁移表的代表工具**，不允许回退旧入口绕过该工程路径的权限/上下文门——**未纳入迁移范围的旧工具不适用本条，不得泛化为"所有旧入口"**。不能无损表达时返回明确不兼容错误。

与旧公开表面的关系（对齐 PLAN §10）：旧标量参数、`required/default`、自动追加 `response_format`（默认 JSON）与 Markdown 字符串返回**保持**；公开调用经 `run_locked` 返回字符串**保持**。本契约的 `Quantity`／`ExecutionOutcome` 属新增工程结构，走**新工程适配入口的版本化扩展**或**旁路证据**承载，不直接改变旧工具返回形状。旧 `precheck` 异常／`unchecked`／`SW_PRECHECK=off` 的放行行为保持，新工程硬义务由**独立工程入口**失败关闭。

## 11. 契约验收清单

- [ ] 所有纳入范围的工具有公开身份、量纲、域、注入、来源、风险与效果义务。
- [ ] 原始量值与规范化量值不会重复进入转换。
- [ ] 未保存文档/配置/内存版本与文件哈希分开。
- [ ] 关系存在与几何满足不混为一项。
- [ ] true无效果、回读失败、部分执行、超时均有负例。
- [ ] 错对象/歧义/忙状态在修改前阻断。
- [ ] 证据过期和阶段等级由可信代码检查。
- [ ] 迁移代表工具的**工程调用**不可回退旧入口绕门；**旧公开表面未声明全局硬化**（precheck 异常／`unchecked`／`SW_PRECHECK=off` 的放行行为保持，见 PLAN §10 决策 4）。
- [ ] 未运行/未知/域外不冒充通过。

本清单全部保持未完成；正式schema、实现及证据未产出。
