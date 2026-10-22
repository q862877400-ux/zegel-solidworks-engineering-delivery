"""★ 真机：B3 批草图编辑 7 个逐个试（★ 判据**分操作定**：计数增量 或 几何增量）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_b3_sketch_edit.py
# 定位:   ★ 2026-10-03（轮 465）★ `specs/201-toolbar-gaps` **B3 批**的真机探针。
#   ★★★ **判据按操作分**（★ 这是本探针的关键 —— 一个判据套不住 7 个操作）：
#     ```
#     ★ 计数涨：等距(offset) / 圆角(fillet) / 线性阵列 / 圆周阵列
#     ★ 计数减：剪裁(trim) —— ★ 剪掉一段 ⇒ **段数会掉**，拿"涨"当判据会误判成失败！
#     ★ 几何变：延伸(extend) —— ★ 段数不变，改的是**长度/端点**
#     ★ 特例：交叉曲线 —— ★ 官方要求**3D 草图 + 两个相交面**，本探针只用 2D 草图 ⇒
#       ★ **单独记「前置不满足」**，不拿它当"能力坏了"（★ 本会话已栽过：判据错 ⇒ 能力看着坏）
#     ```
#   ⚠ 每个操作**单独开一张新草图**（★ 免副作用污染 —— 本会话在"圆角改边序"上栽过）✓
# 官方依据: `C:\swapi\types\ISketchManager\` 的 7 个成员 + 3 个枚举（见 `sw_sketch_edit_
#           ops.py` 来源块）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 见上（按操作分）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R / "scripts"))
OUT = R / "output" / "b3-sketch-edit-evidence.json"


def main() -> int:
    import sw_connect
    import sw_part as p
    import sw_sketch as SK
    import sw_sketch_edit_ops as E
    from sw_connect import get_com_member, safe_get_com_member

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "B3 批：草图编辑 7 个逐个真机试（specs/201-toolbar-gaps）",
        "judge": "计数增量 / 几何增量（按操作分）",
        "items": [],
    }

    def fresh():
        d = sw_connect.new_document(sw, "part")
        p.start_sketch(d, plane_name="Front Plane")
        return d

    def nseg(d):
        sk = get_com_member(get_com_member(d, "SketchManager"), "ActiveSketch")
        return int(SK.count_segments(sk) or 0)

    def seg_len_sum(d):
        """★ 几何判据：所有草图段的**长度之和**（★ 延伸会改变它，而段数不变）。"""
        sk = get_com_member(get_com_member(d, "SketchManager"), "ActiveSketch")
        tot = 0.0
        for s in SK.get_sketch_segments(sk) or []:
            try:
                tot += float(get_com_member(s, "GetLength") or 0.0)
            except Exception:
                pass
        return round(tot, 9)

    def run(zh, setup, act, judge="count_change", note=""):
        row = {"zh": zh, "verdict": "不能", "judge": judge}
        doc = None
        try:
            doc = fresh()
            setup(doc)
            n0, l0 = nseg(doc), seg_len_sum(doc)
            r = act(doc)
            n1, l1 = nseg(doc), seg_len_sum(doc)
            row.update(
                {
                    "seg": [n0, n1],
                    "len": [l0, l1],
                    "ret": (str(r)[:24] if r is not None else "None"),
                }
            )
            if judge == "count_up":
                row["built"] = n1 > n0
            elif judge == "count_change":
                row["built"] = n1 != n0
            elif judge == "geom_change":
                row["built"] = (n1 != n0) or (abs(l1 - l0) > 1e-9)
            else:
                row["built"] = (n1 != n0) or (abs(l1 - l0) > 1e-9)
            row["verdict"] = "能" if row["built"] else "不能"
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
        if note:
            row["note"] = note
        ev["items"].append(row)
        print(
            "  %-16s %-3s  段 %s\u2192%s  %s"
            % (
                zh,
                row["verdict"],
                (row.get("seg") or [None])[0],
                (row.get("seg") or [None, None])[1],
                str(row.get("err") or "")[:58],
            )
        )
        return row

    #: \u2460 \u526a\u88c1\uff08\u2605 \u5224\u636e = \u6bb5\u6570**\u53d8\u5316**\uff09
    #: \u2014\u2014 \u4e00\u6761\u76f8\u4ea4\u7684\u7ebf + \u5706
    def s_trim(d):
        p.sketch_line(d, -30.0, 0.0, 30.0, 0.0)
        p.sketch_circle(d, 0.0, 0.0, 10.0)

    run(
        "剪裁-最近",
        s_trim,
        lambda d: E.sketch_trim(d, "index:0", option="closest"),
        "count_change",
    )

    #: \u2461 \u5ef6\u4f38\uff08\u2605 \u5224\u636e = \u51e0\u4f55\u53d8 \u2014\u2014 \u
    #: 6bb5\u6570\u4e0d\u53d8\uff09
    def s_ext(d):
        p.sketch_line(d, -20.0, 0.0, 0.0, 0.0)
        p.sketch_line(d, 25.0, 0.0, 40.0, 0.0)

    run("延伸实体", s_ext, lambda d: E.sketch_extend(d, "index:0"), "geom_change")

    #: \u2462 \u7b49\u8ddd\uff08\u2605 \u5224\u636e = \u6bb5\u6570\u6da8\uff09
    def s_off(d):
        p.sketch_corner_rectangle(d, -20.0, -15.0, 20.0, 15.0)

    run("等距实体", s_off, lambda d: E.sketch_offset(d, "index:0", 5.0), "count_up")

    #: \u2463 \u5706\u89d2\uff08\u2605 \u4e24\u6761\u76f8\u4ea4\u7ebf\uff09
    def s_fil(d):
        p.sketch_line(d, -20.0, 0.0, 0.0, 0.0)
        p.sketch_line(d, 0.0, 0.0, 0.0, 20.0)

    run(
        "绘制圆角",
        s_fil,
        lambda d: E.sketch_fillet(d, "index:0,index:1", 5.0),
        "count_change",
    )

    #: \u2464 \u7ebf\u6027\u9635\u5217
    def s_lp(d):
        p.sketch_circle(d, -20.0, 0.0, 4.0)

    run(
        "线性草图阵列",
        s_lp,
        lambda d: E.sketch_linear_pattern(
            d, "index:0", num_x=3, num_y=1, spacing_x_mm=15.0
        ),
        "count_up",
    )

    #: \u2465 \u5706\u5468\u9635\u5217
    def s_cp(d):
        p.sketch_circle(d, 15.0, 0.0, 3.0)

    run(
        "圆周草图阵列",
        s_cp,
        lambda d: E.sketch_circular_pattern(
            d, "index:0", arc_radius_mm=15.0, arc_angle_deg=360.0, pattern_num=4
        ),
        "count_up",
    )

    #: \u2466 \u4ea4\u53c9\u66f2\u7ebf\uff08\u2605 \u524d\u7f6e\u4e0d\u6ee1\u8db3\uff1a\
    #: u5b98\u65b9\u8981 3D \u8349\u56fe + \u4e24\u4e2a\u76f8\u4ea4\u9762\uff09
    run(
        "交叉曲线",
        lambda d: p.sketch_circle(d, 0.0, 0.0, 10.0),
        lambda d: E.sketch_intersect_curves(d),
        "count_change",
        note="★ 官方前置：3D 草图 + 两个相交面；本探针只有 2D 草图 ⇒ 失败不构成能力结论",
    )

    ok = sum(1 for i in ev["items"] if i["verdict"] == "能")
    ev["can"], ev["total"] = ok, len(ev["items"])
    ev["verdict"] = "pass" if ok == ev["total"] else "partial"
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print(
        "  \u2500\u2500 **\u80fd %d / \u5171 %d** \u21d2 %s"
        % (ok, ev["total"], str(ev["verdict"]).upper())
    )
    print("  \u4ea7\u7269\uff1a%s" % OUT)
    try:
        sw.CommandInProgress = False
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
