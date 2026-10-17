"""★ 真机：交叉曲线 —— 补**官方前置**（3D 草图 + 两个相交面）再试。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_b3_intersect_curves.py
# 定位:   ★ 2026-10-03（轮 465）★ `specs/201-toolbar-gaps` B3 批里**唯一没验成**的那条。
#   ★★ 为什么单独一个脚本：★ 第一版探针（`tools/prove_b3_sketch_edit.py`）只给了 **2D 草图**，
#     而官方 `ISketchManager.IntersectCurves` 的前置是 **3D 草图 + 两个相交的面**
#     ⇒ ★ 那次失败**不构成能力结论**（★ 本会话已反复栽在"判据/前置不对 ⇒ 能力看着坏"上）✓
#   ★★★ 本脚本的做法：★ 建两个**相交**的体 ⇒ 起一个 **3D 草图** ⇒ **按对象**选中两个面
#     （事实 32：面按名字选不中）⇒ 调 `IntersectCurves` ⇒ ★ 回读**段数增量** ✓
# 官方依据: `C:\swapi\types\ISketchManager\IntersectCurves.md`（`void IntersectCurves()`）·
#   `Insert3DSketch`（同接口，起 3D 草图）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 3D 草图的段数增量。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R / "scripts"))
OUT = R / "output" / "b3-intersect-curves-evidence.json"


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    import sw_part as P
    import sw_sketch as SK
    import sw_sketch_edit_ops as E

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "B3 批的交叉曲线：补官方前置（3D 草图 + 两个相交面）后单独验",
          "judge": "3D 草图段数增量", "items": []}
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        #: \u2460 \u7b2c\u4e00\u4e2a\u4f53\uff1a\u4e00\u4e2a\u65b9\u5757
        P.start_sketch(doc, plane_name="Front Plane")
        P.sketch_corner_rectangle(doc, -20.0, -20.0, 20.0, 20.0)
        sk1 = P.current_sketch_name(doc, "")
        P.end_sketch(doc)
        P.extrude_boss(doc, sk1, 20.0)
        #: \u2461 \u7b2c\u4e8c\u4e2a\u4f53\uff08\u2605 \u4e0e\u7b2c\u4e00\u4e2a**\u76f8\u4ea4**\uff09\uff1a\u4fa7\u9762\u4e0a\u518d\u62c9\u4e00\u4e2a
        P.start_sketch(doc, plane_name="Right Plane")
        P.sketch_corner_rectangle(doc, -10.0, -10.0, 10.0, 10.0)
        sk2 = P.current_sketch_name(doc, "")
        P.end_sketch(doc)
        P.extrude_boss(doc, sk2, 60.0)
        ev["tree"] = len(list(P.feature_names(doc)))
        #: \u2462 \u8d77\u4e00\u4e2a 3D \u8349\u56fe\uff08\u5b98\u65b9 `Insert3DSketch`\uff09
        sm = get_com_member(doc, "SketchManager")
        r3d = get_com_member(sm, "Insert3DSketch", True)
        ev["insert_3d"] = str(r3d)[:24]
        sk3d = get_com_member(sm, "ActiveSketch")
        n0 = int(SK.count_segments(sk3d) or 0) if sk3d is not None else -1
        ev["active_3d"] = sk3d is not None
        #: \u2463 **\u6309\u5bf9\u8c61**\u9009\u4e24\u4e2a\u9762\uff08\u4e8b\u5b9e 32\uff1a\u9762\u6309\u540d\u5b57\u9009\u4e0d\u4e2d\uff09
        import sw_selection_spec as SS
        c1 = SS.select_entity_by_index(doc, "FACE", 0)
        c2 = SS.select_entity_by_index(doc, "FACE", 1, append=True)
        ev["sel"] = [c1, c2]
        #: \u2464 \u8c03\u4ea4\u53c9\u66f2\u7ebf
        E.sketch_intersect_curves(doc)
        sk3d2 = get_com_member(get_com_member(doc, "SketchManager"), "ActiveSketch")
        n1 = int(SK.count_segments(sk3d2) or 0) if sk3d2 is not None else -1
        ev["seg"] = [n0, n1]
        ev["built"] = n1 > n0
        ev["verdict"] = "pass" if ev["built"] else "fail"
    except Exception as e:
        ev["err"] = "%s: %s" % (type(e).__name__, str(e)[:200])
        ev["verdict"] = "fail"
    finally:
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1, default=str)[:900])
        print("  \u4ea7\u7269\uff1a%s \u21d2 %s" % (OUT, str(ev.get("verdict")).upper()))
        try:
            sw.CommandInProgress = False
        except Exception:
            pass
        if doc is not None:
            try:
                t = str(safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
            except Exception:
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
