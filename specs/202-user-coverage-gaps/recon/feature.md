<!-- domain: 特征 -->

# 特征域 · 官方成员/签名/例子/本仓现状 逐字抄录

来源：`C:\swapi\types\`（递归找 `<成员名>.md`）、`C:\swapi\examples\`（文件名含成员名）、
`D:\AI\SW\scripts\` 与 `D:\AI\SW\mcp-server\`（grep 成员名）。

| 功能 | 官方成员 | 签名 | 官方例子 | 本仓现状 | 指针族 |
|---|---|---|---|---|---|
| 组合相交 | `InsertCombineFeature` | `**Signature**: ` + "`Feature InsertCombineFeature( System.int OperationType, Body2 MainBody, System.object ToolVar )`" | 无 | `scripts\sw_api_sldworks.py:4352`（另 `:7370` `:21109` `:24097`） | — |
| 缩放变形 | `InsertScale` | `**Signature**: ` + "`Feature InsertScale( System.short Type, System.bool Uniform, System.double Xscale, System.double YScale, System.double ZScale )`" | 无 | `scripts\sw_api_sldworks.py:4438`（另 `:5721` `:6339` `:21195` `:22458` `:23076`）；第二候选 `IScaleFeatureData`：`scripts\sw_api_sldworks.py:450`（另 `:7931` `:15147` `:24638`） | — |
| 加厚 | 官方没写（`InsertThickenFeature`、`FeatureThicken` 在 `C:\swapi\types\` 下均无 .md） | 官方没写 | 无 | 无（两候选在 `scripts\` 与 `mcp-server\` 均 0 命中） | 官方没写（无 md 可搜） |
| 孔向导 | `HoleWizard5` | `**Signature**: ` + "`Feature HoleWizard5( System.int GenericHoleType, System.int StandardIndex, System.int FastenerTypeIndex, System.string SSize, System.short EndType, System.double Diameter, System.double Depth, System.double Length, System.double Value1, System.double Value2, System.double Value3, System.double Value4, System.double Value5, System.double Value6, System.double Value7, System.double Value8, System.double Value9, System.double Value10, System.double Value11, System.double Value12, System.string ThreadClass, System.bool RevDir, System.bool FeatureScope, System.bool AutoSelect, System.bool AssemblyFeatureScope, System.bool AutoSelectComponents, System.bool PropagateFeatureToParts )`" | 无 | `scripts\sw_hole_features.py:692`（另 `:960` `:1049` `:1050` `:1051` `:1092` `:1133` `:1142`）、`scripts\sw_api_sldworks.py:4349`、`scripts\sw_part.py:1074`、`mcp-server\tool_specs_batch34.py:32`、`mcp-server\tool_specs_batch57.py:15`（另 `:40`） | — |
| 边界凸台 | `InsertProtrusionBlend2` | `**Signature**: ` + "`Feature InsertProtrusionBlend2( System.bool Closed, System.bool KeepTangency, System.bool ForceNonRational, System.double TessToleranceFactor, System.short StartMatchingType, System.short EndMatchingType, System.double StartTangentLength, System.double EndTangentLength, System.bool StartTangentDir, System.bool EndTangentDir, System.bool IsThinBody, System.double Thickness1, System.double Thickness2, System.short ThinType, System.bool Merge, System.bool UseFeatScope, System.bool UseAutoSelect, System.int GuideCurveInfluence )`" | 无 | `scripts\sw_loft.py:14`（另 `:33` `:41` `:65` `:87` `:130` `:207` `:218`）、`scripts\sw_api_sldworks.py:4426`（另 `:5708` `:6325` `:21183` `:22445` `:23062`）、`scripts\sw_surface_ref_ops.py:21`、`scripts\sw_sweep.py:143`、`mcp-server\tool_specs_batch47.py:16`（另 `:38`） | — |
| 曲线驱动阵列 | 官方没写（`InsertCurveDrivenPattern` 在 `C:\swapi\types\` 下无 .md；`ICurveDrivenPatternFeatureData` 亦无 .md） | 官方没写 | 无 | `InsertCurveDrivenPattern`：无；`ICurveDrivenPatternFeatureData`：`scripts\sw_pattern.py:9`（另 `:21` `:34` `:151` `:314` `:355`）、`scripts\sw_api_sldworks.py:171`（另 `:2925` `:11172` `:17720` `:19818`） | 官方没写（无 md 可搜） |

## 补充事实（逐条抄录，不改写）

### 各候选成员的 md 落点（`C:\swapi\types\` 递归搜结果）

- `InsertCombineFeature.md` → `C:\swapi\types\IFeatureManager\InsertCombineFeature.md`（存在）
- `InsertScale.md` → `C:\swapi\types\IFeatureManager\InsertScale.md` **与** `C:\swapi\types\IModelDoc2\InsertScale.md`（两处都存在）
- `IScaleFeatureData.md` → 不存在
- `InsertThickenFeature.md` → 不存在
- `FeatureThicken.md` → 不存在
- `HoleWizard5.md` → `C:\swapi\types\IFeatureManager\HoleWizard5.md`（存在）
- `HoleWizard4.md` → `C:\swapi\types\IFeatureManager\HoleWizard4.md`（也存在，但候选清单里 `HoleWizard5` 在前，按「第一个存在的」取 `HoleWizard5`）
- `InsertProtrusionBlend2.md` → `C:\swapi\types\IFeatureManager\InsertProtrusionBlend2.md` **与** `C:\swapi\types\IModelDoc2\InsertProtrusionBlend2.md`（两处都存在）
- `InsertCurveDrivenPattern.md` → 不存在
- `ICurveDrivenPatternFeatureData.md` → 不存在

### 同名成员在另一接口下的签名（逐字照抄，上表未采用的那一份）

- `C:\swapi\types\IModelDoc2\InsertScale.md`
  `**Signature**: ` + "`void InsertScale( System.double ScaleFactor_x, System.double ScaleFactor_y, System.double ScaleFactor_z, System.bool IsUniform, System.int ScaleType )`"
- `C:\swapi\types\IModelDoc2\InsertProtrusionBlend2.md`
  `**Signature**: ` + "`void InsertProtrusionBlend2( System.bool Closed, System.bool KeepTangency, System.bool ForceNonRational )`"

### `AccessSelections` 全文搜索结果（逐个 md 全文搜一次）

| md | 结果 |
|---|---|
| `IFeatureManager\InsertCombineFeature.md` | 无 |
| `IFeatureManager\InsertScale.md` | 无 |
| `IModelDoc2\InsertScale.md` | 无 |
| `IFeatureManager\HoleWizard5.md` | 无 |
| `IFeatureManager\HoleWizard4.md` | 无 |
| `IFeatureManager\InsertProtrusionBlend2.md` | 无 |
| `IModelDoc2\InsertProtrusionBlend2.md` | 无 |

⇒ 四个拿到 md 的功能全部是 `—`，没有 `⚠ 指针族`。

### `C:\swapi\examples\` 文件名搜索结果

按「文件名含成员名」逐个搜，`InsertCombineFeature` / `InsertScale` / `IScaleFeatureData` /
`HoleWizard5` / `InsertProtrusionBlend2` / `InsertCurveDrivenPattern` / `ICurveDrivenPatternFeatureData`
在 `C:\swapi\examples\`（共 2839 个文件）下**文件名 0 命中** ⇒ 官方例子栏全部写「无」。

事实补充（文件名里是关键词、不是成员名，未计入上表）：
`Combine_Assembly_Components_into_Part_Example_VB.md`、`Combine_Bodies_Example_CSharp.md`、
`Combine_Bodies_Example_VB.md`、`Combine_Bodies_Example_VBNET.md`、
`Create_Thicken_Feature_Example_VB.md`、`Thicken_Sheet_Body_Example_VB.md`、
`Thicken_Surface_and_Generate_Boss_Example_CSharp.md`、`Thicken_Surface_and_Generate_Boss_Example_VB.md`、
`Thicken_Surface_and_Generate_Boss_Example_VBNET.md`。

### grep 范围说明

`D:\AI\SW\scripts\` 与 `D:\AI\SW\mcp-server\` 下的 `__pycache__\*.pyc` 二进制缓存也命中同样成员名，
属构建产物，上表「本仓现状」栏**只列源码 `.py` 行号**。

### 未做的事

未跑 SolidWorks，未跑 pytest，未改动任何已有文件。