"""★ 探针：`IDrawingDoc::InsertWeldSymbol` —— ★ 焊接符号（★ 前置链全在本机）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B3 焊接符号的真机探针）
# 文件:   tools/probe_spec211_weldsymbol.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的「焊件 / 焊接符号」。
# 官方依据（★ 三样逐字读过）：
#   · ★★ `C:\swapi\types\IDrawingDoc\InsertWeldSymbol.md`
#     `void InsertWeldSymbol( System.string Dim1, System.string Symbol, System.string Dim2,
#      System.bool Symmetric, System.bool FieldWeld, System.bool ShowOtherSide, System.bool DashOnTop,
#      System.bool Peripheral, System.bool HasProcess, System.string ProcessValue )` ⇒ ★ **参数式 10 参** ✓
#     ★ `## Parameters` 逐字：★ `Dim1` = First text value **to the left of** the symbol ·
#       ★ `Symbol` = **Weld symbol name**（see Remarks）· ★ `Dim2` = Text value **to the right of** the symbol ·
#       ★ `Symmetric` = True puts the symbol above **and below** the horizontal line ·
#       ★ `FieldWeld` = True puts a **flag** for field welding · ★ `ShowOtherSide` ·
#       ★ `DashOnTop` = True puts the dash line **on top** · ★ `Peripheral` = True puts a peripheral symbol ·
#       ★ `HasProcess` = True uses `ProcessValue` ✓
#     ★★ `## Remarks` 逐字：「`Symbol` specifies the weld symbol name. You can find a list of
#       weld symbol names in **C:\ProgramData\SolidWorks\SolidWorks 20…**」✓
#   · ★★★ **宿主是 `IDrawingDoc`** ✓ —— ★ 上一批全扫时确认过：
#     `IModelDoc2` 下另有 `InsertWeldSymbol3`/`2`/`IInsertWeldSymbol3`；★ **本探针走 `IDrawingDoc` 那个** ✓
# 前置核实（★ 本批现场查的，★ 不是假设）：
#   ★ ① **零件要落盘**（★ `create_three_standard_views` 要 `part_path` ✓）⇒ ★ 写到**仓库内 `output/`** ✓
#   ★ ② **工程图**：★ 仓里 `sw_session.new_drawing()` ✓ + `sw_drawing_expose.create_three_standard_views` ✓
#   ★ ③ **符号名清单**：★ 本机**有** —— `…\SOLIDWORKS 2026\design library\annotations\`
#     下的 `.sldweldfvt`：★ `0.25 fillet both side` · `blend weld` · `fillet-allround` · `plug-bevelfillet` ✓
# 判据:   ★★ 主判据一律**回读**；★ 而官方该成员**回 `void`** ✗ ⇒ ★★ **判据要落在「它真正改变的东西」上**
#     （★ 第 38 轮立的定则 ✓）—— ★ 焊接符号是**标注** ⇒ ★ 试**读回**；
#     ★ 本探针**同时落两组读数**：★ ① 调用是否抛 · ★② 工程图的**注释/符号计数**（★ 有没有读回成员待查）
#   ★★ 前置逐条落布尔字段（★ 「读数无效」与「真的不建」长得一模一样 —— ★ 已五次 ✓）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

WORK = ROOT / "output" / "spec211-b3-weldsym"      #: ★ 仓库内产物目录（★ 非用户目录 ✓）
ANN = Path(r"C:\ProgramData\SolidWorks\SOLIDWORKS 2026\design library\annotations")


def _symbol_names() -> list:
    """★ 从本机 `annotations\\` 目录取**真实存在**的焊接符号名 ✓"""
    if not ANN.is_dir():
        return []
    return sorted(p.stem for p in ANN.glob("*.sldweldfvt"))


def main() -> int:
    import sw_connect
    import sw_part

    out: dict = {"official": "IDrawingDoc.InsertWeldSymbol",
                 "step": "全链：零件→落盘→工程图→三视图→焊接符号"}
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    WORK.mkdir(parents=True, exist_ok=True)

    names = _symbol_names()
    out["symbol_names_found"] = names[:8]
    print("★ ③ 本机焊接符号名 ⇒ %r" % names[:6])
    if not names:
        out["verdict"] = "★★ 前置缺：★ 本机 `annotations\\` 下没有 `.sldweldfvt` ✗"
        print(out["verdict"])
        return 0

    #: ① 零件 + 落盘（★ `create_three_standard_views` 要路径 ✓）
    part = sw_connect.new_document(sw, "part")
    sw_part.start_sketch(part, "Front Plane")
    sw_part.sketch_corner_rectangle(part, 0.0, 0.0, 60.0, 40.0)
    sk = sw_part.current_sketch_name(part)
    sw_part.end_sketch(part)
    sw_part.extrude_boss(part, sk, 12.0)
    p1 = WORK / "ws1.sldprt"
    try:
        sw_connect.save_document(part, str(p1))
    except Exception as e:                                              # noqa: BLE001
        out["save_error"] = "%s: %s" % (type(e).__name__, str(e)[:120])
    out["part_saved"] = p1.is_file()
    print("★ ① 零件落盘 ⇒ %r" % out["part_saved"])

    #: ② 工程图 + 三视图（★ 仓里已覆盖 ✓）
    drawing = None
    views_ok = False
    if out["part_saved"]:
        try:
            #: ★★ **不要用 `sw_session.session()`** ✗ —— ★ 它**自己管连接**
            #:   ⇒ 在**已连上 `sw` 之后**再调它，★ 可能**启第二个 SolidWorks 实例** ✗
            #:   （★ 铁律：★ **单源运行** —— 多个进程抢同一 COM 连接会死锁 ✓）
            #:   ⇒ ★ 用**已有连接**建工程图 ✓
            drawing = sw_connect.new_document(sw, "drawing")
        except Exception as e:                                          # noqa: BLE001
            out["drawing_error"] = "%s: %s" % (type(e).__name__, str(e)[:120])
        if drawing is not None:
            try:
                import sw_drawing_expose as DE
                DE.create_three_standard_views(drawing, str(p1))
                views_ok = True
            except Exception as e:                                      # noqa: BLE001
                out["views_error"] = "%s: %s" % (type(e).__name__, str(e)[:130])
    out["drawing_created"] = drawing is not None
    out["views_created"] = views_ok
    print("★ ② 工程图 ⇒ %r · 三视图 ⇒ %r" % (drawing is not None, views_ok))

    #: ③ **焊接符号**（★ 10 参逐位 ✓）—— ★ 宿主 `IDrawingDoc`
    ret = None
    exc = None
    if drawing is not None:
        try:
            #: ★★★ **不要绕 `GetDrawingDoc`** ✗ —— ★ 工程图文档**本身就是 `IDrawingDoc`** ✓
            #:   ★★ 这与上一批 SpeedPak 那次是**同一类错**（★ 我写过 `get_com_member(top, "AssemblyDoc")`
            #:    ⇒ `AttributeError: <unknown>.AssemblyDoc` ✗）⇒ ★★ **推广后的定则**：
            #:     ★★★ **`IModelDoc2` 的族接口（`IAssemblyDoc` / `IDrawingDoc` / `IPartDoc`）
            #:     就是文档本身** ✗ —— ★ **不需要 `GetXxxDoc` 那一层** ✓
            ret = sw_connect.get_com_member(
                drawing, "InsertWeldSymbol",
                "",                      #: Dim1（★ 符号左边文字）
                str(names[0]),           #: Symbol（★ 符号名 —— 用本机清单里的第一个 ✓）
                "",                      #: Dim2（★ 符号右边文字）
                False,                   #: Symmetric
                False,                   #: FieldWeld
                False,                   #: ShowOtherSide
                False,                   #: DashOnTop
                False,                   #: Peripheral
                False, "")               #: HasProcess · ProcessValue
        except Exception as e:                                          # noqa: BLE001
            exc = e
    out["returned"] = str(ret)[:80]
    out["exception"] = None if exc is None else "%s: %s" % (type(exc).__name__, str(exc)[:160])

    #: ④ **判据**（★ 官方回 `void` ⇒ ★ 只能"抛不抛" + ★ 找读回成员 ✓）
    #: ★★★★ **判据要落在「它真正改变的东西」上**（★ 第 38 轮定则 ✓）——
    #:   ★ 焊接符号是**视图上的标注** ✗ ⇒ ★ 顶层注释计数取不到（`GetAnnotationCount` 回 None ✗）
    #:   ★★ 正解：★ **`IView::GetWeldSymbolCount` / `GetWeldSymbols`** ✓（★ B0 全扫时见过 ✓）
    #:     ★ 官方逐字：★ `GetWeldSymbolCount` 的 `## Returns` = **Total number of weld symbols
    #:     on this drawing view** ✓ —— ★★ **那正是"它真正改变的东西"** ✓
    readback = {}
    if drawing is not None:
        #: ★★★★★ 官方 `IDrawingDoc::GetFirstView` 的 `## Remarks` **逐字**（★ 层次说透了 ✓）：
        #:   「★ **Because the drawing sheet also has sketch geometry, notes, GTols, and so on,
        #:    this method returns the current drawing sheet.** ★ The **next** view returned by
        #:    `IView::GetNextView` is the **first drawing view** in the current sheet.」✓✓
        #:   ★ 且 `GetViews` 的 `## Returns` 逐字：「**An array of arrays**」+「the first view in the
        #:    list being **the sheet itself**」✗
        #:   ⇒ ★★★★ **所以第一个对象是**图纸**、★ 不是视图** ✗ ——
        #:     ★★ 上一轮我把图纸当视图 ⇒ `GetWeldSymbolCount` 回 `None` ✗（★ 根因就在这里 ✓）
        chain, cur = [], None
        try:
            cur = sw_connect.get_com_member(drawing, "GetFirstView")
        except Exception:                                               # noqa: BLE001
            cur = None
        while cur is not None and len(chain) < 16:
            chain.append(cur)
            try:
                cur = sw_connect.get_com_member(cur, "GetNextView")
            except Exception:                                           # noqa: BLE001
                cur = None
        #: ★★★ **跳过链首那个"图纸"** ✓（★ 官方 Remarks 明写它就是 sheet ✓）
        readback["chain_len"] = len(chain)
        readback["first_is_sheet"] = True
        views = chain[1:] if len(chain) > 1 else []
        readback["view_count"] = len(views)
        per_view = []
        for i, v in enumerate(views):
            row = {"index": i}
            for label, member in (("weld_symbol_count", "GetWeldSymbolCount"),
                                  ("annotation_count", "GetAnnotationCount")):
                try:
                    row[label] = sw_connect.get_com_member(v, member)
                except Exception:                                       # noqa: BLE001
                    row[label] = None
            try:
                row["name"] = str(sw_connect.get_com_member(v, "GetName2") or "")
            except Exception:                                           # noqa: BLE001
                row["name"] = None
            per_view.append(row)
        readback["per_view"] = per_view
        readback["total_weld_symbols"] = sum(
            int(r["weld_symbol_count"] or 0) for r in per_view
            if isinstance(r.get("weld_symbol_count"), int))
    out["readback"] = readback

    if exc is None:
        out["verdict"] = ("★★ **调用完成、不抛**（★ 官方该成员回 `void` ⇒ ★ 没有返回值判据 ✓）· "
                          "★ 读回：%r ⇒ ★ **符号名清单是真前置**、★ 而「到底插进去了没有」要另找判据"
                          "（★ 第 38 轮定则：★ 判据要落在它真正改变的东西上 —— ★ 符号是标注、★ 不再是特征树 ✓）"
                          % out["readback"])
    else:
        out["verdict"] = ("★★ **抛**：%s ⇒ ★ 按官方 `## Parameters` 复核 10 个实参位 ✓" % out["exception"])
    print("★★ 调用后 ⇒ 回 %r · 异常 %r" % (out["returned"], out["exception"]))
    print("★★★ 判定 ⇒ %s" % out["verdict"])

    p = ROOT / "output" / "spec211-b3-weldsymbol.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    import traceback
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:                                              # noqa: BLE001
        tb = traceback.format_exc()
        (ROOT / "output" / "spec211-b3-weldsymbol-traceback.txt").write_text(tb, encoding="utf-8")
        print("★★ 异常已落盘：\n%s" % tb[-1200:])
        raise SystemExit(3)
