# audit-05-drawing-A —— 域 05-drawing · 核对 A（签名一致性）

**核对范围（本路只做 A）**：把我们在点名文件里的每个 COM 调用逐个实参，与官方 `types/*.md` 的
Signature 形参表并排数 ⇒ 只报「参数个数不符 / 顺序不符 / 明显类型不符」。
**不查**前置与 mark（B）、**不查** Obsolete 与枚举字面量（C）。

## 范围与覆盖（先说清核了什么、没核什么）

| 我们这边的文件 | COM 调用点 | 说明 |
|---|---|---|
| `scripts/sw_drawing.py` | **0** | 该文件不含任何 COM 调用：它是桥接文件，原文 `importlib.util.spec_from_file_location` 指向 `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`，再由 `globals()[_name] = getattr(_MODULE, _name)` 再导出。⇒ 本路**逐字核了它，但没有调用可对**。 |
| `scripts/sw_drawing_expose.py` | 15 个调用点 / 13 个成员 | 其中 `D.add_view` / `D.add_detail_view` / `D.add_note` / `D.add_section_view` / `D.create_standard_views_with_projection` / `D.auto_insert_center_marks` 是**本仓 Python 包装函数调用**，其 COM 实参落在上面那第一个文件里，**不在本路点名范围**，故不计入。 |
| `scripts/sw_drawing_create_missing.py` | 25 个调用点 / 21 个成员 + **15 处 `IAutoBalloonOptions` 属性写入** | 属性写入逐条对着 `C:\swapi\types\IAutoBalloonOptions\*.md` 的 `**Signature**:` 行核过类型（int / string / bool 全部对上）。 |

**共核 55 处**：34 个 COM 成员的 40 个调用点 + 15 处属性写入。
另按铁律 4，把这 8 个有实参的成员的官方文档 arity 与出厂类型库反射 dump（`scripts/sw_api_sldworks.py`）
逐条并查，**未发现两源 arity 不一致**：
`InsertHoleTable3` 文档 9 / 反射 9 · `InsertRevisionTable2` 7 / 7 · `InsertSurfaceFinishSymbol3` 14 / 14 ·
`CreateAuxiliaryViewAt2` 7 / 7 · `InsertBreak3` 6 / 6 · `AutoBalloon5` 1 / 1 · `CreateAutoBalloonOptions` 0 / 0 ·
`InsertDatumTag2` 0 / 0。

## 发现

| # | 我们的原文（文件 + 片段） | 官方的原文（文件 + 片段） | 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | `scripts/sw_drawing_expose.py` · `_selection_marks()`<br>`mark = C.get_com_member(mgr, "GetSelectedObjectType3", i, -1)`<br>紧接着 `out[str(mark)] = out.get(str(mark), 0) + 1`；该函数 docstring 原文：「回读"当前选区里**每个 mark** 各有几个对象"」 | `C:\swapi\types\ISelectionMgr\GetSelectedObjectType3.md` ·<br>**Returns**: `Type of object as defined in [[swSelectType_e]]`<br><br>对照同目录 `GetSelectedObjectMark.md` ·<br>**Signature**: `System.int GetSelectedObjectMark( System.int AtIndex )`<br>**Returns**: `Number used as a mark for the selected item; this number is used by certain API functions that require ordered entity selection` | **返回类型被换了语义域**：我们取的是 `GetSelectedObjectType3`，官方把它定义为 `swSelectType_e` 的**选区对象类型**（顶点/边/面/注解……），而代码把它当 **mark** 存、并在下游按 mark 取值（`marks.get("1", 0) >= 1 and marks.get("2", 0) >= 1`）。官方取 mark 的成员是**另一个**、且形参只有 1 个（`AtIndex`）的 `GetSelectedObjectMark`。⇒ 两处 arity（2 vs 1）与返回类型都对不上。 | 高 |

## 范围外备注（不计入本表，属核对 C，本路未下结论）

以下两行只是**本轮亲手读到的两段原文对不上**，**不属核对 A**，故不进上表、也不计入下方三行统计：

- 我们：`scripts/sw_drawing_expose.py` · `_view_by_name()` —— `if str(C.get_com_member(view, "Name") or "") == str(view_name):`
- 我们：`scripts/sw_drawing_create_missing.py` · `_view_name()` —— `raw = _read(view, "Name")`（`GetName2` 返回 `None` 时的回退）
- 官方：`C:\swapi\types\IView\Name.md` 原文 —— `Obsolete. Superseded by [[IView::GetName2]] and [[IView::SetName2]].`

---

核了 55 处 · 报 1 条 · 置信度为高的是第 1 条。
