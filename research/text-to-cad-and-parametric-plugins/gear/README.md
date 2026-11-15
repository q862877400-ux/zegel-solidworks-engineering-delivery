# 齿轮族：真曲线构造与拉伸（2026-11-07 这一轮的完整实证）

读完这份能解决什么：知道齿轮「画得对、拉得出来」这条路的**每一段代码在哪、每个结论的证据在哪**，
以及哪几条路已经被证伪（不要重走）。目录里全部是**真曲线**实现，无折线（AGENTS.md §十四之五）。

## 结论先行

| 项 | 值 | 证据 |
|---|---|---|
| 齿形 | 真渐开线齿面 + 真摆线齿根过渡 + 真圆弧齿顶/槽底 | `_gear_v3_curves.py`；闭合超差 0.000 µm |
| 每条齿曲线数 | 6 条（左右齿根过渡、左右齿面、齿顶面、槽底） | 同上 |
| 直线段数量 | **0** | 同上 |
| 真机建成 | 是，体积 **3092.021 mm³** | `evidence/sw_gear_ok.png`、`_try_merge.py` |
| 与解析值偏差 | **0.03%**（截面积 309.2 mm² × 10 mm） | `evidence/_probe_gear_closed_profile.json` |
| 整圈拉伸能否直接成功 | **不能**，必须先 `MergePoints` | `evidence/_probe_gear_closed_profile.json`（`extrude: false`） |

## 关键发现：为什么整圈拉伸会静默失败

`FeatureExtrusion3` 回 `None`，但 `GetSketchContours()=1`、`IsClosed()=true` 都报「闭合」——
**这两套判据与建特征时的判据不一致**。用 SolidWorks 自己的
`ISketch::CheckFeatureUse`（等价工具「检查草图合法性」）才查出真因：

```
检查(修补前)  status=15  开放轮廓 0  闭合轮廓 0
MergePoints(1e-6 m) = True
检查(修补后)  status=0   OK 可用于该特征  开放轮廓 0  闭合轮廓 1
FeatureExtrusion3 返回 = Feature
体积 = 3092.021 mm³
```

根因：`CreateSpline2` 生成的样条端点不会精确穿过给定首尾点，120 段累积后留下 **15.6 µm** 首尾缝
（业主用「检查草图合法性」也定位到同一点）。缝存在 ⇒ 整条链是**开放的** ⇒ 闭合轮廓为 0
⇒ 拉伸失败、草图里没有蓝色区域阴影。

## 文件清单

### 正式流程（按执行顺序）

| 文件 | 作用 |
|---|---|
| `_gear_v3_curves.py` | **齿廓几何构造**。每齿 6 条真曲线，输出可直接喂 `sketch_spline`/`sketch_arc` 的坐标（毫米）。这是最该复用的一个文件。 |
| `_draw_gear_sketch.py` | 把上一步的轮廓画进 SolidWorks 草图，留给人工目视。 |
| `_gear_audit.py` | **离线拓扑自检**：顶点度数、自由端点、圆弧跨度方向。送真机之前先把不合格的轮廓判死。 |
| `_try_merge.py` | **完整建成流程**：检查 → `MergePoints(1e-6)` → 再检查 → 拉伸 → 读体积。这是唯一真机建成的那条路。 |

### 隔离实验（每个都回答了一个具体问题）

| 文件 | 回答了什么 |
|---|---|
| `_probe_square.py` | 拉伸 API 是否正常 —— 方形 1000.000 mm³ 精确，**证明 API 没问题** |
| `_probe_petal.py` | 2 样条 + 2 圆弧能不能拉伸 —— 能（体积 355.475 mm³） |
| `_probe_petal_variants.py` | 扇角/半径/点数哪个是瓶颈 —— 四个变体全成，**证明都不是** |
| `_probe_tooth_isolate.py` | 去掉齿根过渡还剩什么 —— 仍失败，排除齿根过渡 |
| `_probe_tooth_bisect.py` | 样条点数 12→130 —— 全失败，排除点数 |
| `_probe_checkfeatureuse.py` | `CheckFeatureUse` 返回形态与 `out` 参数写法 |
| `_probe_check_compare.py` | 方形 status=0 vs 齿轮 status=15 —— **证明该检查能判别** |
| `_probe_diag_apis.py` | 6 个诊断接口逐个跑通（实体/特征/草图/会话日志） |
| `_probe_extrude_routes.py` / `_probe_extrude3.py` / `_probe_tooth_pattern3.py` | `FeatureExtrusion3` 的多种选法与参数组合 |
| `_verify_debug.py` | `scripts/sw_debug.py` 的自验证，**带负例**：合格草图不报、不合格草图必报 |

### 证据

`evidence/` 下：

- `sw_gear_ok.png` —— 真机建成后的 SolidWorks 窗口截图，特征树含 `凸台-拉伸4`、`实体(1)`
- `_probe_gear_closed_profile.json` —— 整圈 120 段直接拉伸失败的完整记录
- `_probe_gear_merge_points.json` —— `MergePoints` 前后对比
- `_probe_petal_variants.json`、`_probe_tooth_isolate.json`、`_probe_tooth_bisect.json` —— 三组排除实验

> 还有一次**折线对照实验**（每边 30 / 120 个采样点，用 `sketch_line` 连成折线，共 62 / 242 段）：
> 两次都 `轮廓数 3`、`拉伸 False`。即**折线也拉不出来**，所以「拉伸失败」从来不是曲线类型的问题，
> 而是首尾缝导致没有闭合轮廓。该实验的实现按 AGENTS.md §十四之五**不留代码**（它是折线实现），
> 只留这条结论。`scripts/check_no_polyline.py` 已覆盖本目录。

## 不要重走的路（都有证据）

1. **整圈一次拉伸** —— 见 `_probe_gear_closed_profile.json`。必须先 `MergePoints`。
2. **折线模拟渐开线** —— 已被业主明令禁止（AGENTS.md §十四之五），且齿形不再是共轭渐开线。
3. **调 `FeatureExtrusion3` 的 23 个参数** —— 试过 `UseFeatScope`/`UseAutoSelect` 三种组合，都不成；
   真正的差别是草图有没有闭合轮廓，不是参数。
4. **加大样条点数** —— 12 到 130 全试过，全失败。
5. **抬渐开线起点避开基圆尖点**（`t_start` 0.00~0.30）—— 全失败。

## 未完成

齿轮族在 `capabilities.yaml` 里仍是 `stitched`，**不得升 `verified`**：生成器尚未并入 `scripts/`，
三视图未导出，缺 `execute.py` 与 `verify.py` 的正式接线。见 `specs/354-make-side-generation/tasks.md`。

## 单位陷阱（这三处不一致，本目录代码已按此处理）

| 接口 | 收的单位 |
|---|---|
| `sketch_line` / `sketch_circle` / `sketch_arc` / `sketch_spline` | **毫米** |
| `extrude_boss` / `FeatureExtrusion3` 的 D1 | **米** |
| `mass_properties()["volume"]` | **立方米**（须 × 1e9 得 mm³） |
| `CreateEquationSpline2` 的系数 | **毫米** |
