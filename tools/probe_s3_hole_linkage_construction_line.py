"""★ S3 测量：用**构造线单段长度**把孔位绑到板边，让孔随板宽联动。

## 为什么用这个方案

E2 的负例明令含「孔未随板宽变化」⇒ T011 的「板变宽、孔不动」不合格。
而孔位参数化只有两条路：

| 路 | 状态 |
|---|---|
| 给「孔心 ↔ 板角」加**跨实体**尺寸 | ❌ 第 13 轮真机两次把 SolidWorks 弄崩 |
| 给它加**单段长度**尺寸 | ✅ `known-facts` 事实 422 验过（一条线段 ⇒ 得该段长度） |

⇒ 本轮把「孔心到边线的距离」**转写成一条构造线的长度**：

```
边长 100 × 60 的矩形 + 圆心在 (90, 10) 的孔
构造线：从 (100, 10) 到 (90, 10)
  · 起点落在**右边线**上（sgCOINCIDENT：点在线上）
  · 终点与**孔心**重合（sgCOINCIDENT）
给这条构造线加**水平尺寸** ⇒ 得到 10mm 的偏移
```

板宽 100 → 120 时右边线右移 ⇒ 构造线起点跟走 ⇒ 因为长度被尺寸锁住（10mm），
终点（孔心）也右移 ⇒ **孔跟着动**。

## 判据（都是独立读数，不看返回值）

| 读数 | 怎么取 |
|---|---|
| 构造线造出来没有 | `ISketchSegment.ConstructionGeometry` |
| 尺寸加上没有 | `count_sketch_dimensions` |
| **孔心在哪** | `ISketchArc.GetCenterPoint2()` → `ISketchPoint.X` / `.Y`（米） |
| 板宽 | `IFeature.GetFirstDisplayDimension` 里值 ≈100 的那条 |

★ 关键判据：改宽度后**孔心 X 是否从 90 变成 110**。

## 只读

建临时文档；`CommandInProgress`（铁律 2）；收尾只关**自己开的**。
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as c_  # noqa: E402
from scripts import sw_part as p_  # noqa: E402
from scripts.sw_connect import get_com_member  # noqa: E402
from scripts.sw_connect import try_call as _try  # noqa: E402
from scripts.sw_connect import try_member as _member  # noqa: E402
from scripts.sw_document_data import update_dimension_mm  # noqa: E402
from scripts.sw_sketch import active_sketch as _active_sketch  # noqa: E402
from scripts.sw_sketch import get_sketch_segments as _get_segments  # noqa: E402
from scripts.sw_sketch_dimensions import (  # noqa: E402
    add_horizontal_dimension,
    count_sketch_dimensions,
)

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_s3_hole_linkage_construction_line.py
# 定位:   specs/350-first-part-delivery T011 / E2 —— 让孔随板宽联动。
#           做法：把「孔心到边线的距离」转写成**一条构造线的长度**，
#           因为单段长度尺寸是 known-facts 事实 422 验过的选法，
#           而跨实体点-点/点-线尺寸在第 13 轮真机两次崩掉。
# 官方依据: ISketchManager.CreateCenterLine（6 参，米）· ISketchSegment.ConstructionGeometry
#           ISketchArc.GetCenterPoint2 · ISketchPoint.X / .Y（米）
#           IModelDoc2.AddHorizontalDimension2（X/Y/Z = 文字放置点）
#           ISketchManager.AddRelation（sgCOINCIDENT：点在线上 / 两点重合）
#           IFeature.GetFirstDisplayDimension + IDisplayDimension.GetNext2（数尺寸）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────



def _pick(obj) -> bool:
    """★ 选中一个实体。

    ★ 照抄 `tools/probe_hv_dimension_with_selection.py`（轮 542 验过）的调法：
      **单段用 `append=False`**，而不是 `append=True`。
    """
    ok, v = _try(lambda: p_._select_com_object(obj, append=False, mark=0))
    return bool(ok and v)


def _center_xy_mm(arc) -> dict:
    """★ 孔心坐标（毫米）—— 这是判「孔动没动」的独立读数。"""
    pt = _member(arc, "GetCenterPoint2")
    if pt is None:
        return {"ok": False}
    x = _member(pt, "X")
    y = _member(pt, "Y")
    return {
        "ok": x is not None and y is not None,
        "x_mm": round(float(x) * 1000.0, 4) if x is not None else None,
        "y_mm": round(float(y) * 1000.0, 4) if y is not None else None,
    }


def _dims(doc) -> list:
    out: list = []
    try:
        from scripts.sw_feature_readback import feature_names

        names = feature_names(doc)
    except Exception:  # noqa: BLE001
        return out
    for nm in names:
        if not (nm.startswith("草图") or nm.lower().startswith("sketch")):
            continue
        ok_f, feat = _try(get_com_member, doc, "FeatureByName", nm)
        if not ok_f or feat is None:
            continue
        dd = _member(feat, "GetFirstDisplayDimension")
        g = 0
        while dd is not None and g < 100:
            g += 1
            dim = _member(dd, "GetDimension")
            if dim is not None:
                full = _member(dim, "FullName")
                sv = _member(dim, "SystemValue")
                out.append(
                    {
                        "sketch": nm,
                        "full_name": str(full) if full else "",
                        "value_mm": round(float(sv) * 1000.0, 4) if sv is not None else None,
                    }
                )
            dd = _member(dd, "GetNext2")
    return out


def _seg_info(seg) -> dict:
    """★ 判断是不是构造线，并取两端点坐标（毫米）。"""
    cg = _member(seg, "ConstructionGeometry")
    info = {"construction": bool(cg)}
    a = _member(seg, "GetStartPoint2")
    b = _member(seg, "GetEndPoint2")
    for tag, pt in (("start", a), ("end", b)):
        if pt is not None:
            info[tag + "_x_mm"] = round(float(_member(pt, "X") or 0.0) * 1000.0, 4)
            info[tag + "_y_mm"] = round(float(_member(pt, "Y") or 0.0) * 1000.0, 4)
    return info


def main() -> int:
    ev: dict = {"probe": "s3-hole-linkage-construction-line"}
    sw = doc = None
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        doc = c_.new_document(sw, "part")

        p_.start_sketch(doc, plane_name="Front Plane")
        p_.sketch_corner_rectangle(doc, 0.0, 0.0, 100.0, 60.0)
        #: 一个右侧孔：圆心 (90, 10)、半径 3
        _try(
            lambda: get_com_member(
                doc.SketchManager, "CreateCircleByRadius", 0.090, 0.010, 0.0, 0.003
            )
        )
        #: 构造线：从右边线上的 (100, 10) 到孔心 (90, 10)
        ok_cl, center_line = _try(
            lambda: get_com_member(
                doc.SketchManager,
                "CreateCenterLine",
                0.100,
                0.010,
                0.0,
                0.090,
                0.010,
                0.0,
            )
        )
        ev["create_center_line"] = {"ok": ok_cl, "ret": str(center_line)[:60]}
        print("① 构造线：ok=%s" % ok_cl)

        sk = _active_sketch(doc)
        segs = list(_get_segments(sk) or [])
        ev["segments"] = len(segs)
        infos = [(_seg_info(s), s) for s in segs]
        ev["constr_count"] = sum(1 for i, _ in infos if i.get("construction"))
        print("② 草图段 %d · 其中构造线 %d" % (len(segs), ev["constr_count"]))
        if not ok_cl or center_line is None:
            ev["conclusion"] = "★ 构造线没建成"
            print(ev["conclusion"])
            return 1

        circle = next((s for i, s in infos if _member(s, "GetCenterPoint2") is not None), None)
        if circle is None:
            ev["conclusion"] = "★ 找不到圆"
            print(ev["conclusion"])
            return 1
        before = _center_xy_mm(circle)
        ev["hole_before"] = before
        print("③ 孔心（改动前）：x=%s y=%s mm" % (before.get("x_mm"), before.get("y_mm")))

        #: ④ 先给**矩形底边**加水平尺寸 ⇒ 得到板宽（单段，放置点 0,0,0）
        #:    ★ 放置点传 0,0,0 —— 事实 422 原话「三个参数只是**放置点**，传 0,0,0 就行」；
        #:    官方 Remarks 另说尺寸按**位置**放置，位置不落在可见几何上会失败。
        #:    第 13 轮我传了 95,20 这种远离实体的点，可能就是崩溃的原因之一。
        bottom = next(
            (
                s
                for s in segs
                if _member(s, "GetCenterPoint2") is None
                and not _seg_info(s).get("construction")
            ),
            None,
        )
        w_before = count_sketch_dimensions(doc)
        ok_w, ret_w = False, None
        if bottom is not None:
            doc.ClearSelection2(True)
            _pick(bottom)
            ok_w, ret_w = _try(add_horizontal_dimension, doc, 0.0, 0.0)
        w_after = count_sketch_dimensions(doc)
        ev["add_width_dim"] = {
            "call_ok": ok_w,
            "call_ret": str(ret_w)[:60],
            "dims": "%s → %s" % (w_before, w_after),
        }
        print("④a 给矩形底边加水平尺寸：尺寸 %s → %s" % (w_before, w_after))

        #: ④b 给构造线加**水平尺寸**（单段 ⇒ 事实 422 验过的选法，放置点同样 0,0,0）
        doc.ClearSelection2(True)
        picked = _pick(center_line)
        d_before = count_sketch_dimensions(doc)
        ok_hd, ret_hd = _try(add_horizontal_dimension, doc, 0.0, 0.0)
        d_after = count_sketch_dimensions(doc)
        ev["add_dim"] = {
            "picked": picked,
            "call_ok": ok_hd,
            "call_ret": str(ret_hd)[:60],
            "dims": "%s → %s" % (d_before, d_after),
            "added": (d_after - d_before)
            if (
                d_before is not None
                and d_after is not None
                and d_before >= 0
                and d_after >= 0
            )
            else None,
        }
        print("④b 给构造线加水平尺寸：选中=%s · 尺寸 %s → %s" % (picked, d_before, d_after))

        #: ⑤ 找宽度尺寸（值 ≈100 的那条），改成 120
        dims = _dims(doc)
        ev["dims"] = dims
        width = next(
            (
                d
                for d in dims
                if d.get("value_mm") is not None and abs(d["value_mm"] - 100.0) < 1.0
            ),
            None,
        )
        ev["width_dim"] = width
        if width is None:
            ev["conclusion"] = "★ 没有值≈100 的尺寸 ⇒ 板宽不是参数"
            print(ev["conclusion"])
            return 1
        ok_u, upd = _try(update_dimension_mm, doc, width["full_name"], 120.0)
        ev["update_width"] = {"ok": ok_u, "detail": str(upd)[:200]}
        print("⑤ 板宽 → 120mm：%s" % ("ok" if ok_u else str(upd)[:60]))

        after = _center_xy_mm(circle)
        ev["hole_after"] = after
        print("⑥ 孔心（改动后）：x=%s y=%s mm" % (after.get("x_mm"), after.get("y_mm")))

        x0, x1 = before.get("x_mm"), after.get("x_mm")
        moved = None
        if x0 is not None and x1 is not None:
            moved = round(x1 - x0, 4)
        ev["verdict"] = {
            "dimension_added": (ev["add_dim"] or {}).get("added"),
            "hole_before_x_mm": x0,
            "hole_after_x_mm": x1,
            "hole_shift_mm": moved,
            "expect_shift_mm": 20.0,
        }
        ok = bool(moved is not None and abs(moved - 20.0) < 1.0)
        ev["ok"] = ok
        ev["conclusion"] = (
            "★ 孔随板宽联动成立：孔心 x %s → %s mm（位移 %s，期望 +20）"
            % (x0, x1, moved)
            if ok
            else "★ 未联动：见 verdict（孔心位移 %s，期望 +20）" % moved
        )
        print(ev["conclusion"])
        return 0 if ok else 1
    except Exception as exc:  # noqa: BLE001
        import traceback

        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        ev["traceback"] = traceback.format_exc()[-1200:]
        print("★ 失败：", ev["err"])
        return 1
    finally:
        if sw is not None and doc is not None:
            try:
                sw.CloseDoc(doc.GetTitle())
            except Exception:  # noqa: BLE001
                pass
        if sw is not None:
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
        ev["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        dest = R / "output" / "s3-hole-linkage-construction-line.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())
