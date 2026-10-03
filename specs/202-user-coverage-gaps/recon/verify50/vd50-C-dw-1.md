# vd50-C-dw-1 —— 工程图「视图」片（三视图/投影/剖视/局部放大/断裂视图/辅助视图）契约核对

★ 范围：`docs/user-feature-coverage.md` §九 里工程图域的**视图类 6 行**（标准三视图/模型视图 · 投影视图 · 剖面视图 · 局部视图 · 断裂视图 · 辅助视图），核的是「仓内怎么说」与「官方怎么说」是否对得上。
★ 纪律：只读 + 只写本文件；每条给两段可搜索原文（仓内段 / 官方段）；给不出两段的不写；查不到就说查不到；宁少勿滥；**不写行号**，只写原文片段。
★ 与同批 `vd50-A-drawing.md` / `vd50-B-drawing.md` 不重叠：那份核的是 capability 的 `level` 与证据一致性、那份核的是 `_selection_marks` / `SetTemplateName` / `IView.Name` 等调用点缺陷；本片核的是**视图族六个官方成员在本仓的落地形态**。

---

## 总表

| # | 视图 | 待核的说法 | 仓内原文 | 官方原文 | 判定 |
|---|---|---|---|---|---|
| 1 | 断裂视图 | 「断裂视图」已覆盖，V4 建成 | 在 | 在（且相反） | **成立** |
| 2 | 三视图 | 本机 COM 代理没有 `CreateFirstAngleViews2` | 在 | 在 | **存疑** |
| 3 | 剖面视图 | 传空 `SectionLabel` 即可 | 在 | 在 | **成立** |
| 4 | 辅助视图 | `NotAligned=True` 是「不对齐」 | 在 | 在（自相矛盾） | **存疑** |
| 5 | 局部视图 | 两个枚举字典与官方取值域可能不一致 | 在 | 在 | **不成立**（逐项对得上） |

---

## 1 · 断裂视图：仓内认的是 `InsertBreak3`（断裂线），官方的断裂视图入口一次都没被调用 ★★★

**判定：成立**

**一句话依据**：官方把「插断裂线」（`IView.InsertBreak3`）与「生成断裂视图」（`IDrawingDoc.BreakView`）写成两个成员、另有一条 `CreateBreakOutSection`，而仓内只调了 `InsertBreak3`，另两个成员在 `scripts/` `mcp-server/` `tools/` `subskills/` `tests/` 里**各 0 个调用点** —— 那格 ✅ 只证明了断裂线插进去了。

**仓内原文（三段，同源）**

`docs/user-feature-coverage.md` §九 工程图域：

```
| 工程图 | 断裂视图 | ✅ | ✅ | · | · | · |
```

`scripts/sw_drawing_create_missing.py` 的缺口映射表（表头逐字：「★ 本模块覆盖到的缺口项 ⇒ 官方成员（★ 与 `docs/user-feature-coverage.md` §八 对齐用）」）：

```
    "断裂视图": "IView.InsertBreak3（★ InsertBreak / InsertBreak2 都标 Obsolete）",
```

`docs/known-facts.md` 事实 496 的真机读数：

```
        · ✅ **建成**：V1 投影视图 · V3 局部视图 · **V4 断裂视图**（★ `breakline_delta=1` ⇒
```

★ 判据名字本身就写着 `breakline_delta`，即**断裂线**的增量。

**官方原文（三段）**

`C:\swapi\types\IView\InsertBreak3.md` 的 `## Remarks`：

```
A break in a drawing view consists of a pair of break lines. This method inserts the break lines at the locations indicated by Position1 and Position2.
```

`C:\swapi\types\IDrawingDoc\BreakView.md` 的描述行与 `## Remarks`：

```
Breaks the drawing view along the existing break lines.
```

```
Use [[IDrawingDoc::InsertBreakHorizontal]] or [[IDrawingDoc::InsertBreakVertical]] to insert break lines to a drawing view. Customize the break by dragging and repositioning the break lines. Then, call this method to create the break view.
```

`C:\swapi\types\IDrawingDoc\CreateBreakOutSection.md` 的描述行与签名：

```
Creates a broken-out section in a drawing document.
```

```
**Signature**: `System.bool CreateBreakOutSection( System.double Depth )`
```

★ 官方逐字把「插线」与「成视图」分成两步（`Then, call this method to create the break view.`），而 `BreakView` 与 `CreateBreakOutSection` 在仓内除 `scripts/sw_api_sldworks.py` 的官方 arity 索引（`'BreakView': 0,` / `'CreateBreakOutSection': 1,`）与 `tools/audit_gap_implementations.py` 的缺口名单（`"工程图/断裂视图": ["InsertBreak", "BreakView"],`）外，**没有任何调用点**。

⚠ 附一句限度（不改变判定）：中文词「断裂视图」在仓内**没有**与官方英文术语的对照说明，本条的判定只用官方英文原话立论，不靠中英对应（见 §查不到 1）。

---

## 2 · 三视图：`DRAWING_PROJECTION_API_UNAVAILABLE` 与仓内自己的官方反射索引互相矛盾

**判定：存疑**

**一句话依据**：`blocked` 的唯一判据是 `getattr(drawing_model, "CreateFirstAngleViews2", None)` 取到 `None`，而本仓那份「照抄自官方 interop 程序集的纯元数据反射」的索引里明确登记着这两个成员（arity 1）—— 两段仓内原文互相打架，我本轮不上真机，判不了谁对。

**仓内原文（三段）**

`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::create_standard_views_with_projection`：

```
    method_name = "CreateFirstAngleViews2" if projection == "first_angle" else "Create3rdAngleViews2"
    method = getattr(drawing_model, method_name, None)
```

```
            "error_code": "DRAWING_PROJECTION_API_UNAVAILABLE",
```

`output/drawing-standard-views-probe.json`（仓内唯一的运行记录）：

```
    "status": "blocked",
    "projection": "first_angle",
    "method": "CreateFirstAngleViews2",
    "error_code": "DRAWING_PROJECTION_API_UNAVAILABLE",
```

`scripts/sw_drawing_expose.py::create_three_standard_views` 的 docstring（逐字把结论写死）：

```
    ★★ **已知限制（真机实测）**：底层先试 `CreateFirstAngleViews2`，本机 COM 代理**没有该成员**
```

★ **与上面矛盾的那一段** —— `scripts/sw_api_sldworks.py` 的模块头逐字：

```
**官方 API 的完整抄录** —— 523 个接口族、**8210 个成员**，
逐个照抄自对官方 interop 程序集的**纯元数据反射**。
```

同一文件的 `'IDrawingDoc': {` 字典里：

```
        'Create1stAngleViews': 1,
        'Create1stAngleViews2': 1,
        'Create3rdAngleViews': 1,
        'Create3rdAngleViews2': 1,
```

**官方原文**

`C:\swapi\types\IDrawingDoc\Create1stAngleViews2.md`：

```
Creates standard three orthographic views (first angle projection) for the specified model.
```

```
**Signature**: `System.bool Create1stAngleViews2( System.string ModelName )`
```

★ 一句话依据的落点：官方签名 1 参、仓内调用 `method(part_path)` 也 1 参（**arity 这条对得上**）；争的只是「本机 COM 上这个成员在不在」，而 `getattr` 返回 `None` 只说明 pywin32 迟到绑定没暴露它，**不等于**官方成员不存在 —— 仓内自己的反射索引说的正好相反。

---

## 3 · 剖面视图：官方把标签写进形参、并另给 `SetLabel2`；仓内传空串且从不设标签

**判定：成立**

**一句话依据**：官方 `SectionLabel` 形参逐字是「Letter for the label for the section view」、官方例子传 `"D"` 并在返回后调 `SetLabel2 "ABCD"`，而仓内 `add_section_view` 固定传 `""`、全仓无 `SetLabel2` 调用 ⇒ 建出来的剖视图没有标签字母。

**仓内原文**

`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py::add_section_view`（整个函数体就这一行）：

```
def add_section_view(drawing_model, x, y):
    """在当前选择的剖切线位置创建剖视图"""
    return drawing_model.CreateSectionViewAt5(x, y, 0, "", 0, None, 0)
```

★ 第 4 个实参（`SectionLabel` 位）是空串；`scripts/sw_drawing_expose.py::create_section_view` 原样透传这个函数（`res = D.add_section_view(drawing_model, _mm(x_mm), _mm(y_mm))`）。
★ `SetLabel2` / `GetSection` 在 `scripts/` `mcp-server/` `tools/` `subskills/` `tests/` 里**只出现在 `scripts/sw_api_sldworks.py` 的官方索引**（`'SetLabel2': 1,` / `'GetSection': 0,`），没有任何调用点。

**官方原文**

`C:\swapi\types\IDrawingDoc\CreateSectionViewAt5.md` 的 `## Parameters` 与 `## Remarks`：

```
- **SectionLabel**: Letter for the label for the section view
```

```
Use [[IView::GetSection]] to get the [[IDrSection]] object, and use [[IDrSection::SetLabel2]] to set the name for the label, which provides a warning if the name is a duplicate and the standard does not accept duplicate names.
```

`C:\swapi\examples\Create_Section_View_and_Get_Some_Data_Example_VB.md`：

```
    Set swView = swDrawing.CreateSectionViewAt5(0.1604082711061, 0.2048687170364, 0, "D", 32, (excludedComponents), 0.00835)
```

```
    swSectionView.SetLabel2 "ABCD"
```

⚠ 一句限度（不改变判定）：官方**没有**写「传空串会怎样」（见 §查不到 3）⇒ 「没有标签」这个事实成立，后果轻重查不到。

---

## 4 · 辅助视图：`NotAligned` 默认值与官方描述的字面意思相反（官方自相矛盾，仓内已披露）

**判定：存疑**

**一句话依据**：仓内默认 `not_aligned=True` 并逐字透传，官方这一页逐字写「True **aligns** the view from its owner」＝ True 是**对齐**；而同族 `swCreateSectionView_NotAligned` 的官方描述却是「置位＝不对齐」⇒ 两处官方口径相反，仓内已如实披露且未真机定论。

**仓内原文**

`scripts/sw_drawing_create_missing.py::create_auxiliary_view` 的签名与 docstring：

```
                          not_aligned: bool = True,
```

```
    ⚠★ **`NotAligned` 的官方说明与形参名自相矛盾，本模块**原样透传、照抄，不替官方解释**：
      官方 Parameters 逐字写的是「**NotAligned**: True **aligns** the view from its owner,
      false does not」—— ★ 名字说"不对齐"、说明说"对齐" ⇒ ★ 本模块**默认传 `True`**（跟形参名），
```

调用处逐字透传：

```
        bool(not_aligned), str(label), bool(show_arrow), bool(flip),
```

**官方原文**

`C:\swapi\types\IDrawingDoc\CreateAuxiliaryViewAt2.md` 的 `## Parameters`：

```
- **NotAligned**: True aligns the view from its owner, false does not
```

同域旁证 —— `C:\swapi\enums\swCreateSectionViewAtOptions_e.md`：

```
| swCreateSectionView_NotAligned | 1 or 0x1; If set, then the section does not snap into alignment with the parent view; if not set, then the section snaps into alignment with the parent view |
```

★ 这一条**不是「仓内写错」**：仓内把矛盾写在 docstring 里、默认值按形参名取、并在返回值里原样引出官方那句；它只是**至今没有被真机定论**（该模块自己的 `preconditions_held` 机制在选区为空时也拿不到结论）。

---

## 5 · 局部视图：`Style` / `Showtype` 两个枚举字典是否与官方取值域一致 —— **一致**

**判定：不成立**（待核的说法「可能不一致」不成立）

**一句话依据**：两个字典逐项与官方枚举表对上，5 项 0–4、3 项 0–2，无增删改写。

**仓内原文**（`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`，两处来源块自述「官方 5 项全量照录，逐行对应，未增删、未改写」/「官方 3 项全量照录」）：

```
DET_VIEW_STYLES = {
    "standard": 0,      # swDetViewSTANDARD  = 0
    "broken": 1,        # swDetViewBROKEN    = 1
    "leader": 2,        # swDetViewLEADER    = 2
    "noleader": 3,      # swDetViewNOLEADER  = 3
    "connected": 4,     # swDetViewCONNECTED = 4
}
```

```
DET_CIRCLE_SHOW_TYPES = {
    "profile": 0,       # swDetCirclePROFILE  = 0
    "circle": 1,        # swDetCircleCIRCLE   = 1
    "dont_show": 2,     # swDetCircleDONTSHOW = 2
}
```

**官方原文**

`C:\swapi\enums\swDetViewStyle_e.md`（`enum_member_count: 5`）：

```
| swDetViewBROKEN | 1 = Use broken detail view style |
| swDetViewCONNECTED | 4 = Use connected detail view style |
| swDetViewLEADER | 2 = Use leader detail view style |
| swDetViewNOLEADER | 3 = Use no leader detail view style |
| swDetViewSTANDARD | 0 = Use standard detail view style |
```

`C:\swapi\enums\swDetCircleShowType_e.md`（`enum_member_count: 3`）：

```
| swDetCircleCIRCLE | 1 = Use sketch circle to create detail view |
| swDetCircleDONTSHOW | 2 = Do not show a sketch profile |
| swDetCirclePROFILE | 0 = Use sketch profile to create detail view |
```

---

## ★ 查不到（如实记，不顶替）

1. **中文「断裂视图」对应哪个官方术语** —— 仓内只有 `DRAWING_CREATE_MISSING_STATUS` 与 `docs/user-feature-coverage.md` 两处提到这个词，**没有一处**给出中英对照 ⇒ **查不到**。第 1 条因此只用官方英文原话（`break lines` / `break view` / `broken-out section` 三者逐字不同）立论，不用中文词去推断官方含义。
2. **`CreateFirstAngleViews2` 在本机 COM 上到底存不存在** —— 本轮是只读核对，不上真机；仓内唯一运行记录 `output/drawing-standard-views-probe.json` 只记了 `getattr` 的结果，**没有**记 COM 类型信息或失败异常 ⇒ **查不到**。第 2 条只能判「存疑」。
3. **`CreateSectionViewAt5` 传空 `SectionLabel` 的后果** —— 官方 `CreateSectionViewAt5.md` 的 Parameters / Remarks 与三个官方例子都**没有**写空串会怎样 ⇒ **查不到**。第 3 条只判「传的是空串、且没有设标签这条路」。
4. **仓内一处内部不自洽（缺官方那一半，按铁律 2 不作条目）** —— `scripts/sw_drawing_expose.py::create_section_view` 把判据字符串写成「视图数增量（★ 前置成立才算）」，而同一函数里实际的 `ok` 是 `{"ok": res is not None, "view": res}`（判「返回非 None」，**没有**数视图增量）。两段都在仓内，但**找不到官方那一段**可以对照 ⇒ 不写成条目，只在此记录。
5. **`IView.InsertBreak3` 的 6 个实参与官方签名逐位是否对齐** —— 仓内调用逐字是 `InsertBreak3` 后接 `int(orientation), mm(position1), mm(position2), int(style), int(shape_intensity), bool(break_sketch_blocks)`（6 参），官方签名逐字为 `System.object InsertBreak3( System.int Orientation, System.double Position1, System.double Position2, System.int Style, System.int ShapeIntensity, System.bool BreakSketchBlocks )`（6 参）⇒ **这一项对得上**，故不作条目，只在此备查。

---

## 三行

- **核了几处**：**5 处**（断裂视图 · 三视图 · 剖面视图 · 辅助视图 · 局部视图）
- **对不上几处**：**4 处** —— 成立 **2**（断裂视图挂错成员、剖面视图不设标签）· 存疑 **2**（三视图 blocked 与自家反射索引矛盾、辅助视图 `NotAligned` 官方自相矛盾）· 核对一致 **1**（局部视图两个枚举字典）