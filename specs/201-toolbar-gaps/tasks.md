# 工具栏攻关 · 任务（tasks）

**编号**：201-toolbar-gaps ｜ 规格 `spec.md` ｜ 计划 `plan.md`

> 每条格式：**任务** → 验收（可执行）。
> ★ 状态：`[ ]` 未做 · `[~]` 进行中 · `[x]` 完成 · `[-]` 已判不做（带依据）。

## T000 前置：台账与规格

- [x] **T001** 把五轮截图的 119 条固化成 `docs/toolbar-ledger.json`（人工读图 = 需求原文）
  → 验收: `python -c "import json;print(len(json.load(open(r'D:\AI\SW\docs\toolbar-ledger.json',encoding='utf-8'))['items']))"` 输出 `119`
- [x] **T002** 写核实器：逐条对 `C:\swapi\` 核官方成员名，分「已能/可攻关/待查/待验证」四档
  → 验收: `python tools/build_toolbar_ledger.py` 退出 0 且生成 `docs/toolbar-ledger.md`
- [x] **T003** 规格与计划落 `specs/201-toolbar-gaps/`
  → 验收: 三个文件存在（`spec.md` `plan.md` `tasks.md`）
- [ ] **T004** 把 `docs/toolbar-ledger.md` 挂进收尾链，台账过期即拦
  → 验收: `tools/round_chain.ps1` 的生成器段含 `build_toolbar_ledger.py`

## B1 草图绘制·图元（9 条）✅ 已完成（轮 464）

- [x] **T101** 3 点边角矩形 `ISketchManager.Create3PointCornerRectangle`
- [x] **T102** 3 点中心矩形 `Create3PointCenterRectangle`
- [x] **T103** 平行四边形 `CreateParallelogram`
- [x] **T104** 切线弧 `CreateTangentArc`
- [x] **T105** 3 点圆弧 `Create3PointArc`
- [x] **T106** 部分椭圆 `CreateEllipticalArc`
- [x] **T107** 抛物线 `CreateParabola`
- [x] **T108** 圆锥 `CreateConic`
- [x] **T109** 周边圆 `PerimeterCircle`
  → 每条验收: 建一个新零件 → 在草图里画出该图元 → **回读草图实体计数增加**（`sw_sketch.count_segments`）→ 证据落 `output/sketch-primitives-evidence.json`
  → 整批验收: `python tools/sw_guard.py --timeout 600 -- python tools/prove_sketch_primitives.py` 退出 0 且 `pass == total`

## B3 草图编辑（7 条）✅ 6/7（轮 465；交叉曲线前置 3D 草图未通）

- [x] **T301** 剪裁实体 `ISketchManager.SketchTrim`
- [x] **T302** 延伸实体 `SketchExtend`
- [x] **T303** 等距实体 `SketchOffset2`
- [x] **T304** 绘制圆角 `CreateFillet`
- [x] **T305** 线性草图阵列 `CreateLinearSketchStepAndRepeat`
- [x] **T306** 圆周草图阵列 `CreateCircularSketchStepAndRepeat`
- [~] **T307** 交叉曲线 `IntersectCurves` —— **包装已写，前置未通**：官方要 3D 草图 + 两个相交面，而 `Insert3DSketch` 在本机回 `None`
  → 验收: 同上模式（数组长度 / 实体计数增量）

## B4 草图编辑·移动族（5 条）

- [ ] **T401** 移动实体 `IModelDoc2.SketchModifyTranslate`
- [ ] **T402** 复制实体 `SketchModifyCopy`
- [ ] **T403** 旋转实体 `SketchModifyRotate`
- [ ] **T404** 缩放实体比例 `SketchModifyScale`
- [ ] **T405** 伸展实体 `SketchModifyStretch`
  → 验收: ★ 判据是**几何变了**（草图实体坐标 / 计数）—— ★ 移动不改计数，故要读坐标

## B5 草图尺寸与关系（8 条）

- [ ] **T501** 水平尺寸 `AddHorizontalDimension2`
- [ ] **T502** 竖直尺寸 `AddVerticalDimension2`
- [ ] **T503** 尺寸链 `InsertChainDimensions`（★ 真名已核）
- [ ] **T504** 路径长度尺寸 `AddPathLengthDim`（★ 真名已核）
- [ ] **T505** 完全定义草图 `FullyDefineSketch`
- [ ] **T506** 显示/删除几何关系
  → 验收: 回读 `DisplayDimension` 计数 / 关系计数

## B6 曲面特征（9 条）

- [ ] **T601** 旋转曲面 · **T602** 扫描曲面 · **T603** 放样曲面 · **T604** 边界曲面
- [ ] **T605** 平面区域 · **T606** 等距曲面 · **T607** 剪裁曲面
- [ ] **T608** 直纹曲面 `InsertRuledSurfaceFromEdge`（★ 真名已核）
- [ ] **T609** 替换面 `InsertFeatureReplaceFace`（★ 真名已核）
- [ ] **T610** 加厚 `FeatureBossThicken` / 加厚切除 `FeatureCutThicken`（★ 真名已核）
  → 验收: 特征树增量 + `sw_surface.collect_surface_evidence` 的曲面体计数

## B7 特征下拉（6 条）

- [ ] **T701** 边界框 `Create3DBoundingBox`（★ 真名已核）
- [ ] **T702** 配合参考 `InsertMateReference2`（★ 真名已核）
- [ ] **T703** 通过参考点的曲线 `InsertCurveFile*`（★ 真名已核）
- [ ] **T704** 变量阵列 `InsertVaryInstanceIncrement/Override`（★ 真名已核）
- [ ] **T705** 分割线 · **T706** 投影曲线
  → 验收: 特征树增量

## B8 参考几何体（4 条）

- [ ] **T801** 基准面 `InsertRefPlane` · **T802** 坐标系 `InsertCoordinateSystem`
- [ ] **T803** 点 `InsertReferencePoint` · **T804** 质心 `InsertCenterOfMass`
  → 验收: 特征树增量且类型名对

## X 单列（**判不做，写明依据**）

- [ ] **TX01** 写 `docs/toolbar-gaps-backend-limits.md`：线性阵列族 / `IAccessSelections` 指针族 / 结构系统
  → 验收: 该文件存在，每条带**事实号**与**真机证据路径**，且**不含**「其实可以」的含糊话
- [ ] **TX02** 螺柱向导：官方源**查不到**入口 ⇒ 记「查不到」（铁律 5）
  → 验收: 台账里该条 `tier=待查` 且 `note` 写「官方源查不到」

## W 最终验收（对应 `spec.md` §四）

- [ ] **TW1** 台账可重建（W1） · **TW2** 凡「能」必有真机证据（W2）
- [ ] **TW3** 新模块过签名审计（W3） · **TW4** 判据是树/几何（W4）
- [ ] **TW5** 查不到的写明（W5） · **TW6** 后端口单列（W6）
- [ ] **TW7** `release_check.py` 退出 0（W7）
