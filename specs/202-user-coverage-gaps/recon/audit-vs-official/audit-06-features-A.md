# audit-06 · 域 `06-features` · 核对 A（签名一致性）

**范围**：域 `06-features` ∩ 核对 A（实参个数 / 顺序 / 明显类型 与官方 Signature 形参表并排数）
**我方文件**：`scripts/sw_part.py` · `scripts/sw_feature_entry_ops.py` · `scripts/sw_feature_readback.py`（三份都在，无替代）
**官方源**：`C:\swapi\types\<接口>\<成员>.md` 的 `**Signature**` 行 · `C:\swapi\examples\*.md` 的调用序 · `C:\swapi\enums\*.md` · 出厂类型库反射 `D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt`
**纪律**：只报「两段原文对不上」；给不出两段的不写；不下结论、不给建议。

---

## 表

| # | 我们的原文（文件 + 片段） | 官方的原文（文件 + 片段） | 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | `scripts/sw_part.py`（`sketch_slot`）：<br>`return model.SketchManager.CreateSketchSlot(`<br>`    0,  # swSketchSlotCreationType_e: 0=Straight`<br>`    radius, radius,  # 宽度` | ① `C:\swapi\types\ISketchManager\CreateSketchSlot.md`：<br>`**Signature**: `SketchSlot CreateSketchSlot( System.int SlotCreationType, System.int SlotLengthType, System.double Width, ...``<br>② `C:\swapi\examples\Insert_and_Resize_Sketch_Slot_Example_VB.md`：<br>`Set swSketchSlot = skManager.CreateSketchSlot(swSketchSlotCreationType_e.swSketchSlotCreationType_line, swSketchSlotLengthType_e.swSketchSlotLengthType_CenterCenter, 0.05, -0.05, 0, 0, 0.05, 0, 0, 0, 0, 0, 1, False)`<br>③ 出厂类型库反射 `D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt`：<br>`SketchSlot CreateSketchSlot(Int32, Int32, Double, Double, Double, Double, Double, Double, Double, Double, Double, Double, Int32, Boolean)` | 第 2 个形参 `SlotLengthType` 官方三处一致声明为**整数/枚举**（`System.int` / `swSketchSlotLengthType_e.swSketchSlotLengthType_CenterCenter` / `Int32`），我方把**同一个浮点长度值 `radius`** 同时喂给了第 2 位与第 3 位（`Width` 才是 `System.double`）—— 实参类型与形参类型不符（实参个数 14 = 形参个数 14，**不符点在类型不在个数**）。 | 高 |

---

## 核对覆盖（逐点数的，不含"看起来没问题"的推断）

| 文件 | 核了的调用点数 | 其中 |
|---|---|---|
| `scripts/sw_part.py` | 52 | `SelectByID2`(9/9) · `Select2`(2/2) · `Select3`(3/3) · `Select4`(2/2) · `ClearSelection2`(1/1) · `InsertSketch`(1/1) · `FeatureByName`(1/1) · `ActiveSketch`(0) · `GetFeature`/`GetSketchContours`/`GetSketchRegions`/`GetSketchSegments`(0) · `CreateLine`(6/6) · `CreateCenterRectangle`(6/6) · `CreateCornerRectangle`(6/6) · `CreateCircleByRadius`(4/4) · `CreateArc`(10/10) · `CreatePolygon`(8/8) · `CreateSketchSlot`(14/14，类型见 #1) · `CreateSpline2`(2/2) · `GetStartPoint2`/`GetEndPoint2`(0) · `AutoDimension2`(5/5) · `GraphicsRedraw2`(0) · `AddDimension2`(3/3) · `SketchAddConstraints`(1/1) · `FeatureExtrusion3`(23/23，两处) · `FeatureCut4`(27/27) · `FeatureRevolve2`(20/20，两处) · `FeatureFillet`(7/7) · `InsertFeatureChamfer`(8/8) · `FeatureLinearPattern3`(10/10，两处) · `FeatureCircularPattern4`(7/7) · `InsertFeatureShell`(2/2) · `InsertMirrorFeature2`(5/5) · `InsertRib`(10/10) · `GetBodies2`(2/2) · `GetBodyBox`(0) · `CreateEllipse`(9/9) · `CreateCenterLine`(6/6) · `InsertDome`(3/3) · `InsertCompositeCurve`(0) · `GetActiveSketch2`(0) · `InsertAxis2`(1/1) · `GetSpecificFeature2`(0) |
| `scripts/sw_feature_readback.py` | 8 | `FirstFeature`(0) · `Name`(0) · `GetTypeName2`(0) · `GetNextFeature`(0) · `Extension`(0) · `GetWhatsWrongCount`(0) · `GetWhatsWrong`(3/3) · `EditRebuild3`(0) |
| `scripts/sw_feature_entry_ops.py` | 16 | `GetBodies2`(2/2，三处) · `GetFaces`(0，两处) · `GetEdges`(0，两处) · `GetSurface`(0) · `IsCylinder`(0) · `ClearSelection2`(1/1，三处) · `GetStartVertex`/`GetEndVertex`(0) · `InsertCosmeticThread3`(7/7) · `FeatureBossThicken`(7/7) · `FeatureCutThicken`(6/6) · `InsertFlattenSurface2`(2/2) |
| **合计** | **76** | — |

**"两源不一致"记录（本轮 0 条）**：本轮核到的每个成员，`C:\swapi\types\*.md` 的 Signature 与出厂类型库反射的**参数个数都相同**，未出现「文档 7 个 / 类型库 14 个」那类分歧（`FeatureFillet` 在两源都是 7 个；反射里的 `FeatureFillet3` 14 个是**另一个成员**）。

**"查不到"记录**：`ISketch\GetFeature.md` 在 `C:\swapi\types\` 下**不存在**（同族 `IBodyFolder\GetFeature.md` 等在，`ISketch\` 下没有）⇒ 我方 `sw_part.py` 里 `_safe_com_member(sketch_obj, "GetFeature")` **在本机两套离线源里查不到对应页**；本轮无官方原文可比 ⇒ 不计入表内。

---

核了 **76** 处 · 报 **1** 条 · 置信度为高的是 **第 1 条**（`CreateSketchSlot` 第 2 实参类型不符）。