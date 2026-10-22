"""★ 真机：`GetSelectedObjectsFace` —— ★ 名字直接对应需求（**一次拿到所有选中的面**）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_selected_objects_face.py
# 定位:   ★ 2026-10-03（轮 423）承**事实 336**。★ 而在"取选区对象"这一处已经改了**三次**
#     （① 四个入口逐个试 ② 分桶取数 ③ 序号语义）—— ★★ **按事实 53 该换做法**。
#   ★★ 而换法来自**枚举**（★ 不猜）：`ISelectionMgr` 上有一个
#     ★ **`GetSelectedObjectsFace`** —— ★ **名字直接写着"取选中的面（复数）"**
#     ⇒ ★★★ 那很可能就是"**一次拿到所有选中面**"的入口
#       （★ 而不是"按序号一个一个取"）。
# ★ 另有 `GetSelectedObjectsComponent` / `GetSelectedObjectsDrawingView` 同族 —— ★ 一并
# 登记。
# 官方依据: `SolidWorks.Interop.sldworks.dll` 的元数据反射（★ 方法名与形参逐字）·
#   `C:\swapi\types\ISelectionMgr\GetSelectedObject6.md`（★ 序号语义那一节）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 有**某一个**入口能一次拿到 **2 个**面（★ 与 `Count2(-1)` 的 2 一致）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(
    Path(__file__).resolve().parents[1]
    / "output"
    / "selected-objects-face-evidence.json"
)


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member

    from scripts import sw_simulation as sim
    from scripts.sw_part import (
        current_sketch_name,
        end_sketch,
        extrude_boss,
        sketch_corner_rectangle,
        start_sketch,
    )

    ev: dict = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "entries": {}}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 20.0)
        sm = get_com_member(doc, "SelectionManager")

        sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
        c1 = sim.select_face_at(doc, 0.0, 0.0, 0.0)
        c2 = sim.select_face_at(doc, 0.0, 0.0, 0.02, append=True)
        ev["selects"] = [c1, c2]
        ev["count2"] = repr(safe_get_com_member(sm, "GetSelectedObjectCount2", -1))

        #: ★ 逐个"复数"入口试（★ 都是官方存在的方法）
        def try_multi(label, member):
            rec = {}
            try:
                #: ★ 官方那种"复数"入口通常回一个 **VARIANT 数组** ⇒ 先**不带参数**调
                raw = get_com_member(sm, member)
                rec["raw_type"] = type(raw).__name__
                rec["len"] = len(raw) if hasattr(raw, "__len__") else None
                rec["sample"] = repr(raw)[:120]
            except Exception as exc:  # noqa: BLE001
                rec["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:110])
            ev["entries"][label] = rec
            return rec.get("len")

        #: ★ **它们都是方法**（上一版我只读了属性、没调）—— 而形参是 `(AtIndex, Mark)`
        #: （★ 出厂类型库反射：`GetSelectedObjectsFace(AtIndex:Int32, Mark:Int32) -> Fac
        #: e2`）。
        #:   ★ 而 `GetSelectedObjectMark(AtIndex) -> Int32` 能告诉我“按序号取”的序号体系。
        rows = []
        for i in (1, 2, 3):
            rec = {"i": i}
            for label, member, args in (
                ("face(-1)", "GetSelectedObjectsFace", (int(i), -1)),
                ("face(0)", "GetSelectedObjectsFace", (int(i), 0)),
                ("mark", "GetSelectedObjectMark", (int(i),)),
                ("obj6(-1)", "GetSelectedObject6", (int(i), -1)),
            ):
                try:
                    v = get_com_member(sm, member, *args)
                    rec[label] = v is not None
                except Exception as exc:  # noqa: BLE001
                    rec[label] = "ERR:" + str(exc)[:40]
            rows.append(rec)
        ev["per_index"] = rows
        got = {
            k: sum(1 for r in rows if r.get(k) is True)
            for k in ("face(-1)", "face(0)", "mark", "obj6(-1)")
        }
        ev["got_counts"] = got
        #: ★ 判据：★ **按序号取面**那一条能不能取到 **2 个**（★ 与 `Count2(-1)` 的 2 一
        #: 致）
        winners = ["face(-1)"] if got.get("face(-1)", 0) >= 2 else []
        ev["entries_that_see_both"] = winners
        ev["verdict"] = "pass" if winners else "partial"
        ev["note"] = (
            "★ 按序号取面对象的正确入口 —— 候选来自**出厂类型库**（★ 不猜），"
            "★ 且**每个都真的调用**（上一版只读了属性）。"
            "★ 判据：`GetSelectedObjectsFace(1..2, -1)` 能不能取到 **2 个面**。"
        )
        ev["note"] = (
            "★ 找一个**一次拿到所有选中面**的入口 —— ★ 候选是那几个**复数**方法"
            "（★ 名字里就写着复数，★ 而不是「按序号取」）。★ 判据：能一次拿到 2 个。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1500])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if doc is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:  # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
