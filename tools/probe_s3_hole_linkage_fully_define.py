"""★ S3 测量：孔与板轮廓放**同一张草图** + `FullyDefineSketch`，孔会不会随板宽联动？

## 为什么值得试

E2 的硬要求是「孔随板宽变化」（`ENGINEERING-PATH` 第四节 E2 的负例逐字）。
而给孔心加**尺寸**这条路在本机已退化（事实 560：`AddHorizontalDimension2` /
`AddDimension2` 会崩进程）。

但还有一条**没试过、且不依赖那两个方法**的路：

| 手段 | 状态 |
|---|---|
| 新建尺寸（`AddDimension2` / `AddHorizontalDimension2`） | ❌ 本机崩（事实 560） |
| **`ISketchManager.FullyDefineSketch`** | ✅ 可调（第 12 轮：`call_ok=True`、状态 2→3） |

第 12 轮真机量到：把矩形 + 4 个孔圆放**同一张草图**，`FullyDefineSketch` 之后

```
关系 5 → 21（全关系组）/ 19（只加尺寸组）
尺寸 0 → 1
状态 2 → 3
```

⇒ **它加了 16 条关系**。若其中有些把孔心绑到了矩形边上（重合 / 中线 / 共线），
  那么改板宽尺寸时孔**就会跟着动** —— 那 E2 的联动就能成立，且完全不需要 HV 尺寸。

## 判据（只用独立读数）

| 读数 | 手段 |
|---|---|
| 孔心坐标（毫米） | `ISketchArc.GetCenterPoint2` → `ISketchPoint.X/.Y`（第 14/18 轮验过可读） |
| 板宽尺寸 | `IFeature.GetFirstDisplayDimension` 里值 ≈100 的那条 |
| 改尺寸 | `update_dimension_mm`（`SetSystemValue3`，**改已有**，不新建 ⇒ 不崩） |

★ 不预设结论：位移 0 也是结果，照样记。

## 只读纪律

建临时文档；`CommandInProgress`；收尾核**文档数归零**。
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
from scripts.sw_connect import (  # noqa: E402
    create_empty_dispatch_variant as _nothing,
)
from scripts.sw_connect import get_com_member, open_doc_count  # noqa: E402
from scripts.sw_connect import try_call as _try  # noqa: E402
from scripts.sw_connect import try_member as _member  # noqa: E402
from scripts.sw_document_data import update_dimension_mm  # noqa: E402
from scripts.sw_feature_readback import feature_names  # noqa: E402
from scripts.sw_sketch import active_sketch as _active_sketch  # noqa: E402
from scripts.sw_sketch_dimensions import count_sketch_dimensions  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · S3 测量）
# 文件:   tools/probe_s3_hole_linkage_fully_define.py
# 定位:   E2「孔随板宽联动」的最后一条未试路径：孔与轮廓同草图 + FullyDefineSketch
#          加的关系，是否足以让孔随主参数移动。不依赖已退化的事实 560 那条方法族。
# 官方依据: ISketchManager.FullyDefineSketch（10 参；Placement 只能 0/1；
#           RelationsToApply = swSketchFullyDefineRelationType_e 位掩码 1023；
#           Datum 传 VARIANT Nothing —— 第 12 轮验过 call_ok=True）·
#          ISketchArc.GetCenterPoint2 → ISketchPoint.X/.Y ·
#          IDimension.SetSystemValue3（经 update_dimension_mm，单位米）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

REL_ALL = 1023
HOLES = ((10.0, 10.0), (90.0, 10.0), (10.0, 50.0), (90.0, 50.0))
EXPECT_SHIFT_MM = 20.0


def _hole_centers(sk) -> list:
    out = []
    ok, segs = _try(get_com_member, sk, "GetSketchSegments")
    for seg in list(segs) if ok and segs else []:
        pt = _member(seg, "GetCenterPoint2")
        if pt is None:
            continue
        x, y = _member(pt, "X"), _member(pt, "Y")
        if x is not None and y is not None:
            out.append((round(float(x) * 1000.0, 2), round(float(y) * 1000.0, 2)))
    return sorted(out)


def _all_dims(doc) -> list:
    """★ 把所有尺寸的原名与值都列出来 —— 不猜「哪个是板宽」。"""
    out = []
    for nm in feature_names(doc) or []:
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
                sv = _member(dim, "SystemValue")
                out.append({
                    "sketch": nm,
                    "full_name": str(_member(dim, "FullName") or ""),
                    "value_mm": round(float(sv) * 1000.0, 3) if sv is not None else None,
                })
            dd = _member(dd, "GetNext2")
    return out


def _width_dim(doc) -> dict | None:
    for nm in feature_names(doc) or []:
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
                sv = _member(dim, "SystemValue")
                if sv is not None and abs(float(sv) * 1000.0 - 100.0) < 1.0:
                    return {"full_name": str(_member(dim, "FullName") or ""),
                            "value_mm": round(float(sv) * 1000.0, 3)}
            dd = _member(dd, "GetNext2")
    return None


def main() -> int:
    ev: dict = {"probe": "s3-hole-linkage-fully-define"}
    sw = doc = None
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        doc = c_.new_document(sw, "part")

        #: ① 一张草图：矩形 + 4 个孔圆
        p_.start_sketch(doc, plane_name="Front Plane")
        p_.sketch_corner_rectangle(doc, 0.0, 0.0, 100.0, 60.0)
        for (hx, hy) in HOLES:
            _try(
                lambda x=hx, y=hy: get_com_member(
                    doc.SketchManager, "CreateCircleByRadius",
                    x / 1000.0, y / 1000.0, 0.0, 3.0 / 1000.0,
                )
            )
        sk = _active_sketch(doc)
        ev["holes_initial"] = _hole_centers(sk)
        ev["status_initial"] = _member(sk, "GetConstrainedStatus")
        ev["dims_initial"] = count_sketch_dimensions(doc)
        print("① 初始：孔心 %s · 状态 %s · 尺寸 %s"
              % (ev["holes_initial"], ev["status_initial"], ev["dims_initial"]))
        if len(ev["holes_initial"]) != 4:
            ev["conclusion"] = "★ 没画出 4 个孔 ⇒ 测不了"
            print(ev["conclusion"])
            return 1

        #: ② FullyDefineSketch（第 12 轮验过的参数）
        ok_f, ret_f = _try(
            lambda: get_com_member(
                doc.SketchManager, "FullyDefineSketch",
                True, REL_ALL, REL_ALL, True,
                1, _nothing(), 1, _nothing(), 0, 0,
            )
        )
        ev["fully_define"] = {"ok": ok_f, "ret": str(ret_f)[:60],
                              "dims_after": count_sketch_dimensions(doc),
                              "status_after": _member(sk, "GetConstrainedStatus")}
        print("② FullyDefineSketch：ok=%s · 尺寸 %s · 状态 %s"
              % (ok_f, ev["fully_define"]["dims_after"],
                 ev["fully_define"]["status_after"]))

        #: ③ 找板宽尺寸（≈100）
        ev["all_dims"] = _all_dims(doc)
        print("   所有尺寸：%s" % ev["all_dims"])
        w = _width_dim(doc)
        ev["width_dim"] = w
        print("③ 板宽尺寸：%s" % w)
        if w is None:
            ev["conclusion"] = "★ 没找到值≈100 的尺寸 ⇒ 改不了主参数"
            print(ev["conclusion"])
            return 1

        #: ④ 改 100 → 120，再看孔心
        ok_u, upd = _try(update_dimension_mm, doc, w["full_name"], 120.0)
        ev["update"] = {"ok": ok_u, "detail": str(upd)[:200]}
        after = _hole_centers(sk)
        ev["holes_after"] = after
        shifts = [
            round(b[0] - a[0], 2)
            for a, b in zip(ev["holes_initial"], after)
        ]
        ev["shifts_mm"] = shifts
        moved = [s for s in shifts if abs(s) > 1.0]
        print("④ 改板宽 120：ok=%s · 孔心 %s · 位移 %s"
              % (ok_u, after, shifts))

        ok = bool(moved) and any(abs(abs(s) - EXPECT_SHIFT_MM) < 1.0 for s in moved)
        ev["ok"] = ok
        ev["conclusion"] = (
            "★ 孔随板宽联动成立（经 FullyDefineSketch 的关系）：位移 %s，期望 ±%s"
            % (shifts, EXPECT_SHIFT_MM)
            if ok
            else "★ 孔仍未联动：位移 %s ⇒ FullyDefineSketch 加的关系没有把孔绑到板边"
            % shifts
        )
        print(ev["conclusion"])
        return 0 if ok else 1
    except Exception as exc:  # noqa: BLE001
        import traceback

        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        ev["traceback"] = traceback.format_exc()[-1000:]
        print("★ 失败：", ev["err"])
        return 1
    finally:
        if sw is not None:
            if doc is not None:
                ok_t, title = _try(get_com_member, doc, "GetTitle")
                if ok_t and title:
                    _try(sw.CloseDoc, str(title))
            ev["docs_left"] = open_doc_count(sw)
            print("   收尾后剩余文档数：%s" % ev["docs_left"])
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
        ev["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        dest = R / "output" / "s3-hole-linkage-fully-define.json"
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("   证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())
