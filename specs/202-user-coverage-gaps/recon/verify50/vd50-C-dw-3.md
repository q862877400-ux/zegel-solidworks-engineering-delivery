# vd50-C-dw-3 —— 工程图域契约摘要（BOM 表 / 孔表 / 图纸格式 / 输出 PDF 与 DXF / 图层）

> ★ **格式模板**：`api-pre/api-03-weldment.md`（同格式：① 精确签名 · ② `## Remarks` 逐字 · ③ 官方例子调用序 · ④ 枚举 · ⑤ 废弃链 · 每条末 `前置一句话` / `配方一句话`），并沿用 `api-pre/INDEX.md` 的「每条带判定与源」读法。
>
> ★ **本文件的立场与五条纪律**（与任务书一致）：
> 1. 只读 + 只写这一个文件；仓内任何文件未改动。
> 2. **每条结论必须给两段可搜索的原文**：**「仓内那一段」+「官方/目标那一段」**。给不出两段的**一律不写**。
> 3. **查不到就说查不到**，不用相似名字顶替。
> 4. **宁少勿滥** —— 报 4 条实的，好过 30 条含水的。
> 5. **不写行号**，只写可搜索的原文片段。
>
> ★ **本片范围**：工程图的 **BOM 表 / 孔表 / 图纸格式 / 输出 PDF 与 DXF / 图层**。视图、尺寸、气泡、基准符号不在本片（那是别的片）。

---

## 0. 抄录范围与源（★ 先说清抄了什么、没抄什么）

| 源 | 本文件简称 | 抄什么 |
|---|---|---|
| `C:\swapi\types\<接口>\<成员>.md` | **[md]** | 精确签名（`System.*` 口径）、`## Parameters`、`## Remarks`、`## Returns`、`## See Also` 逐字 |
| `C:\swapi\enums\<枚举>.md` | **[en]** | 枚举描述与成员数值 |
| `C:\swapi\examples\<例子>.md` | **[ex]** | 官方例子逐字调用序（每份自带 `**Source**: sldworksapi/<原名>.htm`） |
| 仓内 `scripts/` `mcp-server/` `tools/` `subskills/` | **[仓]** | 「仓内那一段」—— 仓内的调用点 / 注释 / 出处块 |
| 仓内 `scripts/sw_api_sldworks.py` 的 `ARITY` 段 | **[仓·反射]** | 出厂类型库反射抄进仓内的**形参个数**表（该文件顶部有 `ARITY: dict[str, dict[str, int]] = {` 定义） |

★ **判定口径**：`成立` = 仓内写法与官方原文逐字对得上 · `不成立` = 对不上且能指出对不上的那一句 · `存疑` = 两段原文本身互不一致或口径不明 · `查不到` = **官方或仓内任一侧根本没有可引的原文**（按纪律 3 停手，不推断）。

★ **本片共核 23 处**：成立 11 · **不成立 4** · 存疑 3 · 查不到 5。

---

## 〇、名字缺席（纪律 3：查不到就说查不到）

| 想找的 | 结果 | 仓内那一段 | 官方那一段 |
|---|---|---|---|
| `ISheet.SetTemplate`（仓内按 API 成员名列出） | **查不到该成员** | **[仓]** `tools/audit_gap_implementations.py` 的 `GAP_KEYWORDS` 里有逐字的一行 `"工程图/图纸格式模板": ["SetupSheet5", "SetTemplate"],` | **[md]** `C:\swapi\types\ISheet\` 下按 `*Template*.md` 过滤只得到 **4 个文件**：`GetTemplateName.md` / `GetTemplateSketch.md` / `ReloadTemplate.md` / `SetTemplateName.md` —— **没有 `SetTemplate.md`**；全 `C:\swapi\types\` 递归 `-Filter 'SetTemplate.md'` 返回 **0 个文件** |
| 官方 `ISheet.SetTemplateName` 的**形参个数** | **查不到第二源** | **[仓]** `scripts/sw_api_sldworks.py` 的 `ARITY` 里 `ISheet` 段有 `'SetTemplateName': 1,` | **[md]** `C:\swapi\types\ISheet\SetTemplateName.md` 逐字 `void SetTemplateName( System.string NameIn )` —— 官方 md **没有**列出与反射同名的字段，**两源口径无法互证** |

★ 上表第一行**判据**：仓内那句在 `audit_gap_implementations.py` 里是**检索关键词表**（与它同表的 `"工程图/孔表": ["InsertHoleTable2", "InsertHoleTable"]` 是「新版名 + 旧版名」配对），**不是 API 调用点**；按 API 成员名读，`SetTemplate` 在官方类型表里名字缺席，官方对应成员是 `ISheet.SetTemplateName`。**判定：成立**（对应关系成立）· 一句话依据：仓内 `SetTemplate` 指向的官方成员是 `SetTemplateName`，两者都在「图纸格式模板」这条线上。

---

# 一、BOM 表 / 通用表（7 条）

## 1.1 `IDrawingDoc.InsertTableAnnotation`

**① 精确签名** —— **[md]** `C:\swapi\types\IDrawingDoc\InsertTableAnnotation.md`：

```
TableAnnotation InsertTableAnnotation( System.double X, System.double Y, System.int AnchorType, System.int Rows, System.int Columns )
```

★ **5 个参数**。该文件**没有 `## Remarks` 段**、**没有 `## Returns` 段**、**没有 `## Examples` 段**，`## Parameters` 五行**全是** `- **X**: No description`。

**② `## Remarks`** —— **查不到**（文件里没有该段）。[chm-api] 本轮**未查**（见 §7.3）。

**③ 官方例子调用序** —— **查不到**（没有 `## Examples` 段）。

**④ 枚举** —— 签名里无枚举形参（`AnchorType` 是裸 `int`，`## Parameters` 写 `No description`，**没点名枚举**）。

**⑤ 废弃链** —— **[md]** 紧跟标题的第一句逐字：

> `Obsolete. Superseded by [[IDrawingDoc::InsertTableAnnotation2]].`

⇒ **后继 = `InsertTableAnnotation2`**。

**前置一句话**：查不到（官方页无 `## Remarks`）。
**配方一句话**：查不到（官方页无 `## Examples`）。

**判定：成立** · 一句话依据：**[仓]** `scripts/sw_drawing_expose.py` 的 `create_hole_table` 文档串逐字写着「官方签名逐字 `IDrawingDoc.InsertTableAnnotation(X, Y, **AnchorType**, Rows, Columns)`」，与 **[md]** 上面那行签名**逐字同形**（同为 5 参、第三个形参同为 `AnchorType`）。

---

## 1.2 `IDrawingDoc.InsertTableAnnotation2`

**① 精确签名** —— **[md]** `C:\swapi\types\IDrawingDoc\InsertTableAnnotation2.md`：

```
TableAnnotation InsertTableAnnotation2( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string TableTemplate, System.int Rows, System.int Columns )
```

★ **7 个参数**。描述句逐字：`Inserts a table annotation in this drawing.`
`## Returns` = `Pointer to the [[ITableAnnotation]] object`。
`## Parameters` 逐条：`UseAnchorPoint`: `True to anchor the table to the general table anchor point and ignore any coordinates specified for X and Y, or false to use the coordinates specified for X and Y` · `X`: `X coordinate to insert this table annotation` · `Y`: `Y coordinate to insert this table annotation` · `AnchorType`: `Type of anchor as defined in [[swBOMConfigurationAnchorType_e]] (see **Remarks**)` · `TableTemplate`: `Path and filename of the general table template to use  (see **Remarks**)` · `Rows`: `Number of rows in the table annotation` · `Columns`: `Number of columns in the table annotation`。

**② `## Remarks` 逐字** —— **[md]** 该段是一张两行表：

```
**If TableTemplate is...**

**Then..**

A valid path and filename

AnchorType and Columns are ignored, and the information from the table template is used instead

Empty

General table is inserted based only on the other input arguments
```

**③ 官方例子调用序** —— `## Examples` 列 4 个文件：`Insert_General_Table_Example_VB.md` / `Get_General_Table_Feature_Example_{CSharp,VBNET,VB}.md`。★ **本轮未逐字读这 4 个例子文件** ⇒ **逐字调用序查不到**。

**④ 枚举** —— `AnchorType` → 官方拼作 `swBOMConfigurationAnchorType_e`（**大写 BOM**，见 §1.7 的拼写差异）。

**⑤ 废弃链** —— **非 Obsolete**（文件里无 `Obsolete` 字样）。

**前置一句话**：`TableTemplate` 给有效路径时 `AnchorType and Columns are ignored`；给空串才按其余实参插通用表。
**配方一句话**：查不到（4 个例子文件本轮未逐字读）。

**判定：成立** · 一句话依据：**[仓·反射]** `scripts/sw_api_sldworks.py` 的 `ARITY` 里 `IDrawingDoc` 段有逐字 `'InsertTableAnnotation': 5,` 与 `'InsertTableAnnotation2': 7,`，与 **[md]** 两行签名的形参数 **5 / 7** 一致。

---

## 1.3 `ISheet.InsertRevisionTable2`（修订表，仓内走的那条）

**① 精确签名** —— **[md]** `C:\swapi\types\ISheet\InsertRevisionTable2.md`：

```
RevisionTableAnnotation InsertRevisionTable2( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string TableTemplate, System.int Shape, System.bool AutoUpdateZoomCells )
```

★ **7 个参数**。`## Returns` 逐字：`[[Revision table]] or null if a revision table already exists`。
`## Parameters` 逐条：`UseAnchorPoint`: `True to insert the revision table at the existing revision table anchor point, false to anchor the table at the point specified by X and Y` · `X`: `X coordinate for the placement of the revision table annotation` · `Y`: `Y coordinate for the placement of this revision table annotation` · `AnchorType`: `Anchor type as defined by [[swBOMConfigurationAnchorType_e]]` · `TableTemplate`: `Path and filename of the template that corresponds to this type of table (see **Remarks**)` · `Shape`: `Revision symbol shape as defined in [[swRevisionTableSymbolShape_e]]` · `AutoUpdateZoomCells`: `True to automatically update zone cells, false to not`。

**② `## Remarks` 逐字** —— **[md]**：

```
By default, the revision table templates are in install_dir\**lang**\language and have a filename extension of **.sldrevtbt**. The template and table must be of the same type. For example, you must specify TableTemplate with *install_dir***\lang\English\standard revision block.sldrevtbt** if you want to insert the English version of a revision block table.
```

**③ 官方例子调用序** —— `## Examples` 列 `Create_Drawing_Sheet_Zones_Example_{VB,VBNET,CSharp}.md`。★ 本轮未逐字读 ⇒ **查不到**。

**④ 枚举** —— `AnchorType` → `swBOMConfigurationAnchorType_e`（[en] 见 §1.7）· `Shape` → `swRevisionTableSymbolShape_e`（**本轮未读该枚举文件** ⇒ 成员与数值**查不到**）。

**⑤ 废弃链** —— **非 Obsolete**（文件里无 `Obsolete` 字样）。

**前置一句话**：`TableTemplate` 用 `install_dir\<lang>\language` 下的 `.sldrevtbt`，且 `The template and table must be of the same type.`。
**配方一句话**：查不到（3 个例子文件本轮未逐字读）。

**判定：成立** · 一句话依据：**[仓]** `scripts/sw_drawing_expose.py` 的 `create_revision_table` 传参逐字 `C.get_com_member(sheet, "InsertRevisionTable2", False, _mm(x_mm), _mm(y_mm), int(anchor_type), str(template), int(shape), bool(auto_update_zoom_cells))`（**7 个实参**、顺序与官方签名逐位对应），其文档串「★ 官方 Returns 逐字：已有修订表时回 `null`」与 **[md]** `## Returns` 的 `or null if a revision table already exists` 一致。

---

## 1.4 `ISheet.GetBomTable`（旧 BOM 表取回）

**① 精确签名** —— **[md]** `C:\swapi\types\ISheet\GetBomTable.md`：

```
System.object GetBomTable()
```

★ **0 个参数（无参）**。该文件**没有 `## Remarks` / `## Returns` / `## Parameters` / `## Examples` 段**。

**② `## Remarks`** —— **查不到**。

**③ 官方例子调用序** —— **查不到**。

**④ 枚举** —— 无参，**无**。

**⑤ 废弃链** —— **[md]** 紧跟标题第一句逐字：

> `Obsolete. Superseded by [[IView::GetBOMTable]].`

★ **注意拼写**：官方 Obsolete 行写的是 `IView::GetBOMTable`（**全大写 BOM**），而本机实际存在的文件是 `C:\swapi\types\IView\GetBomTable.md`（**`GetBomTable`**）。**两种拼法都要记，不替它改。**

**前置一句话**：查不到（无 `## Remarks`）。
**配方一句话**：无参调用。

**判定：存疑** · 一句话依据：**[md]** `ISheet\GetBomTable.md` 把后继写成 `[[IView::GetBOMTable]]`，而 **[md]** `C:\swapi\types\IView\GetBomTable.md` 的 front-matter 是 `member: GetBomTable` —— **官方同一族两处拼法不一致**，无法判定后继名的权威写法（不猜）。

---

## 1.5 `IView.GetBomTable` ★本片最硬的一条

**① 精确签名** —— **[md]** `C:\swapi\types\IView\GetBomTable.md`：

```
System.object GetBomTable()
```

★ **0 个参数（无参）**。描述句逐字：`Gets the BOM table found in this drawing view.` `## Returns` = `[[BOM table]]`。

**② `## Remarks` 逐字** —— **[md]** 全文只有一句：

```
This method only returns a BOM table if there is a Microsoft Excel-based BOM for the drawing view.
```

**③ 官方例子调用序** —— **查不到**（该文件**没有 `## Examples` 段**）。

**④ 枚举** —— 无参，**无**。

**⑤ 废弃链** —— **非 Obsolete**。

**前置一句话**：`This method only returns a BOM table if there is a Microsoft Excel-based BOM for the drawing view.`（官方未给 mark）
**配方一句话**：查不到（该成员官方页无 `## Examples` 段）。

**判定：不成立** · 一句话依据：**[仓]** `tools/prove_drawing_batch.py` 把它当「有没有 BOM 表」的通用判据，逐字是 `bom = _get(view, "GetBomTable") if view is not None else None` 且随后 `row["preconditions_held"] = bool(bom is not None)`；而 **[md]** `IView\GetBomTable.md` 的 `## Remarks` 明写「**only** returns a BOM table if there is a **Microsoft Excel-based** BOM」—— **SOLIDWORKS 自带表功能的 BOM（`InsertBomTable2` 起那一族）取不回来**，这个判据在非 Excel BOM 上必然为假。

---

## 1.6 `IView.InsertBomTable6`（工程图 BOM 建表现行入口）

**① 精确签名** —— **[md]** `C:\swapi\types\IView\InsertBomTable6.md`：

```
System.object InsertBomTable6( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.int BomType, System.string Configuration, System.string TableTemplate, System.bool Hidden, System.int IndentedNumberingType, System.bool DetailedCutList, System.bool DissolvePartLevelRows, System.bool DisplayAsOneItem )
```

★ **13 个参数**。描述句逐字：`Inserts a bill of materials (BOM) table for this drawing view using SOLIDWORKS table functionality.`
`## Parameters` 逐条（含 valid-only）：`UseAnchorPoint`: `If true and the appropriate sheet format anchor point exists, then insert table at this point; if false, then use the values specified for the X and Y arguments as the insertion point` · `X`: `X coordinate for the placement of the BOM table` · `Y`: `Y coordinate for the placement of the BOM table` · `AnchorType`: `Anchor type as defined by [[swBomConfigurationAnchorType_e]]` · `BomType`: `Type of BOM table as defined by [[swBomType_e]]` · `Configuration`: `Name of the configuration for this BOM table (see **Remarks**)` · `TableTemplate`: `Path and filename of the template that you want to use that corresponds to this type of table (see **Remarks**)` · `Hidden`: `True to hide the BOM table, false to show it` · `IndentedNumberingType`: `Type of numbering as defined by [[swNumberingType_e]]; valid only for BomType = swBomType_e.swBomType_Indented` · `DetailedCutList`: `True to show the detailed cut list, false to not` · `DissolvePartLevelRows`: `True to dissolve part level rows, false to not; valid only when DetailedCutList is true` · `DisplayAsOneItem`: `True to group into one item number, false to display separately`。
`## Returns` = `[[BOM table annotation]]`。

**② `## Remarks` 逐字（关键三句）** —— **[md]**：

```
If the drawing was created using a configuration other than the Default configuration, then the configuration active at the time the drawing was created is the configuration used in the BOM table when an empty string is specified for the Configuration parameter.
```

```
BOM table templates are in the install_dir\**lang**\<language> folder and have a filename extension of **.sldbomtbt**. The template and table must be of the same type. …
```

```
**NOTE:** Use [[IView::InsertBomTable]] to insert a BOM using Microsoft Excel.
```

★ 最后这句与 §1.5 合起来正面回答了那个判据：**Excel BOM 走 `InsertBomTable`，SOLIDWORKS 表 BOM 走 `InsertBomTable2` 起那一族，两族互不通用。**

**③ 官方例子调用序** —— `## Examples` 列 `Dissolve_Subassembly_in_a_BOM_Table_Example_{VB,VBNET,CSharp}.md` 与 `Insert_and_Show_BOM_Table_and_BOM_Balloon_Example_{VB,VBNET,CSharp}.md`。★ 本轮未逐字读 ⇒ **查不到**。

**④ 枚举** —— `AnchorType` → `swBomConfigurationAnchorType_e`（[en] 见 §1.7）· `BomType` → `swBomType_e`（**本轮未读该枚举文件** ⇒ 成员与数值**查不到**）· `IndentedNumberingType` → `swNumberingType_e`（**本轮未读** ⇒ **查不到**）。

**⑤ 废弃链** —— **非 Obsolete**。

**前置一句话**：`BomType` 为 `swBomType_TopLevelOnly` 时官方说 `do not specify Configuration`；`Configuration` 传空串时用「建图时激活的配置」。
**配方一句话**：查不到（6 个例子文件本轮未逐字读）。

**判定：查不到** · 一句话依据：**[仓]** 全仓按 `InsertBomTable` 检索（`scripts/` `mcp-server/` `tools/` `subskills/` `tests/`），**仓内唯一的命中全在 `scripts/sw_api_sldworks.py` 的反射 dump 与 `_merged_test.py` 的副本里**（逐字 `'InsertFamilyTableEdit': 0,` 一类的表项），**没有一处建表调用点** ⇒ 仓内这一侧**没有可引的第二段原文**，按纪律 2 / 3 不下判断。

---

## 1.7 `swBomConfigurationAnchorType_e`（锚点枚举 · ★ 官方两处拼写不一）

**[en]** `C:\swapi\enums\swBomConfigurationAnchorType_e.md` 的 `## Description` 逐字 `BOM table configuration anchor types.`，成员表：

| Member | Value |
| --- | --- |
| `swBOMConfigurationAnchor_BottomLeft` | 3 = Lower-left corner |
| `swBOMConfigurationAnchor_BottomRight` | 4 = Lower-right corner |
| `swBOMConfigurationAnchor_TopLeft` | 1 = Upper-left corner |
| `swBOMConfigurationAnchor_TopRight` | 2 = Upper-right corner |

★ **本机文件名是小写 `swBom…`，成员名是大写 `swBOM…`** —— 文件名与成员名自身不一致，**照抄，不改**。

> ★★★★ **2026-10-04（接手轮）更正 —— 上面那一句的两处事实错误**（★ 来源：`JUDGE-C_D_E.md` §3.1
> 「**待回写**」+ ★ **我独立复核**）
>
> ★ **错 ①**：★ 原句说「本机文件名是**小写** `swBom…`」⇒ ★★ **实为大写** ✓
> ★ **错 ②**：★ 原句说「文件名与成员名**自身不一致**」⇒ ★★ **实为一致** ✓
>
> ★★ **我怎么核的（★ 两个命令，可复跑）**：
> · ★ `C:\swapi` **全库递归找 `*omConfigurationAnchor*`** ⇒ ★ **只有一个文件**：
>   `C:\swapi\enums\sw**BOM**ConfigurationAnchorType_e.md` ⇒ ★ **文件名是**大写 `swBOM`**** ✓
> · ★★ 读它的 front-matter ⇒ 逐字 `name: sw**BOM**ConfigurationAnchorType_e`
>   ⇒ ★ **文件名与枚举名**一致**** ✓
> · ★★★ 而它的四个成员逐字 `sw**BOM**ConfigurationAnchor_BottomLeft / _BottomRight /
>   _TopLeft / _TopRight` ⇒ ★ **成员名也是大写** ✓
>
> ★★★★ **所以「本机落地的是小写那一种」「文件名与成员名自身不一致」两句都要改** ✓
>
> ⚠⚠ **而下面那个数我也要更正 —— 这次是**裁判**那句**：★ 裁判写「`swBOM…` 与 `swBom…`
>   在官方 `types/` 库里**各 18 次、正好对半**」⇒ ★★ **我复现不出来**：
>   · ★ **文件名**：★ `swBOM*` **7 个** · ★ `swBom*` **3 个**（★ 全 `C:\swapi` 递归）✓
>   · ★★ **全文出现**：★ `swBOM` **462 次** · ★ `swBom` **395 次**（★ 接近、★ **不相等**）✓
>   · ★★★ **而"两种拼法并存"这个**结论**是对的**（★ 两个量法都显示两三种拼法都在）✓
>   ⇒ ★ **按铁律 5：★ 我只写我量到的数**；★ 而"18/18"那个数**我既没复现也没否证**
>     （★ 它可能量的是**另一个范围** —— ★ 例如只 `types/` 不含 `enums/`）⇒
>     ★★ **不把它当错，只把我量到的如实并列** ✓
>
> ★★★ **核心判定不变**：★ 官方在同一套文档里**两种拼法都用**（★ 上面那句的依据仍成立）✓
> ★★★★ **但推理方向要翻**：★ 既然本机落地的**就是与文件名一致的大写**，★
>   那**能落地这一种**本身**就是官方本意的更强证据** ⇒ ★ 「无法判定哪种链接才是官方本意」
>   **偏保守** ✓
> ⚠ **按裁判建议：★ 本条降级为「记档」**（★ 不影响任何代码路径）·
>   ★★ **而它**不能照抄进 `docs/known-facts.md`**（★ 除非把上面这段更正一并带上）✓

**判定：存疑** · 一句话依据：**[md]** `ISheet\InsertRevisionTable2.md` 与 `IDrawingDoc\InsertTableAnnotation2.md` 写 `[[swBOMConfigurationAnchorType_e]]`（大写 BOM），而 **[md]** `IView\InsertBomTable6.md` 与 `IView\InsertHoleTable3.md` 写 `[[swBomConfigurationAnchorType_e]]`（小写 bom）—— **官方在同一套文档里两种拼法都用**，而本机枚举文件只落地了~~**小写文件名**~~那一种 <ins>（★ **2026-10-04 更正：实为**大写** `swBOMConfigurationAnchorType_e.md` —— ★ 见上方更正块）</ins>，无法判定哪种链接才是官方本意 <ins>（★ **2026-10-04 补充：这句偏保守** —— ★ 既然本机落地的**就是与文件名一致的大写**，★ 那**能落地这一种**本身就是官方本意的更强证据）</ins>。

---

## 1.8 `ISheet.InsertFamilyTable`（族表）

**① 精确签名** —— **[md]** `C:\swapi\types\ISheet\InsertFamilyTable.md`：

```
System.object InsertFamilyTable( System.bool AttachToAnchorPoint, System.double X, System.double Y, System.string ModelName, System.string TableTemplateName, System.int DimColumnType, System.bool UseAllConfigs, System.object ConfigArray, System.int ItemNumberStart, System.int ItemNumberIncrement, System.bool FollowConfigTreeOrder )
```

★ **11 个参数**。`## Returns` = `[[IFamilyTableAnnotation]]`。

**② `## Remarks` 逐字** —— **[md]**：

```
Family tables display the variations in part and assembly configurations or custom properties in table format.

By default, the family table templates are in install_dir\**lang**\language and have a filename extension of **.sldfamtbt**. The template and table must be of the same type. For example, you must specify TableTemplate with *install_dir***\lang\English\family-standard.sldfamtbt** if you want to insert an English version of a family table.
```

**③ 官方例子调用序** —— **查不到**（该文件**没有 `## Examples` 段**）。

**④ 枚举** —— `DimColumnType` → `[[swFamilyTableDimColumnType_e]]`（**本轮未读该枚举文件** ⇒ 成员与数值**查不到**）。

**⑤ 废弃链** —— **非 Obsolete**。

**前置一句话**：`ConfigArray`: `valid only if UseAllConfigs is false`（`## Parameters` 逐字）。
**配方一句话**：查不到（该成员官方页无 `## Examples` 段）。

**判定：成立** · 一句话依据：**[仓·反射]** `scripts/sw_api_sldworks.py` 的 `ARITY` 里 `ISheet` 段有逐字 `'InsertFamilyTable': 11,`，与 **[md]** 上面 11 个形参一致。

---

# 二、孔表（3 条）

## 2.1 `IView.InsertHoleTable3`（仓内孔表走的真入口）

**① 精确签名** —— **[md]** `C:\swapi\types\IView\InsertHoleTable3.md`：

```
System.object InsertHoleTable3( System.bool UseAnchorPoint, System.double X, System.double Y, System.int AnchorType, System.string StartValue, System.string Template, System.int TagOrder, System.int TagType, System.object ManualTags )
```

★ **9 个参数**。描述句逐字：`Inserts a hole table in this drawing view.` `## Returns` = `[[Hole table annotation]]`。
`## Parameters` 逐条：`UseAnchorPoint`: `If true, and the sheet format anchor point exists, then insert table at the anchor point; if false, then insert the table at the location specified by the X and Y parameters` · `X`: `X coordinate in meters for the anchor of this hole table` · `Y`: `Y coordinate in meters for the anchor of this hole table` · `AnchorType`: `Anchor type as defined by [[swBomConfigurationAnchorType_e]]` · `StartValue`: `Starting value for the specified TagType` · `Template`: `Path and filename of the hole table template that corresponds to the hole table you want to create (see **Remarks**)` · `TagOrder`: `Tag numbering as defined in [[swHoleTableTagOrder_e]]` · `TagType`: `Tag type as defined in [[swHoleTableTagStyle_e]]` · `ManualTags`: `Array of custom tags; valid only if TagType is swHoleTableTagStyle_e.swHoleTable_ManualTags`。

**② `## Remarks` 逐字（★ 本片唯一的 mark 表）** —— **[md]**：

```
Before calling this method, call [[IModelDocExtension::SelectByID2]] to select the datum origin, hole edges, and faces (for multiple holes) as follows:

**Selection**

**Mark**

Datum origin vertex

1

Hole edges and faces

2

Datum origin x axis direction reference

4

Datum origin y axis direction reference

8
```

模板段逐字：

```
Specify Template using a hole table template (***.sldholtbt**):

- in install_dir\**lang**\*language*.

- that matches the table you want to create. For example, to insert a hole table with letter tags, specify Template using *install_dir***\lang\English\standard hole table--letters.sldholtbt**.
```

★ 官方还逐字写了这张表会显示什么：`This method inserts a hole table with the following information for selected holes:` 后跟 `Datum tag` / `X-location of hole center` / `Y-location of hole center` / `Size of the hole`。

**③ 官方例子调用序** —— `## Examples` 列 `Insert_Hole_Table_Example_{VB,VBNET,CSharp}.md`。★ 本轮未逐字读 ⇒ **查不到**。

**④ 枚举** —— `AnchorType` → `swBomConfigurationAnchorType_e`（[en] 见 §1.7）· `TagOrder` → `swHoleTableTagOrder_e` · `TagType` → `swHoleTableTagStyle_e`。
[en] `C:\swapi\enums\swHoleTableTagOrder_e.md` 描述逐字 `Method by which to assign tag numbers to holes of the same size.`，成员表（**数值列带官方解释，逐字保留**）：

| Member | Value |
| --- | --- |
| `swHoleTableTagOrder_Radial` | 3 = Number holes in order of increasing radial angle from the table view origin, starting at -180 degrees in a counterclockwise direction |
| `swHoleTableTagOrder_ReduceToolPath` | 2 = Number holes in next nearest order, starting at the table view origin |
| `swHoleTableTagOrder_XY` | 1 = Number holes in order of their XLoc and YLoc |

★ `swHoleTableTagStyle_e` 的成员表**本轮未读** ⇒ **查不到**（官方 `## Parameters` 里只用它点名了 `swHoleTable_ManualTags` 这一个成员）。

**⑤ 废弃链** —— **非 Obsolete**。

**前置一句话**：**mark 1 = 基准原点顶点 · 2 = 孔边与面 · 4 = 基准原点 x 轴方向参考 · 8 = y 轴方向参考**。
**配方一句话**：查不到（3 个例子文件本轮未逐字读）。

**判定：成立** · 一句话依据：**[仓]** `scripts/sw_drawing_expose.py` 的 `create_hole_table` 文档串逐字「★★ **前置（官方 Remarks 的 mark 表，逐字）**：基准原点**顶点 mark 1** · 孔**边与面 mark 2** · 原点 X 向参考 mark 4 · Y 向参考 mark 8」，其调用逐字 `C.get_com_member(view, "InsertHoleTable3", False, _mm(x_mm), _mm(y_mm), int(anchor_type), str(start_value), str(template), int(tag_order), int(tag_type), C.create_empty_dispatch_variant())`（**9 个实参**），与 **[md]** 的 9 参签名、4 行 mark 表逐位对应。

---

## 2.2 `IView.InsertHoleTable3` 的模板扩展名

**官方那一段** —— **[md]** `IView\InsertHoleTable3.md` 的 `## Remarks` 逐字 `Specify Template using a hole table template (***.sldholtbt**):`（★ 官方原文三个星号，逐字保留）。

**判定：成立** · 一句话依据：**[仓]** `scripts/sw_drawing_expose.py` 的 `create_hole_table` 文档串逐字「★ `Template` 用 `.sldholtbt`（官方 Remarks：在 `install_dir\\lang\\<language>`）」—— 扩展名与安装目录两处都与 **[md]** 的 Remarks 同形。

---

## 2.3 孔表的 `ManualTags` 有效条件

**官方那一段** —— **[md]** `IView\InsertHoleTable3.md` 的 `## Parameters` 逐字：`ManualTags`: `Array of custom tags; valid only if TagType is swHoleTableTagStyle_e.swHoleTable_ManualTags`。

**判定：成立** · 一句话依据：**[仓]** `scripts/sw_drawing_expose.py` 的 `create_hole_table` 末位实参逐字是 `C.create_empty_dispatch_variant()`，其文档串逐字「★ `ManualTags` 传**空 Dispatch**（★ 事实 12；官方例子里是 `Nothing`）」—— **空 Dispatch 与官方的 `valid only if` 条件同族**（不传自定义标签时置空），且仓库把这条 valid-only 条件**原样记在了文档串里**（逐字可见 `ManualTags` 与「空 Dispatch」并列）。

---

# 三、图纸格式（6 条）

## 3.1 `ISheet.GetProperties2`（当前图纸读数）

**① 精确签名** —— **[md]** `C:\swapi\types\ISheet\GetProperties2.md`：

```
System.object GetProperties2()
```

★ **0 个参数（无参）**。`## Returns` = `Array of doubles (see **Remarks**)`。

**② `## Remarks` 逐字** —— **[md]**：

```
The return value is the following array of eight doubles:

 [ paperSize, templateIn, scale1, scale2, firstAngle, width, height, sameCustomProp ]
```

其中逐字：`paperSize = Paper size; this value is a long or integer packed into a double and is represented by the [[swDwgPaperSizes_e]] enumeration` · `templateIn = Template index; … represented by the [[swDwgTemplates_e]] enumeration` · `scale1 = Scale numerator` · `scale2 = Scale denominator` · `firstAngle = Value is a boolean packed into a double and returns true if the sheet is using first angle projection; false if not` · `width = Paper width` · `height = Paper height` · `*sameCustomProp* = Value is a boolean packed into a double and returns true if the **Same as sheet specified in Document Properties** in the Sheet Properties dialog is selected, false if not`。

**③ 官方例子调用序** —— `## Examples` 列 `Set_Drawing_Sheet_Properties_Example_{CSharp,VBNET,VB}.md`。★ 本轮未逐字读 ⇒ **查不到**。

**④ 枚举** —— 无参形参；**值域**指向 `swDwgPaperSizes_e` 与 `swDwgTemplates_e`（★ **本轮未读这两个枚举文件** ⇒ 成员与数值**查不到**）。

**⑤ 废弃链** —— **非 Obsolete**（它是 `GetProperties` 的后继，见 §3.2）。

**前置一句话**：无参、无预选；官方 `## NOTES` 逐字「To ensure a correct return value, open the document as read-write or read-only. Insufficient information is available if you open the document as view-only.」
**配方一句话**：查不到（3 个例子文件本轮未逐字读）。

**判定：成立** · 一句话依据：**[仓]** `scripts/sw_drawing_query.py` 的 `current_sheet_info` 文档串逐字「★ 官方 `ISheet.GetProperties2()` 返回 **8 个 double**，次序照官方 Remarks： `[paperSize, templateIn, scale1, scale2, firstAngle, width, height, sameCustomPrp]`」—— **个数（8）与次序（8 项逐项同名）都与 [md] 的 `eight doubles` 与方括号列表逐项对上**。

---

## 3.2 `ISheet.GetProperties`（旧版，★ 官方正文自相矛盾）

**① 精确签名** —— **[md]** `C:\swapi\types\ISheet\GetProperties.md`：`System.object GetProperties()` ★ **0 个参数**。
**② `## Remarks` 逐字** —— **[md]**：

```
The return value is the following array of seven doubles:

 [ paperSize, templateIn, scale1, scale2, firstAngle, width, height, sameCustomPrp ]
```

★ **正文写 `seven doubles`，紧跟的方括号里却列了 8 项**（最后一项是 `sameCustomPrp`，比 `GetProperties2` 的 `sameCustomProp` 少一个字母）。

**⑤ 废弃链** —— **[md]** 紧跟标题第一句逐字：`Obsolete. Superseded by [[ISheet::GetProperties2]].`

**判定：存疑** · 一句话依据：**[md]** `ISheet\GetProperties.md` 的 `## Remarks` 自称 `seven doubles` 却列出 8 项，而 **[md]** `ISheet\GetProperties2.md`（后继）同一位置逐字写 `eight doubles` 且同样列 8 项 —— **官方旧页这一句自相矛盾**，本轮不替官方裁定旧接口到底返回几个（不猜）。

---

## 3.3 `ISheet.SetScale`（图纸比例）

**① 精确签名** —— **[md]** `C:\swapi\types\ISheet\SetScale.md`：

```
System.bool SetScale( System.double Numerator, System.double Denominator, System.bool ScaleAnnoPosition, System.bool ScaleAnnoTextHeight )
```

★ **4 个参数**。`## Returns` = `True if the scale is set, false if not`。
`## Parameters` 逐条：`Numerator`: `First value in the scale ratio (n : n)` · `Denominator`: `Second value in the scale ratio (n : n)` · `ScaleAnnoPosition`: `True if the position of the annotations is scaled, false if not` · `ScaleAnnoTextHeight`: `True if the text height of the annotations is scaled, false if not`。
**② `## Remarks` 逐字** —— **[md]**：`You can also set the two scale values by using [[IDrawingDoc::SetupSheet4]] or [[ISheet::SetProperties]]. However, you cannot specify the scaling of the position or text height of the annotations. …`
**⑤ 废弃链** —— **非 Obsolete**。

**判定：成立** · 一句话依据：**[仓]** `scripts/sw_drawing_query.py` 逐字 `ret = _get(sheet, "SetScale", num, den, bool(scale_anno_position), bool(scale_anno_text_height))`（**4 个实参**、顺序与 **[md]** 的 4 形参逐位对应）。

---

## 3.4 「`SetScale` 的 `Numerator` 只接受 1」

**官方那一段** —— **[md]** `ISheet\SetScale.md` 对 `Numerator` 只有一句：`First value in the scale ratio (n : n)`。**官方全文没有任何地方写「Numerator 必须为 1」。**

**判定：查不到** · 一句话依据：**[仓]** `scripts/sw_drawing_query.py` 记的是三条**真机实测**逐字「★ 真机三组：`SetScale(1, 5)` → 读回 **1:5** ✓；`SetScale(3, 7)` → 读回 **1:7**；`SetScale(2, 1)` → 读回 **1:1**」，而 **[md]** `ISheet\SetScale.md` 全文**没有**这条约束 ⇒ **仓内这一侧的官方依据不存在**，按纪律 2「给不出两段的一律不写」⇒ 判为**查不到**（记录实测事实，不判官方对错）。

---

## 3.5 `IDrawingDoc.SetupSheet6`（新建 / 重置图纸）

**① 精确签名** —— **[md]** `C:\swapi\types\IDrawingDoc\SetupSheet6.md`：

```
System.bool SetupSheet6( System.string Name, System.int PaperSize, System.int TemplateIn, System.double Scale1, System.double Scale2, System.bool FirstAngle, System.string TemplateName, System.double Width, System.double Height, System.string PropertyViewName, System.bool RemoveModifiedNotes, System.double ZoneLeftMargin, System.double ZoneRightMargin, System.double ZoneTopMargin, System.double ZoneBottomMargin, System.int ZoneRow, System.int ZoneCol )
```

★ **17 个参数**。`## Returns` = `True if drawing sheet setup is successful, false if not`。
`## Parameters` 里的 valid-only 逐条摘录：`PaperSize`: `Size of paper as defined in [[swDwgPaperSizes_e]]; valid only if TemplateIn is set to swDwgTemplates_e.swDwgTemplateNone` · `TemplateName`: `Name of custom template with full directory path; valid only if TemplateIn is set to swDwgTemplates_e.swDwgTemplateCustom` · `Width` / `Height`: `valid only if TemplateIn is set to swDwgTemplates_e.swDwgTemplateNone or PaperSize is set to swDwgPaperSizes_e.swDwgPapersUserDefined`。

**② `## Remarks` 逐字（两句关键）** —— **[md]**：

```
After calling this method, call [[IModelDoc2::ForceRebuild3]] to update any changes to first angle/third angle projections in the drawing views.
```

```
Multiplying ZoneRow by ZoneCol equals the total number of zones in the zone area of this drawing sheet. …
```

**③ 官方例子调用序** —— `## Examples` 列 `Create_Drawing_Sheet_Zones_Example_{VB,VBNET,CSharp}.md` 与 `Modify_Multiple_Drawing_Sheets_Setups_Example_{CSharp,VBNET,VB}.md`。★ 本轮未逐字读 ⇒ **查不到**。

**④ 枚举** —— `PaperSize` → `swDwgPaperSizes_e` · `TemplateIn` → `swDwgTemplates_e`（★ **本轮未读这两个枚举文件** ⇒ 成员与数值**查不到**）。

**⑤ 废弃链** —— **非 Obsolete**。

**前置一句话**：`After calling this method, call IModelDoc2::ForceRebuild3 …`（改一/三投影后必须重建）。
**配方一句话**：查不到（6 个例子文件本轮未逐字读）。

**判定：成立** · 一句话依据：**[仓·反射]** `scripts/sw_api_sldworks.py` 的 `ARITY` 里 `IDrawingDoc` 段有逐字 `'SetupSheet': 5,` … `'SetupSheet5': 11,` `'SetupSheet6': 17,` —— **`SetupSheet6` 的 17 与 [md] 上面 17 个形参逐位对应**（且仓内 `tools/prove_drawing_batch.py` 的调用逐字是 `_get(doc, "SetupSheet6", str(sheet_name), int(paper), int(tmpl_in), …`，同为 17 位）。

---

## 3.6 `ISheet.SetTemplateName`（换图框）

**① 精确签名** —— **[md]** `C:\swapi\types\ISheet\SetTemplateName.md`：

```
void SetTemplateName( System.string NameIn )
```

★ **1 个参数**，**返回 `void`**（★ 不是 `bool`、不是 `Feature`）。
`## Parameters`：`NameIn`: `Path name of the sheet format template`。

**② `## Remarks` 逐字** —— **[md]**：

```
- a custom template name, before calling this method, call [[ISheet::SetProperties]] and specify swDwgTemplates_e.swDwgTemplateCustom for the Templ parameter.

- one of the standard templates provided by SOLIDWORKS, then there is no need to call ISheet::SetTemplateName. Instead, call ISheet::SetProperties and specify the appropriate enumerator for the Templ parameter.
```

**⑤ 废弃链** —— **非 Obsolete**。

**前置一句话**：用**自定义**模板名时，官方要求**先**调 `SetProperties` 并把 `Templ` 设成 `swDwgTemplates_e.swDwgTemplateCustom`。
**配方一句话**：查不到（3 个例子文件本轮未逐字读）。

**判定：成立** · 一句话依据：**[仓]** `scripts/sw_drawing_expose.py` 的文档串逐字「官方逐字：`ISheet.SetTemplateName(System.string NameIn)` ⇒ `void`，**未废弃**」，其调用逐字 `ret = C.get_com_member(sheet, "SetTemplateName", str(format_path))`（**1 个实参**），与 **[md]** 的 1 形参 + `void` 返回逐位一致。

---

# 四、输出 PDF 与 DXF（5 条）

## 4.1 `ISldWorks.GetExportFileData` + `swExportDataFileType_e`（取 PDF 导出数据）

**① 精确签名** —— **[md]** `C:\swapi\types\ISldWorks\GetExportFileData.md`：

```
System.object GetExportFileData( System.int FileType )
```

★ **1 个参数**。描述句逐字：`Gets the data interface for the specified file type to which to export one or more drawing sheets.` `## Parameters`：`FileType`: `File type as defined in [[swExportDataFileType_e]]` `## Returns` = `[[Data interface]] for the specified file type to which to export one or more drawing sheets`。

**④ 枚举** —— [en] `C:\swapi\enums\swExportDataFileType_e.md` 描述逐字 `Export data file types.`，**只有 1 个成员**：

| Member | Value |
| --- | --- |
| `swExportPdfData` | 1 |

★ 即：**这个枚举里除 PDF 没有别的**，且成员名是 `Pdf` 不是 `PDF`。

**判定：成立** · 一句话依据：**[仓]** `scripts/sw_export.py` 逐字 `pdf_data = sw.GetExportFileData(1)  # swExportDataFileType_e.swExportPdfData`，其出处块逐字「`swExportPdfData = 1`（⚠ 是 `Pdf` 不是 `PDF`）· ⚑ 行尾原注释写的是 `swExportPDFData` —— **官方没有这个名字**」—— 与 **[md]** + **[en]** 的「唯一成员 `swExportPdfData` = 1」逐字对上。

---

## 4.2 `IExportPdfData.SetSheets` 的第一实参 ★

**① 精确签名** —— **[md]** `C:\swapi\types\IExportPdfData\SetSheets.md`：

```
System.bool SetSheets( System.int Which, System.object Sheets )
```

★ **2 个参数**。`## Parameters` 逐条：`Which`: `Drawing sheets to export to PDF as defined in [[swExportDataSheetsToExport_e]]` · `Sheets`: `Array of the names of the drawing sheets to export` `## Returns` = `True if the drawings sheets are set to export to PDF, false if not`。

**④ 枚举** —— [en] `C:\swapi\enums\swExportDataSheetsToExport_e.md` 描述逐字 `Export data sheets to export options.`，成员表**全部 3 个**：

| Member | Value |
| --- | --- |
| `swExportData_ExportAllSheets` | 1 |
| `swExportData_ExportCurrentSheet` | 2 |
| `swExportData_ExportSpecifiedSheets` | 3 |

★ **没有任何成员取值为 `0`。**
★ 官方 **[ex]** `C:\swapi\examples\Save_File_as_PDF_Example_VB.md` 逐字：`boolstatus = swExportPDFData.SetSheets(swExportData_ExportSpecifiedSheets, varSheetName)`（= **3**）。

**判定：不成立** · 一句话依据：**[仓]** `scripts/sw_export.py` 的 `export_to_pdf` 逐字 `pdf_data.SetSheets(0, sheet_names)` —— 传 **0**，而 **[en]** `swExportDataSheetsToExport_e.md` 的成员表只有 1 / 2 / 3、**[ex]** 官方例子传的是 `swExportData_ExportSpecifiedSheets`；顺带 **[md]** `IModelDocExtension\SaveAs3.md` 的 `## Remarks` 逐字写「**If ExportData is Nothing or null, then all sheets are saved to PDF**」⇒ **「全部图纸」在官方口径里是「`ExportData` 置空」，不是一个 `Which=0`**。

---

## 4.3 工程图 → PDF 走的保存入口 ★

**① 官方那一段（被调方）** —— **[md]** `C:\swapi\types\IModelDocExtension\SaveAs.md` 紧跟标题第一句逐字：

> `Obsolete. Superseded by [[IModelDocExtension::SaveAs2]].`

其 `**Signature**` 逐字：`System.bool SaveAs( System.string Name, System.int Version, System.int Options, System.object ExportData, out System.int Errors, System.int Warnings )` ★ **6 个形参**。
★ 再往下一级也是废弃的：**[md]** `C:\swapi\types\IModelDocExtension\SaveAs2.md` 逐字 `Obsolete. Superseded by [[IModelDocExtension::SaveAs3]].`，其签名 **8 个形参**（多 `ReferencePrefixOrSuffixText` 与 `AddTextAsPrefix`）。

**② 官方例子那一段** —— **[ex]** `C:\swapi\examples\Save_File_as_PDF_Example_VB.md` 逐字：

```
Set swExportPDFData = swApp.GetExportFileData(1)
...
boolstatus = swExportPDFData.SetSheets(swExportData_ExportSpecifiedSheets, varSheetName)
swExportPDFData.ViewPdfAfterSaving = True
boolstatus = swModelDocExt.SaveAs(filename, 0, 0, swExportPDFData, lErrors, lWarnings)
```

⇒ **官方这个 PDF 例子本身用的也是已废弃的 `SaveAs`**（记事实，不作评价）。

**判定：不成立** · 一句话依据：**[仓]** `scripts/sw_export.py` 的 `export_to_pdf` 逐字 `success = model.Extension.SaveAs(str(output_path), 0, 1, pdf_data, errors, warnings)`（**6 个实参**，与 **[md]** 的 6 形参对得上），但被调的 **[md]** `IModelDocExtension\SaveAs.md` 正文第一句就是 `Obsolete. Superseded by [[IModelDocExtension::SaveAs2]].` ⇒ **本仓这条 PDF 出口压在一个官方已标废弃的成员上**；而同一仓的 `scripts/sw_com_traps.py` 自己写着「**本项目导出/保存一律用 `SaveAs3`**，不要用 SaveAs / SaveAs2」—— **两处自相矛盾**。

---

## 4.4 DXF 出口：`SaveAs4` 到底存不存在 ★

**官方那一段（存在侧）** —— **[md]** `C:\swapi\types\IModelDoc2\SaveAs4.md` 逐字：

```
System.bool SaveAs4( System.string Name, System.int Version, System.int Options, out System.int Errors, out System.int Warnings )
```

其 `## Parameters` 五行**全是** `No description`；紧跟标题第一句逐字 `Obsolete. Superseded by [[IModelDocExtension::SaveAs]].`
**官方那一段（不存在侧）** —— **[md]** `C:\swapi\types\IModelDocExtension\` 下按 `SaveAs*.md` 过滤**只有 3 个文件**：`SaveAs.md` / `SaveAs2.md` / `SaveAs3.md` —— **没有 `SaveAs4.md`**。

**官方例子那一段（DXF）** —— **[ex]** `C:\swapi\examples\Save_Drawing_as_DXF_Example_VB.md` 逐字：

```
bRet = swModel.SaveAs4(sPathName, swSaveAsCurrentVersion, swSaveAsOptions_Silent, nErrors, nWarnings)
```

（该例子还逐字写了 DXF 的用户偏好开关：`swDxfMapping` / `swDXFDontShowMap` / `swDxfVersion` / `swDxfOutputFonts` / `swDxfMappingFileIndex` / `swDxfOutputLineStyles` / `swDxfOutputNoScale` / `swDxfMappingFiles` / `swDxfOutputScaleFactor`。）
★ 另：**[ex]** `C:\swapi\examples\Save_Drawing_Sheets_as_DXF_Example_VB.md` 存在（本轮**未逐字读**）。

**判定：不成立** · 一句话依据：**[仓]** `scripts/sw_com_traps.py` 的出处块逐字写「⚑ 〔反射核〕本机 SolidWorks 版本上三者的 arity：`SaveAs=4 · SaveAs2=6 · **SaveAs3=5**` · **SaveAs4 不存在**」；而 **[仓·反射]** 同一文件 `scripts/sw_api_sldworks.py` 的 `ARITY` 里 **`IModelDoc2` 段自己就有 `'SaveAs4': 3,`** —— **仓内两处自相矛盾**，且 **[md]** `C:\swapi\types\IModelDoc2\SaveAs4.md` 与 **[ex]** 官方 DXF 例子都逐字写明它存在。
★ 该句**只对 `IModelDocExtension` 成立**（那个接口下确实只有 SaveAs/SaveAs2/SaveAs3）；本条判「不成立」针对的是那句**不带接口限定的「SaveAs4 不存在」**。

★ **附带一条（不单独立条）**：**[仓]** `scripts/sw_export.py` 的 `export_to_dxf` 对工程图分支逐字 `if doc_type == 3:  # 工程图` / `return _export_generic(model, output_path)`，而 `_export_generic` 逐字调 `model.Extension.SaveAs(output_path, 0, 1, create_empty_dispatch_variant(), errors, warnings)` —— **工程图 DXF 走的是 `IModelDocExtension.SaveAs`，不是官方 DXF 例子逐字演示的 `IModelDoc2.SaveAs4`**。

---

## 4.5 `ITableAnnotation.SaveAsPDF`（表 → PDF）

**① 精确签名** —— **[md]** `C:\swapi\types\ITableAnnotation\SaveAsPDF.md`：

```
System.bool SaveAsPDF( System.string FileName )
```

★ **1 个参数**。描述句逐字：`Saves this table to a PDF file.` `## Returns` = `True if the table is saved to a PDF file, false if not`。
**② `## Remarks` 逐字** —— **[md]**：`You must specify a filename. It should include the path, filename, and the PDF filename extension to which to save the table.` 后跟一张表：`Exists` → `Overwritten` / `Does not exist` → `Created`。
**③ 官方例子** —— `## Examples` 列 `Save_Table_Annotation_to_PDF_Example_{CSharp,VBNET,VB}.md`。★ 本轮未逐字读 ⇒ **查不到**。
**⑤ 废弃链** —— **非 Obsolete**。

**判定：查不到** · 一句话依据：**[仓]** 全仓按 `SaveAsPDF` 检索，唯一命中在 **[仓·反射]** `scripts/sw_api_sldworks.py` 的 `ARITY` 里 `ITableAnnotation` 段的表项（与 `SaveAsTemplate` / `SaveAsText` / `SaveAsText2` 并列的一行），**没有任何 `scripts/` `mcp-server/` `tools/` 的调用点** ⇒ 仓内这一侧没有可引的第二段原文。

---

# 五、图层（1 条 · 整族）

## 5.1 图层族（建层 / 切层 / 枚举 / 改属性）

**官方那一段（签名逐字）** —— [md] 逐条：

| 成员 | 签名逐字 | 形参数 | 废弃链逐字 |
| --- | --- | --- | --- |
| `IDrawingDoc.CreateLayer` | `System.bool CreateLayer( System.string Layername, System.string LayerDesc, System.int LayerColor, System.int LayerStyle, System.int LayerWidth, System.bool BOn )` | 6 | `Obsolete. Superseded by IDrawingDoc::CreateLayer2.`（★ 官方此处**不带** `[[ ]]`） |
| `IDrawingDoc.CreateLayer2` | `System.bool CreateLayer2( System.string Layername, System.string LayerDesc, System.int LayerColor, System.int LayerStyle, System.int LayerWidth, System.bool BOn, System.bool BPrint )` | 7 | 非 Obsolete |
| `IDrawingDoc.SetCurrentLayer` | `System.bool SetCurrentLayer( System.string Layername )` | 1 | 非 Obsolete |
| `IDrawingDoc.ChangeComponentLayer` | `void ChangeComponentLayer( System.string Layername, System.bool AllViews )` | 2 | 非 Obsolete |
| `ILayerMgr.AddLayer` | `System.int AddLayer( System.string NameIn, System.string DescIn, System.int ColorIn, System.int StyleIn, System.int WidthIn )` | 5 | 非 Obsolete |
| `ILayerMgr.GetLayerList` | `System.object GetLayerList()` | 0 | 非 Obsolete |
| `ILayer.GetItems` | `System.object GetItems( System.int ItemType )` | 1 | 非 Obsolete |

`## Remarks` 摘录逐字：`IDrawingDoc.CreateLayer2.md` 的 `Do not use backslash or @ symbols in Layername.` · `IDrawingDoc.SetCurrentLayer.md` 的 `SOLIDWORKS creates subsequent items on the specified layer.` · `IDrawingDoc.ChangeComponentLayer.md` 的 `AllViews`: `True changes the component layer for all views in the drawing, false changes only the selected view` · `ILayerMgr.GetLayerList.md` 的 `This is a 0-based array (first element is at position 0).`

**④ 枚举** —— [en] `C:\swapi\enums\swLayerItemsOption_e.md` 描述逐字 `Layer item types.`，成员表：

| Member | Value |
| --- | --- |
| `swLayerItemsOption_Annotations` | 1 or 0x1 |
| `swLayerItemsOption_SketchBlockInstance` | 4 or 0x4 |
| `swLayerItemsOption_SketchHatch` | 10 or 0x10 |
| `swLayerItemsOption_SketchPoint` | 8 or 0x8 |
| `swLayerItemsOption_SketchSegments` | 2 or 0x2 |

（`swLayerStyle_e` / `swLineStyles_e` / `swLineWeights_e` 由 `CreateLayer{,2}` / `ILayerMgr.AddLayer` 的 `## Parameters` 点名，★ **本轮未读这三个枚举文件** ⇒ 成员与数值**查不到**。）

**判定：查不到** · 一句话依据：**[仓]** 按 `CreateLayer` / `SetCurrentLayer` / `ChangeComponentLayer` / `GetLayerList` / `ILayerMgr` 检索 `scripts/` `mcp-server/` `tools/` `subskills/` `tests/`，**除 `scripts/sw_api_sldworks.py`（反射 dump 的 `ARITY` / `PROPERTIES` 表项，如 `'ILayerMgr': {` 段下的 `'GetCurrentLayer': 0,` `'GetLayerList': 0,`）与 `_merged_test.py` 的同名副本外，没有任何调用点、没有任何工具封装** ⇒ 仓内这一侧没有可引的第二段原文，**不下「有没有实现」的判断**。

---

# 六、核对结论汇总（★ 23 处）

| # | 结论对象 | 判定 | 一句话依据（仓内段 → 官方/目标段） |
|---|---|---|---|
| 1 | `IDrawingDoc.InsertTableAnnotation` 签名抄录 | **成立** | `sw_drawing_expose.py` 文档串的 `InsertTableAnnotation(X, Y, AnchorType, Rows, Columns)` → `InsertTableAnnotation.md` 同形 5 参 |
| 2 | `InsertTableAnnotation{,2}` 形参数 | **成立** | `sw_api_sldworks.py` `ARITY` 的 `'InsertTableAnnotation': 5` `'InsertTableAnnotation2': 7` → 两份 md 的 5 / 7 形参 |
| 3 | `ISheet.InsertRevisionTable2` 签名 + Returns + 模板 | **成立** | `sw_drawing_expose.py` 的 7 实参调用 + 「回 `null` 是契约」→ md 的 7 参 + `or null if a revision table already exists` + `.sldrevtbt` |
| 4 | `ISheet.GetBomTable` 的后继名拼写 | **存疑** | `ISheet\GetBomTable.md` 写 `[[IView::GetBOMTable]]` → `IView\GetBomTable.md` 的 front-matter 是 `member: GetBomTable` |
| 5 | **`IView.GetBomTable` 当「有没有 BOM 表」判据** | **不成立** | `prove_drawing_batch.py` 的 `bom = _get(view, "GetBomTable")` + `preconditions_held = bool(bom is not None)` → md 的 `only returns a BOM table if there is a Microsoft Excel-based BOM` |
| 6 | `IView.InsertBomTable6`（BOM 建表现行入口） | **查不到** | 全仓无调用点（仅反射 dump 有表项）→ md 有 13 参签名与 `.sldbomtbt` Remarks；仓内无第二段 |
| 7 | `swBomConfigurationAnchorType_e` 拼写 | **存疑** | `InsertRevisionTable2.md` / `InsertTableAnnotation2.md` 写 `swBOM…` vs `InsertBomTable6.md` / `InsertHoleTable3.md` 写 `swBom…`；本机只落地小写文件名那一种 |
| 8 | `ISheet.InsertFamilyTable` 形参数 | **成立** | `sw_api_sldworks.py` `ARITY` 的 `'InsertFamilyTable': 11` → md 的 11 形参 |
| 9 | **`IView.InsertHoleTable3` 签名 + mark 表** | **成立** | `sw_drawing_expose.py` 的 9 实参 + 「顶点 1 · 孔边与面 2 · X 向 4 · Y 向 8」→ md 的 9 参 + 四行 mark 表 |
| 10 | 孔表模板扩展名 `.sldholtbt` | **成立** | `sw_drawing_expose.py` 文档串的 `.sldholtbt` → md 的 `(***.sldholtbt**)` |
| 11 | `ManualTags` 的 valid-only 与空 Dispatch | **成立** | `sw_drawing_expose.py` 的 `C.create_empty_dispatch_variant()` + 文档串「空 Dispatch」→ md 的 `valid only if TagType is …swHoleTable_ManualTags` |
| 12 | `ISheet.GetProperties2` 返回 8 个 double | **成立** | `sw_drawing_query.py` 文档串的 8 项次序表 → md 的 `array of eight doubles` + 同 8 项方括号表 |
| 13 | `ISheet.GetProperties`（旧）返回几个 | **存疑** | md 自称 `seven doubles` 却列 8 项；后继 `GetProperties2.md` 同位置写 `eight doubles` |
| 14 | `ISheet.SetScale` 形参数 | **成立** | `sw_drawing_query.py` 的 4 实参 → md 的 4 形参 |
| 15 | 「`Numerator` 只接受 1」 | **查不到** | `sw_drawing_query.py` 记三条真机实测 → `SetScale.md` 全文只有 `First value in the scale ratio (n : n)`，无此约束 |
| 16 | `IDrawingDoc.SetupSheet6` 形参数 | **成立** | `sw_api_sldworks.py` `ARITY` 的 `'SetupSheet6': 17` → md 的 17 形参 |
| 17 | `ISheet.SetTemplateName` 返回 `void` / 1 参 | **成立** | `sw_drawing_expose.py` 的 1 实参 + 「⇒ `void`，**未废弃**」→ md 的 `void SetTemplateName( System.string NameIn )` |
| 18 | `SetTemplate` 这个成员名 | **查不到（名字缺席）** | `audit_gap_implementations.py` 的 `"工程图/图纸格式模板": ["SetupSheet5", "SetTemplate"]` → `ISheet\*Template*.md` 只有 4 个、全 `types\` 递归 `SetTemplate.md` **0 个文件**（官方对应成员是 `SetTemplateName`，见 #17） |
| 19 | `ISldWorks.GetExportFileData(1)` = PDF | **成立** | `sw_export.py` 的 `GetExportFileData(1)  # swExportDataFileType_e.swExportPdfData` → md 的 1 参签名 + en 的唯一成员 `swExportPdfData = 1` |
| 20 | **`IExportPdfData.SetSheets(0, …)`** | **不成立** | `sw_export.py` 的 `pdf_data.SetSheets(0, sheet_names)` → en 的成员表只有 1/2/3（无 0），官方 ex 传 `swExportData_ExportSpecifiedSheets`；「全部图纸」在 `SaveAs3.md` 里是 `ExportData` 置空 |
| 21 | **PDF 出口压在被废弃成员上** | **不成立** | `sw_export.py` 的 `model.Extension.SaveAs(...)` + `sw_com_traps.py` 自写「一律用 `SaveAs3`」 → `SaveAs.md` 第一句 `Obsolete. Superseded by [[IModelDocExtension::SaveAs2]].` |
| 22 | **「SaveAs4 不存在」** | **不成立** | `sw_com_traps.py` 的「SaveAs4 不存在」 vs 同一仓 `sw_api_sldworks.py` `ARITY` 的 `IModelDoc2` 段 `'SaveAs4': 3` → `IModelDoc2\SaveAs4.md` 存在 + 官方 DXF ex 逐字 `swModel.SaveAs4(...)`（该句只对 `IModelDocExtension` 成立） |
| 23 | 图层族（建层/切层/枚举/改属性） | **查不到** | 仓内 `scripts/` `mcp-server/` `tools/` 零调用（只有 `sw_api_sldworks.py` 的 `ARITY`/`PROPERTIES` 表项）→ md 的 7 条签名 + en 的 `swLayerItemsOption_e` 五成员 |

★ **统计：成立 11 · 不成立 4（第 5、20、21、22 条）· 存疑 3（第 4、7、13 条）· 查不到 5（第 6、15、18、23 条 + §〇 的 `SetTemplateName` 形参第二源缺失）。**

---

# 七、本轮明确「查不到」的项（★ 不猜）

1. **CHM 源本轮完全没查** —— `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\` 与 `sldworksapivb6\` 一页未开 ⇒ 本文件**没有 [chm-api] / [chm-vb6] 那一层互证**，所有「成立」判定都建立在 **[md]（`C:\swapi\types\`）** 与 **[仓]** 两段上。
2. **本片没有逐字读任何官方例子** —— `Insert_General_Table_Example_VB.md`、`Create_Drawing_Sheet_Zones_Example_{VB,VBNET,CSharp}.md`、`Set_Drawing_Sheet_Properties_Example_{CSharp,VBNET,VB}.md`、`Dissolve_Subassembly_in_a_BOM_Table_Example_*`、`Insert_and_Show_BOM_Table_and_BOM_Balloon_Example_*`、`Insert_Hole_Table_Example_{VB,VBNET,CSharp}.md`、`Get_Layers_Example_{CSharp,VBNET,VB}.md`、`Save_Table_Annotation_to_PDF_Example_*`、`Save_Drawing_Sheets_as_DXF_Example_VB.md` 全部**只看见文件名、未逐字读** ⇒ 这些成员的「配方一句话」一律写**查不到**。
   ★ 唯二逐字读过的两个例子：`Save_File_as_PDF_Example_VB.md`、`Save_Drawing_as_DXF_Example_VB.md`（已在本文件 §4.3 / §4.4 引用）。
3. **本轮未读的枚举文件**（成员与数值查不到）：`swBomType_e` · `swNumberingType_e` · `swHoleTableTagStyle_e` · `swFamilyTableDimColumnType_e` · `swRevisionTableSymbolShape_e` · `swDwgPaperSizes_e` · `swDwgTemplates_e` · `swLineStyles_e` · `swLineWeights_e`。
4. **`swDxfFormat_e` 与 `swDxfMultisheet_e` 的归属**：**[en]** 两个枚举文件都在（`swDxfFormat_e` 9 个成员、`R12=0` 至 `swDxfFormat_R2018=8`），但本轮按 `DXF` 全量扫 `C:\swapi\types\*\*.md` 时，**只有 `IPartDoc\ExportFlatPatternView.md` 引用了 `swDxfFormat_e`** —— **工程图域里哪个成员吃这个枚举，查不到**（不拿钣金的 `ExportFlatPatternView` 顶替）。
5. **工程图域有没有专门的 DXF 导出成员** —— 按 `DXF` 扫 `IDrawingDoc\*.md` / `ISheet\*.md` / `IModelDocExtension\*.md` / `ISldWorks\*.md`，命中的全是**导入**侧（`GetImportFileData` / `InsertDwgOrDxfFile2` / `AttachDimensions` 里那句 `for example, in an imported DXF file`）与**用户偏好**侧（`GetUserPreference*Value` 里那几个 DXF 偏好开关）；**导出侧只能查到官方例子用的 `IModelDoc2.SaveAs4`** ⇒ 「有无名为 `ExportDxf` 的成员」**查不到**（`C:\swapi\types\` 全库按 `-Filter '*Dxf*.md'` 只命中 `IFeatureManager\InsertDwgOrDxfFile.md` 与 `…2.md` 两个**导入**成员）。
