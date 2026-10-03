# 核对 05-drawing · 核对 C（废弃链与枚举取值）

**域**：`05-drawing` · **核对项**：C（① 我们调的是不是官方标了 Obsolete 的成员 ② 字面量当枚举传时值是否合法成员）
**我们这边的文件**：`scripts/sw_drawing.py` · `scripts/sw_drawing_expose.py` · `scripts/sw_drawing_create_missing.py`
**官方源**：`C:\swapi\types\*.md` · `C:\swapi\enums\*.md`

> `scripts/sw_drawing.py` 全文 29 行，只做 `spec_from_file_location` 桥接再导出，**不含任何 COM 调用** ⇒ 本核对无可核对项。
> 带 COM 调用的只有 `sw_drawing_expose.py` 与 `sw_drawing_create_missing.py` 两个文件。

---

## 发现（4 条）

| # | 我们的原文（文件 + 片段）| 官方的原文（文件 + 片段）| 分歧点 | 置信度 |
| --- | --- | --- | --- | --- |
| 1 | `scripts/sw_drawing_expose.py` — `if str(C.get_com_member(view, "Name") or "") == str(view_name):` | `C:\swapi\types\IView\Name.md` — `Obsolete. Superseded by [[IView::GetName2]] and [[IView::SetName2]].` | 调用的 `IView.Name` 被官方标 **Obsolete**，官方点名的后继是 `GetName2`/`SetName2`。此处是 `_view_by_name()` 取视图名的**唯一**取名路径（`create_hole_table` 靠它按名解析视图）。 | 高 |
| 2 | `scripts/sw_drawing_create_missing.py` — `    raw = _read(view, "Name")` | `C:\swapi\types\IView\Name.md` — `Obsolete. Superseded by [[IView::GetName2]] and [[IView::SetName2]].` | 同一个 `IView.Name` 的第二处调用：`_view_name()` 里 `GetName2` 回 `None` 时的兜底分支，也是 Obsolete 成员。 | 高 |
| 3 | `scripts/sw_drawing_expose.py` — `                          template: str = "", shape: int = 0,`（该值随后由 `int(anchor_type), str(template), int(shape),` 传给 `ISheet.InsertRevisionTable2` 的 `Shape` 形参）| `C:\swapi\enums\swRevisionTableSymbolShape_e.md` — `enum_member_count: 4`，成员表全为 `swRevisionTable_CircleSymbol | 1` / `swRevisionTable_SquareSymbol | 2` / `swRevisionTable_TriangleSymbol | 3` / `swRevisionTable_HexagonSymbol | 4` | `ISheet.InsertRevisionTable2.md` 逐字写 `Shape`: "Revision symbol shape as defined in [[swRevisionTableSymbolShape_e]]" ⇒ 该实参是该枚举的取值，而 **`swRevisionTableSymbolShape_e` 四个成员的取值是 1/2/3/4，没有 0** ⇒ 默认值 `shape: int = 0` 不是该枚举的任何合法成员。 | 高 |
| 4 | `scripts/sw_drawing_expose.py` — `                       no_outline: bool = False, shape_intensity: int = 0) -> dict:` | `C:\swapi\types\IDrawingDoc\CreateDetailViewAt4.md` — `**ShapeIntensity**: Intensity of jagged outline; valid range is 1 (most) to 5 (least) and only valid if JaggedOutline is true and NoOutline is false` | 该文件 docstring 自述"★ 局部视图（`CreateDetailViewAt4`，12 参）"，而 `shape_intensity` 逐字透传为 `shape_intensity=shape_intensity`（同文件 `create_detail_view` 的转发实参）⇒ 落点是 `CreateDetailViewAt4` 第 12 个形参 `ShapeIntensity`，官方逐字给的有效范围是 **1(most)–5(least)**，而默认值取 **0**，落在官方范围之外。 | 高 |

---

## 核对过、**未**报的两类（避免下游误以为漏检）

**① 我们刻意走的都是「废弃链的最后一环」——官方原文确认我们的选型正确**：

- `scripts/sw_drawing_create_missing.py` — `InsertBreak / InsertBreak2 **都标 Obsolete** ⇒ 本模块只走 InsertBreak3`
  官方：`IView\InsertBreak.md` = `Obsolete. Superseded by [[IView::InsertBreak2]].`；`IView\InsertBreak2.md` = `Obsolete. Superseded by [[IView::InsertBreak3]].` ⇒ **属实**。
- 同款逐条核实后属实的还有：`InsertHoleTable3`（`InsertHoleTable.md`/`InsertHoleTable2.md` 均 Obsolete，链尾是 3）、`ISheet.InsertRevisionTable2`（`InsertRevisionTable.md` Obsolete）、`AutoBalloon5`（`AutoBalloon`/2/3/4 均 Obsolete）、`CreateAuxiliaryViewAt2`、`CreateSectionViewAt5`、`CreateDetailViewAt4`、`CreateDrawViewFromModelView3`、`InsertCenterMark3`、`IView.AutoInsertCenterMarks2`、`IDrawingDoc.SetupSheet6`、`IModelDocExtension.InsertSurfaceFinishSymbol3`（`IDrawingDoc\InsertSurfaceFinishSymbol.md` = `Obsolete. Superseded by [[IModelDocExtension::InsertSurfaceFinishSymbol3]].`）、`IModelDoc2.InsertDatumTag2`（`IDrawingDoc\InsertDatumTag.md` = `Obsolete. Superseded by [[IModelDoc2::InsertDatumTag2]].`）、`IModelDoc2.ForceRebuild3`、`ISelectionMgr.GetSelectedObject6` / `GetSelectedObjectCount2` / `GetSelectedObjectType3`、`IModelDoc2.InsertNote`。

**② 字面量当枚举传的 29 处，逐个对 `enums\*.md` 查过，除上表 2 条外全部合法**：

`swBreakLineOrientation_e`(1/2) · `swBreakLineStyle_e`(1/2/3/4/5) · `swLeaderStyle_e`(swNO_LEADER=0、swSTRAIGHT=1，docstring 另列 2/3/4/8 及 256–4100 位掩码档) · `swSFSymType_e`(0，并 docstring 列全 10 值) · `swAnnotationType_e`(swDatumTag=2、swSFSymbol=7) · `swBalloonLayoutType_e`(Square=1) · `swBalloonStyle_e`(swBS_Circular=1) · `swBalloonFit_e`(swBF_5Chars=5) · `swBalloonTextContent_e`(swBalloonTextItemNumber=1) · `swBalloonItemNumbersOrder_e`(`0x1 or 1`，与我们注释逐字一致) · `swEditBalloonOption_e`(Resequence=1) · `swDrawingViewTypes_e`(swDrawingSheet=1、swDrawingAuxiliaryView=5) · `swSFLaySym_e`(`lay_symbol=0` = swSFNone) · `swArrowStyle_e`(`arrow_type=0` = swOPEN_ARROWHEAD) · `swDetViewStyle_e`(`style=0` = swDetViewSTANDARD) · `swDetCircleShowType_e`(`show_type=0` = swDetCirclePROFILE) · `swHoleTableTagOrder_e`(`tag_order=1` = swHoleTableTagOrder_XY) · `swHoleTableTagStyle_e`(`tag_type=1` = swHoleTable_AlphaNumericTags)。
另：`sw_drawing_create_missing.py` 的 `shape_intensity: int = 2`（断裂视图）落在 `InsertBreak2.md` 逐字 `valid range is 1 (most) through 5 (least)` 之内 ⇒ 不报。
★ 注意 `lay_symbol`/`arrow_type` 两处，本文件第 803–805 行自述"★ `swSFLaySym_e` / `swArrowStyle_e` 的 '0 是什么'**本轮没查**" —— 本次核对查到 0 分别是 swSFNone 与 swOPEN_ARROWHEAD，均为合法成员。

---

## 结论三行

**都核了几处** —— 91 处：废弃链核对 **62 处成员**（`sw_drawing_create_missing.py` 22 个 + `IAutoBalloonOptions` 15 个属性 + `sw_drawing_expose.py` 25 个，含每个成员整条废弃代际的逐页比对）+ **29 处枚举字面量**（14 个 `enums\*.md` 页 + 2 处官方成员页给的取值范围）。

**报了几条** —— 4 条（1 条 Obsolete 成员命中两个调用点，拆成 #1/#2；2 条字面量越界）。

**哪几条置信度为高** —— #1、#2、#3、#4 **四条全为高**：每条的两段原文我都亲手读到，且官方页面对该值的表述是确定值（枚举成员表穷举无 0；`valid range is 1 (most) to 5 (least)` 明文），不存在两源歧义。