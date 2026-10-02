# 官方能力矩阵（capability-matrix）

> 生成日期：2026-09-29 · 轮次 1
> 上游基线：`wzyn20051216/solidworks-automation-skill` @ `8be39ac`（390 文件，MIT）
> 工作副本：`C:\swprojects\sw-skill-fork\`
> **本文档由静态检索与元数据反射生成，未启动 SolidWorks、未执行任何 COM 调用。**

## 〇、本轮的三条覆盖来源与各自效力

| 来源 | 覆盖域 | 本轮核实效力 | 依据 |
|---|---|---|---|
| `C:\swapi` 结构化 markdown | 域 1–12 | ✅ 可用 | 566 类型 / 963 枚举 / 11,557 成员 / 2,839 示例 / 30.3MB |
| CHM `sldworksapi` 册 | 域 1–12 | ✅ 可用 | 11,579 文件，单页 38KB，含 `Syntax` 段，Innovasys 静态格式 |
| CHM `cosworks` 册 | 域 13 | ❌ **空壳，不可作签名源** | 见下 |
| interop DLL 元数据反射 | 域 13–14 | ✅ 唯一可用源 | 7 个程序集，见 §三 |

> ### ⚠ 重大纠正：CHM `cosworks` 册是空壳
>
> 项目文档「已知事实 16」称该册「只覆盖 `ICWLoadsAndRestraintsManager` 一个接口族（34 接口页 + 13 枚举页）」，
> 暗示其内容可用。**本轮核实：该册全部 34 个接口页均为空壳**：
> - 页面正文只有 `Learning Resources / My.SolidWorks / Subscription Services / Loading JS...` 等导航栏文字；
> - 同目录的 `.txt` 伴随文件（`ICWLoadsAndRestraintsManager_members.txt`，502 B）同样只有导航栏；
> - 唯一有内容的文件是页面里指向线上站的 `Analyze_Part_Example_VBNET.txt` 片段。
>
> 根因：该册由新版 JS 模板生成（内容运行时从 help.solidworks.com 拉取），
> 而 `sldworksapi` 册是旧版 Innovasys 静态格式（`hh.exe -decompile` 能拿到完整正文）。
> 这与项目文档 §4.1 警告的「不要爬 help.solidworks.com，爬下来是空壳」是同一个坑，只是这次中招的是**解包产物**。
>
> **后果：cosworks 的 84 个接口签名只能来自反射，没有第二个交叉来源。**

---

## 一、域 1–12 官方接口族全景

来源：`C:\swapi`（`sw_know.py domain <域>`）。数字为该域「入口类型」成员数合计。

| # | 域 | 入口类型数 | 成员合计 | 官方接口族（入口类型） |
|---|---|---|---|---|
| 1 | 应用与会话 | 5 | 1,462 | `ISldWorks`333 · `IModelDoc2`721 · `IModelDocExtension`342 · `ISelectionMgr`62 · `IEnumModelViews`4 |
| 2 | 草图 | 16 | 442 | `ISketchManager`92 · `ISketch`104 · `ISketchSegment`37 · `ISketchLine`12 · `ISketchArc`18 · `ISketchSlot`8 · `ISketchSpline`34 · `ISketchPoint`27 · `ISketchRelation`13 · `ISketchRelationManager`10 · `ISketchContour`11 · `ISketchHatch`21 · `ISketchText`12 · `ISketchPatternFeatureData`31 等 |
| 3 | 零件特征 | 19 | 984 | `IFeatureManager`286 · `IFeature`125 · `ISimpleFilletFeatureData2`70 · `IChamferFeatureData2`29 · `ILinearPatternFeatureData`60 · `ICircularPatternFeatureData`45 · `IMirrorPatternFeatureData`21 · `IShellFeatureData`15 · `IRevolveFeatureData2`28 · `ISweepFeatureData`53 · `ILoftFeatureData`48 · `IRibFeatureData2`16 · `IChainPatternFeatureData`24 · `ICurveDrivenPatternFeatureData`44 |
| 4 | 孔与螺纹 | 11 | 244 | `IWizardHoleFeatureData2`75 · `IAdvancedHoleFeatureData`10 · `ISimpleHoleFeatureData2`30 · `IHoleSeriesFeatureData2`27 · `IHoleStandardsData`4 · `IHoleTable`19 · `IAdvancedHoleElementData`13 · `IStraightTapElementData`7 · `ITaperedTapElementData`5 · `IThreadFeatureData`35 · `ICosmeticThreadFeatureData`19 |
| 5 | 钣金 | 18 | 388 | `ISheetMetalFeatureData`23 · `IBaseFlangeFeatureData`53 · `IEdgeFlangeFeatureData`42 · `IOneBendFeatureData`33 · `ISketchedBendFeatureData`16 · `IHemFeatureData`18 · `IMiterFlangeFeatureData`24 · `ISweptFlangeFeatureData`31 · `IGussetFeatureData`18 · `ISMGussetFeatureData`30 · `IDraftFeatureData2`24 · `ILoftedBendsFeatureData`18 · `ISurfaceCutFeatureData`12 |
| 6 | 焊件 | 14 | 170 | `IStructureSystemFolder`4 · `IStructureSystemMemberFeatureData`10 · `IStructureSystemMemberProfile`17 · `IStructureSystemSplitMember`8 · `IProfileCenterMateFeatureData`5 · `IWeldmentCutListFeature`10 · `IWeldBead`3 · `IWeldmentBeadFeatureData`18 · `ICosmeticWeldBeadFeatureData`26 · `IWeldSymbol`45 · `IWeldmentTrimExtendFeatureData`12 |
| 7 | 曲面 | 13 | 237 | `ISurface`82 · `ISurfaceTrimFeatureData`12 · `ISurfaceExtendFeatureData`18 · `ISurfaceKnitFeatureData`14 · `ISurfaceFlattenFeatureData`10 · `ISurfaceOffsetFeatureData`13 · `ISurfaceCutFeatureData`12 · `ISurfaceRadiateFeatureData`11 · `IFillSurfaceFeatureData`23 · `ISurfacePlanarFeatureData`7 · `ISurfRevolveFeatureData`7 · `IShutOffSurfaceFeatureData`16 ⚠ **这 13 个是「编辑既有特征」用的定义对象，不是创建入口，见下方 §一注** |
| 8 | 装配 | 24 | 537 | `IAssemblyDoc`196 · `IComponent2`165 · `IEnumComponents2`4 · `IMate2`33 · `IMateEntity2`7 · `IMateFeatureData`2 · `IMateInPlace`5 · `IMateReference`8 · `IExplodeStep`25 · `IPartExplodeStep`8 · `IMirrorComponentFeatureData`25 · `ICoincidentMateFeatureData`3 · `IConcentricMateFeatureData`4 · `IDistanceMateFeatureData`7 |
| 9 | 工程图 | 21 | 1,456 | `IDrawingDoc`274 · `IView`461 · `IView3D`13 · `ISheet`53 · `IDimension`52 · `IDisplayDimension`141 · `IAnnotation`101 · `IAnnotationView`17 · `ITableAnnotation`85 · `IModelView`75 · `IModelViewManager`42 · `ISectionViewData`35 · `IBomTableAnnotation`25 · `IHoleTableAnnotation`2 · `IWeldmentCutListAnnotation`7 · `IBendTableAnnotation`1 · `IRevisionTableAnnotation`16 · `IDimensionTolerance`23 · `IMultiJogLeader`12 · `IDrawingComponent`19 |
| 10 | 几何与拓扑 | 15 | 667 | `IBody2`220 · `IFace2`120 · `IEdge`47 · `IVertex`18 · `ICurve`68 · `ISurface`82 · `ILoop2`29 · `IEnumBodies2`4 · `IBoundingBoxFeatureData`10 · `IBoundaryBossFeatureData`36 · `ICenterOfMass`6 · `IMidSurface3`23 · `IEdgePoint`4 ⚠`ISeam2`/`IFeatureRef` **本机库无** |
| 11 | 质量属性与导出 | 7 | 712 | `IMassProperty2`18 · `IMassPropertyOverrideOptions`13 · `ICenterOfMass`6 · `IModelDocExtension`342 · `ISldWorks`333 ⚠`ISaveAsOptions`/`ISaveAsInfo` **本机库无** |
| 12 | 配置/材料/自定义属性 | 8 | 1,006 | `IConfiguration`82 · `IConfigurationManager`21 · `ICustomPropertyManager`26 · `IDesignTable`40 · `IMaterialVisualPropertiesData`8 · `IRenderMaterial`103 · `ITextAndCustomProperty`5 · `IModelDoc2`721 |

**域 1–12 合计：157 个入口类型 · 8,131 个成员（去重前，含跨域重复的 `IModelDoc2`/`ISldWorks`/`ISurface`）**

### 跨域复用的核心类型

| 类型 | 出现在 | 说明 |
|---|---|---|
| `IModelDoc2` | 域 1、12（全域底座 721 成员） | 所有建模动作的落点 |
| `IModelDocExtension` | 域 1、11（342） | 质量属性 / 导出 / 外部引用 |
| `ISldWorks` | 域 1、11（333） | 应用级开关 |
| `ISurface` | 域 7、10（82） | 曲面与拓扑共用 |
| `ICenterOfMass` | 域 10、11（6） | 几何查询与质量属性共用 |

### `sw_know.py verify` 报出的缺口

| 域 | 缺失 | 判定 |
|---|---|---|
| 几何与拓扑 | `ISeam2`、`IFeatureRef` | **未查证**是官方真缺席还是本机库未收录。`sw_know suggest` 对 `ISeam2` 给出的是 `IFeature`/`IBomFeature`/`IFeatureFolder`，对 `IFeatureRef` 给出 `IAdvancedSaveAsOptions` 等，均非近似命中 → 按铁律 5 记「查不到」，不臆造 |
| 质量属性与导出 | `ISaveAsOptions`、`ISaveAsInfo` | 同上。suggest 给 `IAdvancedSaveAsOptions`/`IBalloonOptions`/`IStackedBalloonOptions`，非同类 → 记「查不到」 |
| 配置/材料/自定义属性 | `swCustomPropertyType_e`、`swMaterialPropertyValues_e` | 枚举缺失。suggest 给出的近似名均语义不同 → 记「查不到」 |
| 仿真（域 13） | `ICWModelDoc`/`ICWResults`/`ICWStudyManager`/`ICWStudy`/`ICWBeam`/`ICWPressure` 等 | **已定位根因**：`C:\swapi` 只收录 12 个程序集，不含 `cosworks`。这些类型在 DLL 里存在（见 §二） |

---

### 域 7 的创建入口纠正（本轮新增）

| 项 | 结论 |
|---|---|
| 入口对象 | `ISldWorks.GetModeler()` → `Object`（即 `IModeler`，123 成员 / 123 方法） |
| 指针版 | `ISldWorks.IGetModeler()` → `Modeler`，**属官方限定的进程内非托管 C++ 接口，pywin32 迟到绑定不可用**，不收录 |
| 创建方法 | **19 个非指针 `Create*Surface`**：`CreatePlanarSurface(2)` · `PlanarSurface2(3)` · `CylindricalSurface(3)` · `CylindricalSurface2(4)` · `SphericalSurface(2)` · `SphericalSurface2(4)` · `ConicalSurface(4)` · `ConicalSurface2(5)` · `ToroidalSurface(5)` · `OffsetSurface(2)` · `ExtrusionSurface(2)` · `RevolutionSurface(4)` · `RuledSurface(3)` · `SweptSurface(2)` · `BsplineSurface(4)` · `CoonsBSurface(5)` · `SheetFromSurface(2)` · `LoftSurface(18)` · `RuledSurfaceFromEdge(14)` |
| 落盘清单 | `_raw/reflect_sldworks/iface_sldworks.txt` → `## IModeler` 段 |
| 实现 | `scripts/sw_surface.py`（19 个登记 + 14 个薄封装） |

> ### ⚠ 为什么上面 §一 域 7 那 13 个 `*FeatureData` 不是入口
>
> 对 `sldworks.dll` 全部 **1032 个接口**做扫描，查找「返回这 13 个类型」的方法：
> **一个都没有。** 它们只能由 `IFeature.GetDefinition()` 在编辑既有特征时取得。
>
> ⇒ 靠接口名里的 `FeatureData` 三个字推断入口，会把人带偏一整轮。
> **接口叫什么不重要，谁返回它才决定它是不是入口。**

---

## 二、域 13 仿真（Simulation）—— 只能靠反射

来源：`SolidWorks.Interop.cosworks.dll` 纯元数据反射（`Assembly.LoadFrom().GetTypes()`，未实例化任何 COM 对象）。

| 程序集 | 公开类型条目 | 枚举 | 成员 | 落盘清单 |
|---|---|---|---|---|
| `cosworks` | **168** | **363** | 3,224 | `_raw\reflect\iface_cosworks.txt` / `enum_cosworks.txt` |
| `SWRoutingLib` | 28 | 26 | 170 | `iface_SWRoutingLib.txt` / `enum_SWRoutingLib.txt` |
| `sldcostingapi` | 28 | 24 | 410 | `iface_sldcostingapi.txt` / `enum_sldcostingapi.txt` |
| `fworks`（Toolbox） | 2 | 10 | 7 | `iface_fworks.txt` / `enum_fworks.txt` |
| `sustainability` | 18 | 8 | 136 | `iface_sustainability.txt` / `enum_sustainability.txt` |
| `swdocumentmgr`（PDM） | **296** | 65 | 4,683 | `iface_swdocumentmgr.txt` / `enum_swdocumentmgr.txt` |
| `swmotionstudy` | 20 | 5 | 196 | `iface_swmotionstudy.txt` / `enum_swmotionstudy.txt` |

### 168 的口径问题（待查证）

反射的 168 条目中，`ICW*` 与 `CW*` 成对出现（如 `ICWStudy` / `CWStudy`），
即 **84 个接口族 + 84 个对应 coclass**。项目文档「168 接口」与本表数字同源，但语义上应理解为 84 个接口族。

**成员数 3,224 与项目文档记载的 9,281 不符。** 差异来源**未查证**——
本轮的统计口径是 `接口.GetMembers().Count`，可能未展开继承成员或未计入 coclass 侧成员。
按铁律 5，此处不猜测。**待办**：换 `GetMethods(DeclaredOnly)` / `GetMembers(DeclaredOnly)` 复算，或用 C# 侧 `tlbimp` 交叉核对。

### 接口族归类（按 84 个 `ICW*` 接口）

| 接口族 | 代表接口 | 能力 |
|---|---|---|
| 入口 / 文档 | `ICosmosWorks`、`ICWModelDoc` | 加载项 → 应用 → 文档 |
| 研究管理 | `ICWStudyManager`、`ICWStudy` | 建/复制/重命名/转换研究；网格；求解；结果 |
| 研究选项 | `ICWStaticStudyOptions`、`ICWFrequencyStudyOptions`、`ICWBucklingStudyOptions`、`ICWNonLinearStudyOptions`、`ICWDynamicStudyOptions`、`ICWFatigueStudyOptions`、`ICWDropTestStudyOptions`、`ICWThermalStudyOptions`、`ICWTopologyStudyOptions`、`ICWCompositeShellOptions` | 各研究类型参数 |
| 载荷与夹具 | `ICWLoadsAndRestraintsManager`、`ICWLoadsAndRestraints`、`ICWLoadCaseManager` | **载荷/夹具施加（本域核心）** |
| 载荷实体 | `ICWForce`、`ICWPressure`、`ICWTemperature`、`ICWHeatFlux`、`ICWHeatPower`、`ICWConvection`、`ICWRadiation`、`ICWGravity`、`ICWCWCentriFugalForce`、`ICWCentriFugalForce`、`ICWRemoteLoad`、`ICWDistributedMass`、`ICWRestraint`、`ICWBaseExcitation` | 具体载荷类型 |
| 连接件 | `ICBearingConnector`… 实际为 `ICWBearingConnector`、`ICBoltConnector`、`ICWEdgeWeldConnector`、`ICWElasticConnector`、`ICWLinkConnector`、`ICWPinConnector`、`ICWRigidConnector`、`ICWSpotWeldConnector`、`ICWSpringConnector`、`ICWGeneralSpringConnector`、`ICWJoints`、`ICWLinkageRod` | 11 类连接件 |
| 网格 | `ICWMesh`、`ICWMeshControl` | 网格生成与控制 |
| 结果与后处理 | `ICWResults`、`ICWPlot`、`ICWResultsProbeManager`、`ICWTrendTracker`、`ICWRunStudiesResults`、`ICWRunSpecStudiesRunMeshOptions` | 结果读取、图表、探针、趋势 |
| 拓扑优化 | `ICWTopologyStudyManager` + 10 个 `ICWTopology*` 约束/控制接口 | 拓扑优化约束与目标 |
| 接触 | `ICWContactManager`、`ICWContactSet`、`ICWContactComponent`、`ICWMultipleContactSetsEditManager`、`ICWMultipleComponentContactsEditManager` | 接触与接触对 |
| 材料/质量属性 | `ICWMaterial`、`ICWMassPropertiesManager` | 仿真材料、质量 |
| 几何体 | `ICWSolidManager`、`ICWSolidBody`、`ICWSolidComponent`、`ICWShellManager`、`ICWShell`、`ICWBeamManager`、`ICWBeamBody` | 网格体/壳/梁管理 |
| 疲劳/跌落 | `ICWFatigueEvent`、`ICWDropTestSetup`、`ICWDropTestResultOptions` | 疲劳事件与跌落测试 |
| 阻尼/复合 | `ICWDampingOptions`、`ICWCable`、`ICWSolidComponent` | 阻尼、复合层、线缆 |
| 回调 | `ICwAddincallback` | 加载项回调 |

### `ICWLoadsAndRestraintsManager` 签名全表（反射，权威）

```
CWForce          AddForce(Int32, Object, Object, Int32&)
CWForce          AddForce2(Int32, Int32, Object, Object, Int32&)
CWForce          AddForce3(Int32, Int32, Int32, Int32, Int32, Int32, Object, Object, Boolean, Boolean,
                           Int32, Int32, Int32, Double, Object, Boolean, Boolean, Object, Object, Boolean, Int32&)
CWRestraint      AddRestraint(Int32, Object, Object, Int32&)
CWDynamicInitialCondition AddInitialConditionForDynamicStudy(Int32, Int32, Object, Object, Int32, Int32, Double, Int32, Double, Int32, Double, Int32&)
CWDynamicInitialCondition AddInitialConditionForDynamicStudy2(Int32, Int32, Object, Object, Int32, Boolean, Double, Boolean, Double, Boolean, Double, Int32&)
Int32            CopyLoadsAndRestraintsToStudy(String, Object)
```

CHM 册里另有 28 个 `Add*` 方法页（`AddBearingLoad`/`AddBoltConnector`/`AddConvection`/`AddPressure`/`AddRemoteLoad`/`AddSpringConnector`/`AddTemperature`/…），
**但如 §〇 所述这些页面无正文**，其签名**查不到**，本轮未纳入上表。
⇒ 这是 cosworks 域的**真实覆盖缺口**：34 个载荷/连接件方法中，7 个有反射签名，27 个无签名来源。

---

## 三、域 14 路由 / Composer / PDM / Toolbox

| 域 | 程序集 | 接口 | 落盘 | 本机安装情况 |
|---|---|---|---|---|
| Routing | `SWRoutingLib` | 28 | ✅ | 未安装（无实体路由产品） |
| Costing | `sldcostingapi` | 28 | ✅ | 已装但宿主绑定 |
| PDM | `swdocumentmgr` | 296 | ✅ | 需 PDM 许可证 |
| Sustainability | `sustainability` | 18 | ✅ | 需 Sustainability 许可证 |
| Toolbox / Foundry | `fworks` | 2 | ✅ | 无本体 API，仅 2 接口 |
| Composer | — | — | ❌ **无独立程序集** | `fworks` 即其载体 |

> 域 14 的 5 个程序集在 `C:\swapi` 中**完全没有收录**（`sw_know.py verify` 报缺失），
> 官方来源只有反射一条。这些域**全部标记为「需许可证 + 本机不可达」**，
> 按铁律 2 只能做**签名级**能力声明，不能声称可执行。

---

## 四、随附落盘物

```
D:\AI\SW\_raw\
  domain_01..14_*.txt          14 域入口类型与关键枚举
  swapi_verify.txt             功能域地图校验（含各域缺失项）
  swapi_stats.txt              规模总览
  swapi_domain_list.txt        14 域清单
  reflect\iface_*.txt          7 程序集接口签名清单（<返回> <方法>(<参数类型>, ...)）
  reflect\enum_*.txt           7 程序集枚举取值清单
  chm_cosworks\*.txt           47 页（⚠ 全为空壳，见 §〇）
  audit_batch1_simulation.md   首批签名比对结果（16 项）
D:\AI\SW\tools\reflect-interop.ps1   反射脚本（可复跑）
```
