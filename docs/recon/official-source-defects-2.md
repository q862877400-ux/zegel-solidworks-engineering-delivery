# 官方源（`C:\swapi\`）自身的机械性缺陷 —— 穷举扫描

> **这份文件补的是 `docs/official-source-errors.md`**（那份只记了 **3** 条，全是手工零散撞见的：
> `ISheet.GetProperties` 说 seven 却列 8 项 · `IDrawingDoc` 同族的 8 个死链 · 一个枚举只有 4 个成员）。
> 本文件是**穷举**扫描的产出。
>
> **来源与口径**
> - **扫的源**：`C:\swapi\types\` **566 个接口目录 / 11557 个成员页** ＋
>   `C:\swapi\enums\` **963 个枚举页**，合计 **13086** 份 `.md`。
> - **分工**：**Bunny（`opencode-zen` / `space-bunny-free`）60 路**，按**页数均衡**装箱
>   （每路 197–722 页）。**60/60 零失败**。
> - **两道闸**：① **引文逐字回查**（每条 `quote` 必须真在那个文件里，否则作废）；
>   ② **Lead 独立核验死链目标**（用本机 566 接口目录 + 963 枚举页的名字集合去查目标页在不在）。
>
> ⚠ **本文件不含任何行号**；每条给**文件名 + 可 `grep` 的原文片段**。

## 一、统计

| 指标 | 数 |
|---|---|
| 扫过的接口目录 | **566** |
| 扫过的枚举页 | **963** |
| 实际读过的 `.md`（各路自报之和） | **13086** |
| 报出的缺陷（引文已过闸） | **964** |
| —— `spelling`（同一标识符两种拼法） | 554 |
| —— `dead_link_candidate`（怀疑目标页不存在） | 212 |
| —— `other` | 164 |
| —— `undefined_item`（返回项无定义） | 24 |
| —— `number_mismatch`（散文数字 ≠ 列表长度） | 10 |
| 引文回查**不通过**、已作废 | **6** |

### 1.1 ★ 死链候选的**逐条核验结果**（最有价值的一节）

Bunny 报了 212 条「怀疑目标页不存在」。我拿**本机全部官方页名**去查：

| 核验结果 | 数 | 含义 |
|---|---|---|
| ✅ **目标页确实不存在**（真死链） | **65** | 见 §二 |
| ⚠ 接口名查不到（`iface_name_wrong`） | 50 | **拼错接口名**，见 §三 |
| ⚠ 接口在、**成员不在**（`member_missing`） | 58 | **拼错成员名**，见 §四 |
| —— 归一化后其实存在（我第一版判据太严） | 34 | **不计缺陷**（留档以证没夸大） |

## 二、真死链：链接目标页**确实不存在**（65 条）

> 判据：把 `[[X::Y]]` 拆成接口 `X` 与成员 `Y`，在 `C:\swapi\types\X\` 下**找不到** `Y.md`
> （已做归一：去空格/下划线、去官方页名后缀 `Method`/`Property`/`Function`、忽略大小写）。
> ⇒ **这一条不依赖任何判断力，是文件系统事实。**

| # | 链接（可 grep） | 出现在 |
|---|---|---|
| 1 | You can also get the maximum chordal deviation using [[swUserPreferencesDouble_e]].swImageQualityShadedDeviation. | `GetTessellationQuality.md` |
| 2 | See the [[IMidSurface2]] object for methods that provide access to this topology. | `InsertMidSurfaceExt.md` |
| 3 | - **Options**: Save with references options as defined in [[swSaveWithReferencesOptions]] (see **Remarks**) | `GetAdvancedSaveAsOptions.md` |
| 4 | - **SelType**: Selection type to verify as defined in [[swSelelectType_e]] | `GetSelectionFilter.md` |
| 5 | - [[GetLineFontCount2 Method]] | `GetLineFontInfo2.md` |
| 6 | - [[GetFirstSelectedFace Method]] | `GetProcessedBodyWithSelFace.md` |
| 7 | Type of this DimXpert annotation as defined in [[swDimXpertAnnotationType_e]] | `Type.md` |
| 8 | [[DerivedPartFeatureData]] | `GetTypeName.md` |
| 9 | - **TextureIn**: [[Texture]] | `SetTextureByDisplayState.md` |
| 10 | **Signature**: `void Clone( out EnumSketchHatches Ppenum )` | `Clone.md` |
| 11 | - [[IColorTable:GetStandardCount Method]] | `GetBasicColorCount.md` |
| 12 | Typically, you would call this method from the ISWPropertySheet [[OnOKNotify]] event handler to retrieve data from your ActiveX control. | `GetControl.md` |
| 13 | - [[Insert3DSketch2 Method]] | `Is3D.md` |
| 14 | - [[SetPosition Method]] | `IGetPosition.md` |
| 15 | If this property is set to false, you should specify a detailed error message to display in the What's Wrong dialog when SOLIDWORKS fails to find file … | `EmbedMacroFile.md` |
| 16 | - **FosUsage**: Feature of size usage as defined in [[swDimXpertDistanceFosUsage_e]] | `GetFeature.md` |
| 17 | - [[SuppressNewComponentModels Property]] | `HideNewComponentModels.md` |
| 18 | Array of [[general table annotations]] | `GetTableAnnotations.md` |
| 19 | Before calling this method, call [[ISurface:Parameterization2]] to populate VP0. | `GetBSurfParams3.md` |
| 20 | Thread end condition as defined in [[swWzdHoleThreadEndCondition]] | `ThreadEndCondition.md` |
| 21 | - [[IWizardHoleFeatureData2:CounterSinkAngle Property]] | `MidCounterSinkDiameter.md` |
| 22 | Image size as defined by [[swSaveAVIImageSize_e]] | `ImageSize.md` |
| 23 | - [[Multiply Method]] | `IMultiply.md` |
| 24 | Bend position as defined in [[swFlangePositionType_e]] | `PositionType.md` |
| 25 | [[ILinearPatternFeatureData::PatternBodyArray]], [[PatternFaceArray]], or [[PatternFeatureArray]] | `_overview.md` |
| 26 | - **Index**: [[GetPolygonCount Method]]Index of parabola | `IGetParabolaAtIndex.md` |
| 27 | - [[Simulation3DContactFeatureData Interface]] | `_overview.md` |
| 28 | - [[SetScale Method]] | `GetScale.md` |
| 29 | - [[ISweepFeatureData:TwistControlType]] is set to [[swTwistControlType_e]].swTwistControlFollowPath. | `GetPathAlignmentDirectionVector.md` |
| 30 | - [[ISweepFeatureData:TwistControlType]] is set to [[swTwistControlType_e]].swTwistControlFollowPath. | `SetPathAlignmentDirectionVector.md` |
| 31 | - [[Simulation3DContactFeatureData Interface]] | `_overview.md` |
| 32 | swDimXpertChamferDimensionType_e ChamferType {get;} | `ChamferType.md` |
| 33 | [[Transform]] | `GetTransform.md` |
| 34 | - [[GetEndPoint2 Method]] | `IGetEndPoint2.md` |
\| 35 \| \| swPropertySheetCreateControlNotify \| 5 = [[CreateControlNotify]] \| \| `swPropertySheetNotify_e.md` \|
| 36 | - **Type**: Type of Gtol to insert as defined in [[swDimXpertGtolType_e]] | `InsertGtol.md` |
| 37 | [[swAutodimMarkEntities]] | `swAutodimEntities_e.md` |
| 38 | - [[ICoordinateSystemFeatureData:IGetOriginEntity Method]] | `GetOriginEntityType.md` |
| 39 | - [[vary the spacing of pattern instances]] and dimensions by implementing [[IInstanceToVaryOptions]]. | `_overview.md` |
| 40 | - TopDoc argument is the [[ModelDoc2]] object for the part | `AccessSelections.md` |
| 41 | Array of intersecting [[solids]], [[surfaces]], and [[planes]] in this intersect feature | `GetIntersectionsTools.md` |
| 42 | - **TopDoc**: [[Model]] in which to display the vertex | `Display.md` |
| 43 | - **WhichOne**: Button as defined in [[swPropertyManagerPageButtons e]] | `EnableButton.md` |
\| 44 \| \| swFileSaveAsNotSupported \| 4096 or 0x1000 = Save As operation:<br>- is not supported<br>- was executed is such a way that the resulting file might … \| `swFileSaveError_e.md` \|
| 45 | Line (e.g., [[edge,]] [[co-Edge]], or [[sketch segment]]) that is perpendicular to this gusset's section plane | `ReferenceLine.md` |
| 46 | ## Returns [[Annotation]] | `GetAnnotation.md` |
| 47 | Flange position as defined by [[swSweptFlangePostionTypes_e]] | `FlangePosition.md` |
| 48 | Face propagation type as defined in [[swDraftFacePropagationType]] | `FacePropagation.md` |
| 49 | retval[10] describes the [[line type]] of the triangle | `GetSymTriangles.md` |
| 50 | - [[IMeasure:Y Property]] | `X.md` |
| 51 | - **Entity**: [[Face]] or [[plane]] | `SetProjectionEntity.md` |
| 52 | Gets the drawing [[sheets]] to export. | `GetSheets.md` |
| 53 | Array of [[IExplodeSteps]] in the subassembly explode view | `GetSubAssemblyExplodeSteps.md` |
| 54 | Called whenever the user changes the position of a [[slider control]] on this PropertyManager page. | `OnSliderPositionChanged.md` |
| 55 | Explode step type as defined in [[swAssemblyExplodeStepType_e]] | `ExplodeStepType.md` |
| 56 | This enumerator specifies possible values for the types of [[ISWPropertySheet]]s exported by SOLIDWORKS when a SldWorks notification of type [[swAppPr … | `swPropSheetType_e.md` |
| 57 | - [Insert Camera (C#)](../../examples/Insert_Cavity_Example_CSharp.md) | `Perspective.md` |
| 58 | - [Set Bodies for Move/Copy (C#)](../../examples/Set_Bodies_for_Move_Copy_Example_VBNET.md) | `ReleaseSelectionAccess.md` |
| 59 | - [[ComponentOrientationsAlignToSelection]] | `_overview.md` |
| 60 | Error code as defined in [[dsgnchkError_e]] | `CreateChecksFromSWFile.md` |
| 61 | Material condition modifier as defined in [[swDimXpertMaterialConditionModifier_e]] | `Modifier.md` |
| 62 | Allows access to a [[faces]] enumeration. | `_overview.md` |
| 63 | - [[IEnumCoEdgeClass Interface]] | `_overview.md` |
| 64 | **Signature**: `System.bool AddYAxis( MotionPlotAxisFeatureData YAxis )` | `AddYAxis.md` |
| 65 | - [[IDatumTag:GetTriangleAtIndex Method]] | `GetTriangleCount.md` |

## 三、拼错的**接口名**（50 条）

> 这些链接的**接口名**在 566 个接口里查不到 ⇒ 点进去必然 404。
> 典型形态：少字母（`IVew` ↔ `IView`）· 少 `Doc`（`IModel2` ↔ `IModelDoc2`）·
> 缩写（`IModelViewMgr` ↔ `IModelViewManager`）· 整个词拼错（`IDocumentSpecifiation` · `IDrawngDoc`）。

| # | 链接写的 | 出现在 |
|---|---|---|
| 1 | IFeatureMgrView::ActivateView | `ActivateFeatureMgrView.md` |
| 2 | IModelViewMgr::CreateFeatureMgrView2 | `AddFeatureMgrView3.md` |
| 3 | IVew::GetBendLineCount Method | `GetBendLines.md` |
| 4 | IVew::GetSMBoundaryBoxDisplayData2 | `GetSMBoundaryBoxDisplayData.md` |
| 5 | IModelViewMgr::CreateFeatureMgrView2 | `AddFeatureMgrView3x64.md` |
| 6 | IDocumentSpecifiation::PLMObjectSpecification | `OpenDoc7.md` |
| 7 | ISMNormalCutFeatureData::Offset | `AddSMNormalCutType.md` |
| 8 | IDrawngDoc::IDrawngDoc::ICreateSectionViewAt4 Method | `CreateSectionView.md` |
| 9 | IModel2::ForceRebuild3 | `ForceRebuild.md` |
| 10 | IComponent::IGetRenderMaterials | `GetRenderMaterialsCount.md` |
| 11 | ISketchManagerRelation::IGetAllowedRelations Method | `GetAllowedRelations.md` |
| 12 | IPunch::TagStyle Property | `CombineTags.md` |
| 13 | IPropertyManagerPageStyle::GetRange | `SetRange.md` |
| 14 | IComponent::FirstFeature Method | `GetNextFeature.md` |
| 15 | IAssembyDoc::IToolsCheckInterference3 Method | `ICheckInterference2.md` |
| 16 | ITesssellation::MatchType | `GeneralTopology.md` |
| 17 | IGetDimXpertTolerance::GetPrimaryDatums | `GetPrimaryDatumModifiers.md` |
| 18 | IMagnetLine::GetNotes Method | `GetNotesCount.md` |
| 19 | ITableAnnnotation::InsertColumn2 | `InsertColumn.md` |
| 20 | IReplaceFeatureFeatureData::ISetFacesForReplacement Method | `IGetFacesForReplacement.md` |
| 21 | IModelDoc::GraphicsRedraw2 | `SuppressWaitCursorDuringRedraw.md` |
| 22 | ISimpleFilletFeatureData::IGetHoldLines | `GetHoldLineCount.md` |
| 23 | IMate2Entity::Reference2 | `ReferenceType.md` |
| 24 | ILinearFeaturePatternData::D1Axis Property | `D1ReverseDirection.md` |
| 25 | ICustomerPropertyManager::Delete Method | `Add2.md` |
| 26 | DislayData::GetLineAtIndex3 | `GetLineAtIndex2.md` |
| 27 | ISurfaceRadiateSurfaceData::GetRadiatedEntitiesCount Method | `RadiatedEntities.md` |
| 28 | ISketdhParabola::IGetFocalPoint2 Method | `GetFocalPoint2.md` |
| 29 | ISketchBlockInstnace::GetLeaderStyle | `GetLeaderPoints.md` |
| 30 | IConfgurationManager::GetConfigurationParamsCount | `IGetConfigurationParams.md` |
| 31 | ISweptFlangeFeatuareData::UseGaugeTable | `swSweptFlangeError_e.md` |
| 32 | IDrSectionView::GetAutoHatch | `RandomizeScale.md` |
| 33 | ISurfacePlanarSurfaceData::GetBoundingEntitiesCount Method | `BoundingEntities.md` |
| 34 | IPropertyManagerPage2Handler8::OnListboxRMBUp | `_overview.md` |
| 35 | ITessellate::GetVertexParams Method | `IGetVertexPoint.md` |
| 36 | ISimpleHoleFeature2::SurfaceOffset Property | `ReverseOffset.md` |
| 37 | ISelectionManager::CreateCallout2 | `Callout.md` |
| 38 | ISurfaceParameterization::UProperties Property | `UMax.md` |
| 39 | IMirrorSolidFeaturePattern::IAccessSelections2 Method | `AccessSelections.md` |
| 40 | ISurfTranslateFeatureData::SetTranslateSurface Method | `GetTranslateSurface.md` |
| 41 | IPropertyManagerNumberbox::SetRange2 Method | `SetSliderParameters.md` |
| 42 | ILocalCurveDrivenPatternFeature::SkippedItemArray Property () | `GetSkippedItemCount.md` |
| 43 | IDatumTargetSymbol::GetAnnotation Method | `IGetAnnotation.md` |
| 44 | ISketchHandle::SplinePointNumber Property | `ShowInflectionPoints.md` |
| 45 | ICommandGruop::SelectType | `CustomNames.md` |
| 46 | IAdvancedSelectionCriteriaClass::GetItem | `GetItemCount.md` |
| 47 | IWrapeatureData::AccessSelections | `ReleaseSelectionAccess.md` |
| 48 | IWrapFeatureData2::ReleaseSelectionAccess | `AccessSelections.md` |
| 49 | ITableDrivenPatternFeatureData::IAccessSelections2 Method | `AccessSelections.md` |
| 50 | ISectionView::KeepCapColor | `FirstColor.md` |

## 四、接口在、**成员名**不在（58 条）

> 接口是对的，成员名在该接口下查不到。典型：`ShowNameView2`（应为 `ShowNamedView2`）·
> `SuIppressView`（应为 `SuppressView`）· `EditRebuild2` · `IGetDocumetnDependencies2` ·
> `GetAttachmentCoun`（`…Count` 被截断）。

| # | 链接写的 | 出现在 |
|---|---|---|
| 1 | IModelDoc2::ShowNameView2 | `ShowNamedView.md` |
| 2 | IModelDoc2::ListAuxiliaryExtenalFileReferencesCount | `IListAuxiliaryExternalFileReferences.md` |
| 3 | IDrawingDoc::SuIppressView Method | `SuppressState.md` |
| 4 | IModelDoc2::EditRebuild2 | `ScaleDecimal.md` |
| 5 | IModelDoc2::ViewZoomtofit2 | `GetPolylines6.md` |
| 6 | IModelDocExtension::GetAttachmentCoun | `IGetAttachments.md` |
| 7 | IModelDocExtension::IDecal Interface | `GetDecals.md` |
| 8 | IModelDocExtension::GetPersistentReferenceCount3 | `IGetObjectByPersistReference3.md` |
| 9 | IModelDocExtension::GetMassPropertiesSelectedComp Method | `GetMassProperties.md` |
| 10 | ISldWorks::IGetDocumetnDependencies2 | `IGetDocumentDependenciesCount2.md` |
| 11 | ISldWorks::RemoveToobar2 | `RemoveToolbar.md` |
| 12 | IFeatureManager::InsertProtusionSwept3 | `InsertProtrusionSwept.md` |
| 13 | IFeatureManager::AddVariablePitchHelixFirstPitchAndDiamenter | `EndVariablePitchHelix.md` |
| 14 | IFeature::GetFeatures Method | `GetFeatureCount.md` |
| 15 | IDrawingDoc::IEditOrdinate Method | `InsertOrdinate.md` |
| 16 | IDrawingDoc::1stAngleViews2 | `Create1stAngleViews.md` |
| 17 | IDrawingDoc::UnInsertBreakVertical Method | `InsertBreakHorizontal.md` |
| 18 | IDrawingDoc::SetSelectedSheets | `SetupSheet6.md` |
| 19 | IAssemblyDoc::CreateMate. | `AddMate5.md` |
| 20 | IConfiguration::GetRootComponent. | `GetModelDoc.md` |
| 21 | INote::vGetBalloonOptions Method () | `IsBomBalloon.md` |
| 22 | ISheet::SheetFormatVisible. | `GetNext.md` |
| 23 | IModeler::IICreateBodiesFromSheets2 Method | `ICreateWireBody.md` |
| 24 | IModeler::ICreateBodyFromFace3 | `ICreateBodyFromFaces.md` |
| 25 | IColorTable::ISetBodiesToCombine Method | `GetBodiesToCombineCount.md` |
| 26 | ISketchRegion::GetSketchRegions Method | `GetSketchRegionCount.md` |
| 27 | IModelDocExtension::SetLinkedDisplayStates Method () | `GetLinkedDisplayStates.md` |
| 28 | IShutOffSurfaceFeatureData::IGetLoopsEdges | `GetLoopEdgeCount.md` |
| 29 | ITableAnnotation::ITableAnnotation::GridLineWeight Property | `BorderLineWeight.md` |
| 30 | IConfigurationManager::IConfigurationManager::SetConfigurationParams Method | `ISetParameters.md` |
| 31 | IConfiguration::AddCADFamilyConfiguration Method () | `Set3DExperienceType.md` |
| 32 | IStructuralMemberFeatureData::ReleaseSelctionAccess | `AccessSelections.md` |
| 33 | ISimpleFilletFeatureData2::AutoSelect Property | `PropagateFeatureToParts.md` |
| 34 | ICurve::Length2 | `GetLength3.md` |
| 35 | IMBD3DPdfData::GetTextCustomProperties | `_overview.md` |
| 36 | ITabAndSlotGroupData::D2OffsetFromStart | `D2OffsetFromEnd.md` |
| 37 | ISelectionMgr::ISelectionMgr::GetSelectionPoint2 Method | `DeSelect2.md` |
| 38 | IDisplayData::IDisplayData::GetTextCount Method | `GetTextAngleAtIndex.md` |
| 39 | DisplayData::IGetTextCount Method | `GetTextInBoxWidthAtIndex.md` |
| 40 | ILocalLinearPatternFeatureData::IGetSkippedItemCount Method | `SkippedItemArray.md` |
| 41 | IDrawingDoc::EditTempate | `_overview.md` |
| 42 | IFeature::IModifyDefintion2 | `IAccessSelections2.md` |
| 43 | IDimension::IGetReferencePointsCount | `IGetReferencePoints.md` |
| 44 | IFrame::AddItemToThirdPartyPopupMenu2 Method () | `AddMenuPopupIcon3.md` |
| 45 | IEdge::IGetTangentEdges. | `GetTangentEdgesCount.md` |
| 46 | IMidSurface3::GetGetFirstFaceArray | `GetNextFaceArray.md` |
| 47 | ICoordinateSystemFeatureData::ICoordinateSystemFeatureData::ISetYAxisEntities Method | `IGetYAxisEntities.md` |
| 48 | IRenamedDocumentReferences::ReferenceArray | `_overview.md` |
| 49 | IMoveFaceFeatureData::SetFromEntity Method () | `SetFromEntity.md` |
| 50 | ISketchBlockDefinition::MakeSketchBlockFromFile Method | `LinkToFile.md` |
| 51 | IEnvironment::GetSymArcs2. | `IGetSymArcs.md` |
| 52 | IFlatPatternFeatureData::IBreakCornerFeatureData Interface | `BreakCornerRadius.md` |
| 53 | IShellFeatureData::ReleaseSelections | `AccessSelections.md` |
| 54 | ISketchSegment::GetSketchSegmentCount Method | `GetSketchPaths.md` |
| 55 | IAttribute::Register Method | `AddParameter.md` |
| 56 | ILocalCurvePatternFeatureData::Dir1IsEqualSpaced | `D1Spacing.md` |
| 57 | ICommandGroup::AddComandItem2 | `AddCommandItem.md` |
| 58 | ICommandManager::HasToolbar Property | `ToolbarId.md` |

## 五、`spelling`：同一标识符在一页/一族里**两种拼法**（554 条）

> ★ **这一类对抄录最危险**：抄哪一页都可能抄错。每条都给了**两段逐字原文**。

| # | 形态A（文件） | 形态B（文件） | 差别 |
|---|---|---|---|
| 1 | Obsolete. Superseded by [[IConfiguraiton::GetParameters]], [[IConfiguration::IGetParameters]], [[IConfiguratio …<br>`AddOrEditConfiguration.md` | Obsolete. Superseded by [[IConfiguraiton::GetParameters]], [[IConfiguration::IGetParameters]], [[IConfiguratio …<br>`IAddOrEditConfiguration.md` | 同一句里同一接口两种拼法：IConfiguraiton（字母换位）与 IConfiguration。C:\swapi\types\IConfiguration 目录存在，IConfiguraiton 全库无。 |
| 2 | This method is different from [[IModelDodc2::SelectedEdgeProperties]] and [[IModelDoc2::SelectedFaceProperties …<br>`SelectedFeatureProperties.md` | [[IModelDoc2::SelectedFaceProperties]]<br>`SelectedFeatureProperties.md` | 同一行前半写 IModelDodc2、后半写 IModelDoc2，同一接口两种拼法；Dodc 为 Doc 字母换位。 |
| 3 | Gets the size of the array required to hold data returend by [[IModleDoc2::IVersionHistory]].<br>`IGetVersionHistoryCount.md` | - [[IModelDoc2::VersionHistory Method]]<br>`IGetVersionHistoryCount.md` | 同页第12行写 IModleDoc2（漏 d），第29行同页写 IModelDoc2；同错亦见 GetNext.md:20 的 IModleDoc2。 |
| 4 | [[IModelDocExtension::GetUserPreferenceToggle]] swDisplayPlanes and [[IModelDocExtenison::SetUserPreferenceTog …<br>`ICreatePlaneAtAngle3.md` | [[IModelDocExtension::GetUserPreferenceToggle]]<br>`ICreatePlaneAtAngle3.md` | 同一句前半 IModelDocExtension 正确、后半 IModelDocExtenison（Extenison 字母换位）；无 IModelDocExtenison 目录。 |
| 5 | you can traverse all open documents using [[ISldworks::EnumDocuments2]], [[ISldWorks::IGetFirstDocument2]], or …<br>`IGet3rdPartyStorage.md` | [[ISldWorks::IGetFirstDocument2]]<br>`IGet3rdPartyStorage.md` | 同一句里 ISldworks（小写 w）与 ISldWorks（W 大写）两种拼法；本族其余 50 余处均为 ISldWorks。 |
| 6 | use the pointer returned by this method to access the various get and set methods of the [[IGTol]] interface,  …<br>`InsertGtol.md` | [[IGtol::GetAnnotation]]<br>`InsertGtol.md` | 同一行 IGTol 与 IGtol 两种拼法；IInsertGtol.md:22 有同样写法。 |
| 7 | - IModelDoc2::GraphicsRedraw2 is much faster than ModelDoc2::EditRebuild3.<br>`SetDisplayWhenAdded.md` | The sketch entities appear on the screen after performing [[IModelDoc2::GraphicsRedraw2]] or [[IModelDoc2::Edi …<br>`SetDisplayWhenAdded.md` | 同页第26行写 ModelDoc2::EditRebuild3（少 I），第20行同成员写 [[IModelDoc2::EditRebuild3]]。SetTitle2.md:31 同样写 ModelDoc2::SaveAs。 |
| 8 | - minorAuto - an be interpreted as a BOOLEAN: True if the minor grids are set automatically, false otherwise<br>`GetGridSettings.md` | - angleSnap - can be interpreted as a BOOLEAN: True if snap to angle is on, false otherwise<br>`GetGridSettings.md` | 同页 dispGrid/gridSpacing/snap/dotStyle/angleSnap 五条均作 can be interpreted，minorAuto 这条漏 can 写成 an。 |
| 9 | - **AutoSize**: True to automatically size the the plane, false to not<br>`CreatePlaneAtOffset3.md` | - **AutoSize**: True to automatically size the the plane, false to not<br>`ICreatePlaneAtOffset3.md` | 两页同一句连写两个 the（the the）。 |
| 10 | Displays the the selected object's property sheet.<br>`PropertySheet.md` | Flips the the active or selected sketch about the specified coordinate system axis.<br>`SketchModifyFlip.md` | 两页同句连写两个 the。 |
| 11 | When creating a a spiral, you must specify the pitch and number of revolutions.<br>`InsertHelix.md` | you must specify the pitch and number of revolutions.<br>`InsertHelix.md` | 同句连写两个冠词 a a（creating a a spiral）。 |
| 12 | tolbox2corner2[3] = XYZ corner 2 of tolerance box 2; data returned is valid when isDual is true<br>`GetDimensionDisplayInfo5.md` | dimensionCount, [lineCount, [lineSegmentCount [StartPt[3], endPt[3] ] ], arcCount, [arcSegmentCount, [arcCente …<br>`GetDimensionDisplayInfo5.md` | 同一页第22行总表写 tolbox2Corner2[3]，第98行定义行写 tolbox2corner2[3]，同页两种拼法。IGetDimensionDisplayInfo5.md:103 同。 |
| 13 | - Line1EngPt[3]<br>`GetBreakLineInfo.md` | - Line2EndPt[3]<br>`GetBreakLineInfo.md` | 同一点列表内 Line1EngPt[3] 与 Line2EndPt[3] 两种拼法（Eng/End）；IGetBreakLineInfo.md:87 同。 |
| 14 | angularOrdinateDimInfo[10] This data is only returned for angular ordinate dimiensions; the array of 10 values …<br>`GetDimensionInfo7.md` | isBidirectiona = BOOLEAN returned as a double; true if it is bidirectional<br>`GetDimensionInfo7.md` | dimiensions 多一个 i；isBidirectiona 少尾字母 l，与本行的 bidirectional 不一致。 |
| 15 | This enumeration also contains three other values, swFACETED_WIREFRAME, swFACETED_HIDDEN_GREY, and swFACETEDHI …<br>`SetDisplayMode3.md` | - swFACETED_HIDDEN<br>`SetDisplayMode4.md` | SetDisplayMode3 同行同时出现 swFACETEDHIDDEN 与 sw_HIDDEN；SetDisplayMode4 用 swFACETED_HIDDEN。同一族两种拼法。 |
| 16 | This enumeration also contains three other values, swFACETED_WIREFRAME, swFACETED_HIDDEN_GREY, and swFACETEDHI …<br>`SetDisplayMode3.md` | - swFACETED_HIDDEN_GREYED<br>`SetDisplayMode4.md` | SetDisplayMode3 写 swFACETED_HIDDEN_GREY，SetDisplayMode4 写 swFACETED_HIDDEN_GREYED，同族两种拼法。 |
| 17 | swBreakLineStraight<br>`GetBreakLineInfo.md` | swBreakLine_Straight<br>`GetBreakLineInfo2.md` | 同族两页对同一枚举成员两种拼法：swBreakLineStraight / swBreakLine_Straight。 |
| 18 | swBreakLineZigZag<br>`GetBreakLineInfo.md` | swBreakLine_ZigZag<br>`GetBreakLineInfo2.md` | 同族两页对同一枚举成员两种拼法：swBreakLineZigZag / swBreakLine_ZigZag。 |
| 19 | LineType = line type associated with the second plus-sign line. See the [[swLineTypes_e]] enumeration.<br>`GetCenterMarkInfo.md` | [ numCenterMarks, [ numCenterMarkLines, lineType1, plus1StartPt[3], plus1EndPt[3], lineType2, plus2StartPt[3], …<br>`GetCenterMarkInfo.md` | 同页总表写 lineType，定义行写 LineType；而 lineStartPt/lineEndPt 的总表与定义完全一致，仅此一处不一致。 |
| 20 | Gets the the [[IDisplayData]] object for this drawing view containing only those model items that are visible  …<br>`GetDisplayData4.md` | Gets the the [[IDisplayData]] object for this drawing view containing only those model items that are visible  …<br>`IGetDisplayData3.md` | 同一句连写两个 the：Gets the the [[IDisplayData]]；两页同一处重复。 |
| 21 | Call this method before calling [[IView::IGetPolylines6.]]<br>`GetPolyLineCount5.md` | - **PointCount**: Size of array needed to allocate in doubles for [[IView::IGetPolylines6]]<br>`GetPolyLineCount5.md` | 同页 :18 写 [[IView::IGetPolylines6]]，:24 写成 [[IView::IGetPolylines6.]]，链接串末尾多一个句点。 |
| 22 | - [[IView::IView::EnumSectionLines Method]]<br>`GetSectionLines.md` | - [[IView::IView::EnumHiddenComponents2 Method]]<br>`GetVisibleComponentCount.md` | See Also 写成 [[IView::IView::EnumSectionLines Method]]，前缀 IView:: 重复两次；GetVisibleComponentCount.md:31 同型。 |
| 23 | Valid line styles can be found in [[swLineStyles_e.]]<br>`GetBreakLineInfo.md` | LineStyleIndex = line style; valid line styles as defined in [[swLineStyles_e]]<br>`GetDimensionInfo6.md` | 写成 [[swLineStyles_e.]]，末尾多句点；同族另一页为 [[swLineStyles_e]]。IGetBreakLineInfo.md:45 同。 |
| 24 | [[IView::GetPolylineCount5]]<br>`GetPolylines6.md` | Obsolete. Superseded by [[IView::GetPolyLineCount5]].<br>`GetPolyLineCount.md` | 同一成员两种链接拼法 [[IView::GetPolylineCount5]] 与 [[IView::GetPolyLineCount5]]（成员页文件名为 GetPolyLineCount5.md）。 |
| 25 | Obsolete. Superseded by [[IView::GetPolyLines6]] and [[IView::IGetPolyLines6]].<br>`GetPolylines.md` | This method only returns arcs that were sketched by a user in a drawing view. Use [[IView::GetPolylines6]] or  …<br>`GetArcs4.md` | 同一成员两种链接拼法 [[IView::GetPolyLines6]] 与 [[IView::GetPolylines6]]。GetPolylines2.md:12 同。 |
| 26 | [[IView::GetPolyLinesandCurvesCount]]<br>`IGetPolylines7.md` | [[IView::GetPolyLinesAndCurvesCount]]<br>`GetPolyLinesAndCurves.md` | 同一页 153 行写 [[IView::GetPolyLinesandCurvesCount]]（andCurves 的 C 小写），另一页写 ...AndCurves...。 |
| 27 | Use this method to obtain the array of centerlines all at once instead of calling [[IView::GetFirstCenterLine] …<br>`GetCenterLines.md` | - [[ICenterline::GetNext Method]]<br>`GetFirstCenterLine.md` | 同一接口两种链接拼法 [[ICenterLine::GetNext]] 与 [[ICenterline::GetNext Method]]；IGetCenterLines.md:27 同。 |
| 28 | - [[IViewe::SetMirrorViewOrientation Method ()]]<br>`GetMirrorViewOrientation.md` | # IView.SetMirrorViewOrientation<br>`SetMirrorViewOrientation.md` | See Also 写成 [[IViewe::SetMirrorViewOrientation Method ()]]，接口名多了 e；实际成员页在 types\IView\ 下，全树无 IViewe 目录。 |
| 29 | - [Get View Bounding Box and Position (C#)](../../examples/Get_View_Bounding_Box_and_Position_Example_VBNET.md …<br>`GetOutline.md` | - [Get View Bounding Box and Position (VB.NET)](../../examples/Get_View_Bounding_Box_and_Position_Example_VBNE …<br>`Position.md` | 同一目标文件在 GetOutline.md 被标成 (C#)，在 Position.md 被标成 (VB.NET)：同族两页标签不一致。 |
| 30 | witness line 1[start_point[x,y,z], end_point[x,y,z&cd;<br>`GetWitnessGeomInfo.md` | witness arc 1[start_point[x,y,z], end_point[x,y,z], center_point[x,y,z], normal_point[x,y,z&cd;<br>`GetWitnessGeomInfo.md` | HTML 实体被截断成 &cd;（应为 ]]），且方括号未闭合；本页 4 处、IGetWitnessGeomInfo.md 4 处同型。 |
| 31 | you must call [[IModelDoc2::GetRayIntersectionsPoints]] and [[IModelDoc2::GetRayIntersectionTopology]].<br>`RayIntersections.md` | - [[IModelDoc2::GetRayIntersectionsTopology Method ()]]<br>`SelectByRay.md` | 同一接口两页对同一成员两种拼法：RayIntersections 写 GetRayIntersectionTopology（单数），SelectByRay 写 GetRayIntersectionsTopology；前者无对应 .md 页。 |
| 32 | - [[IModelDocExtenson::CreateTexture Method]]<br>`RemoveTextureByDisplayState.md` | - [[IModelDocExtension::SetTextureByDisplayState Method]]<br>`RemoveTextureByDisplayState.md` | 同一 See Also 列表里接口名两种拼法：多数条目为 IModelDocExtension，末行漏一个 i 写成 IModelDocExtenson（该接口目录不存在）。 |
| 33 | - [[IModelDocExtenson::RemoveTextureByDisplayState Method]]<br>`CreateTexture.md` | - [[IModelDocExtension::RemoveTextureByDisplayState Method]]<br>`SetTexture.md` | 同一成员 RemoveTextureByDisplayState 在同族两页两种拼法：CreateTexture 页接口名写成 IModelDocExtenson，SetTexture 页为正确的 IModelDocExtension。 |
| 34 | - [[IModelDocExtenson::SetTexture Method]]<br>`SetTextureByDisplayState.md` | - [[IModelDocExtension::CreateTexture Method]]<br>`SetTexture.md` | SetTextureByDisplayState 页 5 条 See Also 全部写成 IModelDocExtenson，而同族的 SetTexture 页同一成员写作 IModelDocExtension。 |
| 35 | - [[IModelDocExtension::IModelDocSelectByID2 Method]]<br>`MultiSelect.md` | - [[IModelDocExtension::SelectByID2 Method]]<br>`MultiSelect.md` | 同一 See Also 列表连写两条指向同一成员：一条成员名被粘成 IModelDocSelectByID2，下一条为正确的 SelectByID2。 |
| 36 | Sets document default user preference values. This method is intended for user preferences of type integer.<br>`GetUserPreferenceInteger.md` | Gets document default user preference values. This method is intended for user preferences of type double.<br>`GetUserPreferenceDouble.md` | 同族 Get/Set 用户偏好 5 页首句模板一致，本页写成 Sets（且 Remarks 写 setting），其余为 Gets/getting，属复制 Set 页未回改。 |
| 37 | Obsolete. Superseded [[IModelDocExtension::GetPersistReference3]].<br>`GetPersistReference.md` | Obsolete. Superseded by [[IModelDocExtension::GetPersistReferenceCount3]].<br>`GetPersistReferenceCount.md` | 废弃声明模板在同族页固定为 Superseded by，本页缺 by，句子不成立且与全族写法不一致。 |
| 38 | - reval[6]<br>`GetSectionProperties2.md` | - retval[7]<br>`GetSectionProperties2.md` | 同一 retval[0..23] 列表中第 6 项漏字写成 reval[6]，其余 23 项全部为 retval；同族 IGetSectionProperties2.md 有同一处同样的错。 |
| 39 | - in-process, unmanaged C++: Poitner to an array of material values for this component (see **Remarks**)<br>`IGetMaterialPropertyValues.md` | - in-process, unmanaged C++: Pointer to an array of configuration names for this component<br>`IGetMaterialPropertyValues.md` | 同页同一 Returns 模板两种拼法：Pointer 拼成 Poitner；本族其它 I 方法的 Returns 均作 Pointer。 |
| 40 | - **DipsObj**: Object<br>`IGetPersistReference3.md` | - **DispObj**: Object<br>`GetPersistReference3.md` | 同族同参数的形参名两种拼法：I 版写 DipsObj，非 I 版写 DispObj（IGetPersistReference.md 亦为 DipsObj）。 |
| 41 | True if the current custom drfting standard is deleted, false if not<br>`DeleteDraftingStandard.md` | Delete the current custom drafting standard.<br>`DeleteDraftingStandard.md` | 同页同一词两种拼法：正文写 drafting，Returns 写 drfting（缺 a）。 |
| 42 | - [Get Paths and Titles of Parent of Virutal Component (VB.NET)](../../examples/Get_Paths_and_Titles_of_Parent …<br>`IsVirtualComponent3.md` | - [Get Paths and Titles of Parent of Virtual Component (VBA)](../../examples/Get_Paths_and_Titles_of_Parents_o …<br>`IsVirtualComponent3.md` | 同一 Examples 列表三条链接指向同一文件名却有两种标题拼法，中间一条把 Virtual 写成 Virutal。 |
| 43 | True of the light is on, false if not<br>`GetLightEnabledInRender.md` | True if the light is kept when the scene changes, false if the light is deleted when the scene changes<br>`GetKeepLightInRenderScene.md` | 同族 Get*InRender/Get*InRenderScene 的 Returns 模板相同，本页把 if 写成 of，句子不成立。 |
| 44 | Displays the specified user notfication for this document.<br>`ShowUserNotification.md` | Closes the specified user notification in this document's window.<br>`CloseUserNotification.md` | 同族 Show/Close UserNotification 两页首句写同一名词，本页 notification 漏一个 i 写成 notfication。 |
| 45 | **Signature**: `System.int AddMenuItem( System.int DocType, System.string Menu, System.int Postion, System.str …<br>`AddMenuItem.md` | **Signature**: `System.int AddMenuItem4( System.int DocumentType, System.int Cookie, System.string MenuItem, S …<br>`AddMenuItem4.md` | 同一族的第三个形参，AddMenuItem 写成 Postion，AddMenuItem2/3/4/5 全写 Position。 |
| 46 | True if the add-in callback commands are set, false if if not<br>`SetAddinCallbackInfo.md` | True if the add-in callback commands are set, false if not<br>`SetAddinCallbackInfo2.md` | 后继页同一句是 "false if not"；前一页把 if 连写两次，且这两页是 obsolete/后继关系。 |
| 47 | Gets the open documents is this SOLIDWORKS Design session.<br>`IGetDocuments.md` | Gets the open documents in this SOLIDWORKS Design session.<br>`GetDocuments.md` | I 前缀页与其 late-binding 孪生页首句只差一字母：is / in，同一标识符族的两种拼法。 |
| 48 | In the handler of this event, a third-party application can call [[ISldWorks::SetPromptFileName2]] to open a d …<br>`CloseAndReopen.md` | # ISldWorks.SetPromptFilename2<br>`SetPromptFilename2.md` | 成员页自身声明的成员名是 SetPromptFilename2（N 小写）；同族 CloseAndReopen2.md 同样写成 FileName，两种拼法。 |
| 49 | - [[ISldWorks:GetOpenDocument Method]]<br>`EnumDocuments2.md` | - [[ISldWorks::CloseDoc Method]]<br>`EnumDocuments2.md` | 同一页 See Also 列表里 31-33 行用单冒号 ISldWorks:，34-38 行用双冒号 ISldWorks::；全库其余 300+ 处均为双冒号。 |
| 50 | If the selection filter is active, then the settings found in [[ISldWorks::GetSelectionFilter]] and [[ISldWork …<br>`SetApplySelectionFilter.md` | This method returns an empty array if mass properties are not calculated when saving the model. This is a syst …<br>`IGetMassProperties2.md` | 接口名 ISldWorks 被写成 ISldworks（小写 w）；孪生页 GetMassProperties2.md 同一句写的是 [[ISldWorks::SetUserPreferenceToggle]]。 |
| 51 | For the inital public release of SOLIDWORKS 2005, this method returns **13.0.0**.<br>`RevisionNumber.md` | For the initial public release, the minor decimal number is always **0.0**.<br>`RevisionNumber.md` | 同一页同一词两种拼法：26 行 inital，22/24/28 行 initial。 |
| 52 | Gets the name of the user who has the the specified document open.<br>`GetCurrentFileUser.md` | True if the the referenced document is replaced, false if not<br>`ReplaceReferencedDocument.md` | 两页都把定冠词连写两次 the the；同页/同族其余句子均为单个 the。 |
| 53 | If the conic rho values of Rho, RhoArray, or PointRhoArray are not in the valid range, then this method replac …<br>`FeatureFillet3.md` | - **RhoArr**: Array of conic rho or radius values for the specified ConicRhoType for selected edges for the va …<br>`FeatureFillet3.md` | 同页签名与参数表里参数名是 RhoArr，Remarks 散文写成 RhoArray；并列的 PointRhoArray 才是 Array 后缀，属 RhoArr 被误写。 |
| 54 | - one or more affected bodies or components (only if UseFeatScope is set to true and UseAutoSel is set to fals …<br>`FeatureRevolve2.md` | - **UseAutoSelect**: True to automatically select all bodies and have the feature affect those bodies, false t …<br>`FeatureRevolve2.md` | 同页参数定义与签名都是 UseAutoSelect，Remarks 里截短成 UseAutoSel，按名取参会找不到该形参。 |
| 55 | If you specify a value for TranslationParms or RotationParams, then do not specify a value for Distance or Ang …<br>`InsertMoveFace2.md` | - **TranslationParams**: Array of three doubles for the delta x, delta y, and delta z direction translation<br>`InsertMoveFace2.md` | 同一句中 RotationParams 拼对、TranslationParms 少一个 a；参数表与签名均为 TranslationParams。同错另见 IInsertMoveFace2.md 与 InsertMoveFace3.md。 |
| 56 | UseBaseLineDimensions controls which hole type-specific properties are valid. See [[IAdvancedHoleFeatureData:: …<br>`AdvancedHole.md` | - **UseBaselineDimensions**: True to use baseline dimensions, false to not (see **Remarks**)<br>`AdvancedHole.md` | 同一句内散文主体 UseBaseLineDimensions 与链接目标 UseBaselineDimensions 两种拼法；本页参数定义也是 Baseline。同错见 AdvancedHole2.md:50。 |
| 57 | [[ISelectData::Mark]] and [[Component2::Select3]]<br>`FeatureCircularPattern4.md` | [[ISelectData::Mark]] and [[IComponent2::Select3]]<br>`FeatureLinearPattern3.md` | 同族页面同一句式写成两种接口名；types\IComponent2\Select3.md 存在，而 types 下无 Component2 目录 —— Component2 少 I 前缀。同错见 FeatureCircularPattern5.md 与 Fea … |
| 58 | - [[IDrawngDoc::Create1stAngleViews2 Method]]<br>`CreateSectionView.md` | - [[IDrawingDoc::ActivateSheet Method]]<br>`SheetPrevious.md` | 同一 See Also 构造，CreateSectionView.md 整块 14 条链接把接口名写成 IDrawngDoc（ing/ng 字母换位）；同族页面一律是 IDrawingDoc。 |
| 59 | - [[IDrawingDoc::IICreateAngDim4 Method]]<br>`CreateDiamDim4.md` | - [[IDrawingDoc::ICreateAngDim4 Method]]<br>`CreateDiamDim4.md` | 同一页 6 行 See Also 中 3 条成员名多了一个 I（IICreateAngDim4 / IICreateLinearDim4 / IICreateOrdinateDim4），紧邻的正确写法是 I 前缀；本目录没有 IICreate*.md。 |
| 60 | Solid line: segCount = 1, segLenghts[] = {0.5}<br>`GetLineFontInfo2.md` | Dashed line: segCount = 2, segLengths[] = {0.25, -0.25}<br>`GetLineFontInfo2.md` | 同一段两个示例行，数组名 segLenghts 与 segLengths 字母顺序不同；本页 VARIANT 格式段也写作 double segLengths[segCount]。 |
| 61 | [[ISkethcManager::MakeSketchBlockFromFile]]<br>`CreateCustomSymbol.md` | [[ISketchManager::MakeSketchBlockSelected]]<br>`CreateCustomSymbol.md` | 同一句里接口名出现两种拼法：ISkethcManager（ethc）与 ISketchManager（etch）。本目录另有 5 页同样误写（ICreateCustomSymbol / IMakeCustomSymbol2 / MakeBlockDefinit … |
| 62 | - in-porcess, unmanaged C++: Pointer to an array of longs (see **Remarks**)<br>`IGetPenInfo.md` | - in-process, unmanaged C++: Pointer to an array containing the names of the drawing sheets in this drawing of …<br>`IGetSheetNames.md` | 同族 I* 页的固定措辞 in-process 被写成 in-porcess；IGetInsertionPoint.md 写的也是 in-process。 |
| 63 | - [[IDrawingDoc::SActivateSheet Method]]<br>`SheetNext.md` | - [[IDrawingDoc::ActivateSheet Method]]<br>`SheetPrevious.md` | SheetNext.md 的 See Also 里 11 条链接被统一加了字母 S 前缀（SActivateSheet…SSetupSheet4），而同页最后一条 [[IDrawingDoc::SheetPrevious Method]] 与 SheetPre … |
| 64 | - [[IModelDocExtensioin::AddOrdinateDimension Method]]<br>`InsertOrdinate.md` | - [[IModelDocExtension::AddOrdinateDimension Method]]<br>`InsertVerticalOrdinate.md` | 接口名 Extension 被写成 Extensioin（尾部多一个 i）；同一 See Also 列表里的 IModelDoc2::AlignOrdinate 等也按正确拼法写。 |
| 65 | - [[IDrawingDoc:BreakView Method]]<br>`UnBreakView.md` | - [[IDrawingDoc::BreakView Method]]<br>`InsertBreakVertical.md` | 接口与成员之间被写成单冒号；同族 InsertBreakVertical.md / InsertBreakHorizontal.md 都是双冒号。UnBreakView.md 内 3 条链接同错。 |
| 66 | - [[IDrawingDoc::IDrawingDoc::IActiveDrawingView Property]]<br>`SuppressView.md` | - [[IDrawingDoc::IActiveDrawingView Property]]<br>`UnsuppressView.md` | 接口名重复两遍；两页其余 See Also 完全对称（SuppressView/UnsuppressView 各 13 条），此条应与 quote_b 同形。 |
| 67 | - [[IDrawingDoc::CreateViewport3 Method ()]]<br>`CreateDetailViewAt4.md` | - [[IDrawingDoc::CreateViewport3 Method]]<br>`CreateDetailViewAt3.md` | 同一目标 CreateViewport3 的链接文本有两种写法，多了空括号 “Method ()”。本目录另有多页同错（AttachAnnotation / NewSheet4 / SetupSheet6 / EditTemplate 等）。 |
| 68 | Creates a an empty view in a drawing.<br>`CreateViewport3.md` | # IDrawingDoc.CreateViewport3<br>`CreateViewport3.md` | 正文首句冠词重复写成 “a an”；页面其余行（Remarks 里的 an empty view、empty view）均用单冠词。 |
| 69 | - [[IDrawingDoc:EditOrdinate Method]]<br>`AlignOrdinate.md` | - [[IDrawingDoc::EditOrdinate Method]]<br>`ChangeOrdDir.md` | 接口与成员之间写成单冒号；同一列表里 CreateOrdinateDim4 / InsertHorizontalOrdinate / InsertVerticalOrdinate 都是双冒号。AlignOrdinate.md 内 3 条同错（EditOrdin … |
| 70 | - SWCODYINTERSECT<br>`IMatchedBoolean3.md` | - SWBODYINTERSECT<br>`MatchedBoolean3.md` | 同一个枚举成员在同一族两页拼成两种：SWCODYINTERSECT / SWBODYINTERSECT。后者正确，IMatchedBoolean4 与 MatchedBoolean4 也都用 SWBODYINTERSECT，故 a 页是错字。 |
| 71 | Before changing the name of the body, call [[IFeaturemanager::IsNameUsed]] to find out if the name is unique a …<br>`Name.md` | To see the new name of the body in the FeatureManager design tree, call [[IFeatureManager::UpdateFeatureTree]] …<br>`Name.md` | 同一句里同一接口名两种大小写：IFeaturemanager / IFeatureManager。全库官方名为 IFeatureManager（带大写 M）。 |
| 72 | - 2 = Extend selected edges to PpUpToFace<br>`IExtendSurface.md` | - 2 = Extend selected edges to PUpToFace<br>`ExtendSurface.md` | 形参名多打一个 p。同页签名与参数表写的是 PUpToFace，ExtendSurface.md（Dispatch 版）也写 PUpToFace。 |
| 73 | - [[IModelDocExtenstion::SelectAll Method]]<br>`IGetEdges.md` | - [[IModelDocExtension::SelectAll Method]]<br>`GetEdges.md` | 接口名少一个 e：IModelDocExtenstion。两页讲同一个方法 IBody2::GetEdges / IGetEdges，GetEdges.md 拼写正确。 |
| 74 | Puv00, wuv00, Puv10, wuv10, Puv01, wuv01, Puv11, wuw11<br>`ICreatePsplineSurfaceDLL.md` | ( wu10*Pu10 wu11*Pu11 wuv10*Puv10 wuv11*Puv11 )<br>`ICreatePsplineSurfaceDLL.md` | 同一页同一序列第 8 项写成 wuw11，前 7 项与 W 矩阵第 4 行都是 wuv**。按平行项 v→u 属错字。 |
| 75 | To delete these four faces, specify swHealAction_Shrink for HealAction and swLoopProcess_Together for LoopProc …<br>`DeleteFaces5.md` | To delete the cylindrical face, specify swHealActionShrink_e for HealAction and swLoopProcess_Independent for  …<br>`DeleteFaces5.md` | 同一页前后两段引用同一枚举成员写成两种：swHealAction_Shrink / swHealActionShrink_e。 |
| 76 | ISurface::AddTrimmingLoop2(Numcurves, _<br>`CreateBodyFromSurfaces.md` | NumCurves<br>`CreateBodyFromSurfaces.md` | 同一页：调用示例里写 Numcurves（小写 c），紧接着的参数表第一行写 NumCurves。 |
| 77 | Before calling this method, call [[IModelDoc2::GetConfigurationCount]] to get the value for Config_Count.<br>`IRemoveMaterialProperty.md` | - **Config_count**: Number of configurations in the part or assembly<br>`IRemoveMaterialProperty.md` | 同一页形参名 Config_count（大写 C 的 Config_Count）只在 Remarks 出现一次，拼法不一致。 |
| 78 | - **StartVec**: Array of of 3 doubles representing a point close to the start of the blend spine<br>`CreateBlendSurface.md` | - **StartVec**: Array of 3 doubles representing a point close to the start of the blend spine<br>`ICreateBlendSurface.md` | 同义句连写两个 of。ICreateBlendSurface.md（同族 in-process 版）无此重复。 |
| 79 | - [Get Bodies in Componets (VB.NET)](../../examples/Get_Bodies_in_Components_Example_VBNET.md)<br>`Name.md` | - [Get Bodies in Components (C#)](../../examples/Get_Bodies_in_Components_Example_CSharp.md)<br>`Name.md` | 同一页三个同族示例标题，两个写 Components、一个写 Componets，而链接目标文件名拼的是 Components。 |
| 80 | You can use this method instead of [[IBody2:CreateTrimmedSurface]], [[IBody2::ICreatePlanarSurface]], and [[IS …<br>`ICreatePlanarTrimSurfaceDLL.md` | Then, trim the surface using [[IBody2::CreateTrimmedSurface]].<br>`SetCurrentSurface.md` | 同一 wiki 链接同一标识符两种写法：IBody2:CreateTrimmedSurface（单冒号）/ IBody2::CreateTrimmedSurface（双冒号）。CreatePlanarTrimSurfaceDLL.md 同样用单冒号。 |
| 81 | Before calling this method, call [[IBody2:IDeleteFacesMakeSheetBodiesCount]] to get the number of sheet bodies …<br>`IDeleteFacesMakeSheetBodies.md` | To create sheet bodies from deleted faces, call [[IBody2::IDeleteFacesMakeSheetBodies]].<br>`IDeleteFacesMakeSheetBodiesCount.md` | 同一对互指页，一条用单冒号 IBody2:X，另一条用双冒号 IBody2::X；全库主流写法是双冒号。 |
| 82 | - **ToolBodyArr**: Array of [[bodies]] of size toolBodyCount<br>`IMatchedBoolean4.md` | - **ToolBodyArr**: Array of bodies of size ToolBodyCount<br>`IMatchedBoolean3.md` | 同一接口族的兄弟页把同一形参写成 toolBodyCount / ToolBodyCount，大小写不一致。 |
| 83 | - **NewEnityToMateTo**: Array of new mate references that map to the Repeat arrays;<br>`CopyWithMates.md` | - **Repeat**: Array of boolean values; each value indicates whether to use the existing mate reference for the …<br>`CopyWithMates.md` | 同一页两行：参数定义行拼作 NewEnityToMateTo（少一个 t），紧接着的正文与 FlipAlignment 行都写 NewEntityToMateTo。同一标识符两种拼法。 |
| 84 | - **Values**: Array of distance or angle values for the mate references; specify distance in meters and angle  …<br>`CopyWithMates.md` | - **Values**: Array of distance or angle values for the mate references; specify distance in meters and angle  …<br>`CopyWithMates2.md` | 同族姊妹页 CopyWithMates.md 连写两个 for（valid for for），CopyWithMates2.md 同位置只有一个 for。 |
| 85 | The Where argument indicates where the Source should be moved relative to the Target as defined by swReorderCo …<br>`ReorderComponents.md` | If the Where argument is specified as one of the two folder-related values, but the Target is a component, the …<br>`ReorderComponents.md` | 同一段内两种拼法：swReorderComponentsWhere_e 与 swReorderCompentsWhere_e（Compents 少一个 n）。同族 IReorderComponents.md 也只写正确的 swReorderComponents … |
| 86 | - **Config_opt**: Configurations from which to retrieve active ground planes as defined in [[swInConfiguration …<br>`GetActiveGroundPlane.md` | - **Config_names**: Array of the names of configurations from which to retrieve active ground planes; valid on …<br>`GetActiveGroundPlane.md` | 同一页：参数定义行链的是 swInConfigurationOpts_e，下一行正文写成 swInConfiguration_e（少 Opts）。C:\swapi\enums 下无 swInConfiguration_e.md。 |
| 87 | - swAllConfigurations<br>`ActivateGroundPlane.md` | - swInConfigurationOpts_e.swAllConfiguration,<br>`SetSpeedPakConfigurations.md` | 同一枚举成员两种拼法：swAllConfigurations（复数）vs swAllConfiguration（单数）。C:\swapi\enums\swInConfigurationOpts_e.md 的成员表写的正是 swAllConfiguration。 |
| 88 | - **Face_or_Plane_to_select**: [[Face]] or [[reference plane]] where to insert the new part<br>`InsertNewPart2.md` | - **FaceOrPlaneToSelect**: Plane or planar face<br>`InsertNewVirtualPart.md` | 同族（插入新零件）两页同一个面/平面参数写成两种拼法：Face_or_Plane_to_select 与 FaceOrPlaneToSelect。 |
| 89 | The scope of the assembly feature determines which components are effected by this feature. In other words, it …<br>`AddToFeatureScope.md` | The scope of the assembly feature determines which components are affected by this feature. In other words, it …<br>`RemoveFromFeatureScope.md` | 两句除 affected/effected 外逐字相同：同族姊妹页受影响/未受影响 两种拼法（effected 误用）。 |
| 90 | There are two ways to use the this technique:<br>`RemoveFromFeatureScope.md` | There are two ways to use the IAssemblyDoc::AddToFeatureScope method:<br>`AddToFeatureScope.md` | 同族姊妹页同一句式：RemoveFromFeatureScope.md 连写两个 the（the this），AddToFeatureScope.md 只一个。 |
| 91 | Obsolete. Superseded by [[SelectionMgr::GetSelectedObject6]].<br>`IGetSelectedMember.md` | Obsolete. Superseded by [[ISelectionMgr::GetSelectedObject6]].<br>`GetSelectedMember.md` | 同一对方法的两页写同一个接口名两种拼法：SelectionMgr 少了接口前缀 I。C:\swapi\types\ISelectionMgr\GetSelectedObject6.md 存在（我已 Test-Path 确认）。 |
| 92 | Call this method before calling [[IAssembly_Doc::IGetVisibleComponentsInView]].<br>`GetVisibleComponentsInViewCount.md` | - [[IAssemblyDoc::IGetVisibleComponentsInView Method]]<br>`GetVisibleComponentsInView.md` | 同一接口名两种拼法：IAssembly_Doc（多一个下划线）vs IAssemblyDoc。本族其余 196 处都写 IAssemblyDoc；C:\swapi\types 下无 IAssembly_Doc 目录。 |
| 93 | - in-process, unmanaged C+: Pointer to an array of data used to create the items (converted edge or face, conv …<br>`IListExternalFileReferences2.md` | - in-process, unmanaged C++: Pointer to an array of path names of documents of size NumRefs<br>`IListExternalFileReferences2.md` | 同一页 Parameters 里 7 个平行条目全部写 "unmanaged C++:"，唯独 DataType 那条写成 "unmanaged C+:"，少一个加号。 |
| 94 | - **PceltFetched**: Pointer to the number of model views returned from the list; this value can be less than c …<br>`Next.md` | - **Rgelt**: Pointer to an array of [[model views]] of size Celt<br>`Next.md` | 同一页同一签名里形参是 **Celt**（大写 C），下一条散文却写成小写 celt，标识符两种拼法。 |
| 95 | After calling IComponent2::RemovePresentationTransfrom, the component is next drawn in a position consistent w …<br>`RemovePresentationTransform.md` | # IComponent2.RemovePresentationTransform<br>`RemovePresentationTransform.md` | 同页标题与上一行正文都写 RemovePresentationTransform，唯独此行把 Transform 拼成 Transfrom（r 移到 n 后）。 |
| 96 | specify -120 to to zoom in one click<br>`MouseWheelXYZ.md` | and specify 120 to to zoom out<br>`MouseWheelXYZ.md` | 同一行两次把 "to" 连写两遍（to to）；同族 Move.md / MoveXYZ.md 的对应句无此重复。 |
| 97 | - swSeleVERTICES<br>`IGetEntityByName.md` | - swSelVERTICES<br>`GetEntityByName.md` | 同族同位置的枚举成员拼成两种：swSeleVERTICES（多一个 e）与 swSelVERTICES。全树 13 处用后者，仅此 1 页用前者。 |
\| 98 \| - The last three elements of the array are valid only if Action = swExportToDWG_e.swExportToDW_ExportSelectedF …<br>`ExportToDWG2.md` \| \| swExportToDWG_ExportSelectedFacesOrLoops \| 2 \|<br>`swExportToDWG_e.md` \| 同页上文另两处写 swExportToDWG_ExportSheetMetal / ...ExportAnnotationViews（带 G），唯独此行漏 G；枚举页权威名为 swExportToDWG_...。 \|
| 99 | - [[IGetEntityByName Method]]<br>`GetEntityByName.md` | - [[IPartDoc::IDeleteEntityName Method]]<br>`GetEntityByName.md` | 同一 See Also 列表里其余 9 条成员链接都带 IPartDoc:: 前缀，只有这条漏掉接口限定符。这是 179 页里唯一一条无限定符的成员链接（裸链无法解析）。 |
| 100 | - [[IDisplayDimensioin::GetArcLengthLeader Method]]<br>`SetArcLengthLeader.md` | - [[IDisplayDimension::GetArcLengthLeader Method]]<br>`GetAutoArcLengthLeader.md` | 同一接口名在本族两页拼成两种：SetArcLengthLeader.md 把 IDisplayDimension 字母顺序写反成 IDisplayDimensioin（i-o-i-n），GetAutoArcLengthLeader.md 是正确拼法。 |
| 101 | - **UType**: Unit display setting as defined in [[swLengthUnits_e]] or [[swAngleUnits_e]]<br>`SetUnits.md` | - **UType**: Unit display setting as defined in [[swLengthUnit_e]] or [[swAngleUnit_e]]; valid only if UseDoc  …<br>`SetUnits2.md` | 同族两页指向同一组单位枚举，只差一个 s。enums 目录下只有 swLengthUnit_e / swAngleUnit_e，没有 ...Units_e 版本。 |
| 102 | - [[IDisplayDimension::GetPrimaryTolPrecision2 Method]]<br>`GetAlternatePrecision2.md` | - [[IDisplayDimension:GetAlternatePrecision2 Method]]<br>`GetPrimaryPrecision2.md` | 同族 See Also 里接口与成员的连接符写成两种：多数页用 ::，GetPrimaryPrecision2/GetPrimaryTolPrecision2/GetAlternatePrecision2 三页用单冒号，单冒号目标解析不到。 |
| 103 | Expand, compress, or leave the state of the PropertyManage page's message as is.<br>`_overview.md` | Allows you to access a [[PropertyManager page]] slider control.<br>`_overview.md` | 同一批 target 里接口名出现两种拼法：swconst 那页写成 PropertyManage（少一个 r），Slider 那页与其自身 name: 字段均为 PropertyManager。 |
\| 104 \| \| swExternalFileReferencesLockAll \| 2 \|<br>`swExternalFileReferencesUpdate_e.md` \| \| swExternalFileReferencesunlockAll \| 3 \|<br>`swExternalFileReferencesUpdate_e.md` \| 同一成员列表里 BreakAll / LockAll / UpdateNone 都大写开头，唯独这一条把 unlock 的 u 写成小写，同一标识符前缀出现两种拼法。 \|
| 105 | Obsolete. Superseded by IPropertyManagerpageGroup::AddControl2.<br>`AddControl.md` | Obsolete. Superseded by IPropertyManagerPageGroup::AddControl2.<br>`IAddControl.md` | 接口正式名 IPropertyManagerPageGroup（目录名与 IAddControl 页标题都是它），AddControl 页把 Page 的 P 写成小写 page。 |
| 106 | When you specify swAddControlOptions_e.swControlOptions_SmallGapAbove for the Options parameter, the gap creat …<br>`AddControl2.md` | # IPropertyManagerPageGroup.IAddControl<br>`IAddControl.md` | 同一句里两个成员同属一个接口，第二个少了 Page；本接口的 IAddControl 页自身标题用的是带 Page 的写法。 |
| 107 | The data returned from this method is in terms of document apace.<br>`GetArcAtIndex.md` | The data returned from this method is in terms of document space. If the document containing this note is a dr …<br>`GetLineAtIndex.md` | GetArcAtIndex 与 IGetArcAtIndex 把 space 拼成 apace；同族 GetLineAtIndex / IGetLineAtIndex / GetTextPositionAtIndex 的同一句是 space。 |
| 108 | - [[INote::INote::AddText Method]]<br>`GetTextCount.md` | - [[INote::GetTextJustification Method]]<br>`GetTextCount.md` | 同一 See Also 列表内接口前缀被写了两遍 INote::INote::（第 45、46 行）；INote 目录下并无 INote.md，这两条按此写法解析不到。 |
| 109 | Obsolete. Superseded by [[IAnnotation::GetTextFormat]] and [[IAnnotation::GetTextFormat]].<br>`IGetTextFormatAtIndex.md` | Obsolete. Superseded by [[IAnnotation::GetTextFormat]] and [[IAnnotation::IGetTextFormat]].<br>`IGetTextFormat.md` | 两个并行页同一句：IGetTextFormatAtIndex 把第二个 IGetTextFormat 写成 GetTextFormat，两条链接指向同一目标，后继项实际缺失。 |
| 110 | - HasExtraLeader() == false implies a straight leaderline and1 line (PointCount=2)<br>`GetLeaderInfo.md` | - HasExtraLeader() == false implies that this is a straight leaderline and 1 line (PointCount=2)<br>`GetLeaderAtIndex.md` | 同族同一条规则，GetLeaderInfo 与 IGetLeaderInfo 把 “and 1” 连写成 “and1”，GetLeaderAtIndex/IGetLeaderAtIndex 则分开写。 |
| 111 | To set this the specified text's line spacing, use [[IAnnotation::SetTextFormat]] and [[IAnnotation::ISetTextF …<br>`GetTextLineSpacingAtIndex.md` | Before using this method, use [[INote::GetTextCount]]. To set the specified text's font, use [[IAnnotation::Se …<br>`GetTextFontAtIndex.md` | 同族同一句式，GetTextLineSpacingAtIndex 多插了一个 this，连成 “this the”；GetTextFontAtIndex 等页均为 “To set the specified text's ...”。 |
| 112 | Obsolete for documents created in SOLIDWORKS 2016 and later. Gets whether the text item's offset relative to n …<br>`IGetTextOffsetAtIndex.md` | Obsolete for documents created in SOLIDWORKS 2016 and later. Gets the text item's offset relative to note's te …<br>`GetTextOffsetAtIndex.md` | 同一对 Get/IGet 页的首句，本页把 the 换成 whether；该方法返回坐标数组（见 Returns: Array of doubles），不是布尔。 |
| 113 | This property cannot be changed after it is set by [[ICornerReliefFeatureData::Intialize]].<br>`CornerType.md` | # ICornerReliefFeatureData.Initialize<br>`Initialize.md` | 同目录真实成员名是 Initialize（见 b）；a 处拼成 Intialize，少一个 t。该链接目标因此也不存在。 |
| 114 | - [[IAsemblyDoc::GetBox Method]]<br>`IGetBox.md` | - [[IAssemblyDoc::GetBox Method]]<br>`GetBox.md` | 同一族两页指向同一接口，a 少一个 s（IAsemblyDoc）。C:\swapi\types 下只有 IAssemblyDoc，无 IAsemblyDoc。 |
| 115 | The tolerance zone types returned by this method map on-to-one and onto with tolerance zone values returned by …<br>`GetTolTypes.md` | The array returned by this method maps one-to-one and onto with the array returned by [[IPMIGtolBoxData::GetTo …<br>`GetTolTypeValues.md` | 同族两页互相引用同一对方法，a 写 on-to-one，b 写 one-to-one，同一术语两种拼法。 |
| 116 | **Then Feature::SetBodyw...**<br>`SetBody2.md` | **Then Feature::ISetBody3...**<br>`ISetBody3.md` | 同一张 If/Then 表模板，a 处方法名多一个尾字母 w（SetBodyw），本方法实名是 SetBody2。 |
| 117 | A change in a the state setting of a feature causes all its dependents to inherit the same behavior, without a …<br>`SetUIState.md` | A change in a feature state setting causes all the dependents of the feature to inherit the same behavior, wit …<br>`GetUIState.md` | 同族成对方法同段落，a 多出冠词写成 a the state setting，b 无误。 |
| 118 | Applied to this feature in Cofig_name<br>`GetTexture.md` | - **Config_name**: Name of the configuration<br>`GetTexture.md` | 同一页：形参名是 Config_name（签名与参数段），Returns 表里同一标识符拼成 Cofig_name，少一个 n。 |
| 119 | Before you can get a feature's IDisplayDimension, use [[IModelDoc2::SetUserPreferenceToggle]] and swDisplayFea …<br>`GetFirstDisplayDimension.md` | Before you can get a feature's IDisplayDimension, use [[IModelDoc2::SetUserPreferenceToggle]] and swDisplayFea …<br>`GetNextDisplayDimension.md` | 同族相邻两页同一句前置，枚举名一为复数 Dimensions、一为单数 Dimension，同一标识符两种写法。 |
| 120 | - [[IFeature:CreatedBy Property]]<br>`DateCreated.md` | - [[IFeature::CreatedBy Property]]<br>`DateModified.md` | 同族两页互指，a 用单冒号 IFeature:CreatedBy，b 用双冒号 IFeature::CreatedBy，全库交叉引用均为双冒号写法。 |
| 121 | - [[IComponent2:IListExternalFileReferences2 Method]]<br>`IListExternalFileReferences2.md` | - [[IComponent2::UpdateExternalFileReferences Method]]<br>`IListExternalFileReferences2.md` | 同一页同一 See Also 块内：第 58/59/60 行用单冒号 IComponent2:，第 61 行用双冒号 IComponent2::。 |
\| 122 \| \| swInsertholeCallout \| 1048576 or 0x100000 \|<br>`swInsertAnnotation_e.md` \| \| swInsertCThreads \| 1 or 0x1; insert annotation cosmetic threads \|<br>`swInsertAnnotation_e.md` \| 同一成员表内 26 项一律用 swInsert + 大写名词；仅此项 h 为小写。全库仅此一处 swInsertholeCallout，无第二种拼法可对照。 \|
| 123 | - [[IModeler:::CreateRuledSurface Method]]<br>`CreateLoftSurface.md` | - [[IModeler::CreateRuledSurface Method]]<br>`CreateExtrusionSurface.md` | 分隔符三个冒号；IModeler 全族其余交叉引用一律是两个冒号。 |
| 124 | - **RefDir**: rray containing 3 doubles<br>`CreateSphericalSurface2.md` | - **RefDir**: Array containing 3 doubles<br>`ICreateSphericalSurface2.md` | 同名参数 RefDir 在同族两页各一种拼法，CreateSphericalSurface2 那行缺首字母 A。 |
| 125 | - **Sheets**: Array containing the [[shee]]ts<br>`CreateBodiesFromSheets2.md` | - **Sheets**: Array containing the [[sheets]]<br>`ICreateBodiesFromSheets2.md` | 同一参数两页两种写法；前者 wiki 链接被截成 [[shee]] 再接 ts。 |
| 126 | ref Curve CurveArra1<br>`ICreateBrepBody3.md` | The CurveArray1 and CurveArray2 must be paired<br>`ICreateBrepBody3.md` | 同一页签名与参数表写 CurveArra1，同页 Remarks 写 CurveArray1。对照 CreateBrepBody3.md 签名用 System.object CurveArray1。 |
| 127 | - [[IFeature::ModifyDefintion]] or [[IFeature::IModifyDefinition2]] if you modified the feature<br>`AccessSelections.md` | use [[IFeature::ModifyDefinition]] if you did modify the heal edges feature<br>`ReleaseSelectionAccess.md` | 同一族两页引用同一成员，两种拼法；Defintion 少一个 i。 |
| 128 | - **SemiAngle**: e **Remarks**<br>`CreateConicalSurface2.md` | - **Radius**: See **Remarks**<br>`CreateConicalSurface2.md` | 同一页相邻两行同一格式，SemiAngle 那行首词被截成单字母 e。 |
| 129 | TheCylArray argument is the following array of doubles:<br>`CreateBodyFromCyl.md` | The ConeArray argument is the following array of doubles:<br>`CreateBodyFromCone.md` | 同族同句式两种写法；且两页形参实名分别是 CylDimArray / ConeDimArray，正文写的 ConeArray/CylArray 都不是形参名。 |
| 130 | - **Children**: Array of parents, one in each relationship<br>`CreateBrepBody3.md` | - **Children**: Array of children, one in each relationship<br>`ICreateBrepBody3.md` | 同一参数的说明在同族两个页面被写成不同文字；本页 Parents 一行也是 Array of parents，两行无法区分。 |
| 131 | - [[IGTol::SetAllOver Method ()]]<br>`GetAllOver.md` | - [[IGtol::GetAllOverThisSide Method ()]]<br>`GetAllAroundThisSide.md` | 同一 IGtol 目录内接口名两种大小写：6 个页面共 11 处写 [[IGTol]]，其余全部写 [[IGtol]]。 |
| 132 | - [Get Text Items in GTol Frame (VB. NET)](../../examples/Get_Text_Items_in_GTol_Frame_Example_VBNET.md)<br>`GetTextAtIndex.md` | - [Get Text Items in GTol Frame (VB.NET)](../../examples/Get_Text_Items_in_GTol_Frame_Example_VBNET.md)<br>`GetTextCount.md` | 两处指向同一个 VBNET 例子文件；同族 19 处写 (VB.NET)，只有 GetTextAtIndex.md 在 VB 与 NET 之间多一个空格。 |
| 133 | Gets the number of linea in this GTol.<br>`GetLineCount.md` | Number of lines<br>`GetLineCount.md` | 同页摘要行把 lines 拼成 linea，紧接着的 Returns 行又写回 lines；成员名本身是 GetLineCount。 |
| 134 | The temporary buffer of edges is destroyed after each call to IFace2::GetEdges, IFace2::IGetEdges, or IFaces2: …<br>`GetEdges.md` | Therefore, call IFace2::GetEdges, IFace2::IGetEdges, or IFace2::EnumEdges in the same loop and immediately aft …<br>`IGetEdges.md` | 同族两页同一接口两种拼法：GetEdges.md 与 IGetEdges.md 正文把 IFace2::EnumEdges 写成 IFaces2::EnumEdges（多一个 s），而同句后半段与另页都写 IFace2。 |
| 135 | - [[IFae2::GetAllDecalProperties Method]]<br>`GetDecalsCount.md` | Call this method before calling [[IFace2::IGetAllDecalProperties]] to get the size of the array for that metho …<br>`GetDecalsCount.md` | 同一页 See Also 写 IFae2（c 写成 a），同页 Remarks 写 IFace2。无 IFae2 目录；GetAllDecalProperties.md 在 IFace2 目录下存在。 |
| 136 | The return value from this method is the number of floats returned from IFace2::GetTessTriStrips and IFace2::I …<br>`GetTessTriStripSize.md` | Gets the array size required for [[IFace2::GetTessTriStrips]] and [[IFace2::IGetTessTriStrips]].<br>`GetTessTriStripSize.md` | 同一页同一成员两种拼法：首句 IGetTessTriStrips，Remarks 写成 IGEtTessTriStrips（Get 字母换位为 GEt）。IGetTessTriStrips.md 存在。 |
| 137 | - [[IFace2::IFace2::IGetTrimCurveTopology Method]]<br>`GetTrimCurveTopology.md` | - [[IFace2::GetTrimCurveTopologyCount Method]]<br>`GetTrimCurveTopology.md` | 同一 See Also 列表内接口前缀重复：IFace2::IFace2::，其余条目均单前缀。IGetTrimCurveTopology.md 实际存在。 |
| 138 | [[IFace::GetTessTriStripNorms]]<br>`IGetFacetData.md` | [[IFace2::IGetTessTriStripNorms]]<br>`IGetFacetData.md` | 同一页 Obsolete 继承句里同一接口两种拼法：IFace::GetTessTriStripNorms 少末尾 2，其余 11 个链接均为 IFace2::。types 下只有 IFace2 目录，无 IFace。 |
| 139 | Call this method before calling [[IDeleteBodyFeautre::IGetBodies]] to determine the size of the array.<br>`GetBodiesCount.md` | - [[IDeleteBodyFeatureData Interface]]<br>`ISetBodies.md` | 接口名拼错 IDeleteBodyFeautre（Feature 字母换位成 Feautre）。同族 ISetBodies.md 正确写 IDeleteBodyFeatureData；无该拼写的目录。 |
| 140 | Call [[IDeleteBodiesFeatureData::GetBodiesCount]] before calling this method to get the number of bodies to de …<br>`IGetBodies.md` | - [[IDeleteBodyFeatureData Interface]]<br>`IGetBodies.md` | 同一页两种拼法：Remarks 写 IDeleteBodiesFeatureData（Body 多一个 s），See Also 与 frontmatter 写 IDeleteBodyFeatureData。无该拼写目录。 |
| 141 | - [[IDeleteBodyBodyFeatureData::GetBodiesCount Method]]<br>`ISetBodies.md` | - [[IDeleteBodyFeatureData Interface]]<br>`ISetBodies.md` | 同一 See Also 列表内 Body 重复：IDeleteBodyBodyFeatureData，而本页前两条却是正确的 IDeleteBodyFeatureData。该串出现 3 次，全指向不存在的接口。 |
| 142 | This property is valid only if [[ISimpleCornerTreatmentFeatureData::PlanarTrimToolType]] is set to [[swCornerT …<br>`UserDefinedTrimFaces.md` | Planar trim tool type as defined by [[swCornerTreatmentPlanarTrimToolType_e]]<br>`PlanarTrimToolType.md` | 枚举名拼错 swCornerTreatmentPlanarTriimToolType_e（Trim 多一个 i）。同族另两页均写 swCornerTreatmentPlanarTrimToolType_e；enums 下无该 Triim 文件。 |
| 143 | Call this method before calling IFace2::IGetSilhoutte.<br>`IGetSilhoutteEdgeCount.md` | the number of edges returned by [[IFace2::IGetSilhoutteEdges]] for a given vector root point (root) and a vect …<br>`IGetSilhoutteEdgeCount.md` | 同句成员名被截断为 IFace2::IGetSilhoutte，正确名是前半的 IGetSilhoutteEdges。目录内无 IGetSilhoutte.md。 |
| 144 | packedDouble4, packedDouble5, packedDouble6, packedDouble7, surfaceKnotValuesU[ ], surfaceKnotValuesV[ ], surf …<br>`GetTrimCurves2.md` | PackedDouble5<br>`GetTrimCurves2.md` | 同一字段两种大小写：b-spline 数组式样与 packedDouble1/2/3/7/8 全小写 p，而下方定义段标题写成 PackedDouble5、PackedDouble6，同段其余为 packedDouble4、packedDouble7。 |
| 145 | or to both [[IFace2::EnumEdges]] and Face2::GetTrimCurves2, then:<br>`GetTrimCurves2.md` | A call to [[IFace2::IGetTrimCurveSize2]] must precede the call to IFace2::GetTrimCurves2 to get the size of th …<br>`GetTrimCurves2.md` | 同页同一接口名两种写法：Face2::GetTrimCurves2 少开头的 I，全页其余十余处均写 IFace2::GetTrimCurves2。 |
| 146 | Call this method before calling [[ISketch::IGetSketchPcitures]] to get the size of the array for that method.<br>`GetSketchPictureCount.md` | member: IGetSketchPictures<br>`IGetSketchPictures.md` | 同族两页同一成员名两种拼法：Pcitures 与 Pictures（c/t 换位）。实际成员页为 IGetSketchPictures.md，且同目录 GetSketchPictures.md 的 See Also 也写作 [[ISketch::IGetSke … |
| 147 | To get the number of edges, call [[ISketch::GetContourEdgesCount]] before calling this method.<br>`IGetContourEdges.md` | - [[ISketch::GetContourEdgeCount Method]]<br>`GetContourEdges.md` | GetContourEdgesCount 与 GetContourEdgeCount 两种拼法；ISketch 目录下只有 GetContourEdgeCount.md，无 GetContourEdgesCount.md，该链接指向不存在的成员。 |
| 148 | Obsolete. Superseded by [[ISketch::IGetSplineParameters3]].<br>`IGetSplineParams2.md` | # ISketch.IGetSplineParams3<br>`IGetSplineParams3.md` | IGetSplineParameters3 与 IGetSplineParams3 两种拼法（多出 'meter'）。ISketch 目录下不存在 IGetSplineParameters3.md，实际后继成员是 IGetSplineParams3。 |
| 149 | Value is used for polyline font information. This value can be used as an input to the [[IDrawingDoc::GetLineF …<br>`GetEllipses3.md` | Value is used for polyline font information. This value can be used as an input to the [[IDrawingDoc::GetLineF …<br>`IGetEllipses3.md` | 同一句内 IDrawingDoc 与 IDrawinDoc 两种拼法（IDrawinDoc 少一个 g）。已核：C:\swapi\types\IDrawingDoc 目录存在，C:\swapi\types\IDrawinDoc 目录不存在。同一句缺陷在 Get … |
| 150 | Before calling htis method, call [[ISketch::GetSketchSlotCount]] to get Count.<br>`IGetSketchSlots.md` | Before calling this method, call [[ISketch::GetSketchRegionCount]] to get Count.<br>`IGetSketchRegions.md` | 同族两页完全同构的一句，只差 this/htis 的字母换位。IGetSketchRegions.md 为正确拼法。 |
| 151 | f the sketch already has constraints, then no constraints are added (in the same<br>`ConstrainAll.md` | If the sketch contour is not closed or contains interior non-construction elements, this method returns 0.<br>`GetContourEdgeCount.md` | ConstrainAll.md 的 Remarks 段首字母 I 丢失，变成 'f the sketch ...'；同族正确写法见 GetContourEdgeCount.md 的 'If the sketch contour ...'。 |
| 152 | The 32-bit integer returned may be to small to contain the 64-bit window handle/pointer, and will be truncated …<br>`AddPage.md` | This method is only available through early binding and with 64-bit versions of the SOLIDWORKS Design software …<br>`AddPagex64.md` | 同一接口姊妹页谈同一 64-bit 主题；AddPage.md 把 'too small' 拼成 'to small'（少一个 o），且该短语在本批 197 页中别处不存在第二种写法。 |
| 153 | Gets or sets whether the decal hidden.<br>`Hidden.md` | Gets or sets whether the mask is inverted.<br>`MaskInvert.md` | 同接口两页完全同构的一句；Hidden.md 漏掉系动词 is，变成 'whether the decal hidden'。 |
| 154 | **Signature**: `DimXpertDatum IGetPrimaryDatums( System.int Count )`<br>`IGetPrimaryDatums.md` | - in-process, unmanaged C++: Pointer to an array of [[IDimXpertDatum]]<br>`IGetTertiaryDatums.md` | 返回类型在同一接口内两种拼法：DimXpertDatum 与 IDimXpertDatum（少 I）。已核 C:\swapi\types\IDimXpertDatum 目录存在。IGetSecondaryDatums.md 同样如此。 |
| 155 | - [Is Selected Feature a Boundary Box Sektch (VB.NET)](../../examples/Is_Selected_Feature_a_Boundary_Box_Sketc …<br>`IsBoundaryBoxSketch.md` | - [Is Selected Feature a Boundary Box Sketch (C#)](../../examples/Is_Selected_Feature_a_Boundary_Box_Sketch_Ex …<br>`IsBoundaryBoxSketch.md` | 同一列表三条示例，C# 与 VBA 写 Sketch、VB.NET 写 Sektch（k/kt 换位）；且三条的链接目标文件名都是 Sketch。 |
| 156 | gets or sets whether the option is selected.<br>`Checked.md` | Gets or sets the caption for this option.<br>`Caption.md` | 同接口三个属性页（Checked / Caption / Style）的描述句首都应为 'Gets or sets'；只有 Checked.md 写成小写 g。 |
| 157 | Ture to have the free length dynamically update model changes while the PropertyManager page is open, false to …<br>`UpdateToModelChanges.md` | True to reverse the direction of this simulation spring feature, false to not<br>`ReverseDirection.md` | 同一接口同一 Returns 句式，UpdateToModelChanges 把 True 拼成 Ture；ReverseDirection 等兄弟页均为 True。 |
| 158 | Scale if more pronounced for low [[amplitude]] values. [[Radius]] also affects the pattern incidence for dimpl …<br>`BumpScale.md` | Scale controls the pattern of surface finish elements. A higher scale decreases the pattern incidence, and a l …<br>`BumpScale.md` | 同一页 Remarks 前句用 controls/decreases/increases 的第三人称 -s，后句却写成 if，应为 is；属同一标识符两种拼法。 |
| 159 | If BumpUseMappingScale is set to FALSE, then specify the [[scale]] and mapping for this surface finish for thi …<br>`BumpUseMappingScale.md` | True to use the material's scale and mapping, false to not<br>`BumpUseMappingScale.md` | 同一页 Returns 用小写 false，Remarks 用全大写 FALSE；布尔字面量大小写两种拼法并存。 |
| 160 | - [[IParagraphis::SetTextSegmentFormat Method ()]]<br>`GetTextSegmentFormat.md` | - [[IParagraphs::GetTextSegmentText Method ()]]<br>`GetTextSegmentFormat.md` | 同一页 See Also 里同一个接口出现两种拼法：IParagraphis（多一个 i）与 IParagraphs。目录名、页面标题、以及本目录其余 13 页一律是 IParagraphs。 |
| 161 | - [[IParagraphics::GetTextSegmentFormat Method ()]]<br>`SetTextSegmentFormat.md` | set the current paragraph using [[IParagraphs::CurrentParagraph]].<br>`SetTextSegmentFormat.md` | 同页两条链接两种拼法：IParagraphics（多 ic）与 IParagraphs。同族两页合起来共出现三种写法 IParagraphs / IParagraphis / IParagraphics。 |
| 162 | Obsolete. Superseded by [[IAnnotation::GetAtatchedEntityCount3]].<br>`GetAttachedEntityCount2.md` | # IAnnotation.GetAttachedEntityCount3<br>`GetAttachedEntityCount3.md` | 交叉引用拼写缺字母 t：Atatched vs Attached。后继页在本目录确实存在（GetAttachedEntityCount3.md），故该引用指向一个不存在的页名，同时构成 dead link。 |
| 163 | in the IAnnotation::GetAttachedEntites2 array<br>`GetAttachedEntities2.md` | # IAnnotation.GetAttachedEntities2<br>`GetAttachedEntities2.md` | 同一页正文把成员名写成 Entites2（漏 i），标题写 Entities2。同型错误在 GetAttachedEntities3.md 正文再次出现（GetAttachedEntites3）。 |
| 164 | Ture if the operation succeeds, false if it fails<br>`AddOrUpdateStyle.md` | True if the operation succeeds, false if it fails<br>`ApplyDefaultStyleAttributes.md` | Returns 首字母拼错：Ture vs True。同句式在同族两页各写一种；LoadStyle.md 还有第三处 Ture if the style is loaded。 |
| 165 | - in-process, in-process, unmanaged C++: Pointer to an array of longs<br>`IGetAttachedEntityTypes.md` | - in-process, unmanaged C++: Pointer to an array of 5 longs<br>`IGetVisualProperties.md` | 同一 in-process 方法族的 Returns 前缀，本页把 in-process 连写两次；同族页只写一次。同型成员还有 IGetLeaderPointsAtIndex.md。 |
| 166 | If a notes contains embedded rich text information in the string<br>`ISetTextFormat.md` | If a note contains embedded rich text information in the string<br>`SetTextFormat.md` | 两句逐字几乎相同，只差一个 s：a notes vs a note。ISetTextFormat 把 SetTextFormat 的原句抄错。 |
| 167 | [[IAnnotation::GetLeaderAllARound]]<br>`SetLeader3.md` | # IAnnotation.GetLeaderAllAround<br>`GetLeaderAllAround.md` | SetLeader3 的 Use.../To... 表里写成 AllARound（AR 大写）。本目录其余十余处链接一律 AllAround，成员页真实名为 GetLeaderAllAround。 |
| 168 | - [[IAnnotation::GetLeaderSide ()]]<br>`GetLeaderCount.md` | - [[IAnnotation::GetLeaderPerpendicular Method ()]]<br>`GetLeaderCount.md` | 同一个 See Also 列表内两种链接写法：GetLeaderSide 漏了 Method 一词。LeaderThicknessCustom.md 的 GetMultiJogLeaders () 同型漏法。 |
| 169 | True if the the sketch entity is successfully replaced, false if not<br>`SketchReplace.md` | True if the the sketch entity is successfully replaced, false if not<br>`SketchReplace2.md` | 两个文件的 Returns 同一句连写两个 the；同族其余页作 "True if the sketch entities are ..."，单个 the。 |
| 170 | - [[ITaskPaneView::AddStandardButton Method]]<br>`AddCustomButton.md` | - [[ITaskpaneView::AddStandardButton Method ()]]<br>`AddCustomButton2.md` | 同一接口名两种大小写：P 大写 vs p 小写；页面 type/name 字段与目录名一律为 ITaskpaneView。 |
| 171 | pt2x, t2y, pt2z,<br>`GetMeshDataAtIndex.md` | pt3x, pt3y, pt3z,<br>`GetMeshDataAtIndex.md` | 同一坐标清单里第 2 点第二个分量漏 p（t2y），同页其余 5 行均为 ptNy。 |
| 172 | - **FirstColumn**: 0-based row column at the beginning of the selection range<br>`SetCellRange.md` | - **FirstColumn**: 0-based column number at the beginning of the selection range<br>`GetCellRange.md` | 同接口同名参数两种写法：SetCellRange 写成 "row column"（疑从上行 Row 复制），GetCellRange 写 "column number"。 |
| 173 | Show draft analsyis options.<br>`swDraftAnalysisShow_e.md` | # swDraftAnalysisShow_e<br>`swDraftAnalysisShow_e.md` | 同页同一词两种拼法：Description 里 analsyis，标识符名里 Analysis 拼写正确。 |
| 174 | Array of [[sketch segments]] of the now split formerly closed sketch skegment<br>`SplitClosedSegment.md` | Array of [[sketch segments]] of the now split formerly open sketch skegment<br>`SplitOpenSegment.md` | 两个文件 Returns 末词均误作 skegment；同句前半的链接名写作 sketch segments，同页标题为 Split...Segment。 |
| 175 | True if automatic inteferencing is on, false if off<br>`AutoInference.md` | Inferencing mode can be seen when creating a sketch segment and your cursor moves past another sketch enitity.<br>`AutoInference.md` | 同页两处误拼：inteferencing（同页后文作 Inferencing/inferencing）、enitity（同句后半作 sketch entity）。 |
| 176 | Obsolete. Superseded by [[ISketchEllipse::GetMajorPoint2]] and [[ISketchEllispe::IGetMajorPoint2]].<br>`GetMajorPoint.md` | - [[ISketchEllipse::IGetMajorPoint2 Method]]<br>`GetMajorPoint2.md` | 同一句里接口名出现两种拼法：ISketchEllipse 与 ISketchEllispe（少一个 p）。同族 IGetMajorPoint.md 第 12 行同错；C:\swapi\types\ISketchEllispe 目录不存在。 |
| 177 | Obsolete. Superseded by [[ISketchEllipse::GetEndPoint2]] and [[ISketch Ellipse::IGetEndPoint2]].<br>`GetEndPoint.md` | - [[ISketchEllipse::GetEndPoint2 Method]]<br>`IGetEndPoint2.md` | 同一句两个链接分隔写法：ISketchEllipse:: 与带空格的 ISketch Ellipse::。同族 GetMinorPoint.md / IGetEndPoint.md / IGetMinorPoint.md 同错。 |
| 178 | This interface and its methods and properties require that the SOLDWORKS MBD add-in be loaded. ([[ISldWorks::L …<br>`_overview.md` | SOLIDWORKS Model Based Definition (MBD) is an integrated drawingless manufacturing solution for SOLIDWORKS.<br>`_overview.md` | 同一页 L19 写 SOLDWORKS（SOLDI 变 SOLD），而 L14/L17/L21/L23 与页内其余全部写 SOLIDWORKS。 |
| 179 | - [[ITableAnnotation:GetCellUseDocTextFormat Method]]<br>`GetUseDocTextFormat.md` | - [[ITableAnnotation::GetCellTextFormat Method]]<br>`GetUseDocTextFormat.md` | 同一 See Also 列表 L23/L28 用双冒号 ::，L24–L27 用单冒号 :，共 4 条写法与同列表其余条目不一致。 |
| 180 | Draft face propagaton types.<br>`swDraftFacePropagationType_e.md` | name: swDraftFacePropagationType_e<br>`swDraftFacePropagationType_e.md` | Description 行写 propagaton（漏 i），而同页 name/标题 swDraftFacePropagationType_e 与成员前缀 swFaceProp* 均用 Propagation。 |
| 181 | Call ths method before calling [[IMacroFeatureData::IGetSelections3]] to determine the size of the array for t …<br>`GetSelectionCount.md` | Call this method before calling [[IMacroFeatureData::IGetDisplayDimensions]] to determine the size of the arra …<br>`GetDisplayDimensionCount.md` | 同族同句式样板句，另一页写 this，本页写 ths（缺 i）。 |
| 182 | - in-process, unmanaged C++: Pointer to an array of parameter data types of size paramCount as defined in [[sw …<br>`IGetParameters.md` | - in-process, unmanaged C++: Pointer to an array of parameter names of size ParamCount<br>`IGetParameters.md` | 同一页三个并列参数描述，ParamTypes 用小写 paramCount，另两个用 ParamCount；形参声明为 ParamCount。 |
| 183 | - in-process, unmanaged C++: Pointer to an array of [[drawing views]] of size selCount<br>`ISetSelections2.md` | - in-process, unmanaged C++: Pointer to an array of marks (integers or longs) of size SelCount<br>`ISetSelections2.md` | 同一页三个并列数组描述，DrViews 用小写 selCount，另两个用 SelCount；形参声明为 SelCount。 |
| 184 | - in-process, unmanaged C++: Pointer to an arrayparameter data types of size ParamCount as defined in [[swMacr …<br>`ISetParameters.md` | - in-process, unmanaged C++: Pointer to an array of parameter data types of size paramCount as defined in [[sw …<br>`IGetParameters.md` | Get/Set 同句对页；本页 arrayparameter 粘连漏空格漏 of，对页为 array of parameter。 |
| 185 | Use this method to restore the rollback state if you did not modify the feature or use [[IFeature::ModifyDefin …<br>`ReleaseSelectionAccess.md` | - [[IFeature::IModifyDefinition2]] if you modified the feature<br>`IAccessSelections.md` | Defintion 少一个 i。已核：C:\swapi\types\IFeature\IModifyDefintion2.md 不存在，IModifyDefinition2.md 存在 ⇒ 死链。 |
| 186 | - [[SecurityHandleProcedureName Property]]<br>`ModuleName.md` | - [[IMacroFeatureData::SecurityHandleProcedureName Property]]<br>`SecurityHandleModuleName.md` | 同族同一目标两种写法；本批 1500 余条见 Also 里仅 3 条无接口前缀，本条即其一。另见 IClosedCornerFeatureData 两处同类。 |
| 187 | Gets the localized message describing he corrective action recommended for this incompatibility.<br>`Action.md` | Gets the localized message describing this incompatibility.<br>`Message.md` | he 缺 t。同族同句式（Gets the localized message describing …）另一页用 this。 |
| 188 | Gets a list of faces and edges that need be assigned user IDs for the macro feature.<br>`GetEntitiesNeedUserId.md` | Gets the number of faces and edges that need to be assigned user IDs for the macro feature.<br>`GetEntitiesNeedUserIdCount.md` | Get/IGet 写成 need be（缺 to），Count 页写成 need to be。IGetEntitiesNeedUserId.md 同样 need be。 |
| 189 | Gets whether the macro file is embedded ini the model with the macro feature.<br>`MacroFileEmbedded.md` | True if the macro file is embedded in the model with the macro feature, false if not<br>`MacroFileEmbedded.md` | 同一页摘要句写 ini，下一句同短语写 in。 |
\| 190 \| \| sw3DInterconnectImportErrors_Disabled \| 1 = 3D Interconnect is not enabled; to enable set **Tools > Option …<br>`sw3DInterconnectImportErrors_e.md` \| \| sw3DInterconnectImportErrors_ParametersUnavailable \| 5 = Only top-level 3D Interconnect features can be ed …<br>`sw3DInterconnectImportErrors_e.md` \| or call calling 连写两个同根词；同表其它行句式正常。属 doubled-word 类机械错。 \|
| 191 | - [[IConfigurationt::GetRootComponent3 Method]]<br>`GetParent.md` | - [[IConfiguration::GetRootComponent3 Method]]<br>`GetChildren.md` | 同族同成员在两页被写成两种拼法：GetParent 页把接口名写成 IConfigurationt（多一个 t），GetChildren 页为 IConfiguration；IConfigurationt 目录不存在。 |
| 192 | in-process, unmanaged C++: Pointe to an array of the values for the parameters of size NParamCount<br>`ISetParameters.md` | in-process, unmanaged C++: Pointer to an array of the values of the parameters of size NParamCount<br>`IGetParameters.md` | 同族 IGetParameters / ISetParameters 的同名参数行只差一个字母：ISetParameters 页把 Pointer 拼成 Pointe（少 r）。 |
| 193 | the suppression state in values (S=suppressed or U=Unsuppressed)<br>`ISetParameters.md` | the suppression state in Values (S=Suppressed or R=Resolved)<br>`SetParameters.md` | 同一抑制状态取值表在两页写成两种：ISetParameters 页为 U=Unsuppressed（小写 suppressed），SetParameters 页为 R=Resolved（大写 Suppressed）。 |
| 194 | 2. IConfiguration::IGetRootComponent 2(called only once)<br>`IGetRootComponent2.md` | 2. IConfiguration::GetRootComponent3 (called only once)<br>`GetRootComponent3.md` | 同一编号列表项的成员名被拆开：IGetRootComponent2 页写成 IGetRootComponent 2（数字 2 前多一个空格），兄弟页 GetRootComponent3 为紧连写法。 |
| 195 | If the return value is -1 values, then material property values are not assigned to the feature.<br>`GetDisplayStateBodyProperties.md` | If the return value is all -1 values, then material property values are not assigned to the feature.<br>`GetDisplayStateComponentProperties.md` | 五张 GetDisplayState*Properties 页的同一句模板，Body 页漏掉 all（写成 "is -1 values"），其余四页均为 "is all -1 values"。 |
| 196 | - [GEt ID of Active Configuration or Current Drawing Sheet (VBA)](../../examples/Get_ID_of_Active_Configuratio …<br>`GetID.md` | - [Get ID of Active Configuration or Current Drawing Sheet (VB.NET)](../../examples/Get_ID_of_Active_Configura …<br>`Name.md` | 同一示例族的标题在两页有两种大小写：GetID 页把 VBA 那条写成 GEt（首字母大写），Name 页写 Get；链接目标文件名相同。 |
| 197 | - [[IAttrbute::IGetDefinition Method]]<br>`IFindAttribute.md` | - [[IAttribute::GetDefinition Method]]<br>`FindAttribute.md` | 同一接口名在同族两页两种拼法：IFindAttribute 页写成 IAttrbute（少一个 i），FindAttribute 页为 IAttribute；IFindAttribute.md 自身其余 4 处也均写 IAttribute。 |
| 198 | [[IRepalceFaceFeatureData::IAccessSelections]]<br>`ReleaseSelectionAccess.md` | # IReplaceFaceFeatureData.IAccessSelections<br>`IAccessSelections.md` | ReleaseSelectionAccess 页把接口名写成 IRepalceFaceFeatureData（ae 换序）；该成员自身的页标题为 IReplaceFaceFeatureData，且 IRepalceFaceFeatureData 目录不存在。 |
| 199 | Use [[IModelDocExtension::SelectByID2]] to select the reference geometry to drive the seed fature and the feat …<br>`_overview.md` | Allows access to the selections that describe this variable pattern feature.<br>`AccessSelections.md` | _overview.md 同一句里 feature 出现两次拼法：前半写 fature（少 e），后半写回 feature；同族 AccessSelections 页为 feature。 |
| 200 | To get the list of custom properties, use [[IRevisonTableAnnotation::GetAllCustomProperties]] or [[IRevisionTa …<br>`GetColumnCustomProperty.md` | - [[IRevisionTableAnnotation::IGetAllCustomProperties Method]]<br>`GetAllCustomProperties.md` | 同一句里两个链接指同一接口：前一个漏字母，IRevison（少 s）；后一个与兄弟页 [[IRevisionTableAnnotation::…]] 拼写一致。 |

（另有 354 条，原始 JSON 见 `specs/203-bunny-sideline-batches/recon/`）

## 六、`number_mismatch` / `undefined_item`（34 条）

| # | 类型 | 原文A（文件） | 原文B（文件） | 说明 |
|---|---|---|---|---|
| 1 | number_mismatch | - next double gives the number of doubles required to hold ellipse geometry ( center, unit vector along majorA …<br>`GetPolyLinesAndCurves.md` | - next three doubles give the coordinates of endPt<br>`GetPolyLinesAndCurves.md` | 括号里点名8项(含 normal)=3+3+3+1+1+3+3+3=20，页面却写 ==17；紧随其后的逐项展开也只有7项、根本没有 normal。 |
| 2 | number_mismatch | The maximum number of doubles contained in the array will be (1 + dimensionCount * 51).<br>`GetDimensionInfo6.md` | The maximum number of doubles contained in the array will be (1 + dimensionCount * 52).<br>`GetDimensionInfo7.md` | Info6 的清单逐项合 51，与其自述一致；Info7 清单是 Info6 全部项再加 angularOrdinateDimInfo[10]（应为 61），却写 52。 |
| 3 | number_mismatch | The next 24 values are valid when showParens is True; for example, when this is a reference dimension.<br>`GetDimensionDisplayInfo5.md` | callout1TextPos[3] = XYZ position of first callout text (text above) callout2TextPos[3] = XYZ position of seco …<br>`GetDimensionDisplayInfo5.md` | 该句下列 10 项（8 个 parenArc*[3] 加 2 个 callout*TextPos[3]）=30 个值；仅 8 个 parenArc 项才是 24。 |
| 4 | undefined_item | - **Points**: Array of [[points]] of size PointsCount<br>`InsertMultiJogLeader3.md` | **Signature**: `System.object InsertMultiJogLeader3( System.object Points, System.int StartPointArrowStyle, Sy …<br>`InsertMultiJogLeader3.md | 参数说明引用了 PointsCount，但签名与 Parameters 里都没有该形参（只有 3 个形参且都有 **name** = 定义行），本页无 PointsCount 的定义行。姊妹页 IInsertMultiJogLeader3.md 才有该形参。 |
| 5 | undefined_item | The value you specify for LoopProcessAction determines how to process multiple loops.<br>`DeleteFaces5.md` | - **LoopProcessOption**: Loop processing as defined in [[swLoopProcessOption_e]] (see **Remarks**)<br>`DeleteFaces5.md` | Remarks 反复用 LoopProcessAction 指该形参，但全页形参定义行只有 LoopProcessOption，且签名与枚举名都用 Option；LoopProcessAction 无任何定义行。 |
| 6 | undefined_item | Float [Normals ] = array of X,Y,Z normal components for each strip from 0 to (VertexPerStrip-1).<br>`GetTessTriStripNorms.md` | NormalComp = Array of X,Y,Z normal components for each vertex on the particular face strip.<br>`GetTessTriStripNorms.md` | Remarks 上半列出的名字是 Normals，下半 where 列表定义的是 NormalComp —— 同页两处不同名，Normals 全页没有定义行。 |
| 7 | undefined_item | - **RefDirection**: Array containing 3 doubles (see **Remarks**)<br>`CreateConicalSurface2.md` | Input arguments: **Argument** **Description** Center XYZ location which represents the center of the bottom Di …<br>`CreateConicalSurface2.md` | 签名有 5 个形参，RefDirection 明确指向 Remarks 的表，但该表只有 Center/Direction/Radius/SemiAngle 四行，无 RefDirection。ICreateConicalSurface2.md 同样缺。 |
| 8 | undefined_item | stripEdgeCount1, stripEdgeCount2,..., stripVertCountN,<br>`GetTessTriStripEdges.md` | stripEdgeCountN = The number of triangle edges for the Nth triangle strip + 1.<br>`GetTessTriStripEdges.md` | 数组式样第三项写作 stripVertCountN，但同页 where: 只定义了 nStrips / stripEdgeCountN / stripN / triStripFlag / edgeId，无 stripVertCountN 定义行。 |
| 9 | number_mismatch | **[** Color, LineType, LineFont, LineWidth, LayerID, LayerOverride, StartPt[3], EndPt[3], CenterPt[3], MajorPt …<br>`GetEllipses3.md` | This set of data repeats for each ellipse in the sketch. The size of the array is (NumEllipses * 20).<br>`GetEllipses3.md` | 同页列出 6 个标量 + StartPt/EndPt/CenterPt/MajorPt/MinorPt 五个 [3] = 21（再加 Direction 为 22），与同句声明的 20 不符。同族 GetArcs2=16、GetParabolas2=18、GetLines2=12、GetUserPo … |
| 10 | undefined_item | click the **Icon size** that matches the size that you set in step 1b<br>`AddCustomButton2.md` | 2. Select a different icon size.<br>`AddCustomButton2.md` | Remarks 引用 step 1b，但本页步骤表用的是 1./2./3./4.，全页无 1b 这一项。 |
| 11 | undefined_item | Call [[IReplaceFaceFeatureData::GetReplacementSurfaces]] before calling this method to get the size of Count.<br>`IGetReplacementSurfaces.md` | Call [[IReplaceFaceFeatureData::GetFacesForReplacementCount]] before calling this method to get the value for  …<br>`IGetFacesForReplacement.md` | 两页是同构句（IGetFaces vs IGetReplacementSurfaces），Face 页引用存在的 GetFacesForReplacementCount，而 ReplacementSurfaces 页引用 GetReplacementSurfaces —— 该接口只有 GetRepl … |
| 12 | undefined_item | - **FaceList**: Array of [[faces]] of size Count<br>`SetFaces.md` | **Signature**: `void SetFaces( System.int WhichFaceList, System.object FaceList )`<br>`SetFaces.md` | 参数说明引用 Count，但本方法签名只有 WhichFaceList 与 FaceList，全页无 Count 的定义行（ISetFaces 才有 Count 形参）。 |
| 13 | undefined_item | # ISimpleFilletFeatureData2.ReverseFaceNormal<br>`ReverseFaceNormal.md` | **Signature**: `System.bool RoundCorners {get; set;}`<br>`RoundCorners.md` | ReverseFaceNormal.md 整页只有 frontmatter 与标题，无描述/签名/Returns/Remarks；_overview 仍把它计入 property_count: 24。 |
| 14 | undefined_item | # IStructuralMemberFeatureData.ConnectionType<br>`ConnectionType.md` | **Signature**: `System.int CornerTreatmentType {get; set;}`<br>`CornerTreatmentType.md` | ConnectionType.md 整页只有 frontmatter 与标题，无描述/签名/Returns/Remarks；同族至少 4 页 See Also 引用该成员。 |
| 15 | number_mismatch | Array of three doubles (see **Remarks**)<br>`ProfileParameters.md` | Square [ height, width ]<br>`ProfileParameters.md` | Returns 声明「three doubles」，但紧接着的 Remarks 表里 Square 一行只列 2 个值，Circular/Trapezoid 才是 3 个。 |
| 16 | undefined_item | Valid reference entities for Type1 and Type2:<br>`SetDirectionReference.md` | - **Type1**: Type of reference entity as defined by [[swSelectType_e]] (see **Remarks**)<br>`GetDirectionReference.md` | SetDirectionReference 的参数只有 Ref1/Ref2 两条定义行，Remarks 却引用 Type1 与 Type2；姊妹页 GetDirectionReference 里 Type1/Type2 都有定义行，说明此处是从该页复制漏改。 |
| 17 | number_mismatch | The return values are in an array of 7 doubles:<br>`GetPointAtIndex.md` | **[** Color, LineType, LineStyleIndex, PointStyle, CircleFilled, X, Y, Z **]**<br>`GetPointAtIndex.md` | 散文写 7 doubles，紧接着列出的数组是 8 项：Color/LineType/LineStyleIndex/PointStyle/CircleFilled/X/Y/Z。同目录 IGetPointAtIndex.md 逐字重复同一段，同样矛盾。 |
| 18 | undefined_item | **[** Color, LineType, LineStyleIndex, PointStyle, CircleFilled, X, Y, Z **]**<br>`GetPointAtIndex.md` | Index location of this line style inside SOLIDWORKS Line Style Manager<br>`GetParabolaAtIndex.md` | GetPointAtIndex.md 的 where 段逐条定义了 Color/LineType/PointStyle/CircleFilled/X/Y/Z 共 7 个，唯独数组里的 LineStyleIndex 没有定义行；同目录 GetParabolaAtIndex.md 给了它定义行。 |
| 19 | undefined_item | - **Entities**: Array of entities of [[edges]], [[sketches]], or a combination of edges and sketches (see **Re …<br>`SetEntitiesWeldPath.md` | ## Remarks<br>`SetEntitiesWeldFrom.md` | SetEntitiesWeldPath.md 的参数说明写着 (see **Remarks**)，但全页只有 Parameters 与 See Also 两节，没有 Remarks。同族 SetEntitiesWeldFrom.md / SetEntitiesWeldTo.md 都确实有 Remar … |
| 20 | undefined_item | Valid reference entities for type1 and type2:<br>`SetDirectionReference.md` | **Signature**: `void SetDirectionReference( System.object Ref1, System.object Ref2 )`<br>`SetDirectionReference.md` | Remarks 提到 type1 和 type2，但本页签名与 Parameters 只有 Ref1/Ref2，全页无 Type1/Type2 定义行；姊妹页 GetDirectionReference.md 才逐字定义了 Type1、Type2。属整段照抄残留。 |
| 21 | undefined_item | - IBaseFlangeFeatureData::UseDefaultRadius is false,<br>`BendRadius.md` | **Signature**: `System.bool UseDefaultBendRelief {get;}`<br>`UseDefaultBendRelief.md` | BendRadius.md 的 Remarks 点名 UseDefaultRadius 作取值条件，但该名全目录仅此 1 次、无成员页（只有 UseDefaultBendAllowance / UseDefaultBendRelief）。 |
| 22 | number_mismatch | The return value is the following array of seven doubles:<br>`GetProperties.md` | [ paperSize, templateIn, scale1, scale2, firstAngle, width, height, sameCustomPrp ]<br>`GetProperties.md` | 散文写 seven，紧接着的数组列出 8 项。同族 IGetProperties.md 写 seven 列 7 项、GetProperties2.md 写 eight 列 8 项，唯独本页对不上。 |
| 23 | undefined_item | [ paperSize, templateIn, scale1, scale2, firstAngle, width, height, sameCustomPrp ]<br>`GetProperties.md` | *sameCustomProp* = Value is a boolean packed into a double and returns true if the **Same as sheet specified i …<br>`GetProperties2.md` | 本页 where: 块只有 7 条定义，数组里的 sameCustomPrp 没有对应定义行；兄弟页 GetProperties2 对同名项是有定义的。 |
| 24 | undefined_item | - **Properties**: 6<br>`_overview.md` | # IToolingSplitFeatureData.Depth<br>`Depth.md` | Depth.md 全文只有 frontmatter 与标题，无 Signature/Returns/Remarks（同族其余5个属性页都有）。该属性被 _overview 计入 6 个属性却无任何定义正文，属空壳页。 |
| 25 | number_mismatch | - in-process, unmanaged C++: Pointer to an array of 3 doubles (see **Remarks**)<br>`IGetArrowInfo.md` | This method returns an array that consists of 12 doubles, the (X, Y, Z) of the start and end point of one arro …<br>`IGetArrowInfo.md` | 同页 Returns 声明数组 3 个 double，紧接的 Remarks 却说该数组由 12 个 double 构成，两者直接冲突；同族 GetArrowInfo.md 的同句也是 12。 |
| 26 | number_mismatch | - in-process, unmanaged C++: Pointer to an array of 3 doubles (see **Remarks**)<br>`IGetTextInfo.md` | The array returned by this method consists of 6 doubles, the (X, Y, Z) origin of one text followed by the (X,  …<br>`IGetTextInfo.md` | 同页 Returns 写 3 doubles，Remarks 写 6 doubles；同族 GetTextInfo.md 的同句也是 6，故 Returns 的 3 与本页正文不符。 |
| 27 | undefined_item | The return value is the following array of doubles : [ textPtX, textPtY, textPtZ ] where these text position v …<br>`GetTextPositionAtIndex.md` | [ lineType, startPt[3], endPt[3] ] where: lineType = Line type as defined in [[swLineTypes_e]] startPt[3] = XY …<br>`GetLineAtIndex.md` | textPtX/textPtY/textPtZ 三个名字在页内被列出却没有任何「*name* = …」定义行；同族 GetLineAtIndex.md 的三个名字逐个都有定义行。 |
| 28 | number_mismatch | Array of five doubles representing the X, Y, Z point on the vertex<br>`GetClosestPointOn.md` | Array of three doubles representing the x, y, and z coordinates of the point<br>`GetPoint.md` | 散文说 five doubles，紧接着只列 X、Y、Z 三项；同族 GetPoint 用同一模板写 three doubles 且正好列三项。 |
| 29 | undefined_item | Use [[IWeldmentBeadFeatureData::BeadType]] to determine the type of weld bead.<br>`UseOtherSide.md` | category: Feature Interfaces/Weldments --- # IWeldmentBeadFeatureData.BeadType<br>`BeadType.md` | UseOtherSide.md 让读者去看 BeadType，但 BeadType.md 只有 frontmatter 与 H1，无签名/描述/Returns，整页无定义行。BeadLength/BeadPitch/BeadSize 同样为空页。 |
| 30 | undefined_item | Use this property before using [[IPropertyManagerPageSelectionBox::SelectionIndex]].<br>`ItemCount.md` | category: User-interface Interfaces/PropertyManager --- # IPropertyManagerPageSelectionbox.SelectionIndex<br>`SelectionIndex.md` | ItemCount.md 指向 SelectionIndex，但 SelectionIndex.md 只有 frontmatter 与 H1，无 Signature/Returns，页内无定义行。ItemText.md 同样是空页。 |
| 31 | undefined_item | --- type: IPropertyManagerPageNumberbox member: ItemText kind: property assembly: SolidWorks.Interop.sldworks  …<br>`ItemText.md` | - [[IPropertyManagerPageNumberbox::ItemText]]<br>`Style.md` | ItemText.md 全文只有 front matter 与标题：没有 Signature、没有 Returns、没有描述，同族每个属性页都有 **Signature** 行。Style.md 把它当可用成员列出。 |
| 32 | undefined_item | --- type: IDragOperator member: Clearance kind: property assembly: SolidWorks.Interop.sldworks namespace: Soli …<br>`Clearance.md` | **Signature**: `System.short TransformType {get; set;}`<br>`TransformType.md` | Clearance.md 全文只有 front matter 与标题，无 Signature/Returns/Remarks；_overview.md 的 property_count: 16 已把它计入。兄弟属性页均有 **Signature** 行。 |
| 33 | undefined_item | - in-process, unmanaged C++: Pointer to an array of [[bodies]] of size Count<br>`IGetBodies.md` | - **NCount**: Number of bodies to move or rotate and copy<br>`IGetBodies.md` | Returns 引用的名字是 Count，同页唯一形参却定义成 NCount，Count 在本页无定义。 |
| 34 | undefined_item | The ArrayOut argument is an array of doubles containing 3 * points:<br>`IGetPointArray.md` | **Signature**: `System.double IGetPointArray()`<br>`IGetPointArray.md` | Remarks 讨论 ArrayOut，但本签名零参数且全页无 Parameters 段、无 ArrayOut 定义行；同族 ISetPointArray.md 则有 `- **ArrayDataIn**:`。 |

## 七、`other`（164 条）—— 未分类，原样列出

| # | 原文A（文件） | 原文B（文件） | 说明 |
|---|---|---|---|
| 1 | This method only returns ellipses that were sketched by a user in this drawing view. Use [[IView::Ge …<br>`GetEllipses5.md` | This method only returns arcs that were sketched by a user in a drawing view. Use [[IView::GetPolyli …<br>`GetArcs4.md` | 同一句两个链接完全相同 [[IView::GetPolylines6]] 或 [[IView::GetPolylines6]]；对照页 GetArcs4.md:20 第二处是 IGetPolylines6。 |
| 2 | sx, y, z, prefixPosx, y, z, suffixPosx, y, z, tolbox1Corner1x, y, z, tolbox1Corner2x, y, z<br>`IGetDimensionDisplayInfo5.md` | Arc2Centerx, y, z, parenArc2Vectorx, y, z, callout1TextPosx, y, z, callout2TextPosx, y, z]<br>`GetDimensionDisplayInfo5.md` | 同一示例数组：GetDimensionDisplayInfo5.md 完整到 callout2TextPosx 并闭合 ]，本页截断在 tolbox1Corner2x 处、缺 8 个条目且无收尾括号。 |
| 3 | - [[IView::GetFirstDisplayDimension5 Method]]<br>`GetDimensionCount4.md` | - [[IView::GetFirstDisplayDimension5 Method]]<br>`GetDimensionCount4.md` | See Also 里同一条链接重复列出两次；GetDimensionDisplayInfo5.md、GetUserPointsCount.md、IGetFaceHatches.md 同型。 |
| 4 | - [[IModelDoc2::IModelDocExtension::GetNamedViewRotation Method]]<br>`IGetNamedViewRotation.md` | - [[IModelDoc2::DeleteNamedView Method]]<br>`IGetNamedViewRotation.md` | 限定符重复：接口名 IModelDocExtension 被塞进 IModelDoc2:: 之后，同列表其余条目均为单层 IModelDoc2:: 形式。 |
| 5 | - [[IModelDocExtension::IModelDocExtension::IGetObjectByPersistReference3 Method]]<br>`GetObjectByPersistReference3.md` | - [[IModelDocExtension::IsSamePersistentID Method]]<br>`GetObjectByPersistReference3.md` | 同一列表里 IModelDocExtension:: 限定符连写两次，成员名被并入接口名；同列表其余条目为单层写法。 |
| 6 | Inserts the a general table annotation in this model document.<br>`InsertGeneralTableAnnotation.md` | Creates a general table annotation for SOLIDWORKS MBD 3D PDF.<br>`GetGeneralTableAnnotation.md` | 同族 Get/Insert GeneralTableAnnotation 两页首句结构相同，本页多出一个冠词 the，成为 the a。 |
| 7 | All numeric values returned from the IEnvironment object are relative to a unit text height of 1.0.; …<br>`GetEnvironment.md` | All numeric values returned from the IEnvironment object are relative to a unit text height of 1.0;  …<br>`IGetEnvironment.md` | 同一句话被抄坏：动词 multiply 在 I 版变成 you（且少了 1.0 后的句点）；两页仅差 multiply/you 一处。 |
| 8 | - in-process, unmanaged C++: Ponter ot an array of long values representing the [[swSelectType_e]] e …<br>`IGetSelectionFilters.md` | - in-process, unmanaged C++: Pointer to an array of strings containing the names of the configuratio …<br>`IGetConfigurationNames.md` | 同一模板句 "Pointer to an array ..." 被抄坏成 "Ponter ot an array"；IGetDocuments.md:20 同样是 "Pointer ot an array"。 |
| 9 | - Use the & symbol to include an accelerator key, e.g., MyItem@, adds MyItem to the File menu with a …<br>`AddMenuItem5.md` | - Use the & symbol to include an accelerator key, e.g., "MyItem@&File" adds MyItem to the File menu  …<br>`AddMenuItem4.md` | 例值 "MyItem@&File" 在本页被截断成 MyItem@（&File 丢失），同族 3/4 页该例值完整，可逐字比对。 |
| 10 | Deselects and enables the menu item. This is the default menu state with if no update function is sp …<br>`RemoveMenuPopupItem2.md` | Deselects and enables the menu item (this is the default menu state if no update function is specifi …<br>`AddMenuPopupItem2.md` | 同族 7 页该句均为 "...menu state if no update function..."，本页多出 with 一词。 |
| 11 | Call this method before calling [[ISldWorks::IGetSelectionFilters]] to determine the size of the arr …<br>`IGetSelectionFiltersCount.md` | Call this method before calling [[ISldWorks::IGetConfigurationNames]] to get the size of the array f …<br>`GetConfigurationCount.md` | 同一模板句 "Call this method before calling ... size of the array ..."；本页把 "that to that" 连写两次。 |
| 12 | Obsolete. Superseded [[ISldWorks::IGetOpenDocumentByName2]].<br>`IGetOpenDocumentByName.md` | Obsolete. Superseded by [[ISldWorks::IGetFirstDocument2]].<br>`IGetFirstDocument.md` | 本目录其余 30 余条 Obsolete 页一律写 Superseded by，只有这一页漏掉介词 by。 |
| 13 | However, if your program started the SOLIDWORKS Designapplication and you assign control of the SOLI …<br>`Visible.md` | Setting this property to true causes the SOLIDWORKS Design application to run in the foreground and  …<br>`UserControl.md` | 同一句里 SOLIDWORKS Designapplication 掉了空格；孪生属性页 UserControl.md 同一短语写作 SOLIDWORKS Design application。 |
| 14 | The 32-bit integer returned may be to small to contain the 64-bit window handle/pointer, and will be …<br>`PreviewDoc.md` | The 32-bit integer returned may be to small to contain the 64-bit window handle/pointer, and will be …<br>`PostMessageToApplication.md` | 同一句固定模板把 too small 误写成 to small；本目录 2 处、全语料 25 处同错。 |
| 15 | - **FaceList2**: Number of matching faces<br>`MatchedBoolean4.md` | - **FaceList2**: Second face list (see **Remarks**)<br>`MatchedBoolean3.md` | MatchedBoolean4 把 FaceList2 的说明复制成了上一行 NumOfMatchingFaces 的说明；同族 IMatchedBoolean3/4 与 MatchedBoolean3 写的都是 Second face list。 |
| 16 | - **NumOfFaces**: Number of faces generated when these two bodies intersect<br>`RemoveFacesFromSheet.md` | - **NumOfFaces**: Number of faces generated when these two bodies intersect<br>`IRemoveFacesFromSheet.md` | 两页同一句都与本页方法说明 Removes the specified faces from a sheet (surface) body 矛盾（本页无任何 intersect 语义），是从别处复制来的。 |
| 17 | Obsolete. by Superseded by [[IComponent2::MakeVirtual2]].<br>`MakeVirtual.md` | Obsolete. Superseded by [[IComponent2::EnumBodies2]].<br>`EnumBodies.md` | 本目录 20 余个废弃页统一句式为 "Obsolete. Superseded by ..."，只有 MakeVirtual.md 多出一个游离的 "by"。 |
| 18 | - [[IModelDocExtension::ListExternalFileReferences Method]] - [[IModelDocExtension::ListExternalFile …<br>`ListExternalFileReferencesCount.md` | - [[IModelDocExtension::ListExternalFileReferences Method]]<br>`ListExternalFileReferences2.md` | ListExternalFileReferencesCount.md 的 See Also 第 36、37 行逐字重复同一链接；同族其它页面该链接只出现一次。 |
| 19 | **Signature**: `void SetCosmosWorksMaterial( System.string ConfigName, System.int Type )`<br>`SetCosmosWorksMaterial.md` | ## Returns True if the material is assigned, false if not<br>`SetCosmosWorksMaterial.md` | 签名返回 void，页内却仍有描述 True/false 的 ## Returns 段。自相矛盾；179 页中 void 签名带 Returns 的仅此一页。 |
| 20 | Obsolete. Superseded by [[IPartDoc::EnumRelatedSectionedBodies]].<br>`EnumRelatedSectionedBodies.md` | Obsolete. Superseded by [[IPartDoc::EnumRelatedBodies2]].<br>`EnumRelatedBodies.md` | 已废弃成员指向自己作为后继（同目录实有 EnumRelatedSectionedBodies2.md）。兄弟页 EnumRelatedBodies 的写法正确指向带 2 的版本。 |
| 21 | Gets or sets the alignment of this angle mate.<br>`MateAlignment.md` | Gets or sets the alignment of this profile center mate.<br>`MateAlignment.md` | 平行配合接口页把自身描述成 angle mate，是从角度配合页复制未改。同族另一页正确写“本接口名 + mate”。 |
| 22 | Call [[ISketchRelationManager::IGetAllowedRelationsCount]] before calling this method to get the val …<br>`IGetAllowedRelations.md` | **Signature**: `System.int IGetAllowedRelationsCount( System.int NumEntities, ref System.object Enti …<br>`IGetAllowedRelationsCount.md | 被调的计数方法签名里 NumEntities 已是入参，不可能由它“得到 NumEntities 的值”；同族 ISketchRegion::IGetEdges 的同类句写的是取 Count。 |
| 23 | These triangles are intended for graphics display purposes and do not represent a tessellation that  …<br>`GetTessTriStrips.md` | These triangles are intended for graphics display purposes and do not represent a tessellation that  …<br>`GetTessTriStrips.md` | 同一页 Remarks 连续两段近乎重复的同义段落（L25 与 L27），内容同义、措辞略异，属重复未删。IGetTessTriStrips.md 同样重复。 |
| 24 | - [[IPartDoc::IDeleteEntityName Method]] - [[IPartDoc::IGetEntityByName Method]]<br>`DeleteEntityName.md` | - [[IPartDoc::SetEntityName Method]] - [[IPartDoc::IDeleteEntityName Method]]<br>`DeleteEntityName.md` | 同一个 See Also 列表内 [[IPartDoc::IDeleteEntityName Method]] 出现两次（L40 与 L45），条目被重复列出。 |
| 25 | - [[IPartDoc::GetNamedEntities Method]] - [[IPartDoc::GetNamedEntities Method]]<br>`IGetEntityByName.md` | - [[IPartDoc::GetEntityName Method]] - [[IPartDoc::DeleteEntityName Method]] - [[IPartDoc::GetNamedE …<br>`IGetEntityByName.md` | L46 与 L57 连续两行完全相同，同一 See Also 列表内 [[IPartDoc::GetNamedEntities Method]] 被列出两次。 |
| 26 | - **MakeRefSurface**: If the body cannot be knit to a solid or if a solid body already exists in thi …<br>`ICreateFeatureFromBody4.md` | - **MakeRefSurface**: If the body cannot be knitted to a solid or if a solid body already exists in  …<br>`CreateFeatureFromBody3.md` | 同一参数说明的多余虚词 “creates of a reference”；同族 CreateFeatureFromBody3 页为 “creates a reference surface feature”。 |
| 27 | ## Returns Annotation ## Remarks The [[IAnnotation]] object is a higher-level object that contains m …<br>`GetArcLengthLeader.md` | - **LeaderType**: Leader style as defined in [[swArcLengthLeaderType_e]] if autoLeader is false<br>`SetArcLengthLeader.md` | GetArcLengthLeader 签名回 System.int，Setter 页说明取的是 leader style 枚举；本页 Returns/Remarks 却整段抄自 IGetAnnotation.md（那里 Returns 是 IAnnotation 对象指针）。 |
| 28 | - **TextFormat**: v<br>`SetTextFormat.md` | - **TextFormat**: No description<br>`SetTextFormatAtIndex.md` | 同一形参在并行页写 No description，本页只剩一个残字 v，等于该形参没有定义行（属 undefined_item 一类的残缺）。 |
| 29 | - [[INote::GetBalloonStack Method]]<br>`SetBalloon.md` | - [[INote::GetBalloonStack Method]]<br>`SetBalloon.md` | 同一文件第 42、43 行是两条逐字相同的 See Also 条目；GetTextRefPositionAtIndex.md 第 44/46 行、SetZeroLengthLeader.md、SetTextFormat.md、GetLeaderAtIndex.md 有同类重复。 |
| 30 | Because a compound note can have multiple pieces of text, many of the compound note methods require  …<br>`SetTextJustificationAtIndex.md` | Because a compound note can have multiple pieces of text, many of the compound note methods require  …<br>`SetTextOffsetAtIndex.md` | 同段散文在 SetTextOffsetAtIndex 挂在 ## Remarks 下，在本页挂在第 20 行的 ## Returns 下；本页签名是 void，本不该有 Returns 段。 |
| 31 | **Signature**: `System.bool IIsSuppressed2( System.int Config_opt, System.int Config_count, ref Syst …<br>`IIsSuppressed2.md | Array of the suppression states for the feature in the specified configurations<br>`IIsSuppressed2.md` | 同一页签名返回 System.bool，Returns 却描述为数组；姊妹页 IsSuppressed2 签名才是 System.object 且 Returns 同样写 Array。 |
| 32 | 5. Specify Body1 and Body1 with the bodies that have been transformed to their correct positions in  …<br>`CheckInterferenceBetweenTwoBodies.md` | - **Body2**: Second body in interference detection (see **Remarks**)<br>`CheckInterferenceBetweenTwoBodies.md` | Remarks 步骤 5 连写两次 Body1，而本页参数表只有 Body1 / Body2 两个形参，第二个应为 Body2。 |
| 33 | - [[IModeler::ICheckInterference3 Method]]<br>`CheckInterference3.md` | - [[ISurface::MakeIsoCurve Method]]<br>`ProjectCurveOnSurface.md` | 两页 See Also 各有一条完全相同的链接连写两遍（已逐行核，两页各出现 2 次）。 |
| 34 | True if the tolerances is reset successfully, false if n<br>`UnsetTolerances.md` | - **Status**: True if the operation was successful, false if<br>`SplitFaceOnParam.md` | 两处末词被截断。同族 ISplitFaceOnParamCount2.md 同一行写完整的是 "false if not"。 |
| 35 | # IHingeMateFeatureData.EntitiesToMate<br>`EntitiesToMate.md` | # IHingeMateFeatureData.Angle Gets or sets the nominal angle between two selected faces.<br>`Angle.md` | EntitiesToMate.md 到标题即结束（文件尾就是该标题行），无描述/签名/Returns；同族每一页都有正文段。该成员仍被 _overview.md 的 property_count: 6 计入。 |
\| 36 \| Simulation graivity axis names.<br>`swSimulationGravityAxisName_e.md` \| \| swSimulationGravityAxis_Invalid \| -1 \|<br>`swSimulationGravityAxisName_e.md` \| 同一页 Description 写 graivity，四个成员名一律写 Gravity，同一个词两种拼法。 \|
| 37 | - [[IFace2::IGetDecalProperties Method]]<br>`GetDecalsCount.md` | - [[IFace2 Interface]]<br>`GetDecalsCount.md` | See Also 里该行逐字连续出现两次（本页 count=2），同列表其余 3 条均只出现一次，属重复条目。 |
| 38 | - [Create Plots and Get Values (C#)](../../examples/Create_Plots_and_Get_Values_Example_CSharp.md)<br>`_overview.md` | - [Create Plots and Get Values (VBA)](../../examples/Create_Plots_and_Get_Values_Example_VB.md)<br>`_overview.md` | Examples 6 条 bullet 恰是 C#/VB.NET/VBA 三条各重复一次（这 3 行本页 count 均为 2），应为 3 条。同型另见 IFace2\GetNextFace.md。 |
| 39 | - [[IFeatureManager::InsertEndCapFeature3 Method ()]]<br>`_overview.md` | - [[IFeatureManager::InsertEndCapFeature2 Method]]<br>`_overview.md` | 同一 See Also 列表紧邻两行同一构造两种渲染：上一行 'Method'，下一行多出空括号 'Method ()'。全批共 10 处 'Method ()'：ISketch/GetSplineParams5.md 7 处、ISketch/IsSketchEditable.m … |
| 40 | To determine the size of the array returned, call [[ISketch:GetSplineInterpolateCount]].<br>`IGetSplinesInterpolate.md` | - [[ISketch::GetSplineInterpolateCount Method]]<br>`GetSplineCount.md` | 分隔符写成单冒号 ISketch:；ISketch 目录 105 页里其余全部交叉引用一律用双冒号 ISketch::（已 grep 确认该单冒号形式全批仅此一处）。 |
| 41 | swAutodimStatusSuccess if the sketch is automatically dimensioned successfully; see [[swAutodimStatu …<br>`AutoDimension2.md` | swSketchCheckFeatureStatus_OK if this sketch can be used to create the specified feature; see [[swSk …<br>`CheckFeatureUse.md` | 同族两个 'see <枚举> for ...' Returns 句式：CheckFeatureUse 为 'for possible failure values'，AutoDimension2 变成 'for values for reasons for possible fa … |
| 42 | - **VDir**: Array of doubles representing the V direction of the texture-based appearance (see **Rem …<br>`GetVDirection.md` | ## Remarks<br>`GetUDirection.md` | GetVDirection.md 参数写「(see **Remarks**)」，但全页无 ## Remarks 小节，紧接着就是 ## See Also；同族 GetUDirection/SetUDirection/SetVDirection 三页都有 Remarks。 |
| 43 | # IPropertyManagerPageLabel.Bold<br>`Bold.md` | - **Properties**: 11<br>`_overview.md` | 该接口 11 个属性里 8 个页（Bold/CharacterBackgroundColor/CharacterColor/Font/Italic/LineOffset/SizeRatio/Underline）只有标题、无 Signature/Returns；overview 却 … |
| 44 | The current styleis set to .<br>`DeleteStyle.md` | by specifying "" for theLayer.<br>`Layer.md` | 两页同型的单词粘连（缺空格）：styleis 与 theLayer。本目录正确写法是 style is、the Layer（见 LayerOverride.md 的 the Layer property）。 |
| 45 | - [[IAnnotation::GetAttachedEntities2 Method]]<br>`GetAttachedEntityCount2.md` | - [[IAnnotation Members]]<br>`GetAttachedEntityCount2.md` | 该页 See Also 里 [[IAnnotation Interface]] 连续出现两次（第 1 条与第 3 条），中间只隔上面引的 Members 一行；同族 GetAttachedEntityCount3.md 只出现一次。 |
| 46 | - [Get More DimXpert Feature Examples (VBA)](../../examples/Get_DimXpert_Feature2_Example_VB.md)<br>`_overview.md` | - [Get DimXpert Features and Annotations Example (C#)](../../examples/Get_DimXpert_Features_and_Anno …<br>`_overview.md` | Examples 段的 6 条实为 3 条连写两遍；上面这两条行各在该文件里出现 2 次（VB.NET 那条同样出现 2 次）。属抓取时的重复追加。 |
| 47 | - **Z1**: z coordinate of point 2<br>`CreateSketchSlot.md` | - **Z3**: z coordinate of point 3<br>`CreateSketchSlot.md` | Z1 被写成 point 2，与同组的 X1/Y1 "point 1" 及 Z2 "point 2" 矛盾，疑为复制错位。 |
| 48 | Curvature density of the curvature combs for this spline; valid values from 0 - 100<br>`CurvatureScale.md` | Curvature density of the curvature combs for this spline; valid values from 0 - 100<br>`CurvatureDensity.md` | CurvatureScale（double，描述写 adjust the size）的 Returns 与 CurvatureDensity 逐字相同且写 density、给 0-100 整数域，疑复制未改。 |
| 49 | After you receive a valid return value, you can evaluate the for the object's data type.<br>`GetEntryValue.md` | To return the cell contents as a string, use [[IBomTable::GetEntryText]].<br>`GetEntryValue.md` | 同段下一句句式完整可对照；本句 "evaluate the for the object's data type" 在 the 后缺宾语。 |
| 50 | - **Y1**: coordinate for point 1<br>`CreateParallelogram.md` | - **Y2**: Y coordinate for point 2<br>`CreateParallelogram.md` | 同列表 9 个参数中仅 Y1 漏掉轴字母；同族 PerimeterCircle 的 X1 同样漏写 "x"。 |
| 51 | - [[ITableAnnotation::GetLockColumnWidth Method]] - [[ITableAnnotation::GetLockColumnWidth Method]]<br>`GetColumnType.md` | - [[ITableAnnotation::GetLockColumnWidth Method]] - [[ITableAnnotation::SetLockColumnWidth Method]]<br>`GetColumnTitle.md` | GetColumnType.md L37/L38 是同一条重复两遍，且漏掉 SetLockColumnWidth；同族 GetColumnTitle.md L34/L35 是 Get/Set 成对。GridLineWeightCustom.md 同型重复。 |
| 52 | then the return value is the same as the row's original width instead of what you specified.<br>`SetRowHeight.md` | then the return value is the same as the column's original width instead of what you specified.<br>`SetColumnWidth.md` | 两页句子结构逐字平行；SetRowHeight.md 讲的是行高，却写成 row's original width，疑从 SetColumnWidth.md 复制未改 width→height。 |
\| 53 \| \| swNumberingFormat2 \| 1 = 1., 2., 3, etc. \|<br>`swNumberingFormat_e.md` \| \| swNumberingFormat3 \| 2 = (1), (2), (3), etc. \|<br>`swNumberingFormat_e.md` \| 同表 L18–L20 三行格式应一致；L19 的第三项写成 3,（缺句点），而 L18 的 3 与 L20 的 (3) 都带结束标点。 \|
\| 54 \| \| swSketchCheckFeatureStatus_EntUnspecBad \| 3 = The sketch contains a self-intersecting entity \|<br>`swSketchCheckFeatureStatus_e.md` \| \| swSketchCheckFeatureStatus_EntXSelf \| 2 = The sketch contains a self-intersecting entity \|<br>`swSketchCheckFeatureStatus_e.md` \| 两个取值不同的成员（3 与 2）描述逐字相同，无法区分；同族 L25 的 EntXEnt(1) 写的是 contour 而非 entity。 \|
| 55 | - **Index**: Index of row for which to get the height<br>`GetRowVerticalGap.md` | Gap in system units<br>`GetRowVerticalGap.md` | 同一页参数说明写 height、Returns 写 Gap，自相矛盾；SetRowVerticalGap.md 第 17 行同样写成 get the height，疑从 GetRowHeight/SetRowHeight 复制未改。 |
| 56 | - in-process, unmanaged C++: Pointer to an array of file names for the icons (see **Remarks)**<br>`IGetIconFiles.md` | - in-process, unmanaged C++: Pointer to an array of the file names for the icons (see **Remarks**)<br>`ISetIconFiles.md` | Get 页的 ** 与右括号顺序颠倒，渲染不出 see Remarks 粗体；Set 页顺序正确。 |
| 57 | Gets or sets the name of the procedure in the macro file from or to the security handle.<br>`SecurityHandleMacroFileName.md` | Gets or sets the name of the procedure in the macro file from or to the security handle.<br>`SecurityHandleProcedureName.md` | 两个不同成员的说明与 Returns 逐字相同；MacroFileName 页写的是 path and file name。属复制粘贴串行。 |
| 58 | - [[IMacroFeatureData::EnableMultiBodyConsume Method ()]]<br>`EditBodies.md` | **Signature**: `System.bool EnableMultiBodyConsume {get; set;}`<br>`EnableMultiBodyConsume.md` | 该成员是 property（kind: property，{get;set;}），却在同族 3 页被写成 Method ()；同列表的 EditBodies 写成 Property。GetEditBodiesCount.md / IGetEditBodies.md 同。 |
| 59 | - **ParamTypes**: Array parameter data types as defined in [[swMacroFeatureParamType_e]]<br>`SetParameters.md` | - **ParamTypes**: Array of parameter data types as defined in [[swMacroFeatureParamType_e]]<br>`GetParameters.md` | Set 页漏 of（ParamValues 同）；Get 页两行都是 Array of。同页 Signature 未受影响，故非签名错。 |
| 60 | - [Get DimXpert Features and Annotations Example (C#)](../../examples/Get_DimXpert_Features_and_Anno …<br>`_overview.md` | - [Get DimXpert Tolerance2 Example (VBA)](../../examples/Get_DimXpert_Tolerance2_Example_VB.md)<br>`_overview.md` | 两个 _overview 的 Examples 都是 3 行连着重复一遍（共 6 行）。前者该行在 L26 与 L29 各出现一次；后者对应行在 L24 与 L27 各出现一次。 |
| 61 | member: DimXpertManager<br>`DimXpertManager.md` | **Signature**: `CustomPropertyManager CustomPropertyManager {get;}`<br>`CustomPropertyManager.md` | DimXpertManager.md 整页仅 10 行（frontmatter + 标题），没有任何 Signature/Returns 段；同接口同为 property 的 CustomPropertyManager.md 有完整签名行。 |
| 62 | Use..<br>`GetInstanceDimensionName.md` | - [[IDimPatternFeatureData::GetTableRowIndex]] to get TableRowIndex.<br>`SetInstanceDimensionValue.md` | GetInstanceDimensionName 页把同族共有的 "Use <方法> to get <参数>" 句表写成 "Use.."（双点）并把表格打散成裸行；兄弟页为完整单行。 |
| 63 | **Signature**: `System.double IGetStereoSeparation()`<br>`IGetStereoSeparation.md` | Array of 2 doubles representing the stereo magnitude and stereo parallax balance settings<br>`IGetStereoSeparation.md` | 签名返回 System.double（单个数），Returns 却自述是 2 个 double 的数组；同族 GetStereoSeparation 的同一句 Returns 配的是 System.object 签名。 |
| 64 | Component in which the feature is to be modified (see **Remarks**)<br>`IAccessSelections.md` | True if the selections were accessed successfully, false if not<br>`AccessSelections.md` | IAccessSelections 签名返回 System.bool，Returns 段却照抄了 Component 参数说明（该句在同页 L18 原样出现一次）。同族 AccessSelections.md 的 Returns 是布尔语义。 |
| 65 | To if end condition is to a vertex, use [[IWizardHoleFeatureData2::SetEndConditionReference]].<br>`IVertex.md` | To set the end condition to a vertex, use [[IWizardHoleFeatureData2::SetEndConditionReference]].<br>`Vertex.md` | 同族 Face.md / IFace.md / Vertex.md / IVertex.md 四页同一句式，只有 IVertex.md 掉了 set，句子不成句（残留 if）。 |
| 66 | - [[IWizardHoleFeatureData2::ThreadClass Property]]<br>`ThreadDepth.md` | - [[IWizardHoleFeatureData2::ThreadDiameter Property]]<br>`ThreadAngle.md` | ThreadDepth.md 的 4 条 See Also 里 ThreadClass 出现两次（L27、L29），ThreadDiameter 一条都没有；同族 ThreadAngle/ThreadDiameter/ThreadClass 三页都完整列出这 4 项。 |
| 67 | - [[IWizardHoleFeatureData2::CounterSinkDiameter Property]]<br>`CounterSinkAngle.md` | - [[IWizardHoleFeatureData2::CounterSinkAngle Property]]<br>`CounterSinkDiameter.md` | CounterSinkAngle.md 的 L28 与 L29 逐字相同，重复一条；且该页始终没链接自己的 CounterSinkAngle。同族 CounterSinkDiameter.md 的对应列表无重复。 |
| 68 | - [Get DimXpert Feature Example (VBA)](../../examples/Get_DimXpert_Feature_Example_VB.md)<br>`_overview.md` | - [Get DimXpert Feature Example (VBA)](../../examples/Get_DimXpert_Feature_Example_VB.md)<br>`_overview.md` | Examples 段 12 条是 6 条的整段重复：同一条目在该文件 L26 与 L32（另 5 条同）各出现一次，逐字相同。 |
| 69 | 4. Specify other ISimpleFilletFeatureData2 properties as follows:.<br>`_overview.md` | 4. Set other properties of IPartialEdgeFilletData as required.<br>`_overview.md` | 冒号后多一个句点（":."）；同文件另两步同位置均无句点。属纯机械标点错。 |
| 70 | - [[IVertex::GetClosestPointOn Method]] - [[IVertex::IGetClosestPointOn Method]] - [[IVertex::IGetCl …<br>`IGetClosestPointOn.md` | - [[ISurface::IGetClosestPointOn Method]] - [[IVertex::GetClosestPointOn Method]] - [[IVertex::IGetC …<br>`IGetClosestPointOn.md` | See Also 末两条逐字重复，疑复制粘贴未去重（同页其余 13 条互不重复）。 |
| 71 | - [Create Motion Studies (VBA)](../../examples/Create_Motion_Studies_Example_VB.md) - [Duplicate, De …<br>`_overview.md` | - [Duplicate, Delete, and Create Motion Study (C#)](../../examples/Duplicate,_Delete,_and_Create_Mot …<br>`_overview.md` | Examples 共 8 条但只有 4 条唯一：后 4 条与前 4 条逐字重复，疑合并两个来源时未去重。 |
| 72 | Gets the pitch of the starting section of a compression spring.<br>`StartingPitch.md` | **Signature**: `System.double StartingPitch {get; set;}`<br>`StartingPitch.md` | 同页签名有 setter 而摘要只写 Gets；同族对应成员 EndingPitch.md 写的是「Gets or sets pitch of the end section」。 |
| 73 | ## Returns Array giving the b-spline representation of the line<br>`IConvertLineToBcurveSize.md` | Size of the data necessary for the conversion to a b-curve<br>`IConvertArcToBcurveSize.md` | 本页签名返回 System.int（即 Size）但 Returns 与 ConvertLineToBcurve 逐字相同；同族的 Arc 版 Size 页 Returns 写的是「Size of the data necessary」。 |
| 74 | - [[ILinearPatternFeatureData::GetPatternFeatureCount Method]]<br>`ISetPatternFeatureArray.md` | - [[ILinearPatternFeatureData::IGetPatternFaceArray Method]]<br>`ISetPatternFaceArray.md` | ISetPatternFeatureArray 的 See Also 把 GetPatternFeatureCount Method 连写两遍，且整条缺 IGetPatternFeatureArray；同形的 ISetPatternFaceArray 是 Count / IGet … |
| 75 | arcNormal[3]<br>`IGetTriangleAtIndex.md` | **[** vertexPt1[3], vertexPt2[3], vertexPt3[3], isFilled, lineType **]**<br>`GetTriangleAtIndex.md` | IGetTriangleAtIndex.md 的 Remarks 数组整段抄自圆弧页 IGetArcAtIndex2.md（含 arcNormal[3]、rotationDir、XYZ arc start point），而三角形真正返回的是 GetTriangleAtIndex. … |
| 76 | Gets the path segments, curves, and edges to create the structure system member.<br>`SetPathSegments.md` | Gets the path segments, curves, and edges used to create the structure system member.<br>`GetPathSegments.md` | Set 开头的成员描述句写成 Gets，整句照抄自同目录 GetPathSegments.md（只差 used/to 一词）。签名是 System.bool SetPathSegments(...)，语义与描述相反。 |
| 77 | # IMateLoadReference.Component<br>`Component.md` | **Signature**: `Mate2 Mate {get;}`<br>`Mate.md` | Component.md 正文只有标题一行，没有 **Signature**、没有描述、没有 Returns/Remarks；而同目录另外 6 个成员页每一个都有 **Signature**。该页仍被 _overview 的 property_count: 3 计入。 |
\| 78 \| \| swTolFIT \| 7 \|<br>`swTolType_e.md` \| \| swTolMETRIC \| 7 \|<br>`swTolType_e.md` \| 同一张枚举表里两个不同成员都写 7，是全表唯一的重复值；其余 11 个成员值互不相同。属机械可验的取值冲突（不判定哪一侧对）。 \|
\| 79 \| \| swRenderMaterialColorFormsOne_Color \| \|<br>`swRenderMaterialColorForms_e.md` \| \| swRenderMaterialColorFormsImage \| 0 \|<br>`swRenderMaterialColorForms_e.md` \| 该页 5 个成员里有 3 个（One_Color / Two_Colors / Three_Colors）Value 列为空，同表另两个都有值。页面说明该列即颜色数，缺值无法查。 \|
\| 80 \| \| swCreateSectionView_DisplaySurfaceCut \| 32 or 0x20; If set, then only the surfaces cut by the se …<br>`swCreateSectionViewAtOptions_e.md` \| all model surfaces appear in the section view<br>`swCreateSectionViewAtOptions_e.md` \| 同一行同一句里出现两种拼法：前半 "apear"（缺 p），后半 "appear" 正确。属可直接逐字比对的错字。 \|
| 81 | - [[ILocalLinearPatternFeatureData::D1Axis Property]]<br>`D2ReverseDirection.md` | - [[ILocalLinearPatternFeatureData::D2Axis Property]]<br>`D2Spacing.md` | D2 页的 See Also 指向 D1Axis 与 D1Spacing，而同族 D2 页一律指向 D2Axis/D2Spacing（见 D2Spacing.md）；D1ReverseDirection.md 才指向 D1Axis。属 D1→D2 照抄未改。 |
\| 82 \| \| swAddMateError_ErrorUknown \| 0 = Unknown error occurred \|<br>`swAddMateError_e.md` \| 0 = Unknown error occurred<br>`swAddMateError_e.md` \| 同一表格行内，成员名把 Unknown 拼成 Uknown（缺 n），而同行说明文字写的是 Unknown。全库该成员仅此一处，无第二种拼法可比对。 \|
| 83 | Width of the surface<br>`Distance.md` | Gets or sets the radiate distance for this surface radiate feature.<br>`Distance.md` | 成员 Distance 的 Returns 写 "Width of the surface"，与本页自述的 radiate distance 不是同一个量；对照姊妹接口 IRuledSurfaceFeatureData\Distance.md 的 Returns 为 "Dista … |
| 84 | # IHoleSeriesFeatureData2.Size<br>`Size.md` | # IHoleSeriesFeatureData2.Standard Gets the design standard for this hole series. **Signature**: `Sy …<br>`Standard.md | Size.md 与 Type.md 各 220 字节，全文只有 frontmatter 与标题，无 Signature/Returns；同目录其余 12 个属性页都有定义行。 |
| 85 | - **TopDoc**: No description<br>`IAccessSelections.md` | - **TopDoc**: Top-level document<br>`IAccessSelections2.md` | IAccessSelections.md 两个参数都留占位串 "No description"，而后继 IAccessSelections2.md 与 AccessSelections.md 都有实际描述。 |
| 86 | --- type: ISheet member: TableAnchor kind: property assembly: SolidWorks.Interop.sldworks namespace: …<br>`TableAnchor.md` | # ISheet.SheetFormatVisible Gets or sets whether the sheet format is currently visible in this drawi …<br>`SheetFormatVisible.md` | TableAnchor.md 全文只有 10 行：front-matter 加一个 H1，没有散文、没有 Signature、没有 Returns、没有 See Also。同目录 52 个兄弟页都有这些段。 |
| 87 | - [Duplicate, Delete, and Create Motion Study (VBA)](../../examples/Duplicate,_Delete,_and_Create_Mo …<br>`_overview.md` | - [Create Motion Studies (VBA)](../../examples/Create_Motion_Studies_Example_VB.md)<br>`_overview.md` | Examples 列表整段重复：该 7 条链接在 L24-L30 与 L31-L37 各出现一次，逐字相同，生成器疑似把同一列表拼了两次。 |
| 88 | - [Get DimXpert Features and Annotations Example (C#)](../../examples/Get_DimXpert_Features_and_Anno …<br>`_overview.md` | - [Get DimXpert Features and Annotations Example (C#)](../../examples/Get_DimXpert_Features_and_Anno …<br>`_overview.md` | Examples 列表整段重复：同一条链接分别出现在 L29 与 L35。6 条唯一链接被列出 12 次。与 IMotionStudyManager 同型。 |
| 89 | Gets or sets the text for this string variable in a hole callout.<br>`String.md` | **Signature**: `System.string String {get;}`<br>`String.md` | 散文声称可读可写（sets），但同页签名只有 {get;}、无 set；同目录另两个 Callout 变量页亦需比对才能定性，此处仅指出页内自相矛盾。 |
| 90 | ## Examples - [Get DimXpert Tolerance4 Example (VBA)](../../examples/Get_DimXpert_Tolerance4_Example …<br>`_overview.md` | - [Get DimXpert Tolerance4 Example (VBA)](../../examples/Get_DimXpert_Tolerance4_Example_VB.md) - [G …<br>`_overview.md` | Examples 块整体重复：3 条被列两遍，该页共 6 条（实测 Tolerance4 (VBA) 出现 2 次、VB.NET 2 次）。 |
| 91 | - 1.0 (backward scattering) <= Subsurface scattering anisotropy value <= 1.0 (forward scattering)<br>`SubsurfaceAnisotropy.md` | The default value of this property is 0.0 for isotropic scattering.<br>`SubsurfaceAnisotropy.md` | 范围被写成 1.0<=x<=1.0 的退化区间，且与同页默认值 0.0 矛盾（0.0 不在区间内）。下界应为 -1.0，负号丢失。 |
| 92 | hexadecimal or decimal.Search for "Flipflop color in materials science and engineering" in your brow …<br>`FlipFlopColor.md` | You can find online converters to convert RGB to hexadecimal or decimal.<br>`Albedo.md` | 同一句 COLORREF 模板句在 Albedo 等页以 decimal. 收句，此页漏了句间分隔，直接连成 decimal.Search，两句话粘成一句。 |
| 93 | - [Get DimXpert Tolerance Example (VBA)](../../examples/Get_DimXpert_Tolerance_Example_VB.md)<br>`_overview.md` | - [Get DimXpert Features and Annotations Example (C#)](../../examples/Get_DimXpert_Features_and_Anno …<br>`_overview.md` | Examples 块 L23-L25 与 L26-L28 是逐字相同的三条链接，整块重复了一遍；实测该文件 6 条示例恰为 3 条的两倍。 |
| 94 | **NOTE:** **This property is a get-only property.** **Set is not implemented**.<br>`PathName.md` | **Signature**: `System.string PathName {get; set;}`<br>`PathName.md` | 同页散文明说 get-only、Set 未实现，签名却写成 {get; set;}；本接口其余 15 个属性的签名均与散文一致。 |
| 95 | - [Get DimXpert Tolerance1 Example (VBA)](../../examples/Get_DimXpert_Tolerance1_Example_VB.md)<br>`_overview.md` | - [Get DimXpert Tolerance1 Example (VB.NET)](../../examples/Get_DimXpert_Tolerance1_Example_VBNET.md …<br>`_overview.md` | Examples 只有 3 个唯一条目，却被逐字重复成 6 条（L23/L24/L25 与 L26/L27/L28 完全相同），属机械重复。 |
| 96 | - [[IDrSection::SetLineInfo Method]]<br>`GetLineInfo.md` | - [[IDrSection::IGetLineInfo Method]]<br>`SetLineInfo.md` | 两页 See Also 各有一条逐字重复的条目：GetLineInfo.md 第 28 与第 30 行、SetLineInfo.md 第 34 与第 35 行。 |
| 97 | Gets or sets the distance, in meters, to offset the reference plane feature.<br>`Distance.md` | Distance, in radians, to offset the reference plane<br>`Distance.md` | 同一页 Description 说 meters、Returns 说 radians，单位自相矛盾；同族 Angle.md 的 Returns 才是「Angle in radians」。 |
| 98 | - [Get DimXpert Tolerance1 Example (VBA)](../../examples/Get_DimXpert_Tolerance1_Example_VB.md) - [G …<br>`_overview.md` | - [Get DimXpert Tolerance1 Example (VBA)](../../examples/Get_DimXpert_Tolerance1_Example_VB.md) - [G …<br>`_overview.md` | Examples 段 3 行（第 23-25 行）被逐字重复一遍成为第 26-28 行。同样的 3 行重复也见 IDimXpertCompositePositionTolerance\_overview.md 的 24-26 与 27-29。 |
| 99 | - [[IRefPlaneFeatureData::ISetSelections Method]] - [[IRefPlaneFeatureData::Selections Property]] -  …<br>`GetSelectionsCount.md` | - [[IRefPlaneFeatureData::GetSelectionsCount Method]] - [[IRefPlaneFeatureData::IGetSelections Metho …<br>`ISetSelections.md` | See Also 里 ISetSelections Method 连写两次（第 28、30 行）；同族 ISetSelections.md 的同类列表每项只出现一次。 |
| 100 | [ textPtX, textPtY, textPtZ ] where these text position values are offset values from the origin of  …<br>`IGetTextPositionAtIndex.md` | [ textPtX, textPtY, textPtZ ] where these text position values are offset values from the origin of  …<br>`GetTextPositionAtIndex.md` | 同族两页只差一条尾句：I 版在数组说明后又补一次「Call GetTextCount before...」，而该句已在本页第 27 行出现过（第 35 行重复）。 |
| 101 | [[IModelDocExtension::GetUserPreferenceInteger]]((swUserPreferenceIntegerValue_e.swDetailingBOMBallo …<br>`Size.md` | [[IModelDocExtension::GetUserPreferenceInteger]](swUserPreferenceIntegerValue_e.swDetailingBOMLowerT …<br>`LowerTextContent.md` | Size.md/Style.md 的链接后多了一个左括号（](( ），且 Size.md 的 Set 行把链接与实参拆到两行；Lower/UpperTextContent 的同型句只有单个 (。 |
| 102 | --- type: IRefPlaneFeatureData member: ReversedReferenceDirection kind: property assembly: SolidWork …<br>`ReversedReferenceDirection.md` | Gets or sets whether to place the origin on the curve for this reference plane feature. **Signature* …<br>`OriginOnCurve.md` | 本批 6 个成员页只有前置头 + 标题，无描述/签名/Returns：IRefPlaneFeatureData 的 AngleOrDistance、Constraint、Reference、ReversedReferenceDirection 与 ICoreFeatureData … |
| 103 | - [Get DimXpert Tolerance1 Example (VBA)](../../examples/Get_DimXpert_Tolerance1_Example_VB.md) - [G …<br>`_overview.md` | - [Get DimXpert Tolerance1 Example (VBA)](../../examples/Get_DimXpert_Tolerance1_Example_VB.md) - [G …<br>`_overview.md` | ## Examples 段的 3 行在本页（第 23-25 行）逐字重复一次（第 26-28 行），机械性重复。 |
| 104 | - [Get DimXpert Features and Annotations (C#)](../../examples/Get_DimXpert_Features_and_Annotations_ …<br>`_overview.md` | - [Get and Set Pattern (C#)](../../examples/Get_and_Set_Pattern_Example_CSharp.md) - [Get and Set Pa …<br>`_overview.md` | ## Examples 段共 18 行，本页第 21-38 行在第 39-56 行逐字再重复一遍（quote_a 尾行即重复段首行）。 |
| 105 | - [[IChamferFeatureData2::ISetEdges Method]]<br>`Faces.md` | - [[IChamferFeatureData2::ISetFaces Method]]<br>`IGetFaces.md` | Faces.md 的 See Also 指向 ISetEdges，应为 ISetFaces；IGetFaces.md 自身正确写 ISetFaces，Loops.md 正确写 ISetLoops，可见这是笔误。 |
| 106 | Gets the faces to which a chamfer is applied.<br>`ISetFaces.md` | Sets the edges to which a chamfer is applied.<br>`ISetEdges.md` | ISetFaces 签名返回 void（Setter），摘要却复制成 Gets；同族 ISetEdges/ISetLoops 均写 Sets。 |
| 107 | - **Face2**: v<br>`IGetTwoAdjacentFaces.md` | - **Face2**: Pointer to the second adjacent [[face]]<br>`IGetTwoAdjacentFaces2.md` | 参数说明只剩一个残字 v；后继代页面 IGetTwoAdjacentFaces2.md 对同名参数有完整说明，可证此处是截断残留。 |
| 108 | - **VertexNormalErrArrayCount**: Number of vertex point errors<br>`IGetErrorListCount.md` | - **VertexPointErrArrayCount**: Number of vertex point errors<br>`IGetErrorListCount.md` | 五个 out 参数里两个说明逐字相同；VertexNormalErrArrayCount 应为 vertex normal errors，与 VertexPoint 那行复制粘贴未改。 |
| 109 | - in-process, unmanaged C++: Pointer to an array extended items ([[faces]] and [[edges]]) of size Co …<br>`ISetPropagatingEdges.md` | - in-process, unmanaged C++: Pointer to an array of propagating [[edges]] of size Count<br>`IGetPropagatingEdges.md` | EdgeArr 说明从 ISetItems.md 整句复制而来（仍说 extended items / faces），但本方法设置 propagating edges，同页 Returns 亦然。另 IGetItems.md 与 ISetItems.md 同句缺 of。 |
| 110 | - [[IPartingLineFeatureData::PullDirectionType Property]]<br>`DraftAnalysis.md` | - [[IPartingLineFeatureData::DraftAnalysis Method]]<br>`PullDirection.md` | See Also 列表里 PullDirectionType 连续出现两次（第 7、9 条完全相同），属重复条目；同页另两个 pull direction 属性各只列一次。 |
| 111 | - [Get DimXpert Features and Annotations Example (C#)](../../examples/Get_DimXpert_Features_and_Anno …<br>`_overview.md` | - [Get DimXpert Feature Example (VBA)](../../examples/Get_DimXpert_Feature_Example_VB.md)<br>`GetNominalPlane.md` | _overview.md 的 Examples 列 6 条，第 4-6 条是第 1-3 条的完整重复；成员页只引 2 条。 |
\| 112 \| \| swAutodimMarkEntities \| 1 or 0x1; Sketch entities to autodimension when [[swAutodimEntitiesSelec …<br>`swAutodimMark_e.md` \| \| swAutodimMarkHorizontalDatum \| 2 or 0x2; Sketch entities to autodimension when [[swAutodimEntiti …<br>`swAutodimMark_e.md` \| 两个不同取值（1 与 2）的成员描述逐字完全相同；同表另两行描述各不相同，说明这是复制粘贴残留。 \|
| 113 | - [[IVariableFilletFeatureData2::IAccessSelections Method]]<br>`IAccessSelections.md` | - [[IVariableFilletFeatureData2::IAccessSelections Method]]<br>`AccessSelections.md` | IAccessSelections.md 的 See Also 指向自己（同名同族链接），而同族 AccessSelections.md 的同一条才是指向对方；应为自指错误。 |
| 114 | For angular slicing:<br>`GetBoundingBoxDirection3.md` | Sets bounding box direction 3 (left manipulator for linear slicing, inner radius for radial slicing) …<br>`SetBoundingBoxDirection3.md` | 同一条件分支（0.0 < inner radius < outer radius）在 Get 页写 angular slicing，在 Set 页写 radial slicing，且 Get 页自己的摘要行也写 radial。 |
| 115 | Array of setback distances at the specified<br>`GetSetbackVertexDistance.md` | - in-process, unmanaged C++: Pointer to an array of setback distances at the specified<br>`IGetSetbackVertexDistance.md` | 句子在介词后断掉、缺宾语（应为 at the specified vertex）；同族 IGetSetbackVertexDistance.md 与 ISetSetbackVertexDistance.md 复制了同一残句。 |
| 116 | - [Get DimXpert Feature Example (VBA)](../../examples/Get_DimXpert_Feature_Example_VB.md) - [Get Dim …<br>`_overview.md` | - [Get DimXpert Feature Example (VB.NET)](../../examples/Get_DimXpert_Feature_Example_VBNET.md) - [G …<br>`_overview.md` | Examples 列表 6 行只 3 个唯一条目，第 4-6 行与第 1-3 行完全相同，整段被重复了一遍。 |
| 117 | Gets or sets the length for this length variable in a hole callout.<br>`Length.md` | **Signature**: `System.double Length {get;}`<br>`Length.md` | 散文说 gets or sets，签名只有 {get:}；同族 Precision/TolerancePrecision 都是 {get; set:}，三者写法不一致。 |
| 118 | True if the time was selected or cleared, false if not<br>`SetSelectedItem.md` | - **Item**: Index of the item to select or clear<br>`SetSelectedItem.md` | Returns 行把形参 Item 写成 time；同一页 Parameters 定义的名字是 Item。 |
| 119 | Allows access to and modifcation of text in a specific row in a callout.<br>`OnStringValueChanged.md` | - **RowID**: Row in which the text was edi<br>`OnStringValueChanged.md` | 同一页两处机械错字：modifcation 少一个 i；edi 是被截断的单词（edited），句子没有结尾。 |
\| 120 \| \| swPartConvertToBodiesPostNotify \| 78 = [[ConvertToBodiesPostNotify]] \|<br>`swPartNotify_e.md` \| \| swPartPublishTo3DPDFNotify \| 78 = [[PublishTo3DPDFNotify]] \|<br>`swPartNotify_e.md` \| 同一枚举里两个不同成员都取 78；页内其它成员取值互不重复，78 出现两次属页内机械冲突。 \|

## ⚠ 明确记下的限度

* ⚠ **单元格截断**：本表的「原文片段」列在 340 字处截断、以 `…` 标记。
  **截断可能切断行内代码（反引号）** —— 已做过一次配对修复（只删孤立反引号、不动内容），
  但**截断本身仍是有损的**：要看完整原文请回原始 JSON（`specs/203-bunny-sideline-batches/recon/`）。


* ⚠ **`spelling` 与 `other` 两类没有逐条人工复核**（共 718 条）。
  它们的**引文**过了逐字回查，但「两种拼法是否真的指同一个东西」**没有**逐条判 ——
  有些可能是官方**故意**的（如 `swBreakLineStraight` 与 `swBreakLine_Straight` 也许是两次改名）。
  ⇒ 主线若要引用，请先核那一条。
* ⚠ **真死链（§二）与拼错的接口名（§三）是文件系统事实**，不依赖判断力；
  **`member_missing`（§四）依赖我建的「接口 → 成员」索引**，若某个接口的页名与成员名不同形
  （官方少数页的 `member:` 字段与文件名不一致），可能误判。
* ⚠ 本轮**只扫了 `types/` 与 `enums/`**，**没扫** `C:\swapi\examples\`（2839 份）与
  `C:\swapi\docs\`；`D:\AI\SW\AI Solidworks\官方文档\`（CHM 解包 29697 份）也没扫。
* ⚠ Bunny 会编造（本项目实测 5 条）⇒ 本文件所有条目**都已过引文逐字回查**，
  作废 6 条；但**没有**做「把每条链接真的点一遍」那一层（无网络）。
