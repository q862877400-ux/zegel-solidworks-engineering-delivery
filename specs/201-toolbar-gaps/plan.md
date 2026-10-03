# 工具栏攻关 · 计划（plan）

**编号**：201-toolbar-gaps ｜ **规格**：`spec.md`

## 一、总打法（一批一域，每批闭环）

```
① 查（铁律 4）：对该批每条，在 `C:\swapi\types\<接口>\<成员>.md` 取**精确签名与参数顺序**；
   CHM（`AI Solidworks\官方文档\`）补语义；出厂类型库裁决冲突。
② 立柱：按本仓既有模式建包装（`_select_by_id` / `get_com_member` / `_mm`·`_deg` 边界 / 规则 3 声明式选择）。
③ 挂工具：写 ToolSpec（含 `inject`！★ 那是本轮刚修的坑），或加进既有批次文件。
④ 真机验：走 `tools/sw_guard.py`，判据 = **特征树增量 / 几何增量**（不是返回值）。
⑤ 留证据：`output/<name>-evidence.json`，带 `tree_before/tree_after`。
⑥ 标等级：`capabilities.yaml` 新增或升级条目（`verified` 必须带 evidence）。
⑦ 台账回填：把该批的 `level`/`entry` 从「不能」改成「能」，重跑 `tools/build_toolbar_ledger.py`。
⑧ 门禁：若该批引入**可静态判**的规则（如「新包装必须过某门禁」），加一道并做**负例自证**（事实 62）。
```

## 二、批次划分（按可核到的官方成员数与域价值）

| 批 | 域 | 条数 | 官方成员（**已核到**的一批） | 预估难点 |
|---|---|---|---|---|
| **B1** | 草图绘制·图元 | 9 | `Create3PointCornerRectangle` · `Create3PointCenterRectangle` · `CreateParallelogram` · `CreateTangentArc` · `Create3PointArc` · `CreateEllipticalArc` · `CreateParabola` · `CreateConic` · `PerimeterCircle` | 参数顺序；部分成员要 `CreateSpline*` 那族的参数包 |
| **B2** | 草图绘制·样条与槽口 | 6 | `CreateSpline2/3` · `CreateEquationSpline2` · `CreateSplinesByEqnParams2` · `CreateSketchSlot` 的三种模式 | 槽口的模式枚举；方程式样条的参数结构体 |
| **B3** | 草图编辑 | 7 | `SketchTrim` · `SketchExtend` · `SketchOffset2` · `CreateFillet` · `CreateLinearSketchStepAndRepeat` · `CreateCircularSketchStepAndRepeat` · `IntersectCurves` | `SketchTrim` 要选中的实体与「保留哪一侧」；阵列的参数多 |
| **B4** | 草图编辑·移动族 | 5 | `SketchModifyTranslate` · `SketchModifyCopy` · `SketchModifyRotate` · `SketchModifyScale` · `SketchModifyStretch`（★ 在 `IModelDoc2` 上） | 参数形态（`VARIANT` 数组） |
| **B5** | 草图尺寸与关系 | 8 | `AddHorizontalDimension2` · `AddVerticalDimension2` · `InsertChainDimensions` · `AddPathLengthDim` · `FullyDefineSketch` · 删除关系 | 尺寸要 mark 与放置点；链式尺寸要一串实体 |
| **B6** | 曲面特征 | 9 | `InsertRuledSurfaceFromEdge` · `InsertFeatureReplaceFace` · `FeatureBossThicken` / `FeatureCutThicken` · 旋转/扫描/放样/边界曲面 · 平面区域 · 等距 · 剪裁 | 曲面实体选择；加厚的两个入口分凸台/切除 |
| **B7** | 特征下拉 | 6 | `Create3DBoundingBox` · `InsertMateReference2` · `InsertCurveFile*` · `InsertVaryInstance*` · 分割线 · 投影曲线 | 部分属装配域；曲线文件要写临时文件 |
| **B8** | 参考几何体 | 4 | `InsertRefPlane` · `InsertCoordinateSystem` · `InsertReferencePoint` · `InsertCenterOfMass` | 基准面有 8 种类型，参数各异 |
| **B9** | 特征 | 4 | 拔模 · 相交 · 旋转切除 · 放样/边界切除 | 待查清入口 |
| **X1** | **后端到不了**（单列，不做） | 3 族 | 线性阵列族（`FeatureLinearPattern4/5` 静默回 None）· `IAccessSelections` 指针族（钣金折弯/边法兰/角撑板）· 结构系统 | 依事实 47 / 369；**写依据，不假装** |
| **X2** | **官方源查不到**（单列） | 1+ | 螺柱向导（★ 官方源里一个都搜不到） | 按铁律 5 记「查不到」 |

## 三、技术约束（每条都必须守）

- **规则 2**：长度 `_mm`、角度 `_deg`，换算只在工具边界做一次。
- **规则 3**：需要几何的，一律**声明式选择**（`selection="index:0"` / `"__current_selection__"`），**不接受裸坐标**（★ 除草图图元 —— 那是官方文档写明的例外）。
- **规则 6**：建/改特征后**回读**（特征树 / 几何），不认返回值。
- **`inject`**：每个新 ToolSpec **必须显式声明 `inject`**（★ 本轮刚修过 16 个漏声明的，门禁已加）。
- **弹窗护栏**：真机命令一律 `python tools/sw_guard.py --timeout N -- python <脚本>.py`。
- **收尾**：每批收尾跑 `pwsh -File tools/round_chain.ps1 -Tests tests/<该批的>.py`。

## 四、每批的 Definition of Done

1. 包装函数进 `scripts/sw_<域>.py`（或既有模块），带六字段来源块。
2. ToolSpec 进 `mcp-server/tool_specs_batch*.py`（★ 带 `inject`）。
3. **真机建成**，证据落 `output/*-evidence.json`（`verdict: pass`，含树/几何增量）。
4. `capabilities.yaml` 条目升级为 `verified` 并带 `evidence`。
5. 台账回填后重跑生成器，`docs/toolbar-ledger.md` 里该条从「可攻关/不能」变「已能」。
6. `release_check.py` 退出 0。
7. 本文件末的批次表打勾，写清**没做成的**与**为什么**。
