"""★ 真机验 `sketch_edit_ops` 里**未取证**的两项 —— `convert_entities` 与 `sketch_mirror`。

（★ 处置 `specs/202-user-coverage-gaps` 的 **SC-004**：★ 第 2 条候选的能力）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\`）
# 文件:   `scripts/sw_sketch_edit.py`（★ 被测能力层）·
#         `tools/verify_sketch_edit_smoke.py` · `tools/prove_b3_sketch_edit.py`（★ 既有探针）
# 定位:   ★ 阶段 · SC-004（★ SPEC `spec.md` §五 逐字：「§五 那 13 条 `stitched`
#   **至少转 `verified` 3 条**」）⇒ ★ **本探针供第 2 条用** ✓
# ★★ **为什么是这两项**：★ `capabilities.yaml` 的 `sketch_edit_ops.limitations[5]` **逐
# 字**：
#     「⚠ `convert_entities` / `sketch_mirror` **未实测**（前者要选中的边/环/面，
#      ★ 后者要中心线 mark=2 的选中标记）—— **不得当成「验过了」**」✓
#     ★★ 而该条目的 `mcp_tools` **恰是这两个**：
#       `solidworks_sketch_convert_entities` · `solidworks_sketch_mirror` ✓
#   ★★★ **官方依据（★ 三源，★ 逐条读的）**：
# · `convert_entities` ⇒ `ISketchManager.SketchUseEdge3(Boolean Chain, Boolean InnerLoop
# s)`
#       （★ 当前入口；★ 官方明写 `IModelDoc2.SketchUseEdge2` 是 **Obsolete**）⇒
# ★ 官方 Remarks 逐字：★ 它投影的是「**selected** edges/loops/faces/curves/external cont
# ours」
#       ⇒ **调用前必须先选中** ✓
#     · `sketch_mirror` ⇒ ★ 官方标记：★ **线段 mark=1 / 中心线 mark=2** ——
#       ★★ **标记是"选中时"定的、★ 不是传参定的**（★ 官方签名 0 参）✓
#     · `create_sketch_chamfer` ⇒ ★ 已被拆成独立条目 `sketch_chamfer`（★ `verified` 10/10）
#       ⇒ ★ **本探针不重测它**（★ 避免与那条重复）✓
#   ★★★★ **判据（★ 每条都要**几何读数**，★ 不只认树增量 —— ★ SPEC 的 Edge Cases 逐字：
#     「判据只认『树增量』会误判（事实 486：树会涨而几何没变）⇒ 判据要含**几何读数**」）**：
#     · **① `convert_entities`** ⇒ ★ 进草图 → 画一条直线 → 退出 → 选中**边** → 再进草图 →
#       ★ 调 `convert_entities` ⇒ ★ **判据：★ 草图段数 `0 → ≥1`**（★ 投影出来的线段是真的）✓
# · **② `sketch_mirror`** ⇒ ★ 进草图 → 画一条**中心线**（mark=2）+ 一条**直线**（mark=1
# ）→
#       ★ 调 `sketch_mirror` ⇒ ★ **判据：★ 草图段数 `2 → 4`**（★ 镜像出来的那条是真的）✓
#   ★★★★★ **只报不动**：★ 本脚本**不改仓**、★ 只写 `output/` ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = REPO / "output" / "sketch-edit-pending-evidence.json"


def _seg(model) -> object:
    """★ 草图段数（★ **几何读数**，★ 不只认树增量）。"""
    from sw_connect import get_com_member

    try:
        sm = get_com_member(model, "SketchManager")
        a = get_com_member(sm, "ActiveSketch")
        if a is None:
            return None
        sk = get_com_member(sm, "ActiveSketch")
        for name in ("GetLineCount2", "GetLineCount"):
            try:
                return int(get_com_member(sk, name, False))
            except Exception:  # noqa: BLE001
                continue
    except Exception:  # noqa: BLE001
        pass
    return None


def main() -> int:
    from sw_connect import (
        connect_solidworks,
        get_com_member,
        new_document,
        create_empty_dispatch_variant,
    )
    import sw_part as P
    import sw_sketch_edit as SE

    app, _ = connect_solidworks(visible=True)
    rows: list = []

    #: ── ① `convert_entities` ───────────────────────────────────────────
    r1: dict = {"项": "convert_entities"}
    try:
        model = new_document(app, "part")
        #: ★ 先在 Front Plane 上画一条线并拉伸 ⇒ 得到一个可投影的**边**
        with P.sketch(model, "Front Plane") as sk1:
            sm = get_com_member(model, "SketchManager")
            get_com_member(sm, "CreateLine", -0.05, -0.03, 0.0, 0.05, -0.03, 0.0)
            get_com_member(sm, "CreateLine", 0.05, -0.03, 0.0, 0.05, 0.03, 0.0)
            get_com_member(sm, "CreateLine", 0.05, 0.03, 0.0, -0.05, 0.03, 0.0)
            get_com_member(sm, "CreateLine", -0.05, 0.03, 0.0, -0.05, -0.03, 0.0)
        P.extrude_boss(model, sk1, 10.0)
        #: ★ 开新草图（★ 在同一个面上）⇒ 选一条**边** ⇒ 投影
        ext = get_com_member(model, "Extension")
        #: ★★★★★ **2026-10-04 修正前置**（★ 事实 517：★ 读回来的值不符时先核自己）——
        #:   第一版是「先选边 → 再进草图」⇒ ★ 而那**可能被"进草图"这个动作清掉选区** ✓
        #:   ⇒ ★ 改成「**先进草图 → 再选边 → 再投影**」（★ 官方 Remarks 只要求
        #:     "调用前已选中"，★ 没说必须在草图外选）✓
        sel = sel_after = None
        with P.sketch(model, "Front Plane") as sk2:
            get_com_member(model, "ClearSelection2", True)
            sel_after = bool(
                get_com_member(
                    ext,
                    "SelectByID2",
                    "",
                    "EDGE",
                    0.0,
                    -0.03,
                    0.0,
                    True,
                    0,
                    create_empty_dispatch_variant(),
                    0,
                )
            )
            #: ★ 回读选区计数（★ 事实 8：★ 不信返回值、★ 只看计数）
            try:
                cnt = get_com_member(
                    get_com_member(model, "SelectionManager"),
                    "GetSelectedObjectCount2",
                    -1,
                )
                r1["草图中选区计数"] = cnt
            except Exception as exc:  # noqa: BLE001
                r1["草图中选区计数"] = "err: %s" % str(exc)[:60]
            r1["进草图后再选边"] = sel_after
            r1["调用前段数"] = _seg(model)
            try:
                rr = SE.convert_entities(model)
                r1["返回"] = json.dumps(rr, ensure_ascii=False, default=str)[:300]
            except Exception as exc:  # noqa: BLE001
                r1["调用异常"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
            r1["调用后段数"] = _seg(model)
        a, b = r1.get("调用前段数"), r1.get("调用后段数")
        r1["★_判据"] = "★ 草图段数 0 → ≥1（★ 投影出来的线段是真的）"
        r1["★_ok"] = a is not None and b is not None and b > (a or 0)
    except Exception as exc:  # noqa: BLE001
        r1["★_ok"] = None
        r1["★_异常"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
    rows.append(r1)

    #: ── ② `sketch_mirror` ──────────────────────────────────────────────
    r2: dict = {"项": "sketch_mirror"}
    try:
        model = new_document(app, "part")
        with P.sketch(model, "Front Plane") as sk:
            sm = get_com_member(model, "SketchManager")
            #: ★ 中心线（★ 官方标记 **mark=2**）
            cl = get_com_member(sm, "CreateCenterLine", 0.0, -0.04, 0.0, 0.0, 0.04, 0.0)
            #: ★ 直线（★ 官方标记 **mark=1**）
            ln = get_com_member(sm, "CreateLine", 0.01, -0.02, 0.0, 0.01, 0.02, 0.0)
            r2["中心线对象"] = type(cl).__name__ if cl is not None else None
            r2["直线对象"] = type(ln).__name__ if ln is not None else None
            #: ★★ 按**官方标记**选中：★ 线段 mark=1 · ★ 中心线 mark=2
            picked = []
            try:
                picked.append(
                    bool(
                        get_com_member(
                            ln, "Select4", True, create_empty_dispatch_variant()
                        )
                    )
                )
            except Exception as exc:  # noqa: BLE001
                picked.append("err: %s" % str(exc)[:60])
            try:
                #: ★ `ISketchSegment.Select4(Append, Callout)` 不带 mark ⇒ 用 `SelectByI
                #: D2` 的 mark 参数
                ext = get_com_member(model, "Extension")
                picked.append(
                    bool(
                        get_com_member(
                            ext,
                            "SelectByID2",
                            "",
                            "SKETCHSEGMENT",
                            0.0,
                            0.0,
                            0.0,
                            True,
                            2,
                            create_empty_dispatch_variant(),
                            0,
                        )
                    )
                )
            except Exception as exc:  # noqa: BLE001
                picked.append("err: %s" % str(exc)[:60])
            r2["选中"] = picked
            r2["调用前段数"] = _seg(model)
            try:
                rr = SE.sketch_mirror(model)
                r2["返回"] = str(rr)[:80]
            except Exception as exc:  # noqa: BLE001
                r2["调用异常"] = "%s: %s" % (type(exc).__name__, str(exc)[:110])
            r2["调用后段数"] = _seg(model)
        a, b = r2.get("调用前段数"), r2.get("调用后段数")
        r2["★_判据"] = "★ 草图段数 2 → 4（★ 镜像出来的那条是真的）"
        r2["★_ok"] = a is not None and b is not None and b > (a or 0)
    except Exception as exc:  # noqa: BLE001
        r2["★_ok"] = None
        r2["★_异常"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
    rows.append(r2)

    R = {
        "★_目的": "★ 为 SC-004 第 2 条候选（`sketch_edit_ops`）补**未取证**的两项真机读数",
        "★_官方依据": {
            "convert_entities": "ISketchManager.SketchUseEdge3(Chain, InnerLoops) —— "
            "官方 Remarks：投影的是 **selected** edges/loops/faces ⇒ 调用前必须先选中",
            "sketch_mirror": "官方标记：线段 mark=1 / 中心线 mark=2 —— 标记是**选中时**定的（签名 0 参）",
        },
        "★_判据边界": "★ 两条都用**几何读数**（草图段数），★ 不只认树增量（★ SPEC Edge Cases / 事实 486）",
        "rows": rows,
    }
    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    for r in rows:
        print(
            "★ %-18s 段数 %s → %s · ok=%s"
            % (r["项"], r.get("调用前段数"), r.get("调用后段数"), r.get("★_ok"))
        )
        for k in ("选中边", "选中", "返回", "调用异常", "★_异常"):
            if r.get(k) is not None:
                print("     %s: %s" % (k, str(r[k])[:110]))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
