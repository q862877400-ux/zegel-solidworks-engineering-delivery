# Data Model — **EC00 可信工具底座**：对象、状态机、单位、版本、引用、生命周期

**Feature**: `specs/302-ec00-trustworthy-tool-base/`
**日期**: 2026-10-10
**上游**: `output/ENGINEERING_P0_CONTRACTS_DRAFT.md`（五份 P0 草案之四）· `spec.md`（FR-002/003/006/007/008/009/011/013）
**对应任务**: **T008**（Quantity/单位）· **T009**（EffectObservation/ExecutionOutcome/EvidenceManifest）· **T010**（上下文/引用/uncertain）
**★ 单一权威**：★ 本文件是 EC00 数据模型的**唯一权威**；★ `contracts/` 只写**接口形状**，★ **不复制字段定义**（★ 计划 §1.3「以链接建立单一事实源」）。

---

## 一、★★★★ 四件事必须分开（★ 本特性的核心设计）

★★★ **逐字承 `plan.md` §一**：

| ★ 面 | ★ 含义 | ★ 类型 | ★ 例 |
|---|---|---|---|
| ★ **API 返回** | ★ COM 回了什么 | ★ 原始值 | ★ `True` / `None` / `(None, None, None)` |
| ★ **执行状态** | ★ 调用走完了没 | ★ `ExecutionState` | ★ `returned` / `timeout` / `uncertain` |
| ★ **实际效果** | ★ 模型**真的**变了没 | ★ `EffectStatus` | ★ `pass` / `fail` / `unknown` |
| ★ **验证等级** | ★ 我们有多少证据 | ★ `VerificationLevel` | ★ `offline` / `runtime` / `product` |

★★★ **⇒ 单 `success` 字段容纳不了**：★ `true` **可以伴随** effect `fail`；★ 异常**可以伴随**实际已修改；
★ offline `pass` **可以伴随** runtime `not_run`。

---

## 二、★★★★ `Quantity` / `NormalizedQuantity`（★ **T008** · FR-002/003）

### 2.1 ★ `Quantity`（★ 用户提交的原始量值）

| ★ 字段 | ★ 类型 | ★ 规则 |
|---|---|---|
| ★ `value` | ★ 有限数值 | ★★ **禁止 NaN / ±无穷**；★ 域约束由**参数定义**（★ 不是全局） |
| ★ `unit` | ★ 受支持单位标识 | ★ **必填**；★ **旧入口仅在明确历史契约时可补** |
| ★ `quantity_kind` | ★ 物理量枚举/受控类型 | ★★ **长度/角度/力/应力/转速等不能互换** |
| ★ `source` | ★ 来源 | ★ `supplied` / `legacy_contract_default`；★★ **不把模型猜测写成用户输入** |

### 2.2 ★★ `NormalizedQuantity`（★ 规范化结果 · **独立结构**）

| ★ 字段 | ★ 类型 | ★ 规则 |
|---|---|---|
| ★ `value` | ★ 有限数值 | ★ 规范单位下的值 |
| ★ `canonical_unit` | ★ 规范单位 | ★ 长度 → **米** · ★ 角度 → **弧度** |
| ★ `original` | ★ `Quantity` | ★ 保留原始值 |
| ★ `rule_version` | ★ 字符串 | ★ 转换规则版本 |

★★★ **关键规则（★ 逐字承 P0 CONTRACTS §2）**：
- ★★ **`NormalizedQuantity` 不能再次作为原始 `Quantity` 转换** ⇒ ★ **防重复换算**（★ FR-003）；
- ★ 示例：★ **10 mm 与 0.01 m 均对应长度 0.01 m**；★ **90 deg 对应角度 π/2 rad**；
- ★★ **不设「所有 COM 参数都是 SI」全局假设** ⇒ ★ **需先逐成员确认单位**；
- ★★★ **同一成员只允许一次转换**（★ 在**已确认的边界**做，★★ **不得在 Agent/工具/COM 各转一次**）。

### 2.3 ★★ 单位表（★ 本仓实测口径）

| ★ 量 | ★ 公开单位 | ★ 规范单位 | ★ 转换 | ★ 依据 |
|---|---|---|---|---|
| ★ 长度 | ★ 毫米（`_mm` 后缀） | ★ 米 | ★ `× 1/1000` | ★ 规则 2 · ★ `sw_part.py` 的 `_MM_TO_M` |
| ★ 角度 | ★ 度（`_deg` 后缀） | ★ 弧度 | ★ `× π/180` | ★ 规则 2 · ★ `sw_sketch_metal` 的 `math.radians` |
| ★ 温度 | ★ — | ★ — | ★★ **偏置单位，独立定义** | ★★★ **不混用乘法**（★ P0 CONTRACTS §2） |
| ★ 面积 | ★ — | ★ — | ★★ **`unknown`** | ★★ 见 `docs/unit-conflicts.md` 第 1 条（★ `GetArea` 侧面 1000 倍**未解释**） |

---

## 三、★★★★ `ToolExecutionRequest`（★ FR-006/007/009）

★ 逐字承 P0 CONTRACTS §3：

| ★ 字段 | ★ 必需性 | ★ 语义 |
|---|---|---|
| ★ `request_id` | ★ 必需 | ★ 唯一请求标识，★★ **不等于幂等键** |
| ★ `tool_name` / `tool_contract_version` | ★ 必需 | ★ 正式公开 ToolSpec 身份与版本 |
| ★ `arguments` | ★ 必需 | ★ 按 ToolSpec 定义；★★ **不把 COM 对象经网络裸传** |
| ★ `expected_context` | ★ **修改操作必需** | ★ 文档、配置、预期版本、编辑上下文 |
| ★ `object_refs` | ★ 涉及对象时必需 | ★ 持久引用/语义锚点/几何签名/所属文档 |
| ★ `verification_obligations` | ★ 按工具契约 | ★ 预期关系、尺寸、体数、状态等；★★ **Agent 不能删掉硬义务** |
| ★ `execution_policy_ref` | ★ 修改时必需 | ★ 超时、允许目录、恢复、互斥与权限的**可信配置引用** |
| ★ `approval_ref` | ★ 风险策略需要时 | ★ 外部批准记录；★★ **不能由 Agent 自己编造** |
| ★ `idempotency_key` | ★ 适用时 | ★ 绑定工具/参数/上下文与执行版本；★★ **不能跨版本重复使用** |

★★★ **两条硬规则**：
- ★ **同一 `request_id` 收到不同内容必须拒绝**，★★ **不能覆盖旧审计记录**；
- ★ **同一幂等键的重试只能返回可验证已有结果或进入核验**，★★★ **不等于允许再次执行非幂等操作**。

---

## 四、★★★★ `ContextSnapshot` 与 `ObjectReference`（★ **T010** · FR-006/007）

### 4.1 ★★ 文档上下文（★ 逐字承 P0 CONTRACTS §4.1）

| ★ 字段 | ★ 语义 |
|---|---|
| ★ `session_document_id` | ★ 会话内唯一；★★ **未保存文档也必须可区分** |
| ★ `saved_identity` | ★ 可选保存路径/保存版本；★★ **空路径不是唯一身份** |
| ★ `configuration_id` | ★ 目标配置；★★ **不能只凭当前活动配置** |
| ★ `model_revision` | ★ 可靠来源的内存/受控状态标识；★ **不可得则 `unknown`** |
| ★ `saved_artifact_hash` | ★ 可选文件字节哈希；★★ **不能代替未保存内存版本** |
| ★ `edit_state` | ★ 当前是否编辑草图/特征等；★ 与公开工具前置一致 |
| ★ `ownership` / `scope` | ★ 自有测试工件或获授权用户工件及**可操作范围** |

★★★ **`model_revision` 的关键限定**（★ 逐字）：
> ★★ **既有指纹（九类状态）不是完整 `model_revision`**：★ 它只覆盖**有限状态类**，
> ★ 且含**已知不可用桶**（`scripts/sw_fingerprint.py` 的 `KNOWN_UNAVAILABLE.display`），
> ★★★ **读不到不能证明没变**。

★★ **EC00 只接现有本地互斥与上下文边界**；★ **完整节点租约、围栏令牌和批准失效机制属于 EC04**。
★★★ **没有可靠内存指纹时采用保守策略并明确 `unknown`，不把「有字段」当「强一致已实现」**。

### 4.2 ★★ `ObjectReference`

★★ **必须能够解释引用指向什么**：★ 所属文档/配置、★ 实体类型、★ 持久引用、★ 语义锚点、★ 几何签名与容差。
★★★ **几何签名只辅助核验，不是遇到引用失效时自动挑邻近面的授权**。

★★ **解析结果（★ 封闭词表）**：

| ★ 取值 | ★ 含义 | ★ 是否允许进入修改 |
|---|---|---|
| ★ `resolved_unique` | ★ 唯一解析 | ★★ **允许** |
| ★ `not_found` | ★ 找不到 | ★ **拒绝** |
| ★ `ambiguous` | ★ 多候选 | ★ **拒绝** |
| ★ `wrong_context` | ★ 错文档/配置 | ★ **拒绝** |
| ★ `unsupported` | ★ 不支持的引用形态 | ★ **拒绝** |

★★★ **重建后的引用应重新核验，不能仅复用旧对象指针**。

---

## 五、★★★★★ 状态机（★ **T009/T010**）

### 5.1 ★★ 效果状态机（★ 逐字承 P0 PLAN §5.5）

```text
validated → context_checked → executing
  ├─ known no execution → rejected / failed
  ├─ returned → inspecting → pass / fail / unknown
  └─ timeout / ambiguous COM error → uncertain
                                  └─ inspect / recover，不能直接 retry
```

| ★ 状态 | ★ 含义 | ★ 允许的下一步 |
|---|---|---|
| ★ `validated` | ★ 请求已通过 schema/量纲/域校验 | ★ → `context_checked` |
| ★ `context_checked` | ★ 文档/配置/版本/引用/编辑态已核 | ★ → `executing` |
| ★ `executing` | ★ 已进入 COM 调用 | ★ → `returned` / `uncertain` / `rejected` |
| ★ `returned` | ★ 调用已返回 | ★ → `inspecting` |
| ★ `inspecting` | ★ 正在**回读效果** | ★ → `pass` / `fail` / `unknown` |
| ★★ `uncertain` | ★★ **超时或语义不明的 COM 错误** | ★★★ **只能 `inspect`/`recover`，不能直接 `retry`** |
| ★ `rejected` | ★ 已知**未执行** | ★ 终止 |
| ★ `failed` | ★ 已知**失败** | ★ 终止 |

★★★ **三条不可违反的规则**（★ 逐字）：
1. ★★ **「没有完成返回」不等于「没有修改」**；
2. ★ 异步护栏退出、COM 服务错误和读取失败**都可能产生不确定状态**；
3. ★ 只有**操作可证实未执行、已满足或可受控补偿**时，才能选择下一步。

### 5.2 ★★ 验证等级（★ 三级 · ★ **FR-013**）

| ★ 等级 | ★ 含义 | ★ 能否升级 |
|---|---|---|
| ★ `offline` | ★ 纯离线测试通过 | ★ 可 → `runtime`（★ **需真机证据**） |
| ★ `runtime` | ★ 真机验证通过 | ★ 可 → `product`（★ **需发布门**） |
| ★ `product` | ★ 产品发布通过 | ★ 终态 |

★★★ **硬规则**：★ **只完成静态/离线测试的工具不得升级为真机已验证**（★ FR-013 · US5）⇒
★★ **`offline` pass 不能写成 `runtime` pass**。

### 5.3 ★★ 效果状态（★ `EffectStatus` · ★ **FR-008**）

| ★ 取值 | ★ 含义 | ★ 判定依据 |
|---|---|---|
| ★ `pass` | ★ **回读证明**效果成立 | ★★ **确定性回读**（★ 不是 API 返回值） |
| ★ `fail` | ★ **回读证明**效果不成立 | ★★ 同上 |
| ★★ `unknown` | ★★ **无法可信回读** | ★★★ **不得放行**（★ FR-008 逐字：「★ 若不能可信回读则 `unknown`，不得通过」） |

---

## 六、★★★★ `EvidenceManifest`（★ **T009/T021** · FR-011/013/015）

★ 逐字承总计划 §8.1 的**验收记录最小形状**：

```json
{
  "feature_key": "EC00",
  "task_id": "T018",
  "requirement_ids": ["FR-004"],
  "verification_level": "runtime",
  "result": "unknown",
  "artifact_version": "sha256:<actual-content-hash>",
  "environment_ref": "<actual-environment-record>",
  "evidence_refs": [],
  "reason": "缺少关系生效回读，禁止放行"
}
```

★★★ **两条硬规则**（★ 逐字）：
- ★ **这是格式说明，尖括号字段不能进入真实证据**；
- ★★ **真实执行必须填真实值；未运行不生成「通过」manifest**。

| ★ 字段 | ★ 规则 |
|---|---|
| ★ `result` | ★ **封闭词表**：★ `pass` / `fail` / `unknown` / `not_run` / `expired` |
| ★ `verification_level` | ★ `offline` / `runtime` / `product` |
| ★ `artifact_version` | ★★ **`sha256:` 前缀 + 真实哈希**；★★ **未实填不生成真实证据**（★ T021 判据） |
| ★ `environment_ref` | ★ 环境记录引用（★ 未记录 ⇒ `unknown`） |
| ★ `evidence_refs` | ★ 证据文件相对路径；★ **非空才算有据** |
| ★ `reason` | ★ **失败/未知时必须写**（★ 逐字承 T021「失败日志保留错误分类、前后态和恢复建议」） |

★★★ **失效规则**：★ **模型改变后，旧的证据不能直接用于放行新模型**（★ US5 · FR-011）；
★ **`unknown`、`not_run` 和 `expired` 不变成通过**（★ T021 完成判据）。

---

## 七、★★★ 敏感信息过滤（★ **T015** · FR-015）

★★ **日志与证据不得含**（★ 封闭清单）：★ 明文凭据 · ★ token · ★ `Authorization` 头 · ★ 完整配置 · ★ 私人日志路径。
★ 只写**白名单字段**：★ `provider` / `model` / `profile` / 角色名 / 路径（★ **自有目录内**）。

---

## 八、★★★ 本文件与 `contracts/` 的分工（★ 单一事实源）

| ★ 文件 | ★ 写什么 | ★ **不写什么** |
|---|---|---|
| ★ 本文件（`data-model.md`） | ★★ **对象、字段、状态机、单位、版本、引用、生命周期** | ★ 不写接口调用序 |
| ★ `contracts/quantity.md` | ★ Quantity 的**接口形状与失败语义** | ★★ **不复制字段表**（★ 链接到本文件） |
| ★ `contracts/effects.md` | ★ 效果状态机的**接口形状** | ★★ 同上 |
| ★ `contracts/context.md` | ★ 上下文/引用的**接口形状** | ★★ 同上 |
