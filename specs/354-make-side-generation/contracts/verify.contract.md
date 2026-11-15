# 契约 · verify(model, plan) -> Verification

**Feature**: `354-make-side-generation` | **Date**: 2026-11-06

---

## 签名

```python
def verify(model, plan: FeaturePlan, *, views_dir: str | Path | None = None) -> Verification:
    ...
```

## 前置条件

| # | 条件 | 违反时 |
|---|---|---|
| 1 | `model` 非 `None` | 抛 `ValueError` |
| 2 | `plan.units == "mm"` | 抛 `ValueError` |
| 3 | `plan.expected.volume_mm3 > 0` | 抛 `ValueError`（没有预期值就无从比对） |

## 后置条件

| # | 条件 | 判据 |
|---|---|---|
| 1 | 返回 `Verification` 实例 | `isinstance(v, Verification)` |
| 2 | `ok` 为布尔 | — |
| 3 | `ok=False` 时 `failure` 非空 | `v.failure is not None` |

## 判据（三条缺一不可）

### L3-a 体积

```
volume_deviation_pct = |measured - expected| / expected × 100
通过条件：< 1.0
```

**读数来源**：`sw_mass_property.mass_properties(model)["volume"]`
**单位**：`UNITS["volume"] == "mm^3"`（`scripts/sw_mass_property.py:79` 已确认）

### L3-b 包围盒

```
bbox_deviation_mm[i] = |measured[i] - expected[i]|
通过条件：每个方向 < 0.5 mm
```

**读数来源**：`sw_feature_readback.solid_body_extent_mm(model)` → `{ok, x_mm, y_mm, z_mm}`

**⚠ 禁止用 `IFeature.GetBox()`** —— 官方 Remarks 逐字：
> "The values returned are **approximate** and **should not be used for comparison or calculation purposes**"

（出处：`scripts/sw_feature_readback.py:165`）

### L4 三视图

```
views = save_review_previews(model, views_dir, basename=plan.name,
                             views=("isometric", "front", "top", "right"))
通过条件：4 个文件都存在且非空
```

**读数来源**：`scripts/sw_review.py:save_review_previews`（已有）

**注意**：这是**自动导出**，不是**人工目视**。
`Verification.views` 只证明「图出来了」，不证明「图是对的」。
人工目视要在 quickstart 里单独做，并在报告里如实标注
「automated checks passed; not visually reviewed」或「已目视」。

## Verification 返回结构

```python
@dataclass(frozen=True)
class Verification:
    ok: bool
    measured_volume_mm3: float | None
    expected_volume_mm3: float
    volume_deviation_pct: float | None
    measured_bbox_mm: tuple[float, float, float] | None
    expected_bbox_mm: tuple[float, float, float]
    bbox_deviation_mm: tuple[float, float, float] | None
    views: list[str]
    failure: str | None
```

## 失败分类

| 情形 | `failure` 内容 |
|---|---|
| 体积读不到 | `"mass_properties 回空：<原始错误>"` |
| 包围盒读不到 | `"solid_body_extent_mm 失败：<error 字段>"` |
| 体积偏差超限 | `"体积偏差 3.2% > 1.0%（实测 X，预期 Y）"` |
| 包围盒偏差超限 | `"包围盒偏差 X 超限：dz=0.8mm > 0.5mm"` |
| 三视图缺失 | `"三视图只出了 2/4"` |

**多条同时失败时，`failure` 里按 `; ` 拼接，不掩盖任何一条。**

## 禁止

- ❌ 在 `verify` 里重建模型（它只读）
- ❌ 把「偏差 1.2%」四舍五入成 1.0% 让它过
- ❌ 三视图缺失时静默返回 `ok=True`
- ❌ 用 `IFeature.GetBox()` 代替 `solid_body_extent_mm`
