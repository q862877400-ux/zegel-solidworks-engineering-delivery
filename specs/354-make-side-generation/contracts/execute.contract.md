# 契约 · execute(plan) -> (model, evidence)

**Feature**: `354-make-side-generation` | **Date**: 2026-11-06

---

## 签名

```python
def execute(plan: FeaturePlan, *, model=None, plane_name: str = "Front Plane") -> tuple[Any, dict]:
    ...
```

## 前置条件

| # | 条件 | 违反时 |
|---|---|---|
| 1 | `plan.units == "mm"` | 抛 `ValueError`，消息含实际值 |
| 2 | `plan.sketch_entities` 非空 | 抛 `ValueError` |
| 3 | `plan.features` 非空且第一个是 `Extrude` | 抛 `ValueError` |
| 4 | 所有坐标落在 `1.0 <= |c| <= 1000.0` | 抛 `ValueError`，列出越界坐标 |
| 5 | SolidWorks 已连接 | 抛 `ConnectionError`，**不许超时挂死** |

## 后置条件

| # | 条件 | 判据 |
|---|---|---|
| 1 | 返回的 `model` 非 `None` | `model is not None` |
| 2 | 特征树新增 1 个拉伸特征 | `feature_present(model, plan.name)` 为真 |
| 3 | 实体数 ≥ 1 | `solid_body_extent_mm(model)["ok"]` 为真 |
| 4 | `evidence` 含全部键 | 见下表 |

## evidence 必含字段

| 键 | 类型 | 含义 |
|---|---|---|
| `status` | str | `"ok"` / `"failed"` |
| `feature_name` | str | 实际特征名 |
| `primitive` | str | `"extrude"` / `"revolve"` |
| `sketch_entity_count` | int | 实际画了多少条草图实体 |
| `plane_name` | str | 建模基准面 |
| `depth_m` | float | **送进 API 的米值**（Extrude） |
| `angle_deg` | float | 旋转角（Revolve） |
| `profile_form` | str | `"closed_half_section"`（轴族真直线半剖）等；**禁止** `polyline_chord_approximation`（AGENTS.md 十四之五） |
| `uncovered` | list[str] | 未覆盖项 |

## 单位转换规则（唯一出口）

```python
# 送进 API 前：
sketch_line(model, x1_mm, y1_mm, x2_mm, y2_mm)   # 收毫米
sketch_circle(model, cx_mm, cy_mm, r_mm)          # 收毫米（半径）
extrude_boss(model, sketch_name, mm(depth_mm))    # 收米 ⇒ 必须 mm()
```

**来源**：
- `scripts/sw_part.py:1320`「本函数**没有**乘 `_MM_TO_M`（同模块的 `sketch_line` **乘了**）」
- 官方 `C:\swapi\types\IFeatureManager\FeatureExtrusion3.md`：「D1: Depth of extrusion for first end **in meters**」
- `tests/solidworks_configuration_family_regression.py:69`：`extrude_boss(model, sk, mm(8))`

## 失败契约

**不许返回 `None`，不许返回半成品。** 失败必须：

1. 抛异常（带原始错误文本，不吞）
2. 在 `output/execute_failures/<utc-timestamp>.json` 落 `FailureRecord`：

```json
{
  "plan_name": "...",
  "plan_snapshot": {...},
  "exception_type": "RuntimeError",
  "exception_message": "...",
  "stage": "sketch" | "extrude" | "rebuild",
  "sw_document_state": "part has N features",
  "screenshot": "output/execute_failures/<ts>.png"
}
```

3. 若 SolidWorks 仍连着，尽力导一张现场 PNG（导不出就写 `"screenshot": null`，**不掩盖**）

## 收尾义务

| # | 动作 | 依据 |
|---|---|---|
| 1 | 还原 `SketchManager.AddToDB` / `DisplayWhenAdded` | 归档实现的 try/finally |
| 2 | `model.ForceRebuild3(False)` | 归档实现有此调用（未验不调会怎样，见 research §未解决项） |
| 3 | 特征改名 `plan.name` | 便于回读定位 |

## 禁止

- ❌ 在 `execute` 里做参数推导（推导在 `derive()`）
- ❌ 在 `execute` 里做校核（校核在 `derive()` 与 `verify()`）
- ❌ 直接拼 `FeatureExtrusion3` 的 27 个参数（用项目已有 `extrude_boss`）
- ❌ 并发调用（COM 单进程，项目已知事实 24）
