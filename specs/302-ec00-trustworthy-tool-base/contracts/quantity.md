# Contract — **Quantity 与单位边界**

**Feature**: `specs/302-ec00-trustworthy-tool-base/`
**日期**: 2026-10-10
**对应任务**: **T008**
**★ 字段定义在** [`data-model.md`](../data-model.md) §二 —— ★ **本文件不复制字段表**（★ 计划 §1.3「单一事实源」）。

---

## 一、★★★ 接口形状

```text
Quantity(value, unit, quantity_kind, source)
  → normalize() → NormalizedQuantity | Rejection
```

| ★ 步骤 | ★ 输入 | ★ 输出 | ★ 拒绝条件 |
|---|---|---|---|
| ★ ① 量纲校验 | ★ `Quantity` | ★ 通过 / `Rejection` | ★ `quantity_kind` **与字段期望不符** |
| ★ ② 有限性校验 | ★ `value` | ★ 通过 / `Rejection` | ★ **NaN / ±无穷** |
| ★ ③ 域校验 | ★ `value` | ★ 通过 / `Rejection` | ★ **超出参数定义的域**（★ **不是全局域**） |
| ★ ④ 单位校验 | ★ `unit` | ★ 通过 / `Rejection` | ★ **未知单位** |
| ★ ⑤ 规范化 | ★ `Quantity` | ★ `NormalizedQuantity` | ★ — |

## 二、★★★ 拒绝语义（★ 封闭词表）

| ★ 码 | ★ 含义 | ★ 何时 |
|---|---|---|
| ★ `reject-kind-mismatch` | ★ 量纲不符 | ★ **只接受长度的字段传入角度** |
| ★ `reject-nonfinite` | ★ 非有限值 | ★ NaN / ±无穷 |
| ★ `reject-out-of-domain` | ★ 域外 | ★ 超出**该参数**声明的域 |
| ★ `reject-unknown-unit` | ★ 未知单位 | ★ 单位不在受支持表内 |
| ★ `reject-double-conversion` | ★ **重复换算** | ★ `NormalizedQuantity` **再次**进入规范化 |

★★★ **两条硬规则**：
1. ★★ **拒绝必须发生在 COM 之前**（★ FR-003 · ★ 判据 = **修改调用计数为 0**）；
2. ★★ **`NormalizedQuantity` 再次规范化 ⇒ 拒绝**（★ **不是静默再除 1000**）。

## 三、★★★ 兼容与迁移（★ 承 `plan.md` §十 D-001）

| ★ 场景 | ★ 处置 |
|---|---|
| ★ 旧调用**省略单位** | ★★ **仅在该工具确有已登记历史契约时**走兼容路径 |
| ★ 旧调用**无历史契约** | ★★★ **拒绝**，★★ **不得套全局 mm 默认** |
| ★ 旧 `float` 入参 | ★★ **不批量换成 `Quantity` 对象**（★ D-001 逐字） |

## 四、★★ 判据（★ 对应 T012/T016）

| ★ 判据 | ★ 文件 | ★ 要点 |
|---|---|---|
| ★ 单位等价 | `tests/test_ec00_unit_boundary_negative.py` | ★ **10 mm 与 0.01 m 归一到同一结果** |
| ★ 量纲错误 | ★ 同上 | ★ **调用 COM 前拒绝** |
| ★ 非有限 | ★ 同上 | ★ NaN/无穷拒绝 |
| ★ 重复换算 | ★ 同上 | ★ **`NormalizedQuantity` 再规范化 ⇒ 拒绝** |
| ★ 单一边界 | `tests/test_ec00_unit_normalization_entry.py` | ★ **修改调用计数 = 1**（★ 不是 2 或 3） |
