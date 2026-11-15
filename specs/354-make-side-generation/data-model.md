# Data Model — 造环节

**Date**: 2026-11-06 | **Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

所有长度单位 **毫米**；单位转换只在 `FeaturePlan.to_meters()` 一处发生。

---

## 实体关系

```
GearRequest ──derive()──> Derivation{ rows[], specs, uncovered }
                                │
                                └──plan_spur_gear()──> FeaturePlan
                                                          │
                                                          ├──execute()──> (model, evidence)
                                                          │                     │
                                                          └──verify()───────────┘
                                                                  │
                                                          Verification
```

---

## 1. GearRequest（需求对象）

| 字段 | 类型 | 必填 | 校验 | 含义 |
|---|---|---|---|---|
| `ratio` | float | ✅ | > 1.0 | 减速几倍 |
| `center_mm` | float | ✅ | > 0 | 两轴中心距 |
| `bm_ratio` | float | | 3–20，默认 10 | 齿宽系数 |
| `pressure_angle_deg` | float | | 默认 20.0 | 压力角 |
| `pin_z1` | int \| None | | > 0 | 工程师锁定的齿数 |
| `pin_module` | float \| None | | > 0 | 工程师锁定的模数 |
| `z_min_policy` | str | | `"kb"` / `"strict"` | 根切下限口径 |

**已有**：`proto/gear_method.py`。

---

## 2. Row（参数行）

| 字段 | 类型 | 校验 | 含义 |
|---|---|---|---|
| `key` | str | 非空 | 参数名（i / a / m / z1 / …） |
| `meaning` | str | 非空 | 一句话含义（给人看） |
| `value` | str | 带单位 | 值 |
| `source` | str | **∈ {问,算,选,查,锁,假设}** | 来源 |
| `evidence` | str | 非空 | 依据：公式 / 表 / 用户哪句话 |
| `how_to_change` | str | 非空 | 改它的连带影响 |

**校验规则**：`test_every_row_has_a_declared_source` 守着 `source ∈ 六类`。

---

## 3. FeaturePlan（计划）

| 字段 | 类型 | 校验 | 含义 |
|---|---|---|---|
| `name` | str | 非空 | 特征名 |
| `units` | str | **必须 `"mm"`** | 内部单位 |
| `sketch_entities` | list[Line \| Circle] | 非空 | 草图实体 |
| `features` | list[Extrude] | 非空 | 特征序列 |
| `expected` | Expected | — | 预期体积与包围盒 |
| `provenance` | dict | — | 轮廓点数、形式、面积 |

### Expected

| 字段 | 单位 | 校验 |
|---|---|---|
| `volume_mm3` | mm³ | 落在齿根圆柱与齿顶圆柱之间 |
| `bbox_x_mm` / `bbox_y_mm` | mm | = 齿顶圆直径 |
| `bbox_z_mm` | mm | = 齿宽 |

### 坐标量级规则（1000× 事故回归）

`Line` 与 `Circle` 的所有坐标 **必须落在 1~1000**。
`test_entities_are_metric_not_metres` 守着这条。

**已有**：`proto/build_plan.py`。

---

## 4. Verification（验证结果）★ 新增

| 字段 | 类型 | 校验 | 含义 |
|---|---|---|---|
| `ok` | bool | — | 总体通过否 |
| `measured_volume_mm3` | float | > 0 | 实测体积 |
| `expected_volume_mm3` | float | > 0 | 计划体积 |
| `volume_deviation_pct` | float | **< 1.0 才算过** | 体积偏差 |
| `measured_bbox_mm` | [x,y,z] | 三个 > 0 | 实测包围盒 |
| `expected_bbox_mm` | [x,y,z] | — | 计划包围盒 |
| `bbox_deviation_mm` | [dx,dy,dz] | 每个 < 0.5 | 包围盒偏差 |
| `views` | list[Path] | 非空 | 三视图路径 |
| `failure` | str \| None | — | 失败原因 |

---

## 5. ShaftRequest / ShaftPlan ★ 新增（第二族）

### ShaftRequest

| 字段 | 类型 | 校验 | 含义 |
|---|---|---|---|
| `torque_nm` | float | > 0 | 传递扭矩 |
| `span_mm` | float | > 0 | 支点跨距 |
| `shock` | str | `none` / `light` / `heavy` | 冲击工况 |
| `material` | str | 材料库有 | 材料牌号 |

### 派生字段

| 字段 | 公式 | 来源 |
|---|---|---|
| `d_min_mm` | `(16T/(π·τ_allow))^(1/3)` × 冲击系数 | 扭转强度 |
| `tau_allow_mpa` | `σs / (SF)` 按材料 | `material_db.yaml` |

**注意**：轴的直径是**旋转体轮廓**（原语 2），不是闭合轮廓拉伸。

---

## 6. 状态转换

```
Request ──derive──> Derivation
    │                  │
    │ 无解 ──> diagnostics[]（终态，不生成）
    │
    └──plan──> FeaturePlan
                   │
                   ├──execute──> model ──verify──> Verification{ok:true}  （终态：成功）
                   │                      └────> Verification{ok:false}（终态：失败，带 failure）
                   │
                   └──execute 抛异常 ──> FailureRecord{plan, traceback, screenshot}
```

**规则**：失败必须落 `FailureRecord`，**不允许静默返回 None**（`execute` 契约）。
