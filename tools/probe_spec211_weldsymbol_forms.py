"""★ 探针：焊接符号的**第二个成因**（★ `Symbol` 形态 × 开关位）—— ★ 每组都回读。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B3 焊接符号的第四步）
# 文件:   tools/probe_spec211_weldsymbol_forms.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的「焊件 / 焊接符号」。★ 前三步的账：
#   ★ ① 前置全对上（★ 符号名清单 4 个 · ★ 工程图 · ★ 三视图 `view_count = 3` ✓）
#   ★ ② 判据落到位（★ 跳过链首那个**图纸**、★ 逐视图 `IView::GetWeldSymbolCount` ✓）
#   ★③ 而读数是 ★ **`total_weld_symbols = 0`** ✗ ⇒ ★ **调用完成、不抛、什么都没插进去** ✓
#   ⇒ ★★★ **本批追「第二个成因」（参数/档位）** —— ★ 按三成因定则 ✓
# 官方依据（★ 逐字）：
#   · `IDrawingDoc::InsertWeldSymbol` 的 `## Parameters`：★ `Symbol` = **Weld symbol name**（see Remarks）；
#     ★ `Symmetric` = True puts the symbol above **and below** the horizontal line；
#     ★ `FieldWeld` = True puts a **flag** for field welding；★ `DashOnTop` = True puts the **dash line on top**；
#     ★ `Peripheral` = True puts a **peripheral symbol** ✓
#   · ★★ 同页 `## Remarks` 逐字：「`Symbol` specifies the weld symbol name. You can find a list of
#     weld symbol names in **C:\\ProgramData\\SolidWorks\\SolidWorks 20…**」✗
#     ⇒ ★★ **它只给了目录、★ 没说传什么形态**（★ 纯名？带扩展名？完整路径？）✗✓
#   · ★★★ 回读成员（★ 判据）：★ **`IView::GetWeldSymbolCount`** ✓ ——
#     ★ 官方逐字：`## Returns` = 「**Total number of weld symbols on this drawing view**」✓
#   · ★★★ 层次（★ 上一批从官方 Remarks 读出来的）：★ `GetFirstView` **回的是图纸** ✗、
#     ★ `IView::GetNextView` 才是第一个视图 ✓ ⇒ ★ **链首要跳过** ✓
# 判据:   ★★ **每一组都回读 `total_weld_symbols`** ✓ —— ★ 那是"它真正改变的东西" ✓
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

WORK = ROOT / "output" / "spec211-b3-weldsym2"
ANN = Path(r"C:\ProgramData\SolidWorks\SOLIDWORKS 2026\design library\annotations")

#: ★ 要遍历的**形态**（★ 官方只给目录、没说形态 ⇒ ★ 三种都试 ✓）
FORMS = ("plain", "with_ext", "full_path")
#: ★ 要遍历的**开关位**（★ 官方逐字给了每个开关的语义 ✓）
FLAGS = (
    {"name": "all_false", "kw": dict()},
    {"name": "dash_on_top", "kw": dict(dash_on_top=True)},
    {"name": "symmetric", "kw": dict(symmetric=True)},
    {"name": "peripheral", "kw": dict(peripheral=True)},
)


def _views(drawing) -> list:
    """★ 取**真视图**（★ 跳过链首那个**图纸** —— ★ 官方 Remarks 明写它就是 sheet ✓）。"""
    import sw_connect
    chain, cur = [], None
    try:
        cur = sw_connect.get_com_member(drawing, "GetFirstView")
    except Exception:                                                   # noqa: BLE001
        cur = None
    while cur is not None and len(chain) < 16:
        chain.append(cur)
        try:
            cur = sw_connect.get_com_member(cur, "GetNextView")
        except Exception:                                               # noqa: BLE001
            cur = None
    return chain[1:] if len(chain) > 1 else []


def _count(drawing) -> int | None:
    """★ 回读：★ **全部视图上的焊接符号总数** ✓（★ "它真正改变的东西" ✓）"""
    import sw_connect
    total = 0
    got = False
    for v in _views(drawing):
        try:
            n = sw_connect.get_com_member(v, "GetWeldSymbolCount")
            if isinstance(n, int):
                total += n
                got = True
        except Exception:                                               # noqa: BLE001
            pass
    return total if got else None


def main() -> int:
    import sw_connect
    import sw_part
    import sw_drawing_expose as DE

    out: dict = {"official": "IDrawingDoc.InsertWeldSymbol",
                 "step": "第四步：追第二个成因（Symbol 形态 × 开关位）", "runs": []}
    names = sorted(p.stem for p in ANN.glob("*.sldweldfvt")) if ANN.is_dir() else []
    full = str(ANN / (names[0] + ".sldweldfvt")) if names else None
    out["symbol_names"] = names
    out["symbol_full_path"] = full
    print("★ 符号名 ⇒ %r" % names)
    if not names:
        out["verdict"] = "★★ 前置缺：★ 本机没有 `.sldweldfvt` ✗"
        return 0

    variants = {"plain": names[0],
                "with_ext": names[0] + ".sldweldfvt",
                "full_path": full}

    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    WORK.mkdir(parents=True, exist_ok=True)

    #: ★ 建**一个**工程图（★ 它贵 ✓），★ 在同一图上试**多组** ✓
    part = sw_connect.new_document(sw, "part")
    sw_part.start_sketch(part, "Front Plane")
    sw_part.sketch_corner_rectangle(part, 0.0, 0.0, 60.0, 40.0)
    sk = sw_part.current_sketch_name(part)
    sw_part.end_sketch(part)
    sw_part.extrude_boss(part, sk, 12.0)
    p1 = WORK / "ws2.sldprt"
    try:
        sw_connect.save_document(part, str(p1))
    except Exception:                                                   # noqa: BLE001
        pass
    drawing = sw_connect.new_document(sw, "drawing")
    try:
        DE.create_three_standard_views(drawing, str(p1))
    except Exception as e:                                              # noqa: BLE001
        print("★ 建视图失败：%s" % str(e)[:110])
    base = _count(drawing)
    print("★ 建图后基线 ⇒ total_weld_symbols = %r" % base)

    for form in FORMS:
        symbol = variants.get(form)
        for flag in FLAGS:
            kw = {"symmetric": False, "field_weld": False, "show_other_side": False,
                  "dash_on_top": False, "peripheral": False}
            kw.update(flag["kw"])
            exc = None
            try:
                sw_connect.get_com_member(
                    drawing, "InsertWeldSymbol",
                    "", str(symbol), "",
                    kw["symmetric"], kw["field_weld"], kw["show_other_side"],
                    kw["dash_on_top"], kw["peripheral"], False, "")
            except Exception as e:                                      # noqa: BLE001
                exc = "%s: %s" % (type(e).__name__, str(e)[:90])
            after = _count(drawing)
            out["runs"].append({"form": form, "symbol": str(symbol)[:70],
                                "flags": flag["name"], "before": base, "after": after,
                                "exception": exc})
            print("★ form=%-9s flags=%-11s ⇒ 回读 %r → %r %s"
                  % (form, flag["name"], base, after, ("· 抛：" + exc) if exc else ""))
            if isinstance(after, int) and isinstance(base, int) and after > base:
                out["verdict"] = ("★★★★★ **建成**（★ form=%s · flags=%s）⇒ ★★ "
                                  "`total_weld_symbols` **%r → %r** ✓" % (form, flag["name"], base, after))
                break
            base = after if isinstance(after, int) else base
        if out.get("verdict"):
            break
    if not out.get("verdict"):
        out["verdict"] = ("★★★★ **三形态 × 四开关位全试过、★ 而 `total_weld_symbols` 始终没涨** ⇒ "
                          "★ **按三成因定则：①② 都追过** ⇒ ★★ **够格叫「试死」**（★ 后端/该成员在此路不通）✓")
    print("★★★ 判定 ⇒ %s" % out["verdict"])

    p = ROOT / "output" / "spec211-b3-weldsymbol-forms.json"
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
        (ROOT / "output" / "spec211-b3-weldsymbol-forms-traceback.txt").write_text(tb, encoding="utf-8")
        print("★★ 异常已落盘：\n%s" % tb[-1200:])
        raise SystemExit(3)
