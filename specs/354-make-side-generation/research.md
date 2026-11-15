# Phase 0 Research — 造环节

**Date**: 2026-11-06 | **Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

---

## U1 · `extrude_boss` 收米还是毫米

**Decision**: `extrude_boss(model, sketch_name, depth)` 的 `depth` 收 **米**。

**Rationale**（逐条实测，不是推断）：

| 证据 | 内容 |
|---|---|
| 官方 `C:\swapi\types\IFeatureManager\FeatureExtrusion3.md` | 逐字：「**D1**: Depth of extrusion for first end **in meters**」 |
| `scripts/sw_part.py:1320` | 「★ 本函数**没有**乘 `_MM_TO_M`（★ 同模块的 `sketch_line` **乘了** ⇒ 两个口径）」 |
| `tests/solidworks_configuration_family_regression.py:69` | 真机脚本的用法是 `extrude_boss(model, sk, mm(8))` —— 用 `mm(...)` 先转米 |

**⇒ 三处口径互不相同，这是本特性的头号地雷：**

| 接口 | 收什么 | 依据 |
|---|---|---|
| `sketch_line(x1,y1,x2,y2)` | **毫米** | 内部再乘 `_MM_TO_M` |
| `sketch_circle(cx,cy,r)` | **毫米（半径）** | 同上 |
| `extrude_boss(model, sk, depth)` | **米** | 官方 D1 = meters，函数不转换 |
| `outline_points_m` | **米** | 命名即为米 |

**Alternatives considered**: 统一改成毫米 —— **否决**。那要改 `extrude_boss` 的签名，
而它已被现有真机测试依赖；改签名会让既有测试失效，且违反「不重造」。

**落法**：`FeaturePlan` 内部一律毫米；**只有 `to_meters()` 一个函数**做转换（已有 8 条测试里
`test_unit_conversion_happens_exactly_once` 守着）。

---

## U2 · 建模后怎么回读体积与包围盒

**Decision**: 体积用 `sw_mass_property.mass_properties()`，包围盒用 `sw_feature_readback.solid_body_extent_mm()`。

**Rationale**：

```python
# scripts/sw_mass_property.py
def mass_properties(model) -> dict[str, Any]:
    """读质量属性读数。
    :returns: {volume, surface_area, center_of_mass, density, mass, units}
        ★ 不做任何换算
    """
```

```python
# scripts/sw_feature_readback.py
def solid_body_extent_mm(doc) -> dict:
    """★ 实体的包围盒 X/Y/Z 三个跨度（毫米）。
    返回 {"ok": bool, "x_mm", "y_mm", "z_mm", "raw"}；失败时带 error。
    """
```

**⚠ 一条踩过的坑（`sw_feature_readback.py:165` 逐字）**：

> `IFeature.GetBox()` 的官方 Remarks：「The values returned are **approximate** and
> **should not be used for comparison or calculation purposes**」

⇒ **判据必须用 `GetBodyBox`（经 `solid_body_extent_mm`），不能用 `IFeature.GetBox()`。**

**Alternatives considered**: 用 `IFeature.GetBox()` —— 否决，官方明说不许用于比较。

---

## U3 · 三视图怎么导 PNG

**Decision**: `sw_export.export_to_image(model, output_path, silent=True)`。

**Rationale**: 官方 `IModelDocExtension.SaveAs3`；`silent=True` 传 `swSaveAsOptions_Silent`
不弹对话框。扩展名须是 `.png` / `.jpg` / `.jpeg`。

**⚠ 已知限制**：它存的是**当前视图**，不是自动三视图。要出三视图必须**先切视图再导**，
或用 `sw_drawing_view` 建工程图。

**落法（本特性取简单方案）**：切三次标准视图（前/上/右）各导一张 PNG，文件名带视图名。
**不建工程图**——工程图属于图样层，不在造环节范围。

**Alternatives considered**: 用 `sw_drawing_view` 建真正的三视图工程图 —— 否决（超范围）。

---

## U4 · 失败时怎么留证

**Decision**: 复用项目已有的 `tools/sw_guard.py`（70 KB）+ `tools/guard_run.py`，不自建。

**Rationale**（项目已有机制，不重造）：

- `tools/guard_run.py`：弹窗护栏，命令超时或弹窗出现时抓证据并杀进程树
- `tools/sw_guard.py`：分级处置（auto / needs_llm / forbidden），历史事件台账

**落法**：`execute.py` 内部捕获异常后写 `output/execute_failures/<timestamp>.json`
（含 plan、异常栈、当前文档状态），并调 `export_to_image` 留一张现场 PNG。

**⚠ 不自建 apply 层的理由**：`sw_jlcfa_steps.py` 的教训已经写过——
「每步必须有判据、失败必须留证、每步必须有超时」，那三条已经在项目里，
再造一套会形成「一个事实两个家」（宪法 §「三处不许写」）。

---

## U5 · 齿轮轮廓 700 点会不会太慢

**Decision**: 默认 **200 点**（弦高 ≈5 µm），可配置。

**Rationale**（本会话实测，m=1/z=20，轮廓周长 131.63 mm）：

| 分段数 N | 平均弦长 | 弦高误差（R=11 mm） | 草图实体数 |
|---|---|---|---|
| 100 | 1.316 mm | **19.7 µm** | 100 |
| **200** | 0.658 mm | **4.9 µm** | **200** |
| 400 | 0.329 mm | 1.2 µm | 400 |
| 700（归档实现默认） | 0.188 mm | 0.40 µm | 700 |

**关键判断**：弦高 5 µm 已远大于「20 段圆弧 ≈ 0.22 µm」的近似误差
⇒ **真正的瓶颈是分段数，不是「折线 vs 圆弧」**。

`N ≈ 周长 / sqrt(8 · R · tol)`

| 目标容差 | N | 用途 |
|---|---|---|
| 5 µm | **200** | 一般装配（默认） |
| 1 µm | 440 | 加工件、线切割 |
| 0.4 µm | 700 | 只在需要与渐开线解析值比对时 |

**Alternatives considered**: 保持 700 —— 否决（7 倍草图实体，建模/重建/导出都慢）。

---

## R1 · 第二族为什么选轴

**Decision**: 轴。

**Rationale**：轴是 14 类里**唯一不含标准表、不含齿形**的纯几何体（旋转）。
用它验证 `execute()` 抽象是否够用，比拿齿轮验证便宜——
齿轮失败时分不清是抽象的问题还是齿形的问题。

---

## R2 · 已有 24 条测试的边界（不能退化）

| 文件 | 条数 | 守什么 |
|---|---|---|
| `test_gear_method.py` | 9 | 六类来源、交叉校验、无解诊断、口径显式化 |
| `test_build_plan.py` | 8 | 无 COM 依赖、**坐标量级（1000× 回归）**、预期体积可复算 |
| `test_dispatcher.py` | 7 | 分流表与调度器一致性 |

**新增的 `execute.py` / `verify.py` 不得破坏上述任何一条。**

---

## 未解决项 —— 已全部实测（2026-11-06）

### ★ T004：`mass_properties()["volume"]` 的单位是 **m³**，不是 mm³

**实测方法**：建 20×20×5 mm 方块，读 volume。

```
volume = 2.0000000000000003e-06
units  = mm^3          ← UNITS 常量这么写
×1e9   = 2000.000 mm^3  ← 与理论值 2000 完全吻合
```

**⇒ `UNITS["volume"] = "mm^3"` 是错的，实际返回 m³。**

**处置**：`verify.py` 里必须 `volume_mm3 = volume_raw * 1e9`，并把这条写成断言，
**不许依赖 `UNITS` 常量**。这是「文档说的 ≠ 运行时的」的又一例。

**旁证**：`sw_feature_readback.solid_body_extent_mm()` 返回的 `x_mm/y_mm/z_mm` 是**对的**
（20×20×5 读回 20/20/5），所以单位问题只在 volume 这一处。

### T005：`ForceRebuild3(False)` **非必须**

**实测**：同一件，rebuild 前后读数完全一致。

```
rebuild 前: bbox=20/20/5  volume=2.0e-06
rebuild 后: bbox=20/20/5  volume=2.0e-06
```

**处置**：`execute()` 里**保留**该调用（更稳，与归档实现一致），但**不把它当判据**。

### T006：`save_review_previews` 出 **BMP**，不是 PNG

**实测**：

```
cube20x20x5_isometric.bmp  4,800,054 B
cube20x20x5_front.bmp      4,800,054 B
cube20x20x5_top.bmp        4,800,054 B
cube20x20x5_right.bmp      4,800,054 B
```

**处置**：
- `Verification.views` 里存 `.bmp` 路径
- **每个 4.8 MB × 4 = 19 MB/次**，故 `output/views/` 需定期清，不进 git
- 若要 PNG，`sw_export.export_to_image(model, path.png)` 可单独调，但只能导**当前视图**

### 三项结论汇总

| # | 项 | 结论 | 对代码的影响 |
|---|---|---|---|
| T004 | volume 单位 | **m³**（UNITS 写错） | `verify` 里 ×1e9 |
| T005 | rebuild 必要性 | 非必须 | 保留但不判 |
| T006 | 三视图格式 | **BMP** 4.8 MB/张 | 路径存 .bmp，定期清 |
| — | 模板路径 | `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\gb_part.prtdot` | 探针与测试共用 |

**这一轮的副产物**：`D:\SOLIDWORKS Data\Templates\Part.prtdot` **不存在**，
`NewDocument` 会静默返回 `None`（不报错）。正确模板在 `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\`。
