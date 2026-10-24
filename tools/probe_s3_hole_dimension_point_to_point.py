"""★ S3 测量：孔心用**点-点尺寸**约束到板角（同行已验证的选法范围内）。

## 上一版为什么崩了

我先试的是「孔心（`ISketchPoint`）+ 边线（`ISketchLine`）」⇒
`AddDimension2` 直接让 SolidWorks 进程挂掉（`RPC 服务器不可用`，护栏重启实例）。

## 本版改用什么

`known-facts.md` **事实 422**（轮 542 真机验过）的可行选法是：

| 选法 | 结果 |
|---|---|
| 一条线段 | ok=True · 尺寸 0 → H:1 → V:1 |
| **两个端点** | ok=True · 尺寸 0 → H:1 → V:1 |
| 不选 | ok=False · 尺寸 0 → H:0 → V:0 |

⇒ 孔心是 `ISketchPoint`，矩形角点也是 `ISketchPoint` ⇒ **两点选法在已验证范围内**。
  「孔心 ↔ 板角」的水平尺寸就是孔的 X 偏移、竖直尺寸就是 Y 偏移 ——
  这正是「改板宽 → 孔位联动」需要的那两个尺寸。

## 判据

★ 只用**尺寸计数**（事实 422：返回值不可信 —— `AddVerticalDimension2` 回 `None` 但尺寸照样加上）。
★ 计数走 `IFeature.GetFirstDisplayDimension` + `IDisplayDimension.GetNext2`。

## 只读

建临时文档；`CommandInProgress`；收尾只关**自己开的**。
⚠ 崩过之后再跑要先 `reclaim_solidworks --probe` 看会话是否健康。
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
from scripts.sw_sketch import active_sketch as _active_sketch  # noqa: E402
from scripts.sw_sketch import get_sketch_segments as _get_segments  # noqa: E402
from scripts.sw_sketch_dimensions import (  # noqa: E402
    add_horizontal_dimension,
    add_vertical_dimension,
    count_sketch_dimensions,
)

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_s3_hole_dimension_point_to_point.py
# 定位:   specs/350-first-part-delivery T008 —— 「改板宽 → 孔位联动」的前提：
#          孔心能否用尺寸约束到板角。上一版用「点+线」把 SolidWorks 弄崩了，
#          本版改用 known-facts 事实 422 已验证的「两个端点」选法。
# 官方依据: IModelDoc2.AddHorizontalDimension2 / AddVerticalDimension2（X/Y/Z = 文字放置点）
#           ISketchArc.GetCenterPoint2 / ISketchLine.GetStartPoint2（取两个点）
#           IFeature.GetFirstDisplayDimension + IDisplayDimension.GetNext2（数尺寸）
#           事实 422：必须先选中实体；判据用尺寸计数，不看返回值
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────



def _pick(obj) -> bool:
    ok, v = _try(lambda: p_._select_com_object(obj, append=True, mark=0))
    return bool(ok and v)


def main() -> int:
    ev: dict = {"probe": "s3-hole-dimension-point-to-point", "trials": []}
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
        for (hx, hy) in ((10.0, 10.0), (90.0, 10.0), (10.0, 50.0), (90.0, 50.0)):
            _try(
                lambda x=hx, y=hy: get_com_member(
                    doc.SketchManager,
                    "CreateCircleByRadius",
                    x / 1000.0,
                    y / 1000.0,
                    0.0,
                    3.0 / 1000.0,
                )
            )
        sk = _active_sketch(doc)
        segs = list(_get_segments(sk) or [])
        arcs = [s for s in segs if _member(s, "GetCenterPoint2") is not None]
        lines = [s for s in segs if _member(s, "GetCenterPoint2") is None]
        ev["segments"] = len(segs)
        ev["arcs"] = len(arcs)
        ev["lines"] = len(lines)
        d0 = count_sketch_dimensions(doc)
        ev["dims_initial"] = d0
        print("① 草图：段 %d（圆 %d · 线 %d）· 尺寸 %s" % (len(segs), len(arcs), len(lines), d0))
        if not arcs or not lines:
            ev["conclusion"] = "★ 实体不足，没法测"
            print(ev["conclusion"])
            return 1

        center = _member(arcs[0], "GetCenterPoint2")
        corner = _member(lines[0], "GetStartPoint2")
        if center is None or corner is None:
            ev["conclusion"] = "★ 取不到孔心或角点"
            print(ev["conclusion"])
            return 1

        def _trial(tag: str, fn, x: float, y: float) -> dict:
            doc.ClearSelection2(True)
            picked = [("孔心", _pick(center)), ("角点", _pick(corner))]
            before = count_sketch_dimensions(doc)
            ok, ret = _try(fn, doc, x, y)
            after = count_sketch_dimensions(doc)
            #: ★ 只有两个读数都是有效非负数时才算得出增量（-1 = 没数到）
            usable = (
                before is not None
                and after is not None
                and before >= 0
                and after >= 0
            )
            row = {
                "tag": tag,
                "picked": picked,
                "call_ok": ok,
                "call_ret": str(ret)[:80],
                "dims": "%s → %s" % (before, after),
                "added": (after - before) if usable else None,
            }
            ev["trials"].append(row)
            return row

        #: ── 对照组：不选直接调 ──
        doc.ClearSelection2(True)
        b = count_sketch_dimensions(doc)
        ok_c, ret_c = _try(add_horizontal_dimension, doc, 0.0, 0.0)
        a = count_sketch_dimensions(doc)
        ev["trials"].append(
            {
                "tag": "对照 · 不选直接调",
                "call_ok": ok_c,
                "call_ret": str(ret_c)[:80],
                "dims": "%s → %s" % (b, a),
                "added": (a - b) if b is not None and a is not None and a >= 0 else None,
            }
        )
        print("② 对照（不选）：尺寸 %s → %s" % (b, a))

        #: ── A：两点 → 水平尺寸 ──
        row_a = _trial("A · 孔心+角点 → 水平尺寸", add_horizontal_dimension, 5.0, 30.0)
        print("③ A：选中 %s · 尺寸 %s" % (row_a["picked"], row_a["dims"]))

        #: ── B：两点 → 竖直尺寸 ──
        row_b = _trial("B · 孔心+角点 → 竖直尺寸", add_vertical_dimension, -12.0, 8.0)
        print("④ B：选中 %s · 尺寸 %s" % (row_b["picked"], row_b["dims"]))

        n = [t.get("added") for t in ev["trials"]]
        ev["verdict"] = {
            "control_added": n[0],
            "horizontal_added": n[1],
            "vertical_added": n[2],
        }
        ok = bool((n[1] or 0) > 0 and (n[2] or 0) > 0)
        ev["ok"] = ok
        ev["conclusion"] = (
            "★ 孔心用点-点尺寸建成：水平 +%s、竖直 +%s（对照不选 +%s）"
            " ⇒ 「改板宽 → 孔位联动」有可行路径"
            % (n[1], n[2], n[0])
            if ok
            else "★ 未建成，见 trials（判据用尺寸计数，不看返回值）"
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
        dest = R / "output" / "s3-hole-dimension-point-to-point.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())
