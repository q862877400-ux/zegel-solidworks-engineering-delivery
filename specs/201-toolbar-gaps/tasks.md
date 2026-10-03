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

## B4 草图编辑·移动族（5 条）✅ 已完成（轮 471-472；★ 真机 **5/5**，判据按操作分）

- [x] **T401** 移动实体 `IModelDoc2.SketchModifyTranslate` ★ 判据：`ModelToSketchTransform.ArrayData` 平移分量
- [~] **T402** 复制实体 —— ★★ **三源都查不到 2D 入口**（swapi/CHM/反射含 `SketchModify` 的都只有 4 个；官方 `RotateOrCopy3D*` 逐字写「selected **3D sketch** entities」）⇒ 铁律 5，不假装做到
- [x] **T403** 旋转实体 `SketchModifyRotate` ★ 真机：30° ⇒ 3×3 首行 `[0.866025,-0.500001,0]`
- [x] **T404** 缩放实体比例 `SketchModifyScale` ★ 真机：1.5 ⇒ bbox ±20/±10 → **±30/±15**
- [x] **T405** 伸展实体 —— ★**真名是 `IModelDocExtension.Stretch`**（不在 `IModelDoc2` 上）★ 真机已跑
  → 验收: ★ 判据是**几何变了**（草图实体坐标 / 计数）—— ★ 移动不改计数，故要读坐标

## B5 草图尺寸与关系（8 条）

- [x] **T501** 水平尺寸 `AddHorizontalDimension2` —— ⚠ **弹「修改」框、等人填数**（★ 事实 421 修正了“会挂”：`hung=false`）
  → 证据：`output/dialog-events/2026-10-03T13:4*.json`（★ 控件树：SLIDER×3 + THUMB WHEEL×3）
- [x] **T502** 竖直尺寸 `AddVerticalDimension2` —— ⚠ **同上（弹「修改」框）**（★ 事实 421）
- [x] **T503** 尺寸链 `InsertChainDimensions` ✅ 轮 492 —— ★★ **真因查清**：`getattr` 回 `(None, None, None)`
  （★ **事实 386/387**）；★ 而用 `dispid` 直调（轮 494：`dispid=319`、三种包装全 `ok=True`）**特征树仍不动**
  ⇒ ★ **按事实 53 停下**；状态 =「**包装层现象已定性，几何前置未通**」（★ 不是后端到不了）
- [x] **T504** 路径长度尺寸 `AddPathLengthDim` ✅ 轮 490 —— 真机 **`dim=[0,0]` ⇒ 不能**（★ 判据 = `DisplayDimension` 计数）
- [x] **T505** 完全定义草图 `FullyDefineSketch` ✅ 轮 490 —— 真机 **`dim=[0,1]` ⇒ 能**（★ 而枚举取值表两套源都没查到 ⇒ 只记它回了什么数）
- [x] **T506** 显示/删除几何关系 ✅ 轮 490 —— 真机：**关系计数 能** · **删除全部关系 不能** · **添加几何关系 不能**
  （★ 而台账里「添加几何关系」**原标「能」** ⇒ ★ **已按证据回填为「不能」** —— ★ W2 判据反向也管用）
  → 验收: 回读 `DisplayDimension` 计数 / 关系计数
  → 证据: `output/b5-sketch-dimensions-evidence.json`（`verdict: partial` · **6 条**）· 探针 `tools/prove_b5_sketch_dimensions.py`
  → ⚠ **收口说明**：★ 本批**按序号逐条单跑**（★ 整批连跑会挂住 —— ★ 探针 `run()` 的注释早写着）；★ 6/8 有证据、2 条会挂已单列

## B6 曲面特征（9 条）

- [ ] **T601** 旋转曲面 —— ⚠ **入口已核、真机未成**：`InsertRevolvedRefSurface` 回 `Feature` 而**树不动**
  （★ 5 组 `RevType`×`angle` 全试过 ⇒ **按事实 53 停下**）；旋转轴走**捕获 `CreateCenterLine` 返回值**（选中数 2 = 对）
- [ ] **T602** 扫描曲面 —— ★★ **入口找到并实现**（轮 486-488）：**`CreateDefinition(swFmRefSurface = 62)`**
  ⇒ `ISweepFeatureData` ⇒ `CreateFeature`（★ 官方 `CreateDefinition.md` 的合法常量表逐字有 `swFmRefSurface (surface sweep)`；
  反射 `_raw/enum_values_sldworks.txt` 给 **62**；★ 而台账给的 `InsertProtrusionSwept4(Surface)` **不是真路**）
  ⚠ **真机未成**：选区已修对（★ `{1:1, 4:1}`，用 `SelectByID2` 带 mark —— ★ **事实 384**），
  而 **A/B 证明实体(17)与曲面(62)在这套前置下**都**卡在 `AccessSelections`**（★ **事实 385**）
- [x] **T603** 放样曲面 ✅ 轮 479 —— 真机 **建成**（★ 关键：`_capture_sketch_ref` **要在草图开着时**取）
- [ ] **T604** 边界曲面 —— ★ **查不到**（`swapi` 里 `IFeatureManager` 无 `Boundary` 成员）⇒ 按铁律 5 记「查不到」
- [ ] **T605** 平面区域 · **T606** 等距曲面 · **T607** 剪裁曲面 —— ★ 未动
- [ ] **T608** 直纹曲面 `InsertRuledSurfaceFromEdge`（★ 真名已核）—— ★ 未动
- [ ] **T609** 替换面 `InsertFeatureReplaceFace`（★ 真名已核）—— ★ 未动
- [ ] **T610** 加厚 `FeatureBossThicken` / 加厚切除 `FeatureCutThicken`（★ 真名已核）—— ★ 未动
  → 验收: 特征树增量 + `sw_surface.collect_surface_evidence` 的曲面体计数
  → 证据: `output/b6b-surface-ref-evidence.json`（1/2 + 旋转子探针 5 组）· `output/sweep-surface-evidence.json` · `output/sweep-ab-evidence.json`

## B7 特征下拉（6 条）

- [x] **T701** 边界框 `Create3DBoundingBox`（★ 真名已核）—— ★ **更正**：官方写明 `Create3DBoundingBox`
  是「**for a cut list item in a weldment part**」⇒ 工具栏那个该用 **`InsertGlobalBoundingBox2`**（★ 与 B8 同批验过）
- [x] **T702** 配合参考 `InsertMateReference2` ✅ 轮 481 —— 真机 **建成**（★ 树新增 `['配合参考', 'MCP_MateRef-<1>', '配合参考___EndTag___']`）
  ⇒ ★ 而**未登记成工具**：第 2 形参是 **`IEntity`（COM 对象）**，`ToolSpec` 的 `Param` 只表达基本类型 ⇒ 留待接声明式选择器
- [x] **T703** 通过参考点的曲线 `InsertCurveFile*` ✅ 轮 481 —— 真机 **建成**（★ 树新增 `曲线1`）· 已是工具 `solidworks_insert_curve_through_points`
- [ ] **T704** 变量阵列 `InsertVaryInstanceIncrement/Override` —— ★ **标 Obsolete** ⇒ 继任者是
  `IInstanceToVaryOptions` + `CreateDefinition`（★ 新架构）⇒ 另列
- [ ] **T705** 分割线 —— ⚠ 真机两条**树无增量**（★ 前置还不够）
- [x] **T706** 投影曲线 ✅ 轮 508 —— ★★ **定性已下（★ 事实 392）**：
  `InsertProjectedSketch2` 标 **Obsolete** ⇒ 继任者是 **`CreateDefinition(swFmRefCurve = 14)`**
  → **`IProjectionCurveFeatureData`**（★ 存在，4 属性 / 7 方法）—— ★ 而它的成员里**有
  `AccessSelections` / `IAccessSelections` / `IAccessSelections2`** ⇒ ★★ **落进「指针族」
  ⇒ 与线性阵列（事实 385）、扫描曲面同族 ⇒ **到不了**（★ 按 A4 不登记成工具）
  → 验收: 特征树增量
  → 证据: `output/b7a-curve-split-evidence.json`（★ 真机 2/4）

## B8 参考几何体（4 条）

- [ ] **T801** 基准面 `InsertRefPlane` · **T802** 坐标系 `InsertCoordinateSystem`
- [ ] **T803** 点 `InsertReferencePoint` · **T804** 质心 `InsertCenterOfMass`
  → 验收: 特征树增量且类型名对

## X 单列（**判不做，写明依据**）

- [x] **TX01** 写 [`docs/toolbar-gaps-backend-limits.md`](../docs/toolbar-gaps-backend-limits.md) ✅ 轮 482 —— ★★ **而核实结果推翻了两条归因**：线性阵列族与结构系统**不是**后端到不了（旧入口 Obsolete、新架构本仓已实现且有 11+3 份真机证据）；只有 `IAccessSelections` 指针族**成立**
  → 验收: 该文件存在，每条带**事实号**与**真机证据路径**，且**不含**「其实可以」的含糊话
- [x] **TX02** 螺柱向导 ✅ 轮 482 —— `InsertStudWizard` 在 `C:\swapi\types\` 的 `IModelDoc2` 与 `IFeatureManager` **两处都查不到** ⇒ ★ 已记「查不到」（铁律 5）
  → 验收: 台账里该条 `tier=待查` 且 `note` 写「官方源查不到」

## W 最终验收（对应 `spec.md` §四）

- [ ] **TW1** 台账可重建（W1） · **TW2** 凡「能」必有真机证据（W2）
- [ ] **TW3** 新模块过签名审计（W3） · **TW4** 判据是树/几何（W4）
- [ ] **TW5** 查不到的写明（W5） · **TW6** 后端口单列（W6）
- [ ] **TW7** `release_check.py` 退出 0（W7）
