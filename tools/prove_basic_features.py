"""★ 真机：**基础功能逐个过一遍**（★ 每个操作一行判据，不许"大概能"）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_basic_features.py
# 定位:   ★ 2026-10-03（轮 462）★ 起因是用户直接问「**基础功能都齐全吗，别搞了半天不能
#           拉伸切除**」。
#   ★★ 故本探针不体检、不静态分析 —— **把每个基础操作真机跑一遍**，逐个报 verdict ✓
#   ★ 覆盖（★ 一个零件从草图到切除到修饰到导出的完整日常）：
#     ```
# \u8349\u56fe\uff1a\u77e9\u5f62 / \u5706 / \u7ebf       \u7279\u5f81\uff1a\u62c9\u4f38\
# u51f8\u53f0 / \u62c9\u4f38\u5207\u9664 / \u65cb\u8f6c / \u62bd\u58f3
#     \u4fee\u9970\uff1a\u5706\u89d2 / \u5012\u89d2        \u5b54\uff1a\u901a\u5b54
# \u6697\u793a\uff1a\u56de\u8bfb\u7279\u5f81\u6811\u589e\u91cf + \u8d28\u91cf\u5c5e\u602
# 7\uff08\u2605 \u800c\u4e0d\u9760\u8fd4\u56de\u503c\uff09
#     ```
#   ★★ 判据（★ 规则 6 的精神）：★ **每一步看**特征树增量**（★ 或质量属性变化）** ——
#     ★ 因为 COM 的返回值不可信（事实 8），★ 而"建成了"= **树真的长了** ✓
# 官方依据: 本仓 `scripts/sw_part.py` / `sw_hole_features.py` / `sw_surface.py` 的公开包
#           装
#   （★ 与 ToolSpec 的 `function` 同名同签名 —— 工具层就是调它们）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 见上（每个操作：特征树增量 / 质量属性）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R / "scripts"))
sys.path.insert(0, str(R / "tools"))
OUT = R / "output" / "basic-features-evidence.json"


def main() -> int:
    import sw_connect
    from sw_connect import safe_get_com_member
    from sw_part import (
        chamfer,
        current_sketch_name,
        end_sketch,
        extrude_boss,
        extrude_cut,
        feature_names,
        fillet,
        sketch_circle,
        sketch_corner_rectangle,
        start_sketch,
    )

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {"sketch_names": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S"), "steps": []}

    def tree():
        try:
            return len(list(feature_names(doc)))
        except Exception:
            return -1

    def rec(name, fn, judge="tree"):
        before = tree()
        row = {"step": name, "tree_before": before}
        try:
            fn()
        except Exception as e:
            row["err"] = "%s: %s" % (type(e).__name__, str(e)[:150])
        after = tree()
        row["tree_after"] = after
        if judge == "selection":
            #: ★ 选择不改特征树 ⇒ 判据是**回读到的选区计数**（事实 8）
            try:
                row["selection_count"] = int(get_selection_count(doc))
            except Exception:
                row["selection_count"] = -1
            row["built"] = row["selection_count"] >= 1
        else:
            row["built"] = after > before
        row["verdict"] = "pass" if row["built"] else "fail"
        ev["steps"].append(row)
        print(
            "  %-26s %s  \u6811 %s\u2192%s  %s"
            % (
                name,
                "\u2713" if row["built"] else "**\u2717**",
                before,
                after,
                row.get("err", "")[:70],
            )
        )
        return row

    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        ev["doc"] = "part"
        #: ① \u8349\u56fe\uff08\u77e9\u5f62\uff09+ \u62c9\u4f38\u51f8\u53f0
        names = {}

        def s1():
            start_sketch(doc, plane_name="Front Plane")
            sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
            names["sk1"] = current_sketch_name(doc, "")
            end_sketch(doc)

        rec("sketch_rectangle", s1, "doc")
        sk1 = names.get("sk1", "")
        rec("extrude_boss_20mm", lambda: extrude_boss(doc, sk1, 20.0))

        #: ② \u62c9\u4f38\u5207\u9664\uff08\u2605 \u7528\u6237\u70b9\u540d\u7684\u90a3\u
        #: 4e2a\uff09
        def s2():
            start_sketch(doc, plane_name="Front Plane")
            sketch_circle(doc, 0.0, 0.0, 8.0)
            names["sk2"] = current_sketch_name(doc, "")
            end_sketch(doc)

        rec("sketch_circle_for_cut", s2)
        sk2 = names.get("sk2", "")
        rec("extrude_cut_through", lambda: extrude_cut(doc, sk2, 0.0))

        #: ③ 圆角 / 倒角（★ 声明式选边；★ **两步各自重选** ——
        #:   因为圆角会**改变边序**（圆角把一条直边换成一段圆弧），
        #:   而**倒角对圆边无效** ⇒ 若不重选，倒角那步会因为选到了圆弧而"看起来不建" ⚠
        #:   ★★ 那正是**事实 104** 的教训：「看到异常就定性」是误判之源。）
        from sw_selection_spec import (
            clear_selection,
            get_selection_count,
            resolve_selection,
        )

        def _sel0():
            clear_selection(doc)
            resolve_selection(doc, "index:0", "EDGE")

        rec("select_edge0_for_fillet", _sel0, "selection")
        rec("fillet_edge0_r2", lambda: fillet(doc, 2.0))

        def _sel1():
            clear_selection(doc)
            resolve_selection(doc, "index:2", "EDGE")

        rec("select_edge2_for_chamfer", _sel1, "selection")
        rec("chamfer_edge1_1p5", lambda: chamfer(doc, 1.5))

        #: ④ \u65cb\u8f6c\uff08\u65b0\u5efa\u4e00\u4e2a\u8349\u56fe + \u4e2d\u5fc3\u7ebf
        #: \u505a\u8f74\uff09
        def s4():
            from sw_part import sketch_centerline

            start_sketch(doc, plane_name="Right Plane")
            sketch_centerline(doc, 0.0, 0.0, 0.0, 30.0)  # ★ 旋转轴
            sketch_corner_rectangle(doc, 5.0, 0.0, 12.0, 30.0)
            names["sk4"] = current_sketch_name(doc, "")
            end_sketch(doc)

        rec("sketch_for_revolve", s4)
        sk4 = names.get("sk4", "")
        import math

        rec(
            "revolve_boss_360",
            lambda: __import__("sw_part").revolve_boss(doc, sk4, math.radians(360.0)),
        )

        #: ⑤ \u62bd\u58f3
        rec("shell_2mm", lambda: __import__("sw_part").shell(doc, 2.0))
    finally:
        ev["passed"] = sum(1 for s in ev["steps"] if s["verdict"] == "pass")
        ev["total"] = len(ev["steps"])
        ev["verdict"] = "pass" if ev["passed"] == ev["total"] else "partial"
        ev["note"] = (
            "★ 每个基础操作一行；★ 判据是**特征树增量**（★ 不靠返回值 —— 事实 8）。"
            "★ 没建成的会带 err。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
            encoding="utf-8",
        )
        print(
            "  \u2500\u2500 **%d/%d** \u901a\u8fc7 \u21d2 %s"
            % (ev["passed"], ev["total"], str(ev["verdict"]).upper())
        )
        print("  产物：%s" % OUT)
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
