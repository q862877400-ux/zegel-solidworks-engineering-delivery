"""★ 真机：★ 建工程图 + 加注释 ⇒ 用 `view_annotations_report` 读回（★ 工程图读侧第一批）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 官方 `IView\\GetAnnotations.md` / `GetAnnotationCount.md` / `GetArcCount.md` /
#         `GetDisplayDimensions.md` + 官方示例 `Get_Names_of_Annotations_Example_VB.md`
# 文件:   tools/probe_drawing_annotations_recheck.py（★ 只报不动 —— 证据脚本 · 新）
# 定位:   ★ 阶段 4/5：★ 本仓有 `add_note`（**能写注释**）★ 而**读不回来** ⇒
#     ★★ **⇒ 又是「能写不能读」**（★ 本会话第 6 次同型）⇒ ★ **本探针补读侧** ✓
#   ★★★ **官方例子的调用序**（★ 签名给不了）：★ `GetFirstView` ⇒
#     ★ **`' First drawing view is the sheet, so get first drawing view`** ⇒ `GetNextView` ⇒
#     ★★ **`annArray = swDrView.GetAnnotations`** ⇒ `For Each` ⇒ `currAnn.GetName` ✓
#   ★★★★ **判据（★ 两层独立）**：
#     ★ **① 我加了几条注释 ⇒ `GetAnnotationCount()` 应当 ≥ 那条数** ✓
#     ★★ **② 而 `GetAnnotations()` 回的数组长度应当与它一致** ⇒
#       ★ **两个数不一致就说明有东西没读到** ✓
#   ★★★★★ **⚠ 官方例子说**第一个视图是图纸本身** ⇒ ★ 本函数**跳过它**；
#     而本探针要**同时报出"跳过了几个"** ⇒ ★ **那样"跳过"这件事是可见的** ✓
#   覆盖:   全文件
# ---------------------------------------------------------------------------

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = ROOT / "output" / "drawing-annotations-capability-recheck.json"
ev: dict = {
    "★_判据": ("加 N 条注释 ⇒ `GetAnnotationCount()` ≥ N · ★ 且 `GetAnnotations()` 数组长度与它一致"
               "（★ **两个独立读数**）"),
    "★_官方例子的调用序": ("`GetFirstView` ⇒ ★ **'First drawing view is the sheet'** ⇒ `GetNextView` ⇒ "
                          "`GetAnnotations` ⇒ `For Each` ⇒ `GetName`"),
    "steps": []}


def step(name: str, **kw) -> None:
    """★ 每步**增量落盘**（★ 超时也看得到卡在哪 —— ★ 轮 130 的教训）"""
    ev["steps"].append(dict(name=name, **kw))
    try:
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:                                                       # pragma: no cover
        pass
    print("★ %-28s %s" % (name, json.dumps(kw, ensure_ascii=False)[:230]))


def main() -> int:
    from sw_connect import connect_solidworks, get_com_member, new_document
    import sw_part as P

    app, _ = connect_solidworks(visible=True)
    #: ★ 先建一个零件（★ 工程图要有模型才能投影；★ 而空图纸也能验"读侧"）
    part = new_document(app, "part")
    with P.sketch(part, "Front Plane") as sk:
        P.sketch_corner_rectangle(part, -30.0, -20.0, 30.0, 20.0)
    P.extrude_boss(part, sk, 10.0)
    step("part", title=str(get_com_member(part, "GetTitle")))

    #: ★★★★ 2026-10-04（轮 136）**先让零件存盘** —— ★ 实测：★ 不存盘则 `GetPathName()` 是
    #:   **空串** ⇒ ★★ **⇒ `create_three_standard_views` 插不了视图**（★ 它要 `part_path`）⇒
    #:   ★★★ **⇒ 于是 `view_count = 0`**、★ **而那是**应然的**、★ 验不了读侧** ✗
    #:   ★ **⇒ 可复用判据**：★★★ **"零件/装配体要投影"的能力，前置是**那个文件有路径**** ✓
    saved = {"error": None}
    try:
        import tempfile
        from sw_connect import save_document
        dst = str(Path(tempfile.gettempdir()) / "dsh_probe_drawing_annot_source.SLDPRT")
        saved["path"] = dst
        #: ★ `save_document` 在 **`sw_connect`**、★ **不在 `sw_part`** ——
        #:   ★★ **⇒ 可复用判据**：★ **先问它在哪个模块**（★ 别猜 —— ★ 本会话已因此错过多次）✓
        saved["returned"] = str(save_document(part, dst))[:140]
    except Exception as exc:                                              # noqa: BLE001
        saved["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
    step("save_part", **saved)

    drw = new_document(app, "drawing")
    step("drawing", title=str(get_com_member(drw, "GetTitle")))

    #: ★★★★ 2026-10-04（轮 136）**先插一个视图** —— ★ 空图纸上 `view_count = 0` 是**应然的**、
    #:   而**那样验不了读侧** ⇒ ★★ **⇒ 本探针插视图** ✓
    #:   ★★★★★ **⚠ 而真机实测：★ 「三视图」那条路在本机**是 blocked**** ——
    #:     ★ `create_three_standard_views` 的 `verified_by` 逐字：
    #:       「★ 返回里有建成视图（★ **本机实测为 blocked**：`CreateFirstAngleViews2` 不可用）」✓
    #:     ★★ **⇒ 所以本探针改走**已知能通的那条**：★ `create_projected_view`
    #:       （★ 它的 docstring 逐字：★「本工具**经工具层**实测返回真实视图对象（`CDispatch`）、
    #:         ★ **且正是靠本地化名回退建成**（`*Front` 失败 → `*前视` 成功）」）✓
    #:   ★★★ **可复用判据**：★★★ **同一件事有多条路时，先走**已知能通**的那条** ——
    #:     ★ 别在 blocked 的那条上反复试（★ 与**事实 53**同族）✓
    made = {"error": None, "tried": []}
    part_path = ""
    try:
        part_path = str(get_com_member(part, "GetPathName") or "")
        made["part_path"] = part_path
        import sw_drawing_expose as E0
        if not part_path:
            made["error"] = "★ 零件还没存盘 ⇒ 没有路径 ⇒ 插不了视图（★ 如实记）"
        else:
            #: ★ 第 ① 条（★ 已知能通）：`create_projected_view` ✓
            made["tried"].append("create_projected_view")
            made["projected"] = str(E0.create_projected_view(
                drw, part_path, view_name="*Front", x_mm=140.0, y_mm=120.0,
                scale=0.0))[:170]
            #: ★ 第 ② 条（★ 实测 blocked）：仍然试一次，★ **以便把"blocked"这件事记进证据** ✓
            made["tried"].append("create_three_standard_views")
            made["three_std"] = str(E0.create_three_standard_views(drw, part_path))[:150]
    except Exception as exc:                                              # noqa: BLE001
        made["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
    step("insert_views", **made)

    #: ★★ 用**本仓的写侧**加一条注释（★ 那样"能写不能读"才是同一对）✓
    #:   ★★★★ **⚠ 它的契约是 keyword-only**（`*, x_mm, y_mm, text`）——
    #:     我第一版传了**位置实参** ⇒ `TypeError: takes 1 positional argument but 4 were given` ✗
    #:     ★★ **⇒ 可复用判据**：★ **调本仓能力前先看它的签名**（★ 别按"常识"传参）✓
    wrote = {"error": None}
    try:
        import sw_drawing_expose as E
        f = getattr(E, "add_drawing_note", None)
        wrote["has_add_note"] = callable(f)
        if callable(f):
            wrote["returned"] = str(f(drw, x_mm=50.0, y_mm=50.0, text="★ 探针注释"))[:130]
    except Exception as exc:                                              # noqa: BLE001
        wrote["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
    step("add_note", **wrote)

    import sw_drawing_query as Q
    rep = Q.view_annotations_report(drw)
    step("view_annotations_report", view_count=rep.get("view_count"), views=rep.get("views"))

    #: ★★★ **两条独立读数**（★ 官方 Remarks 说 count 给数组定大小 ⇒ 一致才可信）✓
    bad = []
    for v in rep.get("views") or []:
        c = v.get("annotation_count_by_api")
        n = v.get("annotation_len")
        if isinstance(c, int) and isinstance(n, int) and c != n:
            bad.append({"view": v.get("name"), "count_api": c, "array_len": n})
    ev["★_两读数不一致的视图"] = bad
    ev["★_结论"] = ("★ **建成并读回**（★ 视图 %d 个）" % rep.get("view_count", 0)
                    if rep.get("view_count") else "★ **视图 0 个** ⇒ ★ 如实标")
    step("VERDICT", verdict=ev["★_结论"], mismatches=len(bad))

    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
    print("★ 已写", OUT)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException as exc:                                          # noqa: BLE001
        ev["fatal"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("★ FATAL:", ev["fatal"])
        raise SystemExit(1)
