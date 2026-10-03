# audit-03-weldment-A —— 核对 A（签名一致性）

- **域**：03-weldment
- **核对类型**：**只做核对 A（签名一致性）** —— 把我们的调用逐个实参与官方 Signature 的形参表并排数：参数个数 / 顺序 / 明显类型。
- **我们这边的文件**：`scripts/sw_weldment.py`、`scripts/sw_sheet_metal_weld_entry.py`（两者都存在，已通读）
- **官方源**：`C:\swapi\types\<接口>\<成员>.md` + `C:\swapi\examples\*.md` + `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\`（CHM 解包）
- **纪律**：只报「两段原文对得上号、且确实对不上」的地方；给不出两段原文的一律不写；不判谁对、只陈述分歧。

---

## 发现（2 条）

| # | 我们的原文（文件 + 片段）| 官方的原文（文件 + 片段）| 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | **`scripts/sw_weldment.py`**，来源块逐字：<br>`IFeatureManager.InsertWeldmentCutList2(Object SortOptions) -> Feature`<br>与<br>`⚠ InsertWeldmentCutList2 接受一个 Object 参数（排序选项），`<br>`官方未标注其类型，**按 ICutListSortOptions 传**；若本机版本签名不同，`<br>`需按该版本官方文档调整。`<br>调用处 `create_cut_list`：`feature = get_com_member(manager, "InsertWeldmentCutList2", sort_options)` | **`C:\swapi\types\IFeatureManager\InsertWeldmentCutList2.md`**：<br>`**Signature**: `Feature InsertWeldmentCutList2( System.object Bodies )``<br>`- **Bodies**: Array of [[Body2]] objects`<br><br>**CHM `…IFeatureManager~InsertWeldmentCutList2.html`** 同页：<br>`value = instance.InsertWeldmentCutList2(Bodies)`<br>`<DT><I>Bodies</I></DT>` | **参数个数一致（都是 1），但实参类型不符**：官方那一个形参的形参名是 `Bodies`、类型是 `System.Object` 且语义为「**Body2 对象数组**」；我们把 `ICutListSortOptions` 对象当排序选项传了进去。我们来源块里「官方未标注其类型」这句话与官方页直接冲突——官方**命名了该形参并写明是 Body2 数组**。<br>（本文件 `ensure_cut_list` 里另一处同名调用传的是 `VARIANT(VT_ARRAY\|VT_DISPATCH, tuple(...))` 的 Body2 数组，与官方一致；分歧只落在 `create_cut_list` 这一处。） | **高** |
| 2 | **`scripts/sw_weldment.py`**，来源块逐字：<br>`Feature InsertSubWeldFolder2(Object Folder)   ← 1 参`<br>`Feature InsertSubWeldFolder()                ← 0 参（无参旧版）`<br>`本函数走 2 参版以支持指定父文件夹；不传 folder 时传 None。`<br>`⚠ 官方未标注该 Object 参数的确切类型（预期为 IStructureSystemFolder），`<br>`故只透传不校验。`<br>调用处 `create_sub_weld_folder`：`feature = get_com_member(manager, "InsertSubWeldFolder2", folder)` | **`C:\swapi\types\IFeatureManager\InsertSubWeldFolder2.md`**：<br>`**Signature**: `Feature InsertSubWeldFolder2( System.object BodyArray )``<br>`- **BodyArray**: Array of [[Body2]] objects`<br><br>**CHM `…IFeatureManager~InsertSubWeldFolder2.html`** 同页：<br>`value = instance.InsertSubWeldFolder2(BodyArray)`<br>`ByVal BodyArray As System.Object` | **参数个数一致（都是 1），但实参类型不符**：官方形参名是 `BodyArray`、语义为「**Body2 对象数组**」（CHM 摘要句：`Creates a sub weld folder feature containing the specified weldment bodies.`）；我们把「父文件夹对象（预期 `IStructureSystemFolder`）」传了进去，且默认实参是 `None`。我们来源块里「官方未标注该 Object 参数的确切类型」这句话与官方页直接冲突——官方**命名了该形参并写明是 Body2 数组**。 | **高** |

---

## 逐条核对过的调用点（26 处，均已与官方 Signature 并排数过）

### `scripts/sw_weldment.py`（16 处）

| 调用点 | 我们传的实参 | 官方 Signature | 结果 |
|---|---|---|---|
| `call_com_member(manager, "InsertWeldmentFeature")` | 0 | `Feature InsertWeldmentFeature()` | 一致 |
| `call_com_member(manager, "CreateStructuralMemberGroup")` | 0 | `StructuralMemberGroup CreateStructuralMemberGroup()` | 一致 |
| `InsertStructuralWeldment5(...)` | 5：str/int/bool/VARIANT(groups)/str | `( System.string Path, System.int ConnectedSegmentsOption, System.bool AllowProtrusion, System.object Groups, System.string ConfigurationName )` | 一致（含顺序与类型） |
| `method(body_array)`（`ensure_cut_list` 的 `getattr` 路） | 1：Body2 SAFEARRAY | `Feature InsertWeldmentCutList2( System.object Bodies )` | 个数一致、类型一致 |
| `ole_object.Invoke(174, …, body_array)`（DISPATCH_METHOD 路） | 1：Body2 SAFEARRAY | 同上 | 个数一致、类型一致 |
| `get_com_member(manager, "InsertWeldmentCutList2", sort_options)`（`create_cut_list`） | 1：`ICutListSortOptions` | 同上（`Bodies` = Body2 数组） | **分歧 → 第 1 条** |
| `get_com_member(manager, "InsertSubWeldFolder2", folder)` | 1：folder 对象 / `None` | `Feature InsertSubWeldFolder2( System.object BodyArray )`（`BodyArray` = Body2 数组） | **分歧 → 第 2 条** |
| `get_com_member(manager, "CreateDefinition", int(fm_type))` | 1 | `System.object CreateDefinition( System.int Type )` | 一致 |
| `get_com_member(manager, "CreateFeature", data)` | 1 | `Feature CreateFeature( System.object FeatureData )` | 一致 |
| `get_com_member(feature, "GetErrorCode")` | 0 | `System.int GetErrorCode()` | 个数一致（★ 该页首行写 `Obsolete. Superseded by [[IFeature::GetErrorCode2]].` —— **属核对 C 范围，本路不报**） |
| `manager.Get6(name, False, raw, resolved, was_resolved, linked)` | 6 | `System.int Get6( System.string FieldName, System.bool UseCached, out System.string ValOut, out System.string ResolvedValOut, out System.bool WasResolved, out System.bool LinkToProperty )` | 一致（个数 + 顺序 + 4 个 out 位置） |
| `manager.Add3(name, 30, value, 2)` | 4 | `System.int Add3( System.string FieldName, System.int FieldType, System.string FieldValue, System.int OverwriteExisting )` | 个数与顺序一致 |
| `get_com_member(model, "GetBodies2", SW_SOLID_BODY, False)` | 2 | `System.object GetBodies2( System.int BodyType, System.bool BVisibleOnly )` | 一致 |
| `get_com_member(model, "GetBodies2", SW_SOLID_BODY, False)`（`weldment_evidence`） | 2 | 同上 | 一致 |
| `get_com_member(configuration, "GetCutListItems")` | 0 | `System.object GetCutListItems()` | 一致 |
| `call_com_member(body_folder, "UpdateCutList")` | 0 | `System.bool UpdateCutList()` | 一致 |

### `scripts/sw_sheet_metal_weld_entry.py`（10 处）

| 调用点 | 我们传的实参 | 官方 Signature | 结果 |
|---|---|---|---|
| `get_com_member(model, "GetBodies2", 0, True)`（`_body_face_count`） | 2 | `System.object GetBodies2( System.int BodyType, System.bool BVisibleOnly )` | 一致 |
| `get_com_member(model, "GetBodies2", 0, False)`（`create_midsurface`） | 2 | 同上 | 一致 |
| `get_com_member(b, "GetFaces")` | 0 | `System.object GetFaces()` | 一致 |
| `get_com_member(sm, "GetSelectedObjectCount2", mark)` | 1 | `System.int GetSelectedObjectCount2( System.int Mark )` | 一致 |
| `get_com_member(sm, "GetSelectedObjectCount2", -1)` | 1 | 同上 | 一致 |
| `InsertSheetMetalMiterFlange(...)` | **14** | `Feature InsertSheetMetalMiterFlange( System.bool UseDefaultRadius, System.double GlobalRadius, System.double RipGap, System.bool UseDefaultRelief, System.bool UseReliefRatio, System.double ReliefRatio, System.double ReliefWidth, System.double ReliefDepth, System.int ReliefType, System.bool TrimSideBends, System.int FlangePos, System.double OffsetDist1, System.double OffsetDist2, CustomBendAllowance PCBA )` | 一致（14 个形参逐位对上，含末位 PCBA 的 NULL 语义） |
| `get_com_member(model, "InsertSheetMetalClosedCorner")` | 0 | `void InsertSheetMetalClosedCorner()` | 一致 |
| `InsertEndCapFeature3(...)` | **10** | `Feature InsertEndCapFeature3( System.double Depth, System.bool BIsGivenOffset, System.bool BIsChamfer, System.double OffsetValue, System.double WallThicknessRatio, System.double ChamferValue, System.bool BIsCornerTreatment, System.double DepthOffset, System.bool BIsReverse, System.int BIsEndCapInward )` | 一致（10 个形参逐位对上） |
| `InsertGussetFeature3(...)` | **20** | `Feature InsertGussetFeature3( System.double Depth, System.short DirType, System.short LocType, System.bool BIsProfile, System.double ProfileD1, System.double ProfileD2, System.double ProfileD3, System.double ProfileAngle, System.double ProfileD4, System.bool BOffset, System.double DProfileOffset, System.int CrvIndex, System.bool BReverseDir, System.bool BReverseFace, System.bool BUseLenDim, System.double ProfileD5, System.double ProfileD6, System.double ProfileChamferAngle, System.bool BUseLenDimForChamfer, System.bool BNeedChamferInGusset )` | 一致（20 个形参逐位对上；`DirType`/`LocType` 官方是 `System.short`、我们按 `int` 透传——**这一点我们代码里已自行声明**，且整数宽度在 COM 封送上不构成 arity/顺序分歧，故不另起一条） |
| `InsertMidSurface(...)` | **4**：`body, part_doc, placement, knit_flag` | `System.object InsertMidSurface( Body2 PBodyIn, ModelDoc2 PPartDocIn, System.double Placement, System.bool KnitFlag )` | 一致（4 个形参逐位对上，前两位对象形参我们传的就是对象） |

---

## 查不到 / 不在本路范围（据实说明，不猜）

- `C:\swapi\types\IModelDoc2\GetBodies2.md` **不存在**；`GetBodies2` 的官方页只找到 `IPartDoc\GetBodies2.md` 与 `IComponent2\GetBodies2.md`。上表用的是 `IPartDoc` 那份（零件场景）。
- 第 2 条所指的「官方是否还有别的、接受文件夹对象的 `InsertSubWeldFolder*` 重载」——在 `C:\swapi\types\IFeatureManager\` 下只找到 `InsertSubWeldFolder.md`（0 参）与 `InsertSubWeldFolder2.md`（1 参 `BodyArray`）两份；**没找到**接受文件夹对象的版本 ⇒ 按「查不到就说查不到」记此，本条只陈述已查到的那一处对不上，不推断意图。
- `GetErrorCode` 官方页首行 `Obsolete. Superseded by [[IFeature::GetErrorCode2]].`、`SW_FM_MATE_PROFILE_CENTER = 101` 是否在 `swFeatureNameID_e` 合法取值集合内、`Add3` 字面量 `30`/`2`、`SW_RELIEF_*`/`SW_FLANGE_*`/`SW_END_CAP_*`/`SW_GUSSET_*` 等字面量的枚举合法性 —— **均属核对 C（废弃链与枚举取值）**，本路不做，不列。
- 只读、未运行 SolidWorks、未跑 pytest、未改动仓内任何文件；本文件是本次唯一写入。

---

**核了几处**：26 处调用点（`sw_weldment.py` 16 + `sw_sheet_metal_weld_entry.py` 10），逐个与官方 Signature 形参表并排数过。
**报了几条**：2 条。
**高置信的是**：第 1 条（`InsertWeldmentCutList2` 传 `sort_options` 而官方形参是 `Bodies`）、第 2 条（`InsertSubWeldFolder2` 传 `folder` 而官方形参是 `BodyArray`）—— **两条都是高置信**（结构化 md 与 CHM 两套官方源逐字一致）。