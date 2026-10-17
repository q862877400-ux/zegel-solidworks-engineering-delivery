"""★ 探针：焊接符号的**真 API** —— ★ `IModelDoc2::InsertWeldSymbol3`（零参）+ `IWeldSymbol`。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B3 焊接符号的第五步 —— ★ **换到真 API**）
# 文件:   tools/probe_spec211_weldsymbol_real.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的「焊件 / 焊接符号」。★ 前四步的账：
#   ★ ①②③ 前置全对上 · ★ 判据落到位（跳过图纸 + 逐视图 GetWeldSymbolCount）·
#   ★④ **12 组形态 × 开关位** ⇒ 全部 `0 → 0` ✗ ⇒ ★ 我当时**明确说**"还有'选择前置'那一维没追" ✓
#   ⇒ ★★★★ **本批**搜官方示例**，真因找到了** —— ★ 我**走的是另一条 API** ✗✓
# 官方依据（★★★ 第 ③ 样第四次救场，★ 而这次是最强的一次）：
#   · ★★ `C:\swapi\examples\Insert_Weld_Symbol_Example_VB.md` 的 **Preconditions 逐字**：
#       「★ **Select a face, edge, or sketch segment for Weld Symbol insertion**」✓
#       ⇒ ★★ **前置 = 在零件上选面/边/草图段**（★ 不是视图 ✗）
#     ★ 而其**代码**是两步式：
#       `Set swWeldSymbol = swModel.InsertWeldSymbol3` ⇒
#       `swWeldSymbol.SetText True, "Left", "BUTT", "Right", "Stagger", swWeldContourNone` …
#   · ★★★ `IModelDoc2::InsertWeldSymbol3` 的官方页：
#       `System.object InsertWeldSymbol3()` ⇒ ★ **零参** ✓ · ★ `## Returns` = **Newly created weld symbol** ✓
#       ★★ `## Remarks` 逐字：「★ To use this method, **insert the weld symbol into the model and
#         then manipulate the properties and methods on the `IWeldSymbol` object**.」✓✓
#       ★★★ 且**符号名清单根本不在 `annotations\\*.sldweldfvt`** ✗ ——
#         而是 **`C:\ProgramData\SolidWorks\SolidWorks 20*nn*\*lang*\*english*\gtol.sym`** ✓，
#         且**官方逐条列了 16 个 ISO 符号名**：★ `BUTT` · `BUSQ` · `BUSV` · `BUSB` · `BUSVBR` ·
#         `BUSBR` · `BUSU` · `BUSJ` · `BACK` · `FILL` · `PLUG` · `SPOT` · `SEAM` · `SEAMC` · `JSPT` · `JSM` ✓
#   · ★ `IWeldSymbol::SetText` 的签名：
#       `System.bool SetText( System.bool Top, System.string Left, System.string Symbol,
#        System.string Right, System.string Stagger, System.int Contour )` ✓
# 判据:   ★★ **回读**（★ 第 38 轮定则：★ 判据落在"它真正改变的东西"上 ✓）——
#     ★ `IWeldSymbol` **自带一整套读回**（★ 官方示例里逐个用过 ✓）：
#       `GetTextCount` · `GetLineCount` · `GetArcCount` · `GetTriangleCount` · `GetArrowHeadCount` ·
#       `GetLeaderCount` · `IsAttached` · `HasExtraLeader` ✓
#     ★★ 且 `SetText` **回 `bool`** ⇒ ★ 旁证（★ **但主判据仍是读回** —— 事实 8 ✓）
#   ★★ 前置逐条落布尔字段（★ 「读数无效」与「真的不建」长得一模一样 —— ★ 已五次 ✓）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

WORK = ROOT / "output" / "spec211-b3-weldsym3"
#: ★★★ 官方 `## Remarks` **逐条列出的 16 个 ISO 符号名** ✓（★ 前几个就够试 ✓）
ISO_SYMBOLS = ("BUTT", "FILL", "PLUG", "SPOT", "SEAM", "BACK", "BUSQ", "JIS" if False else "JSM")
#: ★ `IWeldSymbol` 的读回成员（★ 官方示例里逐个用过 ✓）
READBACK = ("GetTextCount", "GetLineCount", "GetArcCount", "GetTriangleCount",
            "GetArrowHeadCount", "GetLeaderCount", "IsAttached", "HasExtraLeader")


def main() -> int:
    import sw_connect
    import sw_part
    import sw_selection_spec as SS

    out: dict = {"official": "IModelDoc2.InsertWeldSymbol3 + IWeldSymbol",
                 "step": "第五步：换到真 API（★ 官方示例揭示的两步式）",
                 "iso_symbols_from_official": list(ISO_SYMBOLS)}
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    WORK.mkdir(parents=True, exist_ok=True)

    #: ① 建**零件**（★ 官方示例的 Precondition 是零件、★ 不是工程图 ✗）
    model = sw_connect.new_document(sw, "part")
    sw_part.start_sketch(model, "Front Plane")
    sw_part.sketch_corner_rectangle(model, 0.0, 0.0, 60.0, 40.0)
    sk = sw_part.current_sketch_name(model)
    sw_part.end_sketch(model)
    sw_part.extrude_boss(model, sk, 12.0)
    try:
        sw_connect.save_document(model, str(WORK / "ws3.sldprt"))
    except Exception:                                                   # noqa: BLE001
        pass

    #: ② **选一个面**（★ 官方示例 Preconditions 逐字：「Select a face, edge, or sketch segment」✓）
    face_ok = False
    try:
        SS.select_entity_by_index(model, "FACE", 0)
        face_ok = SS.get_selection_count(model) > 0
    except Exception as e:                                              # noqa: BLE001
        out["select_error"] = "%s: %s" % (type(e).__name__, str(e)[:120])
    out["face_selected"] = face_ok
    print("★ ① 选面（★ 官方示例的前置）⇒ %r" % face_ok)

    #: ③ **`InsertWeldSymbol3()`**（★ 零参 ✓、★ 回 `IWeldSymbol` 对象 ✓）
    ws_obj = None
    exc = None
    try:
        ws_obj = sw_connect.get_com_member(model, "InsertWeldSymbol3")
    except Exception as e:                                              # noqa: BLE001
        exc = e
    out["insert_returned_is_none"] = ws_obj is None
    out["insert_exception"] = None if exc is None else "%s: %s" % (type(exc).__name__, str(exc)[:140])
    print("★ ② `InsertWeldSymbol3()` ⇒ %s"
          % ("None ✗" if ws_obj is None else "★ **回了对象** ✓"))

    #: ④ **`SetText`**（★ 官方 6 参逐位：★ `Top` · `Left` · `Symbol` · `Right` · `Stagger` · `Contour` ✓）
    set_ret = None
    set_exc = None
    symbol_used = None
    if ws_obj is not None:
        for sym in ISO_SYMBOLS:
            try:
                set_ret = sw_connect.get_com_member(ws_obj, "SetText", True, "Left", sym,
                                                    "Right", "Stagger", 0)
                symbol_used = sym
                break
            except Exception as e:                                      # noqa: BLE001
                set_exc = "%s: %s" % (type(e).__name__, str(e)[:110])
    out["symbol_used"] = symbol_used
    out["set_text_returned"] = str(set_ret)
    out["set_text_exception"] = set_exc
    print("★ ③ `SetText(True, 'Left', %r, 'Right', 'Stagger', 0)` ⇒ 回 %r%s"
          % (symbol_used, set_ret, ("（前几个符号名都抛：%s）" % set_exc) if set_exc else ""))

    #: ⑤ **回读**（★ 判据 —— ★ "它真正改变的东西" ✓）
    rb = {}
    if ws_obj is not None:
        for m in READBACK:
            try:
                rb[m] = sw_connect.get_com_member(ws_obj, m)
            except Exception:                                           # noqa: BLE001
                rb[m] = None
    out["readback"] = {k: (v if isinstance(v, (int, bool)) else str(v)[:40]) for k, v in rb.items()}
    print("★ ④ 回读 ⇒ %r" % out["readback"])

    #: ⑥ **判据**：★ `GetLineCount` / `GetTextCount` / `IsAttached` 有实质读数 ⇒ 建成 ✓
    lines = rb.get("GetLineCount")
    texts = rb.get("GetTextCount")
    attached = rb.get("IsAttached")
    if isinstance(lines, int) and lines > 0:
        out["verdict"] = ("★★★★★ **建成** —— ★ `GetLineCount = %r` · ★ `GetTextCount = %r` · "
                          "★ `IsAttached = %r`（★ 符号名 `%s` · ★ 回读、★ 不是信返回值 ✓）"
                          % (lines, texts, attached, symbol_used))
    elif isinstance(texts, int) and texts > 0:
        out["verdict"] = ("★★★★★ **建成** —— ★ `GetTextCount = %r` · ★ `IsAttached = %r`"
                          % (texts, attached))
    else:
        out["verdict"] = ("★★ **回读没给出实质读数**（★ lines=%r · texts=%r · attached=%r）⇒ "
                          "★ **还不算试死** —— ★ 前置复核：★ 选面=%r · `InsertWeldSymbol3` 回对象=%r"
                          % (lines, texts, attached, face_ok, ws_obj is not None))
    print("★★★ 判定 ⇒ %s" % out["verdict"])

    p = ROOT / "output" / "spec211-b3-weldsymbol-real.json"
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
        (ROOT / "output" / "spec211-b3-weldsymbol-real-traceback.txt").write_text(tb, encoding="utf-8")
        print("★★ 异常已落盘：\n%s" % tb[-1200:])
        raise SystemExit(3)
