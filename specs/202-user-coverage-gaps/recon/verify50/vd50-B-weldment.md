# vd50-B · weldment · 核对表「置信度=高」条目复核

- **域**：`weldment`
- **来源**：`D:/AI/SW/specs/202-user-coverage-gaps/recon/audit-vs-official/` 下与该域有关的 **3 份**：`audit-03-weldment-A.md` · `audit-03-weldment-B.md` · `audit-03-weldment-C.md`
- **口径**：★ 只核置信度为「**高**」的条目；A 表第 1、2 条 · B 表第 1、2 条 · C 表第 1、2 条 —— **共 6 条**（A 表无「中/低」，B 表第 3 条与 C 表第 3、4 条为「中」，**按纪律不碰**）。
- **每条两件事**：① 「官方原文」是否真在官方文档里（搜 `C:/swapi` + CHM 解包）② 「我们的原文」是否真在那份文件里（搜 `D:/AI/SW`）· ★ 两段都给得出才写。
- **只读**：未运行 SolidWorks、未跑 pytest、未改动仓内任何文件；★ **本文件是本次唯一写入**。
- ★ 本文件**不写行号**，只写**原文片段**。

## 结论速览

| # | 条目 | 来源文件 | 官方原文在不在 | 我们的原文在不在 | 判定 |
|---|---|---|---|---|---|
| 1 | `InsertWeldmentCutList2` 传 `sort_options` | `audit-03-weldment-A.md` 第 1 条 | ✅ 在 | ✅ 在 | **成立** |
| 2 | `InsertSubWeldFolder2` 传 `folder` | `audit-03-weldment-A.md` 第 2 条 | ✅ 在 | ✅ 在 | **成立** |
| 3 | `InsertSubWeldFolder2` 缺「先选实体」前置 | `audit-03-weldment-B.md` 第 1 条 | ✅ 在 | ✅ 在 | **成立** |
| 4 | `InsertWeldmentCutList2` 该喂实体数组 | `audit-03-weldment-B.md` 第 2 条 | ✅ 在 | ✅ 在 | **成立** |
| 5 | `GetErrorCode` 已被官方标 Obsolete | `audit-03-weldment-C.md` 第 1 条 | ✅ 在 | ✅ 在 | **成立** |
| 6 | `MateAlignment` 注释断言「枚举查不到」 | `audit-03-weldment-C.md` 第 2 条 | ✅ 在 | ✅ 在 | **成立** |

★ **6 条全部成立**：官方原文与我们的原文**都真实存在**，且两段**确实互相矛盾** ⇒ **对不上 0 处**（无一条因「查不到原文」或「原文对不上」而被否）。
⚠ **去重提示**：条目 1 与条目 4 是**同一个分歧**（A 表与 B 表各报一次），条目 2 与条目 3 是**同一个分歧**（B 表补了前置角度）⇒ **6 条 → 4 个独立分歧**。

---

## 1 · `InsertWeldmentCutList2` 传 `sort_options`，官方形参是 `Bodies`

**判定：成立**

**我们的那一段** —— `D:\AI\SW\scripts\sw_weldment.py`，`create_cut_list` 的来源块与调用处：
> `#           IFeatureManager.InsertWeldmentCutList2(Object SortOptions) -> Feature`
> `# ⚠ InsertWeldmentCutList2 接受一个 Object 参数（排序选项），`
> `#   官方未标注其类型，**按 ICutListSortOptions 传**；若本机版本签名不同，`
> `#   需按该版本官方文档调整。`
> `feature = get_com_member(manager, "InsertWeldmentCutList2", sort_options)`

**官方那一段** —— `C:\swapi\types\IFeatureManager\InsertWeldmentCutList2.md`：
> `**Signature**: `Feature InsertWeldmentCutList2( System.object Bodies )``
> `- **Bodies**: Array of [[Body2]] objects`

CHM 同页 `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~InsertWeldmentCutList2.html` 逐字一致：
> `value = instance.InsertWeldmentCutList2(Bodies)`
> `<DL><DT class="popupbubble"><I>Bodies</I></DT>`
> `Inserts a cut-list-item folder feature containing the specified weldment bodies.`

**一句话依据**：官方**命名了该形参并写明是 Body2 数组**，我们来源块「官方未标注其类型、按 `ICutListSortOptions` 传」这句话与官方页**直接冲突**（结构化 md 与 CHM 两套官方源逐字一致）。
★ **严重性补充（不影响判定）**：同一函数的 docstring 自己写着「`⚠⚠ **本函数在当前后端（pywin32 迟到绑定）上跑不通**」⇒ 这条错传**在本机从不真正执行**，但来源块的签名断言本身仍是错的。

---

## 2 · `InsertSubWeldFolder2` 传 `folder`，官方形参是 `BodyArray`

**判定：成立**

**我们的那一段** —— `D:\AI\SW\scripts\sw_weldment.py`，`create_sub_weld_folder` 的来源块与调用处：
> `#           Feature InsertSubWeldFolder2(Object Folder)   ← 1 参`
> `#           Feature InsertSubWeldFolder()                ← 0 参（无参旧版）`
> `#         本函数走 2 参版以支持指定父文件夹；不传 folder 时传 None。`
> `# ⚠ 官方未标注该 Object 参数的确切类型（预期为 IStructureSystemFolder），`
> `#   故只透传不校验。`
> `feature = get_com_member(manager, "InsertSubWeldFolder2", folder)`

**官方那一段** —— `C:\swapi\types\IFeatureManager\InsertSubWeldFolder2.md`：
> `Creates a sub weld folder feature containing the specified weldment bodies.`
> `**Signature**: `Feature InsertSubWeldFolder2( System.object BodyArray )``
> `- **BodyArray**: Array of [[Body2]] objects`

CHM 同页 `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~InsertSubWeldFolder2.html`：
> `value = instance.InsertSubWeldFolder2(BodyArray)`
> `ByVal BodyArray As System.Object`

**一句话依据**：官方形参名是 `BodyArray`、语义是「Body2 对象数组」，我们把它当「父文件夹对象（预期 `IStructureSystemFolder`）」透传且默认 `None` ⇒ 与官方页**直接冲突**（两套官方源逐字一致）。

---

## 3 · `InsertSubWeldFolder2` 缺官方要求的「先选实体」前置

**判定：成立**（与条目 2 同一分歧，本条补的是**调用前置**这一侧）

**我们的那一段** —— `D:\AI\SW\scripts\sw_weldment.py`，`create_sub_weld_folder` 函数体**全部**内容：
> `def create_sub_weld_folder(model, folder=None):`
> `    """在装配体中插入焊接文件夹（子装配层级）。"""`
> `    manager = get_com_member(model, "FeatureManager")`
> `    feature = get_com_member(manager, "InsertSubWeldFolder2", folder)`
> `    if feature is None:`
> `        raise RuntimeError("InsertSubWeldFolder2 未返回特征")`
> `    return feature`

⇒ 全函数**没有任何选实体 / 取 Body2 数组**的动作。

**官方那一段** —— `C:\swapi\examples\Insert_Weldment_Features_Example_VB.md`（官方例子调用序）：
> `'InsertSubWeldFolder2`
> `boolstatus = Part.Extension.SelectByID2("Gusset1", "SOLIDBODY", 0, 0, 0, False, 0, Nothing, 0)`
> `Set obj(0) = selMgr.GetSelectedObject6(1, -1)`
> `Set myFeature = fm.InsertSubWeldFolder2((v))`
> `Part.ClearSelection2 True`

配套官方成员页 `C:\swapi\types\IFeatureManager\InsertSubWeldFolder.md`：
> `Creates a sub weld folder feature containing solid bodies that are pre-selected in the user interface.`
> `The part must contain a weldment folder (Solid Bodies or Cut List) to create a sub-weldment folder.`

**一句话依据**：官方例子是「**先 `SelectByID2` 选实体 → `GetSelectedObject6` 取出 → 才传进去**」，我们那三行**一步都没做**（默认还传 `None`）⇒ 前置确实对不上。

---

## 4 · `InsertWeldmentCutList2` 该喂实体数组，我们按排序选项透传

**判定：成立**（与条目 1 同一分歧，本条补的是**该喂什么**这一侧）

**我们的那一段** —— `D:\AI\SW\scripts\sw_weldment.py`，`create_cut_list` 调用处：
> `feature = get_com_member(manager, "InsertWeldmentCutList2", sort_options)`
> `def create_cut_list(model, sort_options=None, *, collect_identical_bodies: bool = False):`

⇒ 该实参默认 `None`，且这条路径**从未取过实体**。

**官方那一段** —— `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\Insert_Weldment_Cut_List2_Example_VB.htm`（CHM 解包）：
> `v = Part.GetBodies2(0, True)`
> `Set cutListFeature = Part.FeatureManager.InsertWeldmentCutList2(v)`

配套 `C:\swapi\types\IFeatureManager\InsertWeldmentCutList2.md`：
> `Inserts a cut-list-item folder feature containing the specified weldment bodies.`
> `- **Bodies**: Array of [[Body2]] objects`

**一句话依据**：官方页写明是「要归入清单项的实体数组」、官方例子喂的就是 `GetBodies2` 的结果，我们却按**排序选项对象**透传 ⇒ 对不上。
★ **交叉印证（支持该条）**：同文件 `ensure_cut_list` 那条路径传的是 Body2 数组（与官方一致）⇒ **同一模块两条路径自相矛盾**，B 表的这条描述属实。

---

## 5 · `IFeature.GetErrorCode()` 带官方 `Obsolete` 行，代码未换后继

**判定：成立**

**我们的那一段** —— `D:\AI\SW\scripts\sw_weldment.py`，`_create_from_definition` 的来源块、docstring 与调用处：
> `#           → 用 GetErrorCode 拒绝硬错误。`
> `#         沿用而非另写，是为保持「错误码判定」在同一套模块里一致。`
> `    最后用 ``GetErrorCode`` 拒绝硬错误（与上游 ``create_base_flange`` 一致）。`
> `    error_code = int(get_com_member(feature, "GetErrorCode") or 0)`

★ **独立复核**：全仓 `scripts/sw_weldment.py` 内 `GetErrorCode` 只出现在上述几处，**`GetErrorCode2` 一次都没出现** ⇒ 核对表「未提任何后继成员」这句属实。

**官方那一段** —— `C:\swapi\types\IFeature\GetErrorCode.md`：
> `Obsolete. Superseded by [[IFeature::GetErrorCode2]].`
> `This method returns many of the errors indicated by the "What's Wrong" icon seen with an invalid feature in the FeatureManager design tree.`

后继页 `C:\swapi\types\IFeature\GetErrorCode2.md`（**无** Obsolete 行）：
> `**Signature**: `System.int GetErrorCode2( out System.bool IsWarning )``
> `- **IsWarning**: True if the error is a warning, false to not`

**一句话依据**：我们**实际调用**的成员带官方 `Obsolete. Superseded by [[IFeature::GetErrorCode2]].` 行，官方逐字点名的后继（多一个 `out bool IsWarning`）在代码里既没有、也没有任何换用说明 ⇒ 对不上。

---

## 6 · `MateAlignment` 的注释断言「枚举查不到」，官方有枚举页

**判定：成立**

**我们的那一段** —— `D:\AI\SW\scripts\sw_weldment.py`，`create_profile_center_mate` 的来源块与调用处：
> `# ⚠ MateAlignment 的枚举在两套官方源里查不到（`sw_know find MateAlignment``
> `#   未命中可用的枚举定义），故本函数只做 int 透传，不给默认值语义。`
> `    mate_alignment: int = 0,`
> `        set_com_member(data, "MateAlignment", int(mate_alignment))`

**官方那一段** —— `C:\swapi\types\IProfileCenterMateFeatureData\MateAlignment.md`：
> `## Returns`
> `Mate alignment as defined in [[swMateAlign_e]]`
> `## Remarks`
> `If this property is set to swMateAlign_e:`
> `- swMateAlignALIGNED, then vectors normal to the selected entities point in the same direction.`
> `- swMateAlignANTI_ALIGNED, then vectors normal to the selected entities point in opposite directions.`

`C:\swapi\enums\swMateAlign_e.md`（该页真实存在，`enum_member_count: 6`）成员表逐字：
> `| swAlignAGAINST | Obsolete. Do not use. |`
> `| swAlignNONE | Obsolete. Do not use. |`
> `| swAlignSAME | Obsolete. Do not use. |`
> `| swMateAlignALIGNED | 0 |`
> `| swMateAlignANTI_ALIGNED | 1 |`
> `| swMateAlignCLOSEST | 2 |`

官方例子 `C:\swapi\examples\Create_Profile_Center_Mate_Example_VB.md`：
> `        swProfileMateData.MateAlignment = SwConst.swMateAlign_e.swMateAlignALIGNED`

**一句话依据**：官方成员页**点名了枚举 `swMateAlign_e`**、官方例子**直接用枚举名赋值**、该枚举页**本身就有 3 个成员逐字标 `Obsolete. Do not use.`** ⇒ 我们「查不到枚举、只能 int 透传」的注释与三处官方原文**都对不上**。

---

## 按纪律没写进来的（据实说明，不猜）

- **置信度为「中」的条目一律未碰**：`audit-03-weldment-B.md` 第 3 条（`UpdateCutList` 前置）· `audit-03-weldment-C.md` 第 3 条（`swFmMateProfileCenter` 是否在官方列出的 35 项内）· 第 4 条（`swFeatureNameID_e` 完整性断言）。
- **查不到就不写**：本轮未对任何「查不到」的内容下判断；核对表里那些「已核但未报 / 查不到 / 不在本路范围」的记账段**不在本次口径内**（它们不是「置信度=高」的条目）。
- **域范围确认**：在 `audit-vs-official/` 全目录下检索 `焊件|weldment|Weldment`，命中该域的只有上述 3 份 `audit-03-weldment-{A,B,C}.md`；`audit-02-sheetmetal-B.md` 里出现的 `Insert_Weldment_End_Cap_Example_VB.md` 属钣金域那份表且其本身是「不报」记账 ⇒ 不计入本域。
- **两处官方源路径与核对表写的略有出入，但内容逐字对得上，故不影响判定**：核对表 A 表把 CHM 页写作 `…IFeatureManager~InsertWeldmentCutList2.html`，本机实际文件名带更长的前缀 `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~InsertWeldmentCutList2.html`；`C:\swapi\examples\Insert_Weldment_Features_Example_VB.md` 里的 VB 语句被拆成了多行（`Set` / `v` / `fm` 各占一行），按空白归一后与核对表引的整句逐字一致。

## 结尾三行

- 都核了 **6 处**（A 表 2 + B 表 2 + C 表 2，全是置信度「高」；「中」的一律未碰）。
- **对不上 0 处** —— 6 条的两段原文**都能给出**（官方原文在官方源里、我们的原文在 `scripts/sw_weldment.py` 里），且两段**确实互相矛盾** ⇒ **6 条全部成立**，去重后是 **4 个独立分歧**。
- 只读核验，未改仓内任何文件；★ 本文件是本次唯一写入。