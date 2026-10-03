"""★ 真机：B1 批那 9 个草图图元逐个建（★ 判据 = 草图实体段数增加）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_b1_sketch_primitives.py
# 定位:   ★ 2026-10-03（轮 464）★ `specs/201-toolbar-gaps` **B1 批**的真机探针。
#   ★★ 与已有的 `tools/prove_sketch_primitives.py`（轮 398，覆盖 arc/ellipse/polygon/slot/
#     centerline 五个**别的**图元）**不是同一批** —— ★ 故用独立文件名，不覆盖 ✓
#   ★★★ **判据**（★ 规则 6 + 事实 8：不认返回值）：★ 每个图元**单独开一张草图**，
#     建之前/之后各回读一次**草图实体段数**（`sw_sketch.count_segments`）——
#     ★ **计数涨了才算建成** ✓
#   ⚠ **为什么每个都单开草图**：★ 官方这些成员都要求"当前在草图编辑态"，
#     而**同一张草图里连着建**会让"涨的那一段是谁的"说不清（★ 判据范围问题，事实 51）✓
# 官方依据: `C:\swapi\types\ISketchManager\*.md`（★ 9 个成员的签名，逐条读过）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 见上（草图实体段数增量）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R / "scripts"))
OUT = R / "output" / "b1-sketch-primitives-evidence.json"


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    import sw_part as P
    import sw_sketch as SK
    import sw_sketch_primitives as SP

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "B1 批：9 个草图图元逐个真机建（specs/201-toolbar-gaps）",
          "judge": "草图实体段数增量（sw_sketch.count_segments）", "items": []}

    def one(zh, fn):
        row = {"zh": zh, "verdict": "不能"}
        doc = None
        try:
            doc = sw_connect.new_document(sw, "part")
            P.start_sketch(doc, plane_name="Front Plane")

            def nseg():
                sk = get_com_member(get_com_member(doc, "SketchManager"), "ActiveSketch")
                return int(SK.count_segments(sk) or 0)

            n0 = nseg()
            ret = fn(doc)
            n1 = nseg()
            row.update({"seg_before": n0, "seg_after": n1,
                        "ret": type(ret).__name__ if ret is not None else "None"})
            row["built"] = n1 > n0
            row["verdict"] = "能" if row["built"] else "不能"
            P.end_sketch(doc)
        except Exception as e:
            row["err"] = "%s: %s" % (type(e).__name__, str(e)[:120])
        finally:
            if doc is not None:
                try:
                    t = str(safe_get_com_member(doc, "GetTitle") or "")
                    if t:
                        sw.CloseDoc(t)
                except Exception:
                    pass
        ev["items"].append(row)
        print("  %-22s %-3s  段 %s\u2192%s  %s" % (
            zh, row["verdict"], row.get("seg_before"), row.get("seg_after"),
            str(row.get("err") or "")[:62]))
        return row

    one("3点边角矩形", lambda d: SP.sketch_3point_corner_rectangle(d, -30, -10, 30, -10, 30, 15))
    one("3点中心矩形", lambda d: SP.sketch_3point_center_rectangle(d, 0, 0, 30, 0, 30, 15))
    one("平行四边形", lambda d: SP.sketch_parallelogram(d, -25, -10, 25, -10, 5, 15))
    one("3点圆弧", lambda d: SP.sketch_3point_arc(d, -20, 0, 20, 0, 0, 20))
    one("部分椭圆", lambda d: SP.sketch_elliptical_arc(d, 0, 0, 30, 0, 0, 15, 30, 0, -30, 0, 1))
    one("抛物线", lambda d: SP.sketch_parabola(d, 0, 20, 0, 0, -25, 12, 25, 12))
    one("圆锥", lambda d: SP.sketch_conic(d, 0, 20, 0, 0, -25, 12, 25, 12))
    one("周边圆", lambda d: SP.sketch_perimeter_circle(d, -20, 0, 20, 0, 0, 18))

    def _tangent(d):
        P.sketch_line(d, -30.0, 0.0, 0.0, 0.0)
        return SP.sketch_tangent_arc(d, 0.0, 0.0, 15.0, 15.0)
    one("切线弧", _tangent)

    ok = sum(1 for i in ev["items"] if i["verdict"] == "能")
    ev["can"], ev["total"] = ok, len(ev["items"])
    ev["verdict"] = "pass" if ok == ev["total"] else "partial"
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("  \u2500\u2500 **\u80fd %d / \u5171 %d** \u21d2 %s" % (ok, ev["total"], str(ev["verdict"]).upper()))
    print("  \u4ea7\u7269\uff1a%s" % OUT)
    try:
        sw.CommandInProgress = False
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
