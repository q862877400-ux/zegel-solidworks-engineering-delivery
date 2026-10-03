# 工具栏攻关台账

> **本文件由 `tools/build_toolbar_ledger.py` 生成，不要手改。**
> 数据源：`docs/toolbar-ledger.json`（用户 2026-10-03 五轮截图问过的全部条目 = 需求原文）。

## 口径

| 档 | 含义 |
|---|---|
| **已能** | 本仓有入口**且**有真机证据（`capabilities.yaml` 的 `verified` / evidence 文件） |
| **可攻关** | 本仓**无入口**，而**官方成员在 `C:\swapi\` 里核到了** ⇒ 可以按官方签名立柱实现 |
| **待验证** | 本仓有入口，但我还没跑成（判据要重做或入口要修） |
| **待查** | 我填的 api 名在官方源里**没核到** ⇒ 按铁律 5 记「查不到」，先查清再动手 |

## 汇总

| 档 | 条数 |
|---|---|
| 已能 | 76 |
| 可攻关 | 16 |
| 待验证 | 7 |
| 待查 | 20 |
| **合计** | **119** |

## 逐条

| 工具条 | 条目 | 档 | 官方成员（已核） | 本仓入口 |
|---|---|---|---|---|
| 曲面 | 扫描曲面 | **可攻关** | `InsertProtrusionSwept4`, `Surface` | — |
| 曲面 | 自由样式 | **可攻关** | `InsertFreeform` | — |
| 特征下拉 | 填充阵列 | **可攻关** | `FeatureFillPattern` | — |
| 特征下拉 | 曲线-分割线 | **可攻关** | `InsertSplitLineProject` | — |
| 特征下拉 | 曲线-投影曲线 | **可攻关** | `InsertProjectedSketch` | — |
| 特征下拉 | 曲线-通过XYZ点的曲线 | **可攻关** | `InsertCurveFile` | — |
| 特征下拉 | 曲线驱动的阵列 | **可攻关** | `FeatureCurvePattern` | — |
| 特征下拉 | 草图驱动的阵列 | **可攻关** | `FeatureSketchDrivenPattern` | — |
| 特征下拉 | 表格驱动的阵列 | **可攻关** | `InsertTableDrivenPattern` | — |
| 特征下拉 | 高级孔 | **可攻关** | `HoleWizard5` | — |
| 草图尺寸 | 对称线性直径尺寸 | **可攻关** | `AddSymmetricDimension` | — |
| 草图绘制 | 方程式驱动的曲线 | **可攻关** | `CreateEquationSpline2`, `CreateSplinesByEqnParams2` | — |
| 草图绘制 | 样式样条曲线 | **可攻关** | `CreateSpline3` | — |
| 草图编辑 | 侧影实体 | **可攻关** | `SketchUseEdge3` | — |
| 草图编辑 | 复制实体 | **可攻关** | `IModelDoc2` | — |
| 草图编辑 | 曲面上偏移 | **可攻关** | `SketchOffsetOnSurface` | — |
| 曲面 | 圆角(曲面) | **待验证** | `FeatureFillet` | `sw_part.fillet` |
| 特征 | 筋 | **待验证** | `InsertRib` | `sw_part.rib_report` |
| 特征 | 线性阵列 | **待验证** | `FeatureLinearPattern4` | `sw_part.linear_pattern` |
| 特征下拉 | 曲线-组合曲线 | **待验证** | `InsertCompositeCurve` | `sw_part.insert_composite_curve_report` |
| 草图关系 | 显示/删除几何关系 | **待验证** | `ISketch`, `DeleteRelation` | `sw_sketch_dimensions.*` |
| 草图关系 | 添加几何关系 | **待验证** | `SketchAddConstraints` | `sw_part.add_sketch_relation` |
| 草图编辑 | 交叉曲线 | **待验证** | `IntersectCurves` | `sw_sketch_edit_ops.sketch_intersect_curves` |
| 曲面 | 使用曲面切除 | **待查** | — | — |
| 曲面 | 剪裁曲面 | **待查** | — | — |
| 曲面 | 加厚 | **待查** | — | — |
| 曲面 | 加厚切除 | **待查** | — | — |
| 曲面 | 直纹曲面 | **待查** | — | — |
| 曲面 | 边界曲面 | **待查** | — | — |
| 特征 | 扫描切除 | **待查** | — | `sw_sweep.create_sweep_report(cut=True)` |
| 特征 | 拔模 | **待查** | — | — |
| 特征 | 相交 | **待查** | — | — |
| 特征下拉 | 参考几何体-边界框 | **待查** | — | — |
| 特征下拉 | 参考几何体-配合参考 | **待查** | — | — |
| 特征下拉 | 变量阵列 | **待查** | — | — |
| 特征下拉 | 曲线-通过参考点的曲线 | **待查** | — | — |
| 特征下拉 | 螺柱向导 | **待查** | — | — |
| 草图尺寸 | 基准尺寸 | **待查** | — | `sw_sketch_dimensions.*` |
| 草图尺寸 | 尺寸链 | **待查** | — | `sw_sketch_dimensions.*` |
| 草图尺寸 | 水平尺寸链 | **待查** | — | — |
| 草图尺寸 | 竖直尺寸链 | **待查** | — | — |
| 草图尺寸 | 路径长度尺寸 | **待查** | — | `sw_sketch_dimensions.*` |
| 草图尺寸 | 链尺寸 | **待查** | — | `sw_sketch_dimensions.*` |
| 曲面 | 删除孔 | **已能** | `InsertDeleteHole` | — |
| 曲面 | 删除面 | **已能** | `InsertDeleteFace2` | — |
| 曲面 | 填充曲面 | **已能** | `InsertFillSurface2` | `sw_surface_features.insert_fill_surface_report` |
| 曲面 | 平面区域 | **已能** | `InsertPlanarRefSurface` | — |
| 曲面 | 延伸曲面 | **已能** | `InsertExtendSurface` | `sw_surface_features.insert_extend_surface_report` |
| 曲面 | 拉伸曲面 | **已能** | `FeatureExtruRefSurface3` | `sw_surface_features.create_extruded_surface_report` |
| 曲面 | 放样曲面 | **已能** | `InsertProtrusionBlend2`, `Surface` | — |
| 曲面 | 旋转曲面 | **已能** | — | — |
| 曲面 | 曲面展平 | **已能** | `InsertFlattenSurface` | — |
| 曲面 | 替换面 | **已能** | — | — |
| 曲面 | 等距曲面 | **已能** | `InsertOffsetSurface` | — |
| 曲面 | 缝合曲面 | **已能** | `InsertSewRefSurface` | `sw_surface_features.knit_surfaces_report` |
| 曲面 | 解除剪裁曲面 | **已能** | `InsertUntrimSurface` | — |
| 特征 | 包覆 | **已能** | `InsertWrapFeature2` | `sw_wrap.create_wrap_report` |
| 特征 | 参考几何体-基准轴 | **已能** | `InsertAxis2` | `sw_part.create_axis_report` |
| 特征 | 圆角 | **已能** | `FeatureFillet` | `sw_part.fillet` |
| 特征 | 异型孔向导 | **已能** | `HoleWizard5` | `sw_hole_features.*_report` |
| 特征 | 扫描 | **已能** | `ISweepFeatureData` | `sw_sweep.create_sweep_report` |
| 特征 | 抽壳 | **已能** | `InsertFeatureShell` | `sw_part.shell_report` |
| 特征 | 拉伸凸台/基体 | **已能** | `FeatureExtrusion3` | `sw_part.extrude_boss` |
| 特征 | 拉伸切除 | **已能** | `FeatureCut4` | `sw_part.extrude_cut` |
| 特征 | 放样凸台/基体 | **已能** | `InsertProtrusionBlend2` | `sw_loft.create_loft_report` |
| 特征 | 放样切除 | **已能** | `InsertCutBlend` | — |
| 特征 | 旋转凸台/基体 | **已能** | `FeatureRevolve2` | `sw_part.revolve_boss` |
| 特征 | 旋转切除 | **已能** | `FeatureRevolveCut2` | — |
| 特征 | 曲线-螺旋线/涡状线 | **已能** | `InsertHelix` | `sw_helix.insert_helix` |
| 特征 | 边界凸台/基体 | **已能** | `InsertProtrusionBlend2` | — |
| 特征 | 边界切除 | **已能** | `InsertCutBlend` | — |
| 特征 | 镜向 | **已能** | `InsertMirrorFeature2` | `sw_part.mirror_feature` |
| 特征下拉 | 参考几何体-坐标系 | **已能** | `InsertCoordinateSystem` | — |
| 特征下拉 | 参考几何体-基准面 | **已能** | `InsertRefPlane` | — |
| 特征下拉 | 参考几何体-点 | **已能** | `InsertReferencePoint` | — |
| 特征下拉 | 参考几何体-质心 | **已能** | `InsertCenterOfMass` | — |
| 特征下拉 | 圆周阵列 | **已能** | `FeatureCircularPattern4` | `sw_part.circular_pattern` |
| 特征下拉 | 螺纹线 | **已能** | `InsertCosmeticThread3` | — |
| 草图关系 | 完全定义草图 | **已能** | `FullyDefineSketch` | `sw_sketch_dimensions.*` |
| 草图尺寸 | 智能尺寸 | **已能** | `AutoDimension2` | `sw_part.auto_dimension_sketch` |
| 草图尺寸 | 水平尺寸 | **已能** | `AddHorizontalDimension2` | `sw_sketch_dimensions.*` |
| 草图尺寸 | 竖直尺寸 | **已能** | `AddVerticalDimension2` | `sw_sketch_dimensions.*` |
| 草图绘制 | 3点中心矩形 | **已能** | `Create3PointCenterRectangle` | `sw_sketch_primitives.sketch_3point_center_rectangle` |
| 草图绘制 | 3点圆弧 | **已能** | `Create3PointArc` | `sw_sketch_primitives.sketch_3point_arc` |
| 草图绘制 | 3点边角矩形 | **已能** | `Create3PointCornerRectangle` | `sw_sketch_primitives.sketch_3point_corner_rectangle` |
| 草图绘制 | 三点圆弧槽口 | **已能** | `CreateSketchSlot` | — |
| 草图绘制 | 中心点圆弧槽口 | **已能** | `CreateSketchSlot` | — |
| 草图绘制 | 中心点直槽口 | **已能** | `CreateSketchSlot` | — |
| 草图绘制 | 中心矩形 | **已能** | `CreateCenterRectangle` | `sw_part.sketch_rectangle` |
| 草图绘制 | 中心线 | **已能** | `CreateCenterLine` | `sw_part.sketch_centerline` |
| 草图绘制 | 中点线 | **已能** | `CreateLine` | — |
| 草图绘制 | 切线弧 | **已能** | `CreateTangentArc` | `sw_sketch_primitives.sketch_tangent_arc` |
| 草图绘制 | 周边圆 | **已能** | `PerimeterCircle` | `sw_sketch_primitives.sketch_perimeter_circle` |
| 草图绘制 | 圆 | **已能** | `CreateCircle` | `sw_part.sketch_circle` |
| 草图绘制 | 圆心/起/终点画弧 | **已能** | `CreateArc` | `sw_part.sketch_arc` |
| 草图绘制 | 圆锥 | **已能** | `CreateConic` | `sw_sketch_primitives.sketch_conic` |
| 草图绘制 | 平行四边形 | **已能** | `CreateParallelogram` | `sw_sketch_primitives.sketch_parallelogram` |
| 草图绘制 | 抛物线 | **已能** | `CreateParabola` | `sw_sketch_primitives.sketch_parabola` |
| 草图绘制 | 曲面上的样条曲线 | **已能** | `CreateSpline` | — |
| 草图绘制 | 样条曲线 | **已能** | `CreateSpline2`, `CreateSpline3` | `sw_part.sketch_spline` |
| 草图绘制 | 椭圆 | **已能** | `CreateEllipse` | `sw_part.sketch_ellipse` |
| 草图绘制 | 直槽口 | **已能** | `CreateSketchSlot` | `sw_part.sketch_slot` |
| 草图绘制 | 直线 | **已能** | `CreateLine` | `sw_part.sketch_line` |
| 草图绘制 | 绘制倒角 | **已能** | `CreateChamfer` | `sw_sketch_edit.create_sketch_chamfer` |
| 草图绘制 | 绘制圆角 | **已能** | `CreateFillet` | `sw_sketch_edit_ops.sketch_fillet` |
| 草图绘制 | 转换实体引用 | **已能** | `SketchUseEdge3` | `sw_sketch_edit.convert_entities` |
| 草图绘制 | 边角矩形 | **已能** | `CreateCornerRectangle` | `sw_part.sketch_corner_rectangle` |
| 草图绘制 | 退出草图 | **已能** | `InsertSketch` | `sw_part.end_sketch` |
| 草图绘制 | 部分椭圆 | **已能** | `CreateEllipticalArc` | `sw_sketch_primitives.sketch_elliptical_arc` |
| 草图绘制 | 镜向实体 | **已能** | `GetDynamicMirror`, `SetDynamicMirror` | `sw_sketch_edit.sketch_mirror` |
| 草图编辑 | 伸展实体 | **已能** | `IModelDoc2` | — |
| 草图编辑 | 剪裁实体 | **已能** | `SketchTrim` | `sw_sketch_edit_ops.sketch_trim` |
| 草图编辑 | 圆周草图阵列 | **已能** | `CreateCircularSketchStepAndRepeat` | `sw_sketch_edit_ops.sketch_circular_pattern` |
| 草图编辑 | 延伸实体 | **已能** | `SketchExtend` | `sw_sketch_edit_ops.sketch_extend` |
| 草图编辑 | 旋转实体 | **已能** | `IModelDoc2`, `SketchModifyRotate` | — |
| 草图编辑 | 移动实体 | **已能** | `IModelDoc2`, `SketchModifyTranslate` | — |
| 草图编辑 | 等距实体 | **已能** | `SketchOffset2` | `sw_sketch_edit_ops.sketch_offset` |
| 草图编辑 | 线性草图阵列 | **已能** | `CreateLinearSketchStepAndRepeat` | `sw_sketch_edit_ops.sketch_linear_pattern` |
| 草图编辑 | 缩放实体比例 | **已能** | `IModelDoc2`, `SketchModifyScale` | — |
