"""当前活动工程图的**轻量只读读数**（砌墙 W2 / Spec Kit `132`）。

## 为什么需要它（**用法不对口**，不是"少一个读数"）
`solidworks_inspect_drawing`（上游 45 个之一）已经能读工程图结构，但它的形态是：
```python
drawing_model = open_document(sw, params.drawing_path, read_only=True, ...)
structure = drawing_inspect_structure(drawing_model, paper_size_hint=...)
previews  = drawing_save_review_previews(drawing_model, out/"previews", views=(...))
```
⇒ ★ 它要 **`drawing_path`**、**自己开件**、**出三视图预览**、**往 output_dir 落一份 JSON**。
而 AI 的常见需求是：「**这图几张纸？当前图幅多大？有几个视图？**」
—— 不需要出预览、不需要落文件、也不需要知道路径。
⇒ ★ 所以本模块给的是**对"当前已打开的那张图纸"的轻量读数**。

## ★★★ 三个关键事实是**真机探针定的**（`tools/probe_drawing_object_routes.py`，轮 224）
```
                       实测读数
  model.GetType()          **3**（swDocDRAWING；零件是 1）
  model.GetCurrentSheet()  ★ **能直接调** —— pywin32 迟到绑定下 model 本身就是 IDrawingDoc
                             （官方示例 `Get_Drawing_View_Names_and_Types` 就是 (DrawingDoc)swModel 转换）
  ISheet.GetProperties2()  ★ **8 个 double**（官方 `GetProperties` 文档写 7 个，后继多一个）
                             = [paperSize, templateIn, scale1, scale2, firstAngle, width, height, sameCustomPrp]
                             实测 [6.0, 12.0, 1.0, 1.0, 1.0, **0.297**, **0.21**, 1.0]
                             ⇒ paperSize=6 = `swDwgPaperA4size`（swapi 与反射**两源一致**）
                             ⇒ **宽高单位是米**（0.297 m = 297 mm）
  GetFirstView()           ★ **空图纸上返回的是"图纸本身"（`Type == 1`）**，不是 None
                             ⇒ ★ 列视图时**必须排除它**，否则会列出名叫「图纸1」的假视图
```

## ⚠ 单位（并入六条规则 规则 2）
官方给的宽高是**米** ⇒ 本模块对外**一律回毫米**（`_mm` 后缀），换算只在这里做一次。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植）
# 文件:   scripts/sw_drawing_query.py
# 定位:   砌墙 W2（Spec Kit `132`）的能力层：当前活动工程图的轻量只读读数。
# 官方依据: `IDrawingDoc.GetCurrentSheet` / `GetSheetCount` / `GetSheetNames` / `GetFirstView` ·
#          `ISheet.GetName` / `GetProperties2` / `GetSheetFormatName` · `IView.GetName2` / `Type` / `GetNextView`；
#          官方示例 `C:\\swapi\\examples\\Get_Drawing_View_Names_and_Types_Example_CSharp.md`
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本模块为静态比对后新写，**真机验证状态见 `output/drawing-query-evidence.json`**（铁律 2）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from typing import Any

from sw_connect import get_com_member

__all__ = [
    "SWDOC_DRAWING",
    "PAPER_SIZE_NAMES",
    "require_drawing",
    "sheet_count",
    "sheet_names",
    "current_sheet_name",
    "sheets_summary",
    "current_sheet_info",
    "list_views",

    "view_annotations_report"]

#: `swDocumentTypes_e`：零件 1 / 装配 2 / **工程图 3**
SWDOC_DRAWING = 3

#: `swDwgPaperSizes_e`（★ swapi 与出厂反射**两源一致**，13 个成员）
PAPER_SIZE_NAMES = {
    0: "A", 1: "A_vertical", 2: "B", 3: "C", 4: "D", 5: "E",
    6: "A4", 7: "A4_vertical", 8: "A3", 9: "A2", 10: "A1", 11: "A0",
    12: "user_defined",
}


def require_drawing(model):
    """确认 `model` 是**工程图**文档，否则报错（★ 选不中/类型不对要报错，不静默）。

    ★ 为什么要它：`model` 在零件上**也是** `IModelDoc2`，直接调 `GetCurrentSheet`
      会得到无意义结果或让人以为"这图没图纸"。⇒ 先用 `GetType()` 判类型（实测零件=1 / 工程图=3）。
    """
    if model is None:
        raise ValueError("model 为 None")
    try:
        doc_type = int(get_com_member(model, "GetType"))
    except Exception as exc:                                    # noqa: BLE001
        raise RuntimeError("读不到文档类型（GetType 失败）：%s" % str(exc)[:80]) from exc
    if doc_type != SWDOC_DRAWING:
        raise RuntimeError(
            "当前文档不是工程图（GetType()=%d；swDocPART=1 / swDocASSEMBLY=2 / swDocDRAWING=3）"
            % doc_type
        )
    return model


def sheet_count(model) -> int:
    """图纸张数（`IDrawingDoc.GetSheetCount`）。"""
    require_drawing(model)
    return int(get_com_member(model, "GetSheetCount"))


def sheet_names(model) -> list[str]:
    """全部图纸名（`IDrawingDoc.GetSheetNames`）。"""
    require_drawing(model)
    raw = get_com_member(model, "GetSheetNames")
    if raw is None:
        return []
    try:
        return [str(x) for x in raw]
    except TypeError:
        return [str(raw)]


def current_sheet_name(model) -> str:
    """当前图纸名（`GetCurrentSheet` → `ISheet.GetName`）。"""
    require_drawing(model)
    sheet = get_com_member(model, "GetCurrentSheet")
    if sheet is None:
        raise RuntimeError("GetCurrentSheet 回了 None —— 这张工程图没有活动图纸")
    return str(get_com_member(sheet, "GetName"))


def sheets_summary(model) -> dict[str, Any]:
    """★ **图纸总览**（一个工具回答"这图几张纸、都叫什么、现在在哪张"）。

    ★ 为什么合并而不是拆成两个工具：拆开会让 AI 必须调两次才拿到同一件事的全貌，
      而这两样**总是被一起问**（"几张纸？叫什么？"）。
    """
    require_drawing(model)
    return {
        "count": sheet_count(model),
        "names": sheet_names(model),
        "current": current_sheet_name(model),
    }


def current_sheet_info(model) -> dict[str, Any]:
    """当前图纸的**读数**：图幅 + 尺寸（**毫米**）+ 比例 + 图纸格式名。

    ★ 官方 `ISheet.GetProperties2()` 返回 **8 个 double**，次序照官方 Remarks：
      `[paperSize, templateIn, scale1, scale2, firstAngle, width, height, sameCustomPrp]`
    ★ **宽高单位是米** ⇒ 本函数换算成毫米（规则 2：换算只在边界做一次）。
    """
    require_drawing(model)
    sheet = get_com_member(model, "GetCurrentSheet")
    if sheet is None:
        raise RuntimeError("GetCurrentSheet 回了 None —— 这张工程图没有活动图纸")
    props = get_com_member(sheet, "GetProperties2")
    vals = [float(x) for x in props] if props is not None else []
    if len(vals) < 7:
        raise RuntimeError(
            "ISheet.GetProperties2 返回了 %d 个元素（预期 ≥7：paperSize/…/width/height）"
            "—— 官方返回结构可能变了，不要猜" % len(vals)
        )
    paper = int(round(vals[0]))
    return {
        "sheet_name": str(get_com_member(sheet, "GetName")),
        "paper_size_code": paper,
        "paper_size": PAPER_SIZE_NAMES.get(paper, "unknown(%d)" % paper),
        "width_mm": round(vals[5] * 1000.0, 3),
        "height_mm": round(vals[6] * 1000.0, 3),
        "scale_num": vals[2],
        "scale_den": vals[3],
        "first_angle": bool(vals[4]),
        "sheet_format_name": str(get_com_member(sheet, "GetSheetFormatName") or ""),
    }


#: `swDrawingViewTypes_e` 里与"这不是一个视图、而是图纸本身"对应的取值。
#: ★ 真机实测：空图纸上 `GetFirstView()` 返回的对象 `Type == 1`，且 `GetName2()` 就是图纸名。
SHEET_PSEUDO_VIEW_TYPE = 1


def list_views(model) -> list[dict[str, Any]]:
    """**当前图纸上**的视图清单：`[{"name": ..., "type": ...}, ...]`。

    ★ 遍历用官方示例的写法：`GetFirstView()` → `GetNextView()`（官方 Postconditions 明写
      "Traverses the views on the current sheet"）。
    ★★ **必须排除「图纸本身」那一个** —— 真机实测空图纸上 `GetFirstView()` 回的就是它
      （`Type == 1`、名字等于图纸名）⇒ 不排除就会列出一个**假视图**。
    """
    require_drawing(model)
    views: list[dict[str, Any]] = []
    view = get_com_member(model, "GetFirstView")
    seen = 0
    while view is not None and seen < 500:                      #: 防御上限，不无限循环
        seen += 1
        try:
            vtype = int(get_com_member(view, "Type"))
        except Exception:                                       # noqa: BLE001
            vtype = -1
        try:
            name = str(get_com_member(view, "GetName2"))
        except Exception:                                       # noqa: BLE001
            #: ★★★ spec 256：**不再回落调废弃的 `IView::Name`** —— 官方 `IView/Name.md` 首行
            #:   「Obsolete. Superseded by [[IView::GetName2]] and [[IView::SetName2]]」；
            #:   ★ 真机（SW 34.4.1）在 4 个视图上证明 `Name` == `GetName2`（★ 3 个真实模型视图）
            #:   ⇒ ★ 这里失败就是**取不到名字**，★ 报空串，**不换一个废弃成员再试**。
            name = ""
        if vtype != SHEET_PSEUDO_VIEW_TYPE:                     #: ★ 跳过"图纸本身"
            views.append({"name": name, "type": vtype})
        nxt = get_com_member(view, "GetNextView")
        if nxt is None:
            break
        view = nxt
    return views


# ── 工程图读侧第一批（★ 注释 / 尺寸 / 弧数）─────────────────────────────────────
def view_annotations_report(model) -> dict:
    """★ 读**当前图纸每个视图上的注释 / 显示尺寸 / 弧数**（★ 工程图读侧第一批）✓

    ★★★★★★ **为什么做这个**（★ 阶段 4/5）：★ 本仓有 `add_note`（★ **能写注释**）、
      ★ 而**读不回来** ⇒ ★★ **⇒ 又是「能写不能读」**（★ 本会话第 6 次同型）✓

    ★★★★★ **官方例子的**调用序**（★ 签名与 `## Remarks` 都给不了）** ——
      逐字来自 `Get_Names_of_Annotations_Example_VB.md`：
        `GetFirstView` ⇒ ★★ **`' First drawing view is the sheet, so get first drawing view`**
        ⇒ `GetNextView` ⇒ `GetName2` ⇒ ★★★ `annArray = swDrView.**GetAnnotations**` ⇒
        `If Not IsEmpty(annArray)` ⇒ `For Each obj In annArray` ⇒ `currAnn.GetName` ⇒ `GetNextView` ✓
      ★★ **⇒ 那印证了本模块 `list_views` 早就写下的那条**：★ **第一个视图是**图纸本身**（sheet）** ⇒
        ★ **必须跳过它**（★ 否则会列出一个**假视图**）✓

    ★★★★★ **⚠ `GetAnnotations` 直接回数组** —— ★ 而 `GetAnnotationCount()` 的
      `## Remarks` 逐字说「Call this method before `GetAnnotations` to determine the size
      of the array for that method」⇒ ★★ **⇒ 那是给**别的语言**用的（VB 有 `IsEmpty` 判定、
        C++ 要自己分配数组）⇒ ★ **pywin32 上直接拿数组即可** ✓
      ★★★ **而本函数**仍然读 `GetAnnotationCount()`** —— ★ 因为它是**独立的第二个判据**
        （★ 两个数应当一致 ⇒ ★ **不一致就说明有东西没读到**）✓

    ★★★★★ **⚠ 不读**：★ `GetLineCount()` ⇒ ★ **官方标 `Obsolete`** ⇒ **本模块不碰** ✓

    ★★★★★★★ **✅ 真机读数（★ 2026-10-04 轮 136 · ★ 建视图 → 写注释 → 读回）**：
      ★ 证据：★ `output/drawing-annotations-capability-recheck.json` ✓
      · ★ `create_projected_view`（★ 零件**先存盘**）⇒ ★ **`ok: True`** ——
        ★ `verified_by` 逐字：★「返回非 None（★ 底层为 `CreateDrawViewFromModelView3`、
        ★ **视图名自动本地化**）」✓
      · ★★ **`create_three_standard_views`（★ 同一张图）⇒ `ok: False`** ·
        ★ `verified_by` 逐字：★「★ 返回里有建成视图（★ **本机实测为 blocked**：
        ★ `CreateFirstAngleViews2` 不可用）」⇒ ★ **⇒ 那是**本机的一条已知限制****、
        ★★ **⇒ 要插视图请走 `create_projected_view`** ✓
      · ★★★ **写**：★ `add_drawing_note(x_mm=50, y_mm=50, text="…")` ⇒ **`ok: True`** ✓
      · ★★★★ **读回**：★ **`view_count = **1**`** ⇒
        `{"name": "**工程图视图1**", "type": **7**, "annotation_count_by_api": **1**,
          "annotations": ["**细节项目254**"], "annotation_len": **1**,
          "display_dimension_count": **0**, "arc_count": **0**}` ✓
      · ★★★★★ **两条独立读数一致**（★ `annotation_count_by_api = 1` 与 `annotation_len = 1`）⇒
        ★ **`mismatches = 0`** ⇒ **判据成立** ✓
        而 `细节项目254` **正是我写进去的那条注释**（★ SolidWorks **自动编号**）⇒
        ★★ **⇒ 「能写」与「能读」在真机上**对上了**** ✓
      ★★★★★★ **⚠ 而前置有一条**（★ 值记）：★ **零件必须先存盘** ——
        ★ 实测不存盘 ⇒ `GetPathName()` 是**空串** ⇒ `create_projected_view` **插不了视图** ⇒
        ★★ **⇒ 于是 `view_count = 0`、★ 而那是**应然的**、★ 不是读侧坏了** ✓
        ★★★ **可复用判据**：★★★ **"零件/装配体要被投影"的能力，前置是**那个文件有路径**** ✓
    """
    require_drawing(model)
    views = []
    view = get_com_member(model, "GetFirstView")
    seen = 0
    while view is not None and seen < 500:
        seen += 1
        try:
            vtype = int(get_com_member(view, "Type"))
        except Exception:                                                 # noqa: BLE001
            vtype = -1
        try:
            name = str(get_com_member(view, "GetName2"))
        except Exception:                                       # noqa: BLE001
            #: ★★★ spec 256：**不再回落调废弃的 `IView::Name`** —— 官方 `IView/Name.md` 首行
            #:   「Obsolete. Superseded by [[IView::GetName2]] and [[IView::SetName2]]」；
            #:   ★ 真机（SW 34.4.1）在 4 个视图上证明 `Name` == `GetName2`（★ 3 个真实模型视图）
            #:   ⇒ ★ 这里失败就是**取不到名字**，★ 报空串，**不换一个废弃成员再试**。
            name = ""
        if vtype == SHEET_PSEUDO_VIEW_TYPE:                               #: ★ 跳过"图纸本身"
            nxt = get_com_member(view, "GetNextView")
            if nxt is None:
                break
            view = nxt
            continue
        item: dict[str, Any] = {"name": name, "type": vtype}
        #: ★ `GetAnnotationCount()` —— 独立的第一个判据（★ 官方 Remarks 说它给数组定大小）
        try:
            item["annotation_count_by_api"] = int(get_com_member(view, "GetAnnotationCount"))
        except Exception as exc:                                          # noqa: BLE001
            item["annotation_count_by_api"] = "err: %s" % str(exc)[:50]
        #: ★★ `GetAnnotations()` —— 官方例子用的就是它（★ 直接回数组）
        try:
            arr = get_com_member(view, "GetAnnotations")
            names = []
            for a in (arr or []):
                try:
                    names.append(str(get_com_member(a, "GetName")))
                except Exception:                                         # noqa: BLE001
                    names.append("(无名)")
            item["annotations"] = names
            item["annotation_len"] = len(names)
        except Exception as exc:                                          # noqa: BLE001
            item["annotations"] = "err: %s" % str(exc)[:60]
        #: ★ `GetDisplayDimensions()` —— 官方 Remarks 说**用它一次取全部**
        try:
            dims = get_com_member(view, "GetDisplayDimensions")
            item["display_dimension_count"] = len(list(dims or []))
        except Exception as exc:                                          # noqa: BLE001
            item["display_dimension_count"] = "err: %s" % str(exc)[:50]
        #: ★ `GetArcCount()` —— 零参 · ★ 非废弃
        try:
            item["arc_count"] = int(get_com_member(view, "GetArcCount"))
        except Exception as exc:                                          # noqa: BLE001
            item["arc_count"] = "err: %s" % str(exc)[:50]
        #: ★★★★★★★ 2026-10-04（轮 139）**第二批零参读侧（★ 工程图）** ——
        #:   ★ **四个全零参、★ 全非废弃、★ 全非指针**、★ 而它们的 `## Remarks` 都是**同一句**：
        #:     ★「Call this method before `IView::IGet…` to determine the size of the array
        #:       for that method」⇒ ★ **⇒ 即"先数个数、★ 再去取数组"的**前半**** ✓
        #:   · ★ `GetBendLineCount()` ⇒「Number of **bendlines** in a flat-pattern view」✓
        #:   · ★ `GetCThreadCount()` ⇒「Number of **cosmetic threads**」（★ 装饰螺纹）✓
        #:   · ★ `GetDatumOriginCount()` ⇒「Number of **datum origins**」（★ 基准原点）✓
        #:   · ★ `GetCenterLineCount()` ⇒「Number of **centerlines**」✓
        #:   ★★ **⚠ 而另两条**看起来也是候选、★ 本轮**故意不纳入****（★ 逐条读 Remarks 才看见）：
        #:     ★ **① `GetBomTable()`** —— `## Remarks` 逐字：★「This method **only returns a BOM
        #:       table if there is a Microsoft Excel-based BOM** for the drawing view」⇒
        #:       ★★ **⇒ 前置不满足时**静默回 `None`**** ⇒ **⇒ 会误导** ⇒ 不纳入 ✓
        #:     ★ **② `GetCenterMarkCount2(out int Size)`** —— `## Remarks` 逐字：★「**Center marks
        #:       are now annotations. Previously, center marks were features.** ★ This method is
        #:       **only valid for center marks that are features**」⇒
        #:       ★★ **⇒ 它对**新画的**中心标记**不适用****、★ 且**带 `out`**（★ 本仓既有结论：
        #:         带 `out` 的在 pywin32 上到不了）⇒ **不纳入** ✓
        for _key, _mem in (("bend_line_count", "GetBendLineCount"),
                           ("cosmetic_thread_count", "GetCThreadCount"),
                           ("datum_origin_count", "GetDatumOriginCount"),
                           ("center_line_count", "GetCenterLineCount")):
            try:
                item[_key] = int(get_com_member(view, _mem))
            except Exception as exc:                                      # noqa: BLE001
                item[_key] = "err: %s" % str(exc)[:50]
        views.append(item)
        nxt = get_com_member(view, "GetNextView")
        if nxt is None:
            break
        view = nxt
    return {"view_count": len(views), "views": views,
            "★_不读": [
                "GetLineCount（★ 官方标 Obsolete）",
                "GetBomTable（★ 官方 Remarks：★ 只有 Excel 型 BOM 才有 ⇒ 前置不满足时静默回 None）",
                "GetCenterMarkCount2（★ 官方 Remarks：★ 只对**作为特征**的中心标记有效、"
                "★ 且带 `out` ⇒ 在 pywin32 上到不了）"]}


# ── 24h 计划 段 6 续（Spec Kit `164`）：**图纸比例的读与写** ────────────────────────
# ★★★★★ 2026-10-01（轮 301）真机确证：**`ISheet.SetScale` 是**通的**** ——
#   · ★ 读：`ISheet.GetProperties` 回 `[6.0, 12.0, **1.0, 1.0**, 1.0, 0.297, 0.21]`
#     （★ 官方 Remarks 明写「You can get the two scale values from the sheet by using
#      `ISheet::GetProperties`」）—— ★ 位置 3 / 4 就是 **Numerator / Denominator**；
#   · ★ 写：`SetScale(1.0, 2.0, False, False)` ⇒ **回 `True`**，★ **而读回变成 `[6.0, 12.0, 1.0, 2.0, …]`**
#     ⇒ ★★★ **即图纸比例真的从 1:1 改成了 1:2** ✓
#   ★★ **它与"视图比例"形成对照**：★ `IView.ScaleRatio` **读得到、写不进**（★ 事实 227/294）·
#      ★ 而 `ISheet.SetScale` **写得进** ⇒ ★★★ **所以"想改比例"的正解是改**图纸**的比例**
#      （★ 而视图默认 `UseSheetScale=True` ⇒ ★ 它会跟着变）✓
#
# ★ 判据：★ **写之后必须读回**（★ 规则 6 的精神）—— ★ 而读回的判据是
#   **`GetProperties` 的位置 3 / 4 真的变成了 (numerator, denominator)**。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_drawing_query.py —— 本段
# 定位:   段 6 续：图纸比例的读取与设置（★ 声明式：按图纸名，★ 不传坐标）。
# 官方签名依据: `C:\swapi\types\ISheet\SetScale.md`
#   （`bool SetScale(double Numerator, double Denominator, bool ScaleAnnoPosition,
#     bool ScaleAnnoTextHeight)` · "Sets the scale for this drawing sheet." ·
#     "You can get the two scale values from the sheet by using ISheet::GetProperties"）·
#   `C:\swapi\types\ISheet\GetProperties.md`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────


def _sheet_by_name(model, sheet_name: str = ""):
    """★ **按名字取图纸对象**（★ 空名字 ⇒ 当前图纸）。★ 回 `(sheet, err)`。"""
    from sw_connect import get_com_member as _get
    if model is None:
        return None, "model 为 None"
    try:
        if not sheet_name:
            sh = _get(model, "GetCurrentSheet")
            return (sh, None) if sh is not None else (None, "当前图纸取不到（★ 文档是工程图吗）")
        try:
            sh = _get(model, "GetSheetByName", str(sheet_name))
        except Exception:                                      # noqa: BLE001
            sh = None
        if sh is None:
            #: ★ 退路：遍历 GetSheetNames 找同名（★ 有些版本 GetSheetByName 不稳）
            try:
                names = list(_get(model, "GetSheetNames") or [])
            except Exception as exc:                           # noqa: BLE001
                return None, "取图纸名清单失败：%s: %s" % (type(exc).__name__, str(exc)[:120])
            if str(sheet_name) not in [str(n) for n in names]:
                return None, "没有名为 %r 的图纸（现有：%s）" % (str(sheet_name), names)
            sh = _get(model, "GetCurrentSheet")
        return (sh, None) if sh is not None else (None, "图纸对象取不到")
    except Exception as exc:                                   # noqa: BLE001
        return None, "取图纸失败：%s: %s" % (type(exc).__name__, str(exc)[:140])


def get_sheet_scale_report(model, sheet_name: str = "") -> dict:
    """★ **读图纸比例**（★ 走官方 Remarks 指定的 `ISheet.GetProperties`）。

    ★ 回 `{"ok", "sheet_name", "numerator", "denominator", "ratio_text", "properties"}`。
    ⚠ **`GetProperties` 的位置 3 / 4 是比例的两个数**（★ 位置 0/1 是纸张尺寸 · 位置 2 是视图比例标志 ·
      位置 5/6 是宽高）；★ **本函数只认那两位**，★ 其余原样回在 `properties` 里供核对。
    """
    from sw_connect import get_com_member as _get
    sheet, err = _sheet_by_name(model, sheet_name)
    if err:
        return {"ok": False, "error": err}
    try:
        props = list(_get(sheet, "GetProperties") or [])
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "error": "GetProperties 失败：%s: %s" % (type(exc).__name__, str(exc)[:150])}
    if len(props) < 5:
        return {"ok": False, "error": "GetProperties 只回了 %d 个元素（★ 预期 ≥7）" % len(props),
                "properties": [str(x)[:30] for x in props]}
    #: ★★★ 2026-10-01（轮 301）**顺序是真机定的**：传 `SetScale(1, 5)` 而读回
    #:   **`5:1`** ⇒ ★★ **`props[3]` 是 Denominator、`props[4]` 是 Numerator**（与字面相反）。
    #:   ★ 另一组：传 `SetScale(1, 2)` → 读回 `2:1`。⇒ ★ **两组同向 ⇒ 定序可信**。
    den, num = float(props[3]), float(props[4])
    return {"ok": True, "sheet_name": str(sheet_name) or "(当前)", "numerator": num, "denominator": den,
            "ratio_text": "%g:%g" % (num, den),
            "properties": [str(x)[:30] for x in props],
            "★": "位置 3/4 是比例的两个数（官方 Remarks 指定 GetProperties 读比例）"}


def set_sheet_scale_report(model, numerator: float, denominator: float,
                           scale_anno_position: bool = False, scale_anno_text_height: bool = False,
                           sheet_name: str = "") -> dict:
    """★ **设图纸比例并回读**（★ 走 `ISheet.SetScale` —— 官方签名 4 参，★ 回 bool）。

    ★ 判据：★ **`SetScale` 回真** · ★ **且回读的 (位置 3, 位置 4) 真的变成了 (numerator, denominator)**。
    ⇒ ★ 两者缺一 ⇒ `ok: False`（★ 规则 6：不静默成功）。
    """
    from sw_connect import get_com_member as _get
    sheet, err = _sheet_by_name(model, sheet_name)
    if err:
        return {"ok": False, "error": err}
    try:
        num, den = float(numerator), float(denominator)
    except (TypeError, ValueError) as exc:
        return {"ok": False, "error": "比例两个数必须是数字：%s" % str(exc)[:120]}
    if num <= 0 or den <= 0:
        return {"ok": False, "error": "比例的两个数都必须 > 0（★ 收到 %r:%r）" % (num, den)}
    #: ★★★★ 2026-10-01（轮 301）**真机定出的合法值：Numerator 只接受 1**。
    #:   证据（三组，同一个图纸）：
    #:     `SetScale(1, 5)` → 读回 **1:5** ✓；`SetScale(3, 7)` → 读回 **1:7**；
    #:     `SetScale(2, 1)` → 读回 **1:1**
    #:   ⇒ ★★ **Numerator 被强制成 1**（★ 而 `SetScale` **仍回 `True`** ——
    #:     ★★★ **即：它不报错，只是静默地改成 1**）。
    #:   ⇒ ★ 本函数**不替它静默**：★★ `numerator != 1` 时**显式拒绝并列合法值****
    #:     （★ 与事实 197「报错要会列合法值」同族）。
    if abs(num - 1.0) > 1e-9:
        return {"ok": False, "stage": "validate", "asked": [num, den],
                "error": "本机 `ISheet.SetScale` 的 Numerator **只接受 1**"
                         "（★ 真机三组：(1,5)→`1:5` · (3,7)→`1:7` · (2,1)→`1:1`）"
                         "⇒ 图纸比例只能是 **1:n** 形式；"
                         "★ 合法值：Numerator = 1，Denominator > 0（★ 收到 %r:%r）" % (num, den)}
    before = get_sheet_scale_report(model, sheet_name)
    try:
        ret = _get(sheet, "SetScale", num, den, bool(scale_anno_position), bool(scale_anno_text_height))
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "set", "asked": [num, den], "before": before,
                "error": "SetScale 失败：%s: %s" % (type(exc).__name__, str(exc)[:180])}
    after = get_sheet_scale_report(model, sheet_name)
    ok_readback = bool(after.get("ok") and abs(after.get("numerator", -1) - num) < 1e-9
                       and abs(after.get("denominator", -1) - den) < 1e-9)
    return {"ok": bool(ret) and ok_readback, "asked": [num, den], "set_scale_returned": bool(ret),
            "before": before, "after": after, "readback_matches": ok_readback,
            "★": "回读判据 = GetProperties 的位置 3/4 真的变了（★ 规则 6）"}
