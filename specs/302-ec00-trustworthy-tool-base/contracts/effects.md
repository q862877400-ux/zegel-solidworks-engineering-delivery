# Contract — **效果观察与执行结果**

**Feature**: `specs/302-ec00-trustworthy-tool-base/`
**日期**: 2026-10-10
**对应任务**: **T009**（契约冻结）· **T013/T018**（实现）
**★ 状态机与字段定义在** [`data-model.md`](../data-model.md) §五 —— ★ **本文件不复制状态表**。

---

## 一、★★★ 接口形状（★ 逐字承 P0 CONTRACTS §1）

```text
Agent/宿主适配器
  submit(ToolExecutionRequest)
    → 现有公开 ToolSpec 路由
      → 校验/规范化/上下文/互斥/护栏
        → 官方确认的 COM 调用
          → 实际效果回读
            → ExecutionOutcome + EvidenceManifest
```

★★ **以上为逻辑接口，不承诺函数名或网络协议已经存在**。

## 二、★★★★ `ExecutionOutcome`（★ 三件事分开）

| ★ 字段 | ★ 类型 | ★ 规则 |
|---|---|---|
| ★ `api_return` | ★ 任意 | ★★ **原样保留** COM 返回（★ `True`/`None`/元组）—— ★ **不解释** |
| ★ `execution_state` | ★ 封闭词表 | ★ 见 `data-model.md` §5.1 |
| ★ `effect_status` | ★ 封闭词表 | ★ `pass`/`fail`/`unknown` —— ★★ **由回读决定，不由 `api_return` 决定** |
| ★ `verification_level` | ★ 封闭词表 | ★ `offline`/`runtime`/`product` |
| ★ `obligations` | ★ 列表 | ★ 逐条：★ 义务 + 期望 + 实际 + 判定 |
| ★ `recovery_hint` | ★ 字符串 | ★ `uncertain`/`fail` 时**必须写** |

★★★ **FR-008 的核心**：★ **工具结果区分 effect `pass`/`fail`/`unknown`，不直接由 API 返回值决定**。

## 三、★★★ `EffectObservation`（★ 回读的形状）

| ★ 字段 | ★ 语义 |
|---|---|
| ★ `before` | ★ 前态（★ 关系数 / 几何量 / 特征数 / 体数 / 配置） |
| ★ `after` | ★ 后态（★ **同一量具**） |
| ★ `measure` | ★ 量具名（★ 如 `ISketchSegment::GetRelationsCount`） |
| ★ `tolerance` | ★ 容差（★ **`abs(error) ≤ abs_tol + rel_tol × scale`**） |
| ★ `tolerance_source` | ★★★ **外部参考值** —— ★★ **不得取自被测实现** |
| ★ `readback_ok` | ★ 回读是否成功 |

★★★ **两条硬规则**：
1. ★★ **`tolerance_source` 不得取自被测实现**（★ 判据 = ★ 独立 oracle）；
2. ★★ **`readback_ok == False` ⇒ `effect_status` 必须是 `unknown`**，★★ **不得 `pass`**。

## 四、★★★ `uncertain` 的恢复契约（★ 逐字承 P0 PLAN §5.6）

| ★ 规则 | ★ 内容 |
|---|---|
| ★ **R1** | ★★ **不对所有动作提供通用 rollback**；★ COM **不是数据库事务** |
| ★ **R2** | ★ 使用批准的**自有检查点、前向补偿或停止人工处理** |
| ★ **R3** | ★★ **保存重开只操作自有样例**；★★ **用户未保存文档不在自动关闭/重启范围** |
| ★ **R4** | ★ 特征创建超时：★ **先检查是否存在预期效果及多余实体**；★ 无法判断则**停止** |
| ★ **R5** | ★★ **旧入口兼容时不改变恢复语义**，★★ **更不能把 `unknown` 压回 `true`** |

## 五、★★ 判据（★ 对应 T013/T018）

| ★ 判据 | ★ 文件 | ★ 要点 |
|---|---|---|
| ★ **假成功** | `tests/test_ec00_effect_false_success_negative.py` | ★★ **API 回 `true` 但关系数不变 ⇒ `fail` 或 `unknown`，绝不 `pass`** |
| ★ 不可回读 | ★ 同上 | ★★ **回读异常 ⇒ `unknown`** |
| ★ 旧证据错版本 | ★ 同上 | ★★ **模型变了 ⇒ 旧证据 `expired`** |
| ★ 映射正确 | `tests/test_ec00_effect_readback_mapping.py` | ★ 三态映射**无 `true` 直通** |
| ★ 契约 | `tests/test_ec00_effect_observation_contract.py` | ★ 字段齐 + 容差来源**外部** |
