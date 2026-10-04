# 官方源里的**错拼名 → 正确名**表（★ T3-2：554 条 `spelling` 的机械复核）

> 生成物 —— 由 `tools/t3_2_spelling_pairs.py` 产出，不要手改。
> 输入：`specs/203-bunny-sideline-batches/recon/b2-defects.json`（另一个对话的 B2 扫描，只读复用）
> + 本机 `C:\swapi\types`（566 接口目录）与 `C:\swapi\enums`（枚举页）。

## 一 · 口径

| 项 | 值 |
|---|---|
| 本机真名集合 | **1529**（接口目录 + 枚举页）|
| 已核验 `spelling` | **554** 条（★ 其总数 554）|
| ★ 本表配对出 | **130** 对「错拼 → 正确名」|

★★ 本表「不算什么」：

- ★ 判据是**编辑距离 ≤2 且长度差 ≤2** —— ★ 这是**启发式**，不是官方裁定；
  ★ 若两个真名都很近，本表只取**最近的**一个 ⇒ ★ **可能有歧义未标**（需人核）；
- ★ 配不上对的名字**不在本表里**（★ 它们可能是：名字根本没拼错、或错得太多没法猜）⇒ ★ **不要**读成「本表就是全部错拼」✓；
- ★ 来源是另一个对话的 `conditional_pass` 产出 ✓

## 二 · ★ 真错拼（★ 照它写就一定失败的那种）

| 错拼 | ★ 正确名 | 编辑距离 | 官方源的解释 |
|---|---|---:|---|
| `IAVIParamter` | `IAVIParameter` | 1 | 同一页 See Also 两种拼法：IAVIParamter（漏字母 e）vs IAVIParameter；types 目录下无 IAVIParamter。 |
| `IAsemblyDoc` | `IAssemblyDoc` | 1 | 同一族两页指向同一接口，a 少一个 s（IAsemblyDoc）。C:\swapi\types 下只有 IAssemblyDoc，无 IAsemblyDoc。 |
| `IAttrbute` | `IAttribute` | 1 | 同一接口名在同族两页两种拼法：IFindAttribute 页写成 IAttrbute（少一个 i），FindAttribute 页为 IAttribute；IFindAttribute.md 自身其 |
| `IAutoBalloonOption` | `IAutoBalloonOptions` | 1 | 接口名写成 IAutoBalloonOption（少 s），同目录其余 19 页一律 IAutoBalloonOptions；C:\swapi\types\IAutoBalloonOption 不存在 |
| `IAutoBalloonOptons` | `IAutoBalloonOptions` | 1 | 接口名写成 IAutoBalloonOptons（少 i），同族页写 IAutoBalloonOptions；C:\swapi\types\IAutoBalloonOptons 不存在。 |
| `IBreakline` | `IBreakLine` | 1 | 同一页内接口名两种拼法：IBreakLine（大写 L）与 IBreakline（小写 l）；目录实名为 IBreakLine。同族 SetPosition.md / Orientation.md 共 |
| `ICThreadFeatureData` | `IThreadFeatureData` | 1 | 同一成员在同族被写成两种拼法：GetTransformsPatternedCount 与 GetPatternedTransformsCount；后者才是实际存在的成员页。 |
| `ICenterline` | `ICenterLine` | 1 | 同一接口两种链接拼法 [[ICenterLine::GetNext]] 与 [[ICenterline::GetNext Method]]；IGetCenterLines.md:27 同。 |
| `IChainPatterneatureData` | `IChainPatternFeatureData` | 1 | 接口名被拼坏成 IChainPatterneatureData（Feature→Patterneature）。同族 AccessSelections.md 标题是正确名；types 下无 IChain |
| `ICommandManger` | `ICommandManager` | 1 | 接口名少一个 a：ICommandManger。全仓库 types 下无该目录；同族其余 20 余条链接一律 ICommandManager。 |
| `IConfigurationt` | `IConfiguration` | 1 | 同族同成员在两页被写成两种拼法：GetParent 页把接口名写成 IConfigurationt（多一个 t），GetChildren 页为 IConfiguration；IConfiguratio |
| `ICoordinateSsystemFeatureData` | `ICoordinateSystemFeatureData` | 1 | 同一接口的 Y 轴页把接口名写成 ICoordinateSsystemFeatureData（双 s），X/Z 轴同族页均为 ICoordinateSystemFeatureData。该页 6 条 S |
| `ICurveDrivePatternFeatureData` | `ICurveDrivenPatternFeatureData` | 1 | 同族 _overview 讲的是同一条前置条件却写对了接口名 ICurveDrivenPatternFeatureData；D1FaceNormal 页少 n 写成 ICurveDrivePatter |
| `IDisplayDimensioin` | `IDisplayDimension` | 1 | 同一接口名在本族两页拼成两种：SetArcLengthLeader.md 把 IDisplayDimension 字母顺序写反成 IDisplayDimensioin（i-o-i-n），GetAuto |
| `IDrawinDoc` | `IDrawingDoc` | 1 | 同一句内 IDrawingDoc 与 IDrawinDoc 两种拼法（IDrawinDoc 少一个 g）。已核：C:\swapi\types\IDrawingDoc 目录存在，C:\swapi\typ |
| `IDrawngDoc` | `IDrawingDoc` | 1 | 同一 See Also 构造，CreateSectionView.md 整块 14 条链接把接口名写成 IDrawngDoc（ing/ng 字母换位）；同族页面一律是 IDrawingDoc。 |
| `IEdgeFlangeFeaturData` | `IEdgeFlangeFeatureData` | 1 | 同一接口页内接口名少了 e（Featur/Feature）。同页 L26 仍写 [[IEdgeFlangeFeatureData Interface]]，且 types\IEdgeFlangeFeat |
| `IEdgeflangeFeatureData` | `IEdgeFlangeFeatureData` | 1 | 同一接口里同一成员出现两种拼法：小写 f（flange）+ 漏字母（Postion）。PositionOffsetType.md 存在而 PostionOffsetType.md 不存在 → 死链。 |
| `IEquationaMgr` | `IEquationMgr` | 1 | 同族两页同一句，Add2 写成 IEquationaMgr（多一个 a）。已全库搜索 C:\swapi：不存在任何 IEquationaMgr 文件，该链接必为死链。 |
| `IExtrudedFeatureData2` | `IExtrudeFeatureData2` | 1 | 接口名两拼：IExtrudedFeatureData2（多一个 d）/ IExtrudeFeatureData2。本页 frontmatter 与标题都是 IExtrudeFeatureData2；实 |
| `IFace` | `IFacet` | 1 | 同一页 Obsolete 继承句里同一接口两种拼法：IFace::GetTessTriStripNorms 少末尾 2，其余 11 个链接均为 IFace2::。types 下只有 IFace2 目录 |
| `IFaces2` | `IFace2` | 1 | 同族两页同一接口两种拼法：GetEdges.md 与 IGetEdges.md 正文把 IFace2::EnumEdges 写成 IFaces2::EnumEdges（多一个 s），而同句后半段与另页 |
| `IFae2` | `IFace2` | 1 | 同一页 See Also 写 IFae2（c 写成 a），同页 Remarks 写 IFace2。无 IFae2 目录；GetAllDecalProperties.md 在 IFace2 目录下存在。 |
| `IFeaturemanager` | `IFeatureManager` | 1 | 同一句里同一接口名两种大小写：IFeaturemanager / IFeatureManager。全库官方名为 IFeatureManager（带大写 M）。 |
| `IGTol` | `IGtol` | 1 | 同一行 IGTol 与 IGtol 两种拼法；IInsertGtol.md:22 有同样写法。 |
| `IHoleSeriesFeatureData` | `IHoleSeriesFeatureData2` | 1 | 两句模板相同：一处接口名漏尾部 2（IHoleSeriesFeatureData），一处写全（…Data2）；磁盘上无前者目录。 |
| `IImport3DinterconnectData` | `IImport3DInterconnectData` | 1 | 同页接口名两种大小写：Interconnect 的 I 时大时小；front matter 的 type 是 IImport3DInterconnectData，SetReferencedFileNa |
| `IInteferenceDetectionMgr` | `IInterferenceDetectionMgr` | 1 | 同一句式两页两种拼法：Inteference 少一个 r。types 下无 IInteferenceDetectionMgr 目录 ⇒ 死链。 |
| `IInterferenceDectectionMgr` | `IInterferenceDetectionMgr` | 1 | 接口名拼成 Dectection 少一个 e（同族另两页同样）。types 下只有 IInterferenceDetectionMgr 目录，Dectection 版不存在 ⇒ 同时是死链。 |
| `IMBD3PdfData` | `IMBD3DPdfData` | 1 | 接口名两种拼法：IMBD3DPdfData（少一个大写 D）vs IMBD3DPdfData；同页 frontmatter 写的是 IMBD3DPdfData，自相矛盾。 |
| `IMidSurface2` | `IMidSurface3` | 1 | 两页同一句，只差接口名：本页写 IMidSurface2，另一页写 IMidSurface3；types 下只存在 IMidSurface3 目录。 |
| `IModelDocExtensioin` | `IModelDocExtension` | 1 | 接口名 Extension 被写成 Extensioin（尾部多一个 i）；同一 See Also 列表里的 IModelDoc2::AlignOrdinate 等也按正确拼法写。 |
| `IModelDocExtenson` | `IModelDocExtension` | 1 | 同一 See Also 列表里接口名两种拼法：多数条目为 IModelDocExtension，末行漏一个 i 写成 IModelDocExtenson（该接口目录不存在）。 |
| `IModelDocExtenstion` | `IModelDocExtension` | 1 | 接口名少一个 e：IModelDocExtenstion。两页讲同一个方法 IBody2::GetEdges / IGetEdges，GetEdges.md 拼写正确。 |
| `IModelDodc2` | `IModelDoc2` | 1 | 同一行前半写 IModelDodc2、后半写 IModelDoc2，同一接口两种拼法；Dodc 为 Doc 字母换位。 |
| `IMoeCopyBodyFeatureData` | `IMoveCopyBodyFeatureData` | 1 | 接口名少一个 v 写成 IMoeCopyBodyFeatureData（无此目录）；同页 L37 另一条同错，兄弟页均为 IMoveCopyBodyFeatureData。 |
| `IOneBendFeatureDAta` | `IOneBendFeatureData` | 1 | 同一页同一句里接口名写成 IOneBendFeatureDAta（A 大写），front matter 与目录名都是 IOneBendFeatureData。 |
| `IParagraphis` | `IParagraphs` | 1 | 同一页 See Also 里同一个接口出现两种拼法：IParagraphis（多一个 i）与 IParagraphs。目录名、页面标题、以及本目录其余 13 页一律是 IParagraphs。 |
| `IPropertyManagerPage2Handler4` | `IPropertyManagerPage2Handler9` | 1 | 同一表格单元里同一接口两种写法：带 I 前缀与不带。另 C:\swapi\types 下只有 IPropertyManagerPage2Handler9，没有 ...Handler4 目录，疑为死链。 |
| `IPropertyManagerPage2Handler8` | `IPropertyManagerPage2Handler9` | 1 | 接口名少一个 l：Hander8 对 Handler8。同目录其它页一律写 IPropertyManagerPage2Handler8，故 SetCursor 这一处链接目标不存在。 |
| `IPropertyManagerPageSelectionBox` | `IPropertyManagerPageSelectionbox` | 1 | 同族两页接口名两种拼法 SelectionBox(大写B)/Selectionbox(小写b)；官方真名为后者，大写B 的 5 处链接目标页不存在。 |
| `IPropertyManagerpageGroup` | `IPropertyManagerPageGroup` | 1 | 接口正式名 IPropertyManagerPageGroup（目录名与 IAddControl 页标题都是它），AddControl 页把 Page 的 P 写成小写 page。 |
| `IRenameDocumentReferences` | `IRenamedDocumentReferences` | 1 | 同族页把接口名写成 IRenameDocumentReferences（少 d）；正确名 IRenamedDocumentReferences。该页 3 条 See Also 全错。 |
| `IRevisonTableAnnotation` | `IRevisionTableAnnotation` | 1 | 同一句里两个链接指同一接口：前一个漏字母，IRevison（少 s）；后一个与兄弟页 [[IRevisionTableAnnotation::…]] 拼写一致。 |
| `ISWOLEObject` | `ISwOLEObject` | 1 | 同一句 Superseded by 列表里，同一接口出现两种拼法：4 处 ISwOLEObject，1 处 ISWOLEObject（W/O 大写）。IGetOLEObjectSettings.md  |
| `IScaleFeatureDta` | `IScaleFeatureData` | 1 | 同接口名两种拼法：本页正文写 IScaleFeatureDta（少一个 a），同目录 IGetBodies.md 写 IScaleFeatureData；磁盘上无该目录。 |
| `ISketchBlockDefiniton` | `ISketchBlockDefinition` | 1 | 同目录接口名出现两种错拼：Defintion（少 i）与 Definiton（多 t）；正确写法 ISketchBlockDefinition 见 GetNotes.md 等。两处链接都点不到目标页。 |
| `ISketchBlockDefintion` | `ISketchBlockDefinition` | 1 | 同目录接口名出现两种错拼：Defintion（少 i）与 Definiton（多 t）；正确写法 ISketchBlockDefinition 见 GetNotes.md 等。两处链接都点不到目标页。 |
| `ISketdhParabola` | `ISketchParabola` | 1 | 同一 See Also 列表模式，本页接口名第 6 字母写成 d（ISketdhParabola），兄弟页 GetApexPoint2/EndPoint2/StartPoint2 都写 ISketch |
| `ISketdhPatternFeatureData` | `ISketchPatternFeatureData` | 1 | 接口名 Sketch 拼成 Sketdh（h 顶掉 c）。GetPatternBodyCount.md L24 与 GetReferencePointType.md L31 同错；types\ISke |
| `ISldworks` | `ISldWorks` | 1 | 同一句里 ISldworks（小写 w）与 ISldWorks（W 大写）两种拼法；本族其余 50 余处均为 ISldWorks。 |
| `ISweepFeaureData` | `ISweepFeatureData` | 1 | 同一页把接口名写成 ISweepFeaureData（Feature 少一个 t）而同一页 See Also 又是 ISweepFeatureData；本接口目录名亦为 ISweepFeatureDa |
| `ITaskPaneView` | `ITaskpaneView` | 1 | 同一接口名两种大小写：P 大写 vs p 小写；页面 type/name 字段与目录名一律为 ITaskpaneView。 |
| `IViewe` | `IView` | 1 | See Also 写成 [[IViewe::SetMirrorViewOrientation Method ()]]，接口名多了 e；实际成员页在 types\IView\ 下，全树无 IViewe  |
| `IWeldmentCustListAnnotation` | `IWeldmentCutListAnnotation` | 1 | 接口名拼成 CustList 少一个 t。types 下只有 IWeldmentCutListAnnotation 目录 ⇒ 死链。 |
| `IWeldmentTrimExtendFeaturedata` | `IWeldmentTrimExtendFeatureData` | 1 | 接口名 Featuredata 与同族 IGetTrimmingBoundary.md 的 FeatureData 大小写不一致（D 小写），且本页标题与 See Also 全部用 FeatureDa |
| `IWizardHoleFeaturData2` | `IWizardHoleFeatureData2` | 1 | 同页同一 See Also 列表里接口名两种拼法。IWizardHoleFeaturData2 少一个 e；同族共 6 处（DrillAngle.md 3 处、CounterDrill{Angle,D |
| `IswManipulatorHandler2` | `ISwManipulatorHandler2` | 1 | 两页互指却拼法不同：OnEndDrag.md 把接口名首字母后 S 写成小写 s（Isw…），OnEndNoDrag.md 写 ISw…；本目录 _overview.md 亦为 ISwManipula |
| `Body` | `IBody2` | 2 | 同一页两种拼法：Remarks 写 IDeleteBodiesFeatureData（Body 多一个 s），See Also 与 frontmatter 写 IDeleteBodyFeatureDa |
| `Bsurface` | `ISurface` | 2 | 同族两页同一句：IGetBSurfParams 页前脚链接是 GetTrimCurves2，下一句却写成 GetTrimCurves（丢了 2）；GetBSurfParams2 页两处都是 GetTr |
| `CommandGroupa` | `ICommandGroup` | 2 | 两句逐字几乎相同，只有 obsolete 页把 CommandGroups 写成 CommandGroupa（尾部多一个 a），同句后半段自己又写对了。 |
| `CommandGroups` | `ICommandGroup` | 2 | 两句逐字几乎相同，只有 obsolete 页把 CommandGroups 写成 CommandGroupa（尾部多一个 a），同句后半段自己又写对了。 |
| `CommandMananger` | `ICommandManager` | 2 | 同一句里 CommandManager 出现两种拼法：前半 CommandMananger（多一个 n）、后半 CommandMananger 正确；CreateCommandGroup2.md 的同 |
| `Component` | `IComponent2` | 2 | 同一 Examples 列表三条链接指向同一文件名却有两种标题拼法，中间一条把 Virtual 写成 Virutal。 |
| `Components` | `IComponent2` | 2 | 同一页三个同族示例标题，两个写 Components、一个写 Componets，而链接目标文件名拼的是 Components。 |
| `Configurations` | `IConfiguration` | 2 | 同一页：参数定义行链的是 swInConfigurationOpts_e，下一行正文写成 swInConfiguration_e（少 Opts）。C:\swapi\enums 下无 swInConfi |
| `Dimensions` | `IDimension` | 2 | 同族相邻两页同一句前置，枚举名一为复数 Dimensions、一为单数 Dimension，同一标识符两种写法。 |
| `Edges` | `IEdge` | 2 | 同接口同一概念两种大小写。ISetConstraintCurves.md 也用小写 [[edges]]，SetConstraintCurves.md 也用大写 [[Edges]]；C:\swapi 下 |
| `Face` | `IFacet` | 2 | 同族（插入新零件）两页同一个面/平面参数写成两种拼法：Face_or_Plane_to_select 与 FaceOrPlaneToSelect。 |
| `Faces` | `IFacet` | 2 | 同一列表三行示例链接，VB.NET 那行目标名 FAces 与 C#/VBA 的 Faces 拼法不同；该 .md 确实以此名存在。 |
| `Featuare` | `IFeature` | 2 | 同一页 Examples 三个链接里两处把 Feature 拼成 Featuare（a/e 换位），第三处写法正确。 |
| `Featur` | `IFeature` | 2 | 同一接口页内接口名少了 e（Featur/Feature）。同页 L26 仍写 [[IEdgeFlangeFeatureData Interface]]，且 types\IEdgeFlangeFeat |
| `Features` | `IFeature` | 2 | 同一工具栏名两种拼法：本行 Feaures（缺 t），同表其余行一律 Features。 |
| `GTol` | `IGtol` | 2 | 两处指向同一个 VBNET 例子文件；同族 19 处写 (VB.NET)，只有 GetTextAtIndex.md 在 VB 与 NET 之间多一个空格。 |
| `IConfiguraiton` | `IConfiguration` | 2 | 同一句里同一接口两种拼法：IConfiguraiton（字母换位）与 IConfiguration。C:\swapi\types\IConfiguration 目录存在，IConfiguraiton  |
| `IDragArrowMainpulator` | `IDragArrowManipulator` | 2 | 接口名两处拼成 IDragArrowMainpulator（i↔p 换位），同目录另两页均写 IDragArrowManipulator；C:\swapi\types\IDragArrowMainpu |
| `IDragOperation` | `IDragOperator` | 2 | 同一属性链接两种接口名：IDragOperation vs IDragOperator。已核实 types 下无 IDragOperation 目录，只有 IDragOperator。 |
| `IMassProeprtyOverrideOptions` | `IMassPropertyOverrideOptions` | 2 | 同页两处写同一接口名，一种 Proeprty 字母换位、一种 Property 正确。types\IMassProeprtyOverrideOptions 目录不存在 → 死链。 |
| `IMiterFlangeFeautreData` | `IMiterFlangeFeatureData` | 2 | 同一页 frontmatter 与 See Also 都写 IMiterFlangeFeatureData，唯独 EndOffset 链接把 Featur 拼成 Feautre（字母换位）→ 目录不存 |
| `IModelDocExtenison` | `IModelDocExtension` | 2 | 同一句前半 IModelDocExtension 正确、后半 IModelDocExtenison（Extenison 字母换位）；无 IModelDocExtenison 目录。 |
| `IModelVeiwManager` | `IModelViewManager` | 2 | 同族互指链接两种拼法：本页第 26-33 行共 8 条全把 View 拼成 Veiw（ei/ie 换位），兄弟页 GetControl 第 26 行用正确拼法。IModelVeiwManager 这个 |
| `IModleDoc2` | `IModelDoc2` | 2 | 同页第12行写 IModleDoc2（漏 d），第29行同页写 IModelDoc2；同错亦见 GetNext.md:20 的 IModleDoc2。 |
| `IParagraphics` | `IParagraphs` | 2 | 同页两条链接两种拼法：IParagraphics（多 ic）与 IParagraphs。同族两页合起来共出现三种写法 IParagraphs / IParagraphis / IParagraphic |
| `IProeprtyManagerPage2Handler9` | `IPropertyManagerPage2Handler9` | 2 | Proeprty = Property 的 e/r 换位；同族另一页对同一对方法写的正是 IPropertyManagerPage2Handler9。 |
| `IPropertyManagerPage2Hander8` | `IPropertyManagerPage2Handler9` | 2 | 接口名少一个 l：Hander8 对 Handler8。同目录其它页一律写 IPropertyManagerPage2Handler8，故 SetCursor 这一处链接目标不存在。 |
| `IProperytManagerPage2` | `IPropertyManagerPage2` | 2 | 同一句里 IPropertyManagerPage2 出现两种拼法：Show2 用正确名，Close 写成 IProperytManagerPage2（多一个 t、且 Properyt 顺序错）。 |
| `IProperytManagerPageListbox` | `IPropertyManagerPageListbox` | 2 | 同一页把接口名写成 IProperytManagerPageListbox（少 r）与 IPropertyManagerPageListbox 两种拼法；前者无对应目录，链接必失效。Style.md  |
| `IRepalceFaceFeatureData` | `IReplaceFaceFeatureData` | 2 | ReleaseSelectionAccess 页把接口名写成 IRepalceFaceFeatureData（ae 换序）；该成员自身的页标题为 IReplaceFaceFeatureData，且 I |
| `ISet` | `ISheet` | 2 | 形参名是 Count（签名 System.int Count），ISet 页把同一个 size 后的参数名写成小写 count。 |
| `ISketchEllispe` | `ISketchEllipse` | 2 | 同一句里接口名出现两种拼法：ISketchEllipse 与 ISketchEllispe（少一个 p）。同族 IGetMajorPoint.md 第 12 行同错；C:\swapi\types\IS |
| `ISkethcManager` | `ISketchManager` | 2 | 同一句里接口名出现两种拼法：ISkethcManager（ethc）与 ISketchManager（etch）。本目录另有 5 页同样误写（ICreateCustomSymbol / IMakeCu |
| `Inteference` | `IInterference` | 2 | 同一句式两页两种拼法：Inteference 少一个 r。types 下无 IInteferenceDetectionMgr 目录 ⇒ 死链。 |
| `Interfernce` | `IInterference` | 2 | 形参名 Interference 被拼成 Interfernce（少一个 e），同族两页同错；同行返回类型又拼作 Interference。 |
| `LIoop2` | `ILoop2` | 2 | 同一句在同族两页把接口名写成 LIoop2（大写 L + 大写 I）与 ILoop2（大写 I + 小写 L）两种，肉眼近乎不可分。 |
| `MidSurface` | `IMidSurface3` | 2 | 同一列表三行示例链接，VB.NET 那行目标名 FAces 与 C#/VBA 的 Faces 拼法不同；该 .md 确实以此名存在。 |
| `Parameters` | `IParameter` | 2 | 同一页 Parameters 里 7 个平行条目全部写 "unmanaged C++:"，唯独 DataType 那条写成 "unmanaged C+:"，少一个加号。 |
| `PropertyManagerPage2Handler4` | `IPropertyManagerPage2Handler9` | 2 | 同一表格单元里同一接口两种写法：带 I 前缀与不带。另 C:\swapi\types 下只有 IPropertyManagerPage2Handler9，没有 ...Handler4 目录，疑为死链。 |
| `SIketchPoint` | `ISketchPoint` | 2 | 同一页同一段散文里接口名出现 ISketchPoint 与 SIketchPoint 两种写法（I 与 S 换位）；目录名与标题均为 ISketchPoint。 |
| `Sheets` | `ISheet` | 2 | 同一参数两页两种写法；前者 wiki 链接被截成 [[shee]] 再接 ts。 |
| `Sketdh` | `ISketch` | 2 | 接口名 Sketch 拼成 Sketdh（h 顶掉 c）。GetPatternBodyCount.md L24 与 GetReferencePointType.md L31 同错；types\ISke |
| `SketdhPath` | `ISketchPath` | 2 | 接口名写成 SketdhPath（c↔d 换位），且分隔符写成 ":;" 而非全篇统一的 "::"；同族页一律为 ISketchPath。 |
| `Surfce` | `ISurface` | 2 | 同族枚举成员两种拼法：同句前一个写 Surface（正确），后一个写 Surfce 少一个 a。 |

## 三 · ★ 少 `I` 前缀（**不是拼错** —— 是官方**链接写法不完整**）

★ 官方页里写 `[[Attribute::X]]`，而真名是 `IAttribute` ⇒ ★ 这**不影响我们写码**
（我们写的是真名），★ 但**影响我们读官方链接** ⇒ 查的时候要自己补 `I` ✓
★★ 它与上一节是**两个不同的缺陷类** —— ★ 而**编辑距离分不开它们**
（这正是本次判据又宽了一次的根因，★ 已记进事实）✓

| 官方链接里写 | ★ 真名 |
|---|---|
| `Attribute` | `IAttribute` |
| `CenterOfMass` | `ICenterOfMass` |
| `CommandGroup` | `ICommandGroup` |
| `CommandManager` | `ICommandManager` |
| `Component2` | `IComponent2` |
| `Configuration` | `IConfiguration` |
| `Curve` | `ICurve` |
| `DimXpertDatum` | `IDimXpertDatum` |
| `Dimension` | `IDimension` |
| `DrSection` | `IDrSection` |
| `EnumDocuments2` | `IEnumDocuments2` |
| `EnumEdges` | `IEnumEdges` |
| `Face2` | `IFace2` |
| `Feature` | `IFeature` |
| `FeatureManager` | `IFeatureManager` |
| `Frame` | `IFrame` |
| `Interference` | `IInterference` |
| `ModelDoc2` | `IModelDoc2` |
| `Parameter` | `IParameter` |
| `PropertyManagerPage2` | `IPropertyManagerPage2` |
| `SelectionMgr` | `ISelectionMgr` |
| `Sheet` | `ISheet` |
| `Sketch` | `ISketch` |
| `SketchBlockDefinition` | `ISketchBlockDefinition` |
| `Surface` | `ISurface` |
| `TableAnchor` | `ITableAnchor` |
| `Vertex` | `IVertex` |
| `View` | `IView` |

★ **两类计数**：真错拼 **102** · 少 `I` 前缀 **28** ✓

## 三 · ★ 怎么用

★ 与 `scripts/check_official_source_defects.py` 配合：那个门禁管**我们引用的官方页是否存在**；
★ 本表管**名字本身该拼成什么** ⇒ ★ 写码时若不确定某个接口名，先查本表 ✓

★ **两份合起来的覆盖**：本表（名字拼法）· 门禁（引用是否存在）· `docs/official-source-errors.md`（抄录指引）·
`docs/recon/official-source-defects-2.md`（964 条穷举）✓
