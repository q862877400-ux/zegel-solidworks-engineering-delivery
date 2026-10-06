"""★ 探针：`ISketchManager::InsertExplodeLineSketch` —— ★ 爆炸直线（★ 零参）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B6 爆炸直线的真机探针）
# 文件:   tools/probe_spec211_explodeline.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的「装配 / 爆炸直线」。
# 官方依据（★ 三样逐字读过，★ 并**按第 ④ 样**读全）：
#   · ★★ `C:\swapi\types\ISketchManager\InsertExplodeLineSketch.md`
#     `System.bool InsertExplodeLineSketch()` ⇒ ★ **零参** ✓
#     ★ `## Returns` 逐字：True if the explode line sketch is **inserted or closed**, false if not ✓
#     ★★ 六份官方示例（VB.NET ×2 · VBA ×2 · C# ×2）—— ★ 而**示例名本身就说清用法**：
#       「Insert Explode Line Sketch and **Route Line**」· ★「…and **Jog Line**」
#       ⇒ ★★ **它是"先插图、再画线"两步** ✓
#   · ★★★ **宿主是 `ISketchManager`、不是 `IAssemblyDoc`** ✗ ——
#     本仓原先把它记在 `IAssemblyDoc` 下 ✗（★ 那是**又一处"宿主写错"** ✓；
#     ★ 事实 36：★ 同名接口分属不同族、**用错接口 = 对象对任何成员都没反应** ✓）
#     ★ 而 `IAssemblyDoc` 下**只有**"爆炸视图"那一族（`CreateExplodedView` / `AutoExplode` /
#       `ShowExploded2` / `ViewExplodeAssembly` ✓）—— ★ 覆盖表也把两者分两行 ✓
# 前置链（★ 本批逐条立起来的，★ 不是假设）：
#   ★ ① **零件文件** —— ★ `add_component(asm_model, part_path, …)` **要磁盘上的路径** ✗
#     ⇒ ★ 先建零件、`save_document(part, <仓库内 output/ 下>)` ✓
#     ★★ **写在 `output/` 而不是用户目录** ✓（★ 铁律 3：★ `output/` 是产物目录、gitignore ✓；
#        ★ 且"真机跑不许写到用户目录"这条**不受影响** ✓）
#   ★ ② **装配体** —— `new_document(sw, "assembly")` + `sw_assembly.add_component(...)` ✓
#   ★ ③ **爆炸状态** —— ★ 仓里 `sw_assembly_doc.create_exploded_view`（★ `IAssemblyDoc::CreateExplodedView`，
#      **零参**）**已覆盖** ✓
# 判据:   ★★ 主判据一律**回读**：★ **特征树/树里多了新特征**（★ 不看返回值 ✓）
#   ★★ 前置逐条落布尔字段（★ 「读数无效」与「真的不建」长得一模一样 —— ★ 已四次 ✓）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★ 零件落盘目录（★ **仓库内**、★ gitignore 的产物目录 ⇒ 不碰用户目录 ✓）
WORK = ROOT / "output" / "spec211-b6-asm"


def main() -> int:
    import sw_connect
    import sw_part
    import sw_assembly
    import sw_assembly_doc as AD
    import sw_surface_features as SF

    out: dict = {"official": "ISketchManager.InsertExplodeLineSketch",
                 "step": "全链：零件→保存→装配→爆炸→爆炸直线"}

    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    WORK.mkdir(parents=True, exist_ok=True)

    #: ① 建零件并**保存**（★ add_component 要磁盘路径 ✓）
    part = sw_connect.new_document(sw, "part")
    sw_part.start_sketch(part, "Front Plane")
    sw_part.sketch_corner_rectangle(part, 0.0, 0.0, 40.0, 30.0)
    sk = sw_part.current_sketch_name(part)
    sw_part.end_sketch(part)
    sw_part.extrude_boss(part, sk, 10.0)
    p1 = WORK / "p1.sldprt"
    saved = False
    save_err = None
    try:
        sw_connect.save_document(part, str(p1))
        saved = p1.is_file()
    except Exception as e:                                              # noqa: BLE001
        save_err = "%s: %s" % (type(e).__name__, str(e)[:130])
    out["part_saved"] = saved
    out["part_path"] = str(p1)
    out["save_error"] = save_err
    print("★ ① 零件落盘 ⇒ %r（%s）" % (saved, p1.name))

    #: ② 建装配体并加零件
    asm = sw_connect.new_document(sw, "assembly")
    comp_ok = False
    comp_err = None
    if asm is None:
        comp_err = "★ 建不了装配体"
    else:
        try:
            sw_assembly.add_component(asm, str(p1), 0.0, 0.0, 0.0)
            comp_ok = True
        except Exception as e:                                          # noqa: BLE001
            comp_err = "%s: %s" % (type(e).__name__, str(e)[:130])
    out["component_added"] = comp_ok
    out["component_error"] = comp_err
    print("★ ② 装配体加零件 ⇒ %r" % comp_ok)

    #: ③ 爆炸视图（★ 仓里已覆盖 ✓）
    explode_ok = False
    if comp_ok:
        try:
            explode_ok = bool(AD.create_exploded_view(asm))
        except Exception as e:                                          # noqa: BLE001
            out["explode_error"] = "%s: %s" % (type(e).__name__, str(e)[:130])
    out["exploded_view_created"] = explode_ok
    print("★ ③ 爆炸视图 ⇒ %r" % explode_ok)

    #: ④ **爆炸直线**（★ `ISketchManager::InsertExplodeLineSketch`，**零参** ✓）
    #: ★★★ 换判据（★ 上轮补的定则）：★ **判据要落在「它真正改变的东西」上** ✗ ——
    #:   ★ 顶层特征树**只反映「特征」** ✗，★ 而**草图**另有其树 ✓
    #:   ★★ 官方 `## Returns` 逐字：True if the explode line sketch is **inserted or closed** ✓
    #:     ⇒ ★ **inserted 最可能的表现是「进入草图编辑」** ⇒ ★★ 判据 = `ISketchManager.ActiveSketch` ✓
    before_active = None
    if asm is not None:
        try:
            before_active = sw_connect.get_com_member(
                sw_connect.get_com_member(asm, "SketchManager"), "ActiveSketch")
        except Exception:                                               # noqa: BLE001
            before_active = None
    out["active_sketch_before"] = before_active is not None
    before = SF.feature_names(asm) if asm is not None else []
    exc = None
    ret = None
    if asm is not None:
        try:
            sm = sw_connect.get_com_member(asm, "SketchManager")
            out["sketch_manager_ok"] = sm is not None
            ret = sw_connect.get_com_member(sm, "InsertExplodeLineSketch")
        except Exception as e:                                          # noqa: BLE001
            exc = e
            out["sketch_manager_ok"] = out.get("sketch_manager_ok", False)
    after = SF.feature_names(asm) if asm is not None else []
    added = [n for n in after if n not in before]
    after_active = None
    if asm is not None:
        try:
            after_active = sw_connect.get_com_member(
                sw_connect.get_com_member(asm, "SketchManager"), "ActiveSketch")
        except Exception:                                               # noqa: BLE001
            after_active = None
    out["active_sketch_after"] = after_active is not None
    out["sketch_side_changed"] = (before_active is None) != (after_active is None)
    out.update({"new_features": added, "returned": str(ret),
                "exception": None if exc is None else "%s: %s" % (type(exc).__name__, str(exc)[:150])})
    #: ★★ 判据优先级：★ ① 特征新增 ⇒ 建成 · ★② **草图侧变化** ⇒ 建成（★ inserted 的等价物 ✓）
    if added or out.get("sketch_side_changed"):
        out["verdict"] = ("★★★★★ **建成** —— ★ 特征新增 %r · ★★ 草图侧变化 %r"
                          "（★ ActiveSketch %r → %r ⇒ ★ 正是官方 Returns 里那个 inserted ✓）"
                          % (added, out.get("sketch_side_changed"),
                             out.get("active_sketch_before"), out.get("active_sketch_after")))
    elif exc is not None:
        out["verdict"] = "★★ **抛**：%s" % out["exception"]
    elif ret:
        out["verdict"] = ("★★ 回 `True` 而**树没变化** ⇒ ★ 可能「插入了但没落特征」（★ 官方 Returns 逐字："
                          "inserted **or closed** ✓）⇒ ★ 需另找判据（★ 不看返回值 ✓）")
    else:
        out["verdict"] = ("★★ **不建**（★ 回 %r）⇒ ★ **还不算试死** —— ★ 前置复核："
                          "★ 零件落盘=%r · 装配加件=%r · 爆炸视图=%r（★ 定则：「读到静默」≠「判定试死」✓）"
                          % (ret, saved, comp_ok, explode_ok))
    print("★★ 调用后 ⇒ 新增 %r · 回 %r" % (added, ret))
    print("★★★ 判定 ⇒ %s" % out["verdict"])

    p = ROOT / "output" / "spec211-b6-explodeline.json"
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
        (ROOT / "output" / "spec211-b6-explodeline-traceback.txt").write_text(tb, encoding="utf-8")
        print("★★ 异常已落盘：\n%s" % tb[-1200:])
        raise SystemExit(3)
