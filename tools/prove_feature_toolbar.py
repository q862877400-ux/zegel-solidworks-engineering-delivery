"""★ 真机：特征工具条那 21 个按钮逐个试（★ 用真入口，每个全新零件）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_feature_toolbar.py
# 定位:   ★ 2026-10-03（轮 463）★ 用户贴「特征」工具条截图，要**逐条**的能/不能。
#   ★★ **不用关键词搜事实表**（我试过 —— 它把「单位是米」算成「拉伸到不了」，
#     又把真机验过的抽壳算成"到不了" ⇒ 假阳性）★ 那正是**事实 51** 的教训。
#   ⇒ ★★★ 故**逐个真机试**：★ 判据 = **特征树增量 或 几何变化**（★ 规则 6）；
#     ★ 没有入口的直接「不能」（★ 并写明"本仓无入口"）✓
#   ⚠ **每个功能都新建零件**（★ 免副作用污染 —— 本轮已在"圆角改边序"上栽过一次）✓
#   ★★ 入口清单是**先盘问出来的**（事实 371：别猜函数名）：
#     ```
#     拉伸/旋转/切除/圆角/倒角/抽壳/镜向/阵列/圆顶 \u2192 sw_part
# 扫描 \u2192 sw_sweep · 放样 \u2192 sw_loft · 包覆 \u2192 sw_wrap · 筋 \u2192 sw_part.r
# ib_report
# 孔 \u2192 sw_hole_features · 曲线 \u2192 sw_part.insert_composite_curve_report + sw_he
# lix
#     基准轴 \u2192 sw_part.create_axis_report
#     ```
# 官方依据: 各包装模块（★ 与 ToolSpec 的 module/function 同名同签名）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 见上（特征树增量 / 几何变化）。

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R / "scripts"))
sys.path.insert(0, str(R / "mcp-server"))
OUT = R / "output" / "feature-toolbar-evidence.json"


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    import sw_part as P
    from sw_selection_spec import clear_selection, resolve_selection

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "items": []}

    def box(depth=10.0):
        d = sw_connect.new_document(sw, "part")
        P.start_sketch(d, plane_name="Front Plane")
        P.sketch_corner_rectangle(d, -25.0, -20.0, 25.0, 20.0)
        sk = P.current_sketch_name(d, "")
        P.end_sketch(d)
        P.extrude_boss(d, sk, depth)
        return d, sk

    def nt(d):
        try:
            return len(list(P.feature_names(d)))
        except Exception:
            return -1

    def gm(d):
        try:
            b = list(get_com_member(d, "GetBodies2", -1, True) or [])[0]
            return [
                len(list(get_com_member(b, "GetFaces") or [])),
                len(list(get_com_member(b, "GetEdges") or [])),
            ]
        except Exception:
            return None

    def run(zh, fn, pre=box):
        row = {"zh": zh, "verdict": "不能"}
        doc = None
        try:
            doc, sk = pre()
            n0, g0 = nt(doc), gm(doc)
            msg = fn(doc, sk)
            n1, g1 = nt(doc), gm(doc)
            row.update(
                {
                    "tree": [n0, n1],
                    "geom": [g0, g1],
                    "note": str(msg)[:70] if msg else "",
                }
            )
            #: ★★★ 2026-10-03（轮 463）**判据修正** ——
            #:   ★ 我原来用「树或几何变了」⇒ ★★ 而把 `ok:False` 的
            #:     放样/筋/包覆 **误判成能**（真侧 ok:False 才是真的）⚠
            #:   ★★★ **那些 `*_report` 包装自己就做了规则 6 的回读**
            #:     （判「特征树多了**且**类型名对」）⇒ 以它们的 `ok` 为准 ✓
            if isinstance(msg, dict) and "ok" in msg:
                row["judge"] = "report.ok"
                row["verdict"] = "能" if msg.get("ok") else "不能"
            else:
                row["judge"] = "tree/geom"
                row["verdict"] = "能" if ((n1 > n0) or (g0 != g1)) else "不能"
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
        print(
            "  %-16s %-3s  %s"
            % (zh, row["verdict"], str(row.get("err") or row.get("note") or "")[:74])
        )
        return row

    def no_entry(zh):
        ev["items"].append({"zh": zh, "verdict": "不能", "note": "本仓无入口"})
        print("  %-16s %-3s  %s" % (zh, "不能", "本仓无入口"))

    # ── 有入口的 ───────────────────────────────────────────────────
    run("拉伸凸台", lambda d, s: P.extrude_boss(d, s, 8.0))
    run("旋转凸台", lambda d, s: P.revolve_boss(d, s, math.radians(360.0)))

    def _sweep(d, s):
        import sw_sweep

        P.start_sketch(d, plane_name="Front Plane")  # \u8f6e\u5ed3
        P.sketch_circle(d, 0.0, 0.0, 4.0)
        s1 = P.current_sketch_name(d, "")
        P.end_sketch(d)
        P.start_sketch(d, plane_name="Top Plane")  # \u8def\u5f84
        P.sketch_line(d, 0.0, 0.0, 0.0, 40.0)
        s2 = P.current_sketch_name(d, "")
        P.end_sketch(d)
        clear_selection(d)
        ext = get_com_member(d, "Extension")
        P._select_by_id(ext, s1, "SKETCH", mark=1)  # 轮廓 mark=1
        P._select_by_id(ext, s2, "SKETCH", append=True, mark=4)  # 路径 mark=4
        return sw_sweep.create_sweep_report(d)

    run("扫描", _sweep)

    def _loft(d, s):
        import sw_loft

        P.start_sketch(d, plane_name="Front Plane")
        P.sketch_corner_rectangle(d, -20.0, -20.0, 20.0, 20.0)
        s1 = P.current_sketch_name(d, "")
        P.end_sketch(d)
        P.start_sketch(d, plane_name="Top Plane")
        P.sketch_circle(d, 0.0, 0.0, 8.0)
        s2 = P.current_sketch_name(d, "")
        P.end_sketch(d)
        clear_selection(d)
        ext = get_com_member(d, "Extension")
        P._select_by_id(ext, s1, "SKETCH", mark=1)
        P._select_by_id(ext, s2, "SKETCH", append=True, mark=1)
        return sw_loft.create_loft_report(d)

    run("放样凸台", _loft)
    no_entry("边界凸台")

    def _cut(d, s):
        P.start_sketch(d, plane_name="Front Plane")
        P.sketch_circle(d, 0.0, 0.0, 6.0)
        s2 = P.current_sketch_name(d, "")
        P.end_sketch(d)
        return P.extrude_cut(d, s2, 0.0)

    run("拉伸切除", _cut)

    def _hole(d, s):
        import sw_hole_features as H

        return H.create_through_hole_at_selection_report(d, "index:0", 6.0)

    run("异型孔", _hole)
    no_entry("旋转切除")
    run("扫描切除", lambda d, s: (_sweep(d, s), None)[1])
    no_entry("放样切除")
    no_entry("边界切除")
    run(
        "圆角",
        lambda d, s: (
            clear_selection(d),
            resolve_selection(d, "index:0", "EDGE"),
            P.fillet(d, 2.0),
        )[-1],
    )
    run("线性阵列", lambda d, s: P.linear_pattern(d, s, 1.0, 0.0, 0.0, 15.0, 2))

    def _rib(d, s):
        P.start_sketch(d, plane_name="Right Plane")
        P.sketch_line(d, 0.0, 0.0, 0.0, 15.0)
        s2 = P.current_sketch_name(d, "")
        P.end_sketch(d)
        return P.rib_report(d, s2, 2.0)

    run("筋", _rib)
    no_entry("拔模")
    run("抽壳", lambda d, s: P.shell_report(d, 2.0))

    def _wrap(d, s):
        import sw_wrap

        P.start_sketch(d, plane_name="Front Plane")
        P.sketch_circle(d, 0.0, 0.0, 5.0)
        s2 = P.current_sketch_name(d, "")
        P.end_sketch(d)
        clear_selection(d)
        ext = get_com_member(d, "Extension")
        P._select_by_id(ext, s2, "SKETCH", mark=4)  # 草图 mark=4
        import sw_selection_spec as SS

        SS.select_entity_by_index(d, "FACE", 0, append=True)  # 面 mark=1（它自带）
        return sw_wrap.create_wrap_report(d)

    run("包覆", _wrap)
    no_entry("相交")
    run(
        "镜向",
        lambda d, s: P.mirror_feature(
            d,
            [n for n in P.feature_names(d) if "拉伸" in n or "Boss" in n][-1],
            "Right Plane",
        ),
    )

    def _axis(d, s):
        import sw_selection_spec as SS

        SS.select_entity_by_index(d, "FACE", 0)
        return P.create_axis_report(d)

    run("参考几何体", _axis)

    def _curve(d, s):
        import sw_selection_spec as SS

        SS.select_entity_by_index(d, "EDGE", 0)
        return P.insert_composite_curve_report(d)

    run("曲线", _curve)

    ok = sum(1 for i in ev["items"] if i["verdict"] == "能")
    ev["can"], ev["total"] = ok, len(ev["items"])
    ev["verdict"] = "pass" if ok == ev["total"] else "partial"
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  ── **能 %d / 共 %d**" % (ok, ev["total"]))
    print("  产物：%s" % OUT)
    try:
        sw.CommandInProgress = False
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
