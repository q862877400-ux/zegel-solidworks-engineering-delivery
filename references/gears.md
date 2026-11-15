# 齿轮实体建模与装配联动路由

> ★★ **2026-11-07 业主令（硬性禁令）**：全项目**禁止使用任何折线模拟曲线的功能**。
> 把渐开线/摆线/齿顶齿根圆弧采样成点列、再逐段用直线段连起来（含"弦线离散"、
> "多段圆弧逼近"）的做法一律禁止。理由：齿面不再是共轭渐开线、齿根不是真实摆线、
> 段数可调导致同一规格建出不同齿形。详见 `AGENTS.md`「禁止折线模拟曲线」条。

## 先判断用户要的是什么

| 用户意图 | 正确路线 | 禁止做法 |
|---|---|---|
| 画齿轮、建齿轮零件、生成真实齿形 | **当前无可用生成器**：真曲线实现 `scripts/gear_geometry.py` 尚在验证，整圈闭合/单齿阵列均未通过真机验收 | 用 Gear Mate 代替齿轮实体；**尤其禁止**回退到折线逼近 |
| 两个齿轮联动、可拖动传动、配合比 | `sw_assembly.add_gear_mate_by_cylinders()` | 用脚本假动画冒充 Gear Mate |
| 工业生产级齿轮 | 确认齿制、变位、侧隙、公差、修形、材料与强度，使用专用齿轮工具并工程师复核 | 把可视化齿形宣称为可投产齿形 |

用户只说"画个齿轮"时，不要因为启用了 Skill 就自动跳到装配配合。制造任务必须取得模数、齿数、压力角、齿宽和轴孔尺寸；仅用于视觉演示时，可使用默认参数，但必须在结果中明示。

## 当前可用范围

**没有任何可投产的齿轮实体生成器。** 两个历史路线均不可用：

- `archive/inherited-methods/scripts/sw_gear.py`（旧）：把渐开线离散成 `involute_segments` 段直线逐段画 —— **折线拟合，已明令禁用**，仅作归档追溯，不得再作为实现来源。
- `scripts/gear_geometry.py`（新）：方程式驱动的真渐开线 + 真摆线齿根（GB/T 1356 / GB/T 1357 / ISO 53），数学与表达式已具备；但整圈 120 条曲线的闭合相位、单齿阵列的阵列/中心孔两步**都还没通过真机验证**。真机证据见 `output/_probe_gear_closed_profile.json`（曲线 120/120 建成、`FeatureExtrusion3` 返回 None、体积 0）与 `output/_probe_gear_tooth_pattern.json`（单齿拉伸成功、阵列未加体积）。

在真曲线路线通过「特征建成 + 体积 <1% + 包围盒对上 + 三视图 4/4 + 人工目视」之前，齿轮族状态保持 `stitched`，不得升级为 `verified`，也不得对外提供建模入口。

## 解析尺寸（仅参数层，不产几何）

标准全齿高外啮合直齿圆柱齿轮：

- 分度圆直径：`d = m * z`
- 基圆直径：`db = d * cos(alpha)`
- 齿顶圆直径：`da = d + 2m`
- 齿根圆直径：`df = d - 2.5m`
- 分度圆齿厚：`s = pi * m / 2`

参数推理与六类来源溯源表见 `research/text-to-cad-and-parametric-plugins/proto/gear_method.py`（纯计算，不产轮廓）。

## 不得自动宣称支持的范围

- 斜齿轮、人字齿、锥齿轮、内齿轮、齿条、蜗轮蜗杆；
- 变位系数、侧隙、齿顶/齿向修形、精确滚刀齿根；
- ISO/GB/AGMA 公差等级、材料、热处理、接触/弯曲强度或 NVH 验证。

## 参考

- KHK，Calculation of Gear Dimensions：<https://khkgears.net/gear-knowledge/gear-technical-reference/calculation-gear-dimensions/>
- SOLIDWORKS API Help，`ISketchManager::CreateEquationSpline2`：方程式驱动曲线（真曲线路线的技术基础）。

`scripts/gear_geometry.py` 用 `CreateEquationSpline2` 把齿廓交给 SolidWorks 按方程生成真曲线，取代旧 `sw_gear.py` 的点列折线逼近；这条路线尚未完成，不代表已有可用能力。
